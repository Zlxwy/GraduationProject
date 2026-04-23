"""
中国象棋棋子实时识别程序

基于摄像头画面流，使用霍夫圆检测定位棋子，再用 CNN 模型分类。
依赖: chess_cnn.pt (train_cnn.py 训练产出)

用法:
    python recognize.py
"""

import os
import numpy as np
import cv2
import torch
from torchvision import transforms
from chess_cnn_model import ChessCNN

# ==================== 配置 ====================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'chess_cnn.pt')

# 摄像头参数 (与 cam_hough_circle.py 一致)
CAM_INDEX = 1
CAP_WIDTH = 1920
CAP_HEIGHT = 1080
ROI_WIDTH = CAP_HEIGHT
ROI_HEIGHT = CAP_HEIGHT

# 霍夫圆检测参数 (与 cam_hough_circle.py 一致)
HOUGH_PARAM1 = 80
HOUGH_PARAM2 = 25
HOUGH_MIN_RADIUS = 20
HOUGH_MAX_RADIUS = 35
HOUGH_MIN_DIST = 30

# 模型输入尺寸
IMG_SIZE = 128

# 置信度阈值，低于此值显示为 "未知"
CONFIDENCE_THRESHOLD = 0.5

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


# ==================== 推理预处理 ====================

val_transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.5] * 3, [0.5] * 3),
])


def load_model():
    """加载训练好的 CNN 模型"""
    if not os.path.isfile(MODEL_PATH):
        print(f'[错误] 找不到模型文件: {MODEL_PATH}')
        print('请先运行 train_cnn.py 训练模型。')
        return None, None

    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)
    classes = checkpoint['classes']
    num_classes = len(classes)
    print(f'模型类别 ({num_classes}): {classes}')

    model = ChessCNN(num_classes=num_classes).to(DEVICE)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    print(f'模型已加载: {MODEL_PATH}  (设备: {DEVICE})')
    return model, classes


def predict(model, roi_img):
    """
    对裁剪出的棋子区域进行分类推理。
    Args:
        roi_img: numpy BGR 图像 (H, W, 3)
    Returns:
        (class_name, confidence) 或 (None, 0.0)
    """
    # BGR -> RGB
    img_rgb = cv2.cvtColor(roi_img, cv2.COLOR_BGR2RGB)
    tensor = val_transform(img_rgb).unsqueeze(0).to(DEVICE)  # [1, 3, H, W]

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)
        conf, cls_idx = probs.max(dim=1)
        conf_val = conf.item()
        cls_idx = cls_idx.item()

    return cls_idx, conf_val


# ==================== 主循环 ====================

def main():
    # 类别对应显示标签
    CLASS_LABELS = {
        'JIANG': 'J',
        'SHI':   'S',
        'CHE':   'C',
        'MA':    'M',
        'PAO':   'P',
        'XIANG': 'X',
        'BING':  'B',
    }

    model, classes = load_model()
    if model is None:
        return

    # 打开摄像头
    cam = cv2.VideoCapture(CAM_INDEX)
    if not cam.isOpened():
        print('无法打开摄像头')
        return

    cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_WIDTH)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_HEIGHT)

    cv2.namedWindow('Chess Recognition', cv2.WINDOW_NORMAL)
    print('按 ESC 键退出')

    while True:
        ret, frame_origin = cam.read()
        if not ret:
            print('无法读取摄像头帧')
            break

        h, w = frame_origin.shape[:2]
        x = (w - ROI_WIDTH) // 2
        y = (h - ROI_HEIGHT) // 2
        frame_roi = frame_origin[y:y + ROI_HEIGHT, x:x + ROI_WIDTH]

        # 灰度 + 高斯模糊（用于霍夫圆检测）
        gray = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.GaussianBlur(gray, (19, 19), 2.5)

        circles = cv2.HoughCircles(
            gray_blur,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=HOUGH_MIN_DIST,
            param1=HOUGH_PARAM1,
            param2=HOUGH_PARAM2,
            minRadius=HOUGH_MIN_RADIUS,
            maxRadius=HOUGH_MAX_RADIUS,
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for circle in circles[0, :]:
                cx, cy, r = int(circle[0]), int(circle[1]), int(circle[2])

                # 裁剪棋子区域（padding 与 data_collector.py 一致: pad = r * 1.2）
                pad = int(r * 1.2)
                ih, iw = frame_roi.shape[:2]
                x1 = max(cx - pad, 0)
                y1 = max(cy - pad, 0)
                x2 = min(cx + pad, iw)
                y2 = min(cy + pad, ih)
                roi = frame_roi[y1:y2, x1:x2]

                if roi.size == 0:
                    continue

                # 推理
                cls_idx, conf = predict(model, roi)
                class_name = classes[cls_idx]
                label_zh = CLASS_LABELS.get(class_name, class_name)

                if conf < CONFIDENCE_THRESHOLD:
                    display_text = f'{label_zh} ({conf:.0%}) ?'
                    box_color = (0, 255, 255)  # 黄色：低置信度
                else:
                    display_text = f'{label_zh} ({conf:.0%})'
                    box_color = (0, 255, 0)   # 绿色：高置信度

                # 绘制圆和标签
                cv2.circle(frame_roi, (cx, cy), r, box_color, 2)
                cv2.circle(frame_roi, (cx, cy), 2, box_color, -1)

                # 标签背景 + 文字
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                thickness = 2
                (tw, th), baseline = cv2.getTextSize(display_text, font, font_scale, thickness)

                label_x = cx - tw // 2
                label_y = cy - r - 10
                # 防止标签超出画面顶部
                if label_y - th - baseline < 0:
                    label_y = cy + r + th + baseline + 10

                cv2.rectangle(frame_roi,
                              (label_x - 4, label_y - th - baseline),
                              (label_x + tw + 4, label_y + baseline),
                              (0, 0, 0), -1)
                cv2.putText(frame_roi, display_text,
                            (label_x, label_y), font, font_scale, box_color, thickness, cv2.LINE_AA)

        cv2.imshow('Chess Recognition', frame_roi)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cam.release()
    print('相机资源已释放')
    cv2.destroyAllWindows()
    print('所有窗口已关闭')


if __name__ == '__main__':
    main()
