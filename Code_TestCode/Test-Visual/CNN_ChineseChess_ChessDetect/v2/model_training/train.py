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



# # 原参数
# BATCH_SIZE = 32
# EPOCHS = 1000
# LR = 1e-3
# WEIGHT_DECAY = 1e-4
# PATIENCE = 10         # 验证集 loss 连续多少轮不下降则早停

# AI写给4070显卡用的
BATCH_SIZE = 64
EPOCHS = 1000
LR = 1e-3  # 与batch size成比例
WEIGHT_DECAY = 1e-4
PATIENCE = 10



TRAIN_RATIO = 0.8
SEED = 42

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chess_cnn.pt')
HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'train_history.json')
CURVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'train_curve.png')

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


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

    random.shuffle(all_files)
    split = int(len(all_files) * TRAIN_RATIO)
    train_list = all_files[:split]
    val_list = all_files[split:]

    print(f'\n共 {len(all_files)} 张 | 训练 {len(train_list)} | 验证 {len(val_list)}')

    # 数据增强（训练集）
    train_transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.RandomRotation(30),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.ToTensor(),                                          # -> [0,1]
        transforms.Normalize([0.5] * 3, [0.5] * 3),                   # -> [-1,1]
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

    return train_loader, val_loader


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
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        print('[提示] 安装 matplotlib 可生成训练曲线: pip install matplotlib')
        return

    epochs = range(1, len(history['train_loss']) + 1)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(epochs, history['train_loss'], 'b-', label='Train Loss')
    ax1.plot(epochs, history['val_loss'],   'r-', label='Val Loss')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Loss Curve')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.plot(epochs, history['train_acc'], 'b-', label='Train Acc')
    ax2.plot(epochs, history['val_acc'],   'r-', label='Val Acc')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy')
    ax2.set_title('Accuracy Curve')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

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
    train_loader, val_loader = build_datasets()
    print()

    # 2. 创建模型
    model = ChessCNN(num_classes=NUM_CLASSES).to(DEVICE)
    total_params = sum(p.numel() for p in model.parameters())
    print(f'模型参数量: {total_params:,}')
    print()

    # 3. 损失函数 & 优化器 & 学习率调度
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5
    )

    # 4. 训练循环
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
    best_val_loss = float('inf')
    no_improve = 0
    best_state = None

    print('=' * 50)
    print('开始训练')
    print('=' * 50)

    start_time = time.time()

    for epoch in range(1, EPOCHS + 1):
        t0 = time.time()
        train_loss, train_acc = train_one_epoch(model, train_loader, criterion, optimizer, DEVICE)
        val_loss, val_acc = validate(model, val_loader, criterion, DEVICE)
        elapsed = time.time() - t0

        scheduler.step(val_loss)

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        # 记录最优模型
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            no_improve = 0
            marker = ' *best*'
        else:
            no_improve += 1
            marker = ''

        current_lr = optimizer.param_groups[0]['lr']
        print(
            f'[{epoch:3d}/{EPOCHS}] '
            f'Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | '
            f'Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | '
            f'LR: {current_lr:.6f} | '
            f'{elapsed:.1f}s{marker}'
        )

        # 早停
        if no_improve >= PATIENCE:
            print(f'\n验证集 loss 连续 {PATIENCE} 轮无改善，早停。')
            break

    total_time = time.time() - start_time
    print(f'\n训练完成，耗时 {total_time:.1f}s')

    # 5. 加载最优权重并保存
    if best_state is not None:
        model.load_state_dict(best_state)
    torch.save({
        'model_state_dict': model.state_dict(),
        'classes': CLASSES,
        'img_size': IMG_SIZE,
    }, MODEL_PATH)
    print(f'模型已保存: {MODEL_PATH}')

    # 6. 最终验证
    val_loss, val_acc = validate(model, val_loader, criterion, DEVICE)
    print(f'最优模型验证准确率: {val_acc:.4f} ({val_acc*100:.1f}%)')

    # 7. 保存训练记录
    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    print(f'训练记录已保存: {HISTORY_PATH}')

    # 8. 绘制曲线
    plot_history(history)


if __name__ == '__main__':
    main()
