# 导入YOLO模型
from ultralytics import YOLO

def main():
  # 加载预训练的YOLOv8n模型
  model = YOLO('yolov8n.pt')
  # 训练模型（核心参数配置）
  results = model.train(
    data='data.yaml',          # 数据集配置文件路径
    epochs=100,                # 训练轮数
    imgsz=640,                 # 输入图片尺寸（YOLO标准尺寸，兼容800*576）
    batch=16,                   # 批次大小（GPU内存适配）
    device='cpu',                  # 使用第0块GPU训练（CPU训练写cpu）
    patience=20,               # 早停耐心值（20轮无提升则停止）
    save=True,                 # 保存最佳模型
    plots=True,                # 生成训练可视化图表
    val=True,                  # 训练时进行验证
    augment=True,              # 启用数据增强
    close_mosaic=10,           # 最后10轮关闭mosaic增强（提升精度）
    mixup=0.2,                 # mixup增强概率（小幅度提升泛化）
    degrees=5.0,               # 旋转角度范围（±5°，避免棋子角度失真）
    translate=0.1,             # 平移因子（±10%）
    scale=0.1,                 # 缩放因子（±10%）
    shear=0.0,                 # 剪切角度（象棋棋子不适合剪切）
    perspective=0.0,           # 透视变换（禁用，避免棋子变形）
    flipud=0.0,                # 上下翻转概率（象棋棋子无需翻转）
    fliplr=0.0,                # 左右翻转概率（象棋棋子无需翻转）
    mosaic=1.0,                # mosaic增强概率（充分利用小数据集）
  )
  print('训练完成！')

if __name__ == '__main__':
  main()