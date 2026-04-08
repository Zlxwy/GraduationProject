from ultralytics import YOLO

def main():
    model = YOLO('yolov8n.pt')
    
    # results = model.train(
    #     data='data.yaml',
    #     epochs=50,           # 数据少，增加训练轮数
    #     imgsz=1024,           # 原图810×1440，用1024保留小目标细节
    #     batch=1,              # 只有3张图，batch设为1
    #     device='cpu',         # 用CPU训练
    #     patience=5,          # 数据少，早停耐心值降低
    #     save=True,            # 保存模型权重
    #     plots=True,           # 生成训练曲线
    #     val=False,            # 没有验证集，关闭验证
    #     augment=True,         # 开启数据增强
    #     close_mosaic=0,       # 关闭mosaic，避免小目标被裁剪
    #     mixup=0.0,            # 关闭mixup
    #     degrees=15.0,         # 旋转增强
    #     translate=0.1,        # 平移增强
    #     scale=0.5,            # 缩放增强
    #     shear=2.0,            # 剪切增强
    #     perspective=0.0,      # 透视变换
    #     flipud=0.0,           # 上下翻转
    #     fliplr=0.5,           # 左右翻转
    #     mosaic=0.0,           # 关闭mosaic（小目标容易被mosaic裁剪破坏，关闭这些增强）
    # )
    
    results = model.train(
        data='data.yaml',
        epochs=100,           # 大幅降低轮数，避免过拟合
        imgsz=640,           # 降低尺寸，加快训练，减少噪声
        batch=16,
        device='0',
        patience=20,          # 数据少，早停更敏感
        val=True,
        augment=True,
        degrees=15.0,        # 减小旋转角度
        translate=0.1,      # 减小平移
        scale=0.2,           # 大幅降低缩放
        shear=2.0,           # 关闭剪切
        flipud=0.0,
        fliplr=0.5,          # 完全关闭左右翻转，避免6/9混淆
        mosaic=1.0,
        mixup=0.1,
        perspective=0.0
    )
    
    print('训练完成！')

if __name__ == '__main__':
    main()