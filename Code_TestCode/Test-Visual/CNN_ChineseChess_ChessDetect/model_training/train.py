"""
中国象棋棋子分类 CNN 训练脚本

数据来源: data_collector.py 采集的 dataset/ 目录（7 类，128x128 JPG）
输出文件: chess_cnn.pt（模型权重）, train_history.json（训练记录）, train_curve.png（训练曲线）

用法:
    python train_cnn.py
"""

import os
import sys
import glob
import random
import time
import json
from collections import Counter

import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from chess_cnn_model import ChessCNN

# ==================== 配置 ====================

DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data_collection/dataset')
CLASSES = ['JIANG', 'SHI', 'CHE', 'MA', 'PAO', 'XIANG', 'BING']
NUM_CLASSES = len(CLASSES)

IMG_SIZE = 128        # 与 data_collector.py 中 SAVE_SIZE 一致
BATCH_SIZE = 32
EPOCHS = 1000
LR = 1e-3
WEIGHT_DECAY = 1e-4
PATIENCE = 10         # 验证集 loss 连续多少轮不下降则早停
TRAIN_RATIO = 0.8
SEED = 42
LABEL_SMOOTHING = 0.1 # 标签平滑系数，缓解过拟合

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chess_cnn.pt')
HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'train_history.json')
CURVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'train_curve.png')

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


# ==================== 工具函数 ====================

class EMA:
    """指数移动平均，用于平滑训练指标"""
    def __init__(self, decay=0.95):
        self.decay = decay
        self.value = None

    def update(self, val):
        if self.value is None:
            self.value = val
        else:
            self.value = self.decay * self.value + (1 - self.decay) * val
        return self.value


def stratified_split(file_list, train_ratio, seed):
    """
    分层抽样分割数据集，确保每个类别按相同比例分配到训练集和验证集。
    比 random.shuffle 更可靠，特别是数据量少时。
    """
    # 按类别分组
    class_files = {}
    for filepath, label in file_list:
        class_files.setdefault(label, []).append((filepath, label))

    train_list, val_list = [], []
    rng = random.Random(seed)

    for label, files in sorted(class_files.items()):
        rng.shuffle(files)
        split = max(1, int(len(files) * train_ratio))
        train_list.extend(files[:split])
        val_list.extend(files[split:])

    return train_list, val_list


def compute_class_weights(file_list, num_classes):
    """
    根据训练集中各类别的样本数量，计算逆频率权重。
    样本越少的类别权重越高，缓解类别不平衡问题。
    """
    counts = Counter(label for _, label in file_list)
    total = sum(counts.values())
    weights = []
    for c in range(num_classes):
        w = total / (num_classes * max(counts.get(c, 1), 1))
        weights.append(w)
    return torch.tensor(weights, dtype=torch.float32)


# ==================== 数据集 ====================

class ChessDataset(Dataset):
    """从 dataset/ 目录加载棋子图片"""

    def __init__(self, file_list, transform=None):
        """
        Args:
            file_list: [(filepath, class_idx), ...]
            transform: torchvision transforms（期望输入 numpy uint8 RGB）
        """
        self.file_list = file_list
        self.transform = transform

    def __len__(self):
        return len(self.file_list)

    def __getitem__(self, idx):
        filepath, label = self.file_list[idx]
        # Windows 中文路径兼容：用 np.fromfile + imdecode
        img_bytes = np.fromfile(filepath, dtype=np.uint8)
        img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)
        if img is None:
            raise RuntimeError(f'无法读取图片: {filepath}')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # BGR -> RGB

        if self.transform:
            img = self.transform(img)
        return img, label


