import cv2
from ultralytics import YOLO

def main():
    # 1. 加载你训练好的模型 (建议使用绝对路径或确认路径正确)
    model = YOLO('runs/detect/train/weights/best.pt') 
    
    # 2. 打开摄像头
    cap = cv2.VideoCapture(1) 
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)
    cv2.namedWindow('cam')
    print("按 ESC 键退出程序")

    while True:
        ret, frame = cap.read() # 读取一帧画面
        if not ret:
            print("无法读取摄像头帧")
            break
        
        # --- 关键修改开始 ---
        # 3. 对当前帧进行预测
        # stream=True 可以提高处理视频流的效率
        # verbose=False 可以关闭控制台的冗余输出，防止刷屏
        results = model.predict(source=frame, conf=0.5, verbose=False)
        
        # 4. 绘制预测框
        # results[0].plot() 会自动在原图上画出框、标签和置信度
        # 返回的是一个已经画好框的 numpy 数组
        annotated_frame = results[0].plot()
        # --- 关键修改结束 ---

        # 5. 显示画好框的画面 (注意这里显示的是 annotated_frame 而不是原始 frame)
        cv2.imshow('cam', annotated_frame)
        
        # 按ESC键退出
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
