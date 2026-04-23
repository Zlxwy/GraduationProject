import os
import cv2
import time
import math
import copy
import queue
import torch
import numpy as np
from torchvision import transforms
from ChessRecognition.ChessRecognizer import ChessRecognizer

if __name__ == "__main__":
  ChessModel_InputSize = 128
  ChessModel_CONFIDENCE_THRESHOLD = 0.5
  HOUGH_PARAM1 = 80
  HOUGH_PARAM2 = 25
  HOUGH_MIN_RADIUS = 26
  HOUGH_MAX_RADIUS = 37
  HOUGH_MIN_DIST = HOUGH_MIN_RADIUS * 2.2
  ChessModel_DispLabels = ['J', 'S', 'C', 'M', 'P', 'X', 'B']

  ChessModel_Recognizer = ChessRecognizer( # 棋子识别器封装成了一个类，实例化
    chess_model_path=os.path.join( # 模型文件路径
      os.path.dirname(os.path.abspath(__file__)), # 获取当前文件所在目录的绝对路径
      "ChessRecognition/model_files/chess_mobilenetv3.pt" # 模型文件相对于当前文件所在目录的路径
    ),
    chess_model_val_transform=transforms.Compose([ # 模型输入数据预处理流程
      transforms.ToPILImage(), # 将输入数据转换为PIL图像
      transforms.Resize((ChessModel_InputSize, ChessModel_InputSize)), # 将图像缩放到指定大小
      transforms.ToTensor(), # 将图像转换为张量
      transforms.Normalize([0.5]*3, [0.5]*3), # 对图像进行归一化处理
    ]),
    hough_minDist=HOUGH_MIN_DIST, # 霍夫圆变换参数：圆心之间的最小距离
    hough_param1=HOUGH_PARAM1, # 霍夫圆变换参数：圆心检测的累加器阈值
    hough_param2=HOUGH_PARAM2, # 霍夫圆变换参数：圆心检测的累加器阈值
    hough_minRadius=HOUGH_MIN_RADIUS, # 霍夫圆变换参数：圆的最小半径
    hough_maxRadius=HOUGH_MAX_RADIUS, # 霍夫圆变换参数：圆的最大半径
    lower_red1=np.array([0, 43, 46]), # 棋子红黑色检测参数：红色1下界
    upper_red1=np.array([10, 255, 255]), # 棋子红黑色检测参数：红色1上界
    lower_red2=np.array([170, 43, 46]), # 棋子红黑色检测参数：红色2下界
    upper_red2=np.array([180, 255, 255]), # 棋子红黑色检测参数：红色2上界
    # 因为红色在 HSV 颜色环里分成两段，所以必须用两组上下界才能完整检测到所有红色
    red_ratio_threshold=0.05 # 棋子红黑色检测参数：红色占比阈值
  )

  cap = cv2.VideoCapture(1)
  if not cap.isOpened():
    print("Error: Could not open video device 1.") # 打印错误信息，提示用户视频设备1未打开
    exit(1)
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
  cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
  cv2.resizeWindow("frame", 960, 540) # 调整窗口大小

  while True:
    ret, frame = cap.read()
    if not ret: continue
    frame_cp = frame.copy() # 复制一帧图像，避免修改原始图像
    ChessObjects = ChessModel_Recognizer.Recognize(frame_cp) # 调用棋子识别模型，将图片的复制品传进去
    if ChessObjects is not None: # 如果检测到了棋子
      for chessobj in ChessObjects: # 遍历所有棋子
        cx, cy, r, cls_idx, conf, is_red = chessobj # 提取棋子的圆心X坐标、圆心Y坐标、半径、类别索引、置信度、是否红色棋子
        disp_name = ChessModel_DispLabels[cls_idx]
        if conf < ChessModel_CONFIDENCE_THRESHOLD:
          disp_text = f"{disp_name}:{conf:.0%} ?"
          disp_color = (200, 200, 255) if is_red else (200, 200, 200) # 低置信度的话，红棋用浅红，黑棋用浅灰
        else:
          disp_text = f"{disp_name}:{conf:.0%}"
          disp_color = (0, 0, 255) if is_red else (255, 0, 0) # 高置信度的话，红棋用红色，黑棋用蓝色
        
        # 绘制棋子的圆周和圆心
        cv2.circle(frame, (cx, cy), r, disp_color, 2)
        cv2.circle(frame, (cx, cy), 2, disp_color, -1)

        # 绘制棋子的类别和置信度
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        (tw, th), baseline = cv2.getTextSize(disp_text, font, font_scale, thickness)
        label_x = cx - tw // 2
        label_y = cy - r - 10
        if label_y - th - baseline < 0: label_y = cy + r + th + baseline + 10 # 防止标签超出图像边界
        cv2.rectangle(frame, (label_x-4,label_y-th-baseline), (label_x+tw+4,label_y+baseline), (0,0,0), -1)
        cv2.putText(frame, disp_text, (label_x,label_y), font, font_scale, disp_color, thickness, cv2.LINE_AA)
    cv2.imshow("frame", frame)
    PressKey = cv2.waitKey(1) & 0xFF
    if PressKey == 27:
      break
    pass
