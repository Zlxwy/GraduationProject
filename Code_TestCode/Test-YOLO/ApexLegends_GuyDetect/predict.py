from ultralytics import YOLO

def main():
    model = YOLO('runs/detect/train/weights/best.pt')
    
    source = 'images/test'
    
    results = model.predict(
        source=source,
        conf=0.5,  # 置信度阈值：只保留>50%置信度的预测框
        iou=0.5,  # IOU阈值：用于非极大值抑制（NMS），过滤重叠框
        save=True,
        show=False
    )
    
    print('预测完成！')

if __name__ == '__main__':
    main()