def build_datasets():
    """扫描 dataset/ 目录，构建训练集和验证集"""
    print('=' * 50)
    print('加载数据集')
    print('=' * 50)

    all_files = []
    for class_idx, cls_name in enumerate(CLASSES):
        cls_dir = os.path.join(DATASET_DIR, cls_name)
        if not os.path.isdir(cls_dir):
            print(f'  [警告] 目录不存在，跳过: {cls_dir}')
            continue
        jpgs = glob.glob(os.path.join(cls_dir, '*.jpg'))
        for f in jpgs:
            all_files.append((f, class_idx))
        print(f'  {cls_name}: {len(jpgs)} 张')

    if len(all_files) < 10:
        print('\n[错误] 图片太少！请先用 data_collector.py 采集更多数据。')
        sys.exit(1)

    # 分层抽样分割（比随机 shuffle 更均衡）
    train_list, val_list = stratified_split(all_files, TRAIN_RATIO, SEED)

    # 打印各类在 train/val 中的分布
    train_counts = Counter(label for _, label in train_list)
    val_counts = Counter(label for _, label in val_list)
    print(f'\n共 {len(all_files)} 张 | 训练 {len(train_list)} | 验证 {len(val_list)}')
    print('各类分布:')
    for i, cls_name in enumerate(CLASSES):
        print(f'  {cls_name}: train={train_counts.get(i, 0):3d}, val={val_counts.get(i, 0):3d}')

    # 数据增强（训练集）—— 增加 RandomErasing 增强
    train_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.RandomRotation(30),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.ToTensor(),                                          # -> [0,1]
        transforms.Normalize([0.5] * 3, [0.5] * 3),                   # -> [-1,1]
        transforms.RandomErasing(p=0.2, scale=(0.02, 0.15)),          # 随机擦除，模拟遮挡
    ])

    # 验证集只做标准化
    val_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.ToTensor(),
        transforms.Normalize([0.5] * 3, [0.5] * 3),
    ])

    train_ds = ChessDataset(train_list, train_transform)
    val_ds = ChessDataset(val_list, val_transform)

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,  num_workers=0)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    return train_loader, val_loader, train_list


# ==================== 训练 / 验证 ====================

def train_one_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        total_loss += loss.item() * imgs.size(0)
        correct += (outputs.argmax(1) == labels).sum().item()
        total += imgs.size(0)

    return total_loss / total, correct / total


@torch.no_grad()
def validate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        total_loss += loss.item() * imgs.size(0)
        correct += (outputs.argmax(1) == labels).sum().item()
        total += imgs.size(0)
    return total_loss / total, correct / total


# ==================== 绘制训练曲线 ====================

def plot_history(history):
    """绘制训练曲线，包含 Loss、Accuracy 和学习率变化"""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('[提示] 安装 matplotlib 可生成训练曲线: pip install matplotlib')
        return

    epochs = range(1, len(history['train_loss']) + 1)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 4))

    # Loss
    ax1.plot(epochs, history['train_loss'], 'b-', label='Train Loss', linewidth=1.5)
    ax1.plot(epochs, history['val_loss'],   'r-', label='Val Loss', linewidth=1.5)
    # EMA 平滑曲线
    if 'val_loss_ema' in history:
        ax1.plot(epochs, history['val_loss_ema'], 'r--', label='Val Loss (EMA)', linewidth=2)
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Loss Curve')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)

    # Accuracy
    ax2.plot(epochs, history['train_acc'], 'b-', label='Train Acc', linewidth=1.5)
    ax2.plot(epochs, history['val_acc'],   'r-', label='Val Acc', linewidth=1.5)
    # EMA 平滑曲线
    if 'val_acc_ema' in history:
        ax2.plot(epochs, history['val_acc_ema'], 'r--', label='Val Acc (EMA)', linewidth=2)
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Accuracy Curve')
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)

    # Learning Rate
    if 'lr' in history:
        ax3.plot(epochs, history['lr'], 'g-', linewidth=1.5)
        ax3.set_xlabel('Epoch')
        ax3.set_ylabel('Learning Rate')
        ax3.set_title('Learning Rate')
        ax3.set_yscale('log')
        ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(CURVE_PATH, dpi=150)
    plt.close()
    print(f'训练曲线已保存: {CURVE_PATH}')


# ==================== 主函数 ====================

def main():
    print(f'PyTorch 版本: {torch.__version__}')
    print(f'训练设备: {DEVICE}')
    print()

    # 1. 加载数据
    train_loader, val_loader, train_list = build_datasets()
    print()

    # 2. 计算类别权重（缓解类别不平衡）
    class_weights = compute_class_weights(train_list, NUM_CLASSES).to(DEVICE)
    print(f'类别权重: {dict(zip(CLASSES, [f"{w:.3f}" for w in class_weights.tolist()]))}')
    print()

    # 3. 创建模型
    model = ChessCNN(num_classes=NUM_CLASSES).to(DEVICE)
    total_params = sum(p.numel() for p in model.parameters())
    print(f'模型参数量: {total_params:,}')
    print()

    # 4. 损失函数（标签平滑）& 优化器 & 学习率调度
    criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=LABEL_SMOOTHING)
    optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, min_lr=1e-6
    )

    # 5. 训练循环
    history = {
        'train_loss': [], 'train_acc': [],
        'val_loss': [],   'val_acc': [],
        'val_loss_ema': [], 'val_acc_ema': [],
        'lr': [],
    }
    best_val_loss = float('inf')
    no_improve = 0
    best_state = None
    val_loss_ema = EMA(decay=0.85)   # 用 EMA 平滑 val_loss 判断是否真正改善
    val_acc_ema = EMA(decay=0.85)

    print('=' * 50)
    print('开始训练')
    print('=' * 50)

    start_time = time.time()

    for epoch in range(1, EPOCHS + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, DEVICE)
        val_loss, val_acc = validate(model, val_loader, criterion, DEVICE)
        elapsed = time.time() - t0

        # EMA 平滑
        smooth_val_loss = val_loss_ema.update(val_loss)
        smooth_val_acc = val_acc_ema.update(val_acc)

        # 基于 EMA 平滑后的 loss 调整学习率（更稳定）
        scheduler.step(smooth_val_loss)

        current_lr = optimizer.param_groups[0]['lr']
        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        history['val_loss_ema'].append(smooth_val_loss)
        history['val_acc_ema'].append(smooth_val_acc)
        history['lr'].append(current_lr)

        # 记录最优模型（基于 EMA 平滑后的 val_loss）
        if smooth_val_loss < best_val_loss:
            best_val_loss = smooth_val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
            marker = ' *best*'
        else:
            no_improve += 1
            marker = ''

        print(
            f'[{epoch:3d}/{EPOCHS}] '
            f'Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | '
            f'Val Loss: {val_loss:.4f}(ema:{smooth_val_loss:.4f}) '
            f'Acc: {val_acc:.4f}(ema:{smooth_val_acc:.4f}) | '
            f'LR: {current_lr:.6f} | '
            f'{elapsed:.1f}s{marker}'
        )

        # 早停
        if no_improve >= PATIENCE:
            print(f'\n验证集 EMA loss 连续 {PATIENCE} 轮无改善，早停。')
            break

    total_time = time.time() - start_time
    print(f'\n训练完成，耗时 {total_time:.1f}s')

    # 6. 加载最优权重并保存
    if best_state is not None:
        model.load_state_dict(best_state)
    torch.save({
        'model_state_dict': model.state_dict(),
        'classes': CLASSES,
        'img_size': IMG_SIZE,
    }, MODEL_PATH)
    print(f'模型已保存: {MODEL_PATH}')

    # 7. 最终验证
    val_loss, val_acc = validate(model, val_loader, criterion, DEVICE)
    print(f'最优模型验证准确率: {val_acc:.4f} ({val_acc*100:.1f}%)')

    # 8. 保存训练记录（不含 EMA 数据，保持 JSON 简洁）
    history_to_save = {
        'train_loss': history['train_loss'],
        'train_acc': history['train_acc'],
        'val_loss': history['val_loss'],
        'val_acc': history['val_acc'],
        'val_loss_ema': history['val_loss_ema'],
        'val_acc_ema': history['val_acc_ema'],
        'lr': history['lr'],
    }
    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history_to_save, f, ensure_ascii=False, indent=2)
    print(f'训练记录已保存: {HISTORY_PATH}')

    # 9. 绘制曲线
    plot_history(history)


if __name__ == '__main__':
    main()
