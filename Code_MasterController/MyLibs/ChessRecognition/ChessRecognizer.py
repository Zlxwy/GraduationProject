import os
import cv2
import math
import time
import copy
import numpy as np
import torch
from torchvision import transforms
from .chess_mobilenetv3_model import ChessMobileNetV3



class ChessRecognizer(ChessMobileNetV3):
  def __init__(self, chess_model_path,
               chess_model_val_transform,
               hough_minDist,
               hough_param1, 
               hough_param2, 
               hough_minRadius, 
               hough_maxRadius,
               lower_red1,
               upper_red1,
               lower_red2,
               upper_red2,
               red_ratio_threshold):
    self._chess_model_path = chess_model_path # 模型路径
    self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu") # 获取运行设备类型
    self._checkpoint = torch.load(chess_model_path, map_location=self._device, weights_only=False) # 加载模型
    self._chess_model_classes = self._checkpoint["classes"]
    self._chess_model_classes_num = len(self._chess_model_classes)
    super().__init__(num_classes=self._chess_model_classes_num)
    self.to(self._device)
    self.load_state_dict(self._checkpoint["model_state_dict"]) # 加载模型参数
    self._chess_model_val_transform = chess_model_val_transform
    self._hough_minDist = hough_minDist
    self._hough_param1 = hough_param1
    self._hough_param2 = hough_param2
    self._hough_minRadius = hough_minRadius
    self._hough_maxRadius = hough_maxRadius
    self._lower_red1 = lower_red1
    self._upper_red1 = upper_red1
    self._lower_red2 = lower_red2
    self._upper_red2 = upper_red2
    self._red_ratio_threshold = red_ratio_threshold
    self.eval()

  def Predict(self, simple_img):
    """
    对裁剪出的棋子区域进行分类推理。
    Args: img: numpy BGR 图像 (H, W, 3)
    Returns: (class_name, confidence) 或 (None, 0.0)
    """
    simple_img_rgb = cv2.cvtColor(simple_img, cv2.COLOR_BGR2RGB) # 转换为RGB格式
    tensor = self._chess_model_val_transform(simple_img_rgb).unsqueeze(0).to(self._device) # 转换为张量并添加批次维度 [1, 3, H, W]
    with torch.no_grad(): # 禁用梯度计算，节省内存
      logits = self(tensor)
      probs = torch.softmax(logits, dim=1)
      conf, cls_idx = probs.max(dim=1)
      conf_val = conf.item()
      cls_idx = cls_idx.item()
    return cls_idx, conf_val

  def IsRedChessPiece(self, simple_img) -> bool:
    """
    计算红色棋子红色像素占比（0-1之间）。
    Args: simple_img: numpy BGR 图像 (H, W, 3)
    Returns: 红色像素占比 float
    """
    # # 用HSV计算，单通道红色阈值
    # hsv = cv2.cvtColor(simple_img, cv2.COLOR_BGR2HSV) # 转换为HSV格式
    # red_mask = cv2.inRange(hsv, self._lower_red, self._upper_red) # 红色掩码
    # return red_ratio >= self._red_ratio_threshold # 如果红色占比占比大于阈值，返回True

    # # 用RGB计算
    # rgb = cv2.cvtColor(simple_img, cv2.COLOR_BGR2RGB)
    # red_mask = cv2.inRange(rgb, self._lower_red, self._upper_red)
    # total_pixels = simple_img.shape[0] * simple_img.shape[1] # 总像素数
    # red_pixels = cv2.countNonZero(red_mask) # 红色像素数
    # red_ratio = red_pixels / total_pixels # 红色像素占比
    # return red_ratio >= self._red_ratio_threshold # 如果红色占比占比大于阈值，返回True

    # 用HSV计算，双通道红色阈值
    hsv = cv2.cvtColor(simple_img, cv2.COLOR_BGR2HSV)
    mask_red1 = cv2.inRange(hsv, self._lower_red1, self._upper_red1) # 红色掩码1
    mask_red2 = cv2.inRange(hsv, self._lower_red2, self._upper_red2) # 红色掩码2
    mask_red = mask_red1 + mask_red2 # 合并红色掩码1和红色掩码2
    mask_red = cv2.morphologyEx(mask_red, cv2.MORPH_OPEN, np.ones((5,5),np.uint8)) # 开运算：先腐蚀后膨胀，去除噪点
    red_count = cv2.countNonZero(mask_red) # 红色像素数
    total_count = simple_img.shape[0] * simple_img.shape[1] # 总像素数
    red_ratio = red_count / total_count # 红色像素占比
    # print(f"red_ratio: {red_ratio}")
    return red_ratio >= self._red_ratio_threshold # 如果红色占比占比大于阈值，返回True


  
  # 返回的数据结构是[ (cx1,cy1,r1,cls_idx1,conf1), ... (cxn,cyn,rn,cls_idxn,confn) ]
  def Recognize(self, img):
    img_cp = img.copy() # 复制原始图像，避免修改原始图像
    img_cp_gray = cv2.cvtColor(img_cp, cv2.COLOR_BGR2GRAY) # 转为灰度的图像
    img_cp_gray_blur = cv2.GaussianBlur(img_cp_gray, (19,19), 2.5) # 高斯模糊
    circles = cv2.HoughCircles(
      img_cp_gray_blur,
      cv2.HOUGH_GRADIENT,
      dp=1,
      minDist=self._hough_minDist,
      param1=self._hough_param1,
      param2=self._hough_param2,
      minRadius=self._hough_minRadius,
      maxRadius=self._hough_maxRadius,
    )
    result = [] # 待返回的结果列表
    if circles is not None: # 如果检测到了圆
      circles = np.uint16(np.around(circles)) # 将圆的XY坐标和半径转换为整数.
      for circle in circles[0]: # 遍历所有圆，circles数据结构：( ( (x1,y1,r1),(x2,y2,r2),...) ) )
        cx, cy, r = int(circle[0]), int(circle[1]), int(circle[2]) # 提取圆心坐标和半径
        pad = int(r * 1.2) # 准备裁剪棋子区域的范围，增大一点
        ih, iw = img_cp.shape[:2] # 获取图像的高度和宽度
        x1 = max(cx - pad, 0) # 裁剪区域的左边界
        y1 = max(cy - pad, 0) # 裁剪区域的上边界
        x2 = min(cx + pad, iw) # 裁剪区域的右边界
        y2 = min(cy + pad, ih) # 裁剪区域的下边界
        roi_chess = img_cp[y1:y2, x1:x2] # 裁剪棋子区域的图像
        if roi_chess.size == 0: continue # 如果裁剪区域为空，跳过当前循环
        cls_idx, conf = self.Predict(roi_chess) # 预测棋子的类别和置信度
        is_red = self.IsRedChessPiece(roi_chess) # 计算红色棋子红色像素占比
        result.append((cx, cy, r, cls_idx, conf, is_red)) # 将结果添加到列表中
    else: result = None # 如果没有检测到圆，返回None
    return result
      

    
# if __name__ == "__main__":
#   ChessModel_InputSize = 128
#   ChessModel_CONFIDENCE_THRESHOLD = 0.5
#   HOUGH_PARAM1 = 80
#   HOUGH_PARAM2 = 25
#   HOUGH_MIN_RADIUS = 26
#   HOUGH_MAX_RADIUS = 37
#   HOUGH_MIN_DIST = HOUGH_MIN_RADIUS * 2.2
#   ChessModel_DispLabels = ['J', 'S', 'C', 'M', 'P', 'X', 'B']

#   ChessModel_Recognizer = ChessRecognizer(
#     chess_model_path=os.path.join(
#       "chess_mobilenetv3.pt"
#     ),
#     chess_model_val_transform=transforms.Compose([
#       transforms.ToPILImage(),
#       transforms.Resize((ChessModel_InputSize, ChessModel_InputSize)),
#       transforms.ToTensor(),
#       transforms.Normalize([0.5]*3, [0.5]*3),
#     ]),
#     hough_minDist=HOUGH_MIN_DIST,
#     hough_param1=HOUGH_PARAM1,
#     hough_param2=HOUGH_PARAM2,
#     hough_minRadius=HOUGH_MIN_RADIUS,
#     hough_maxRadius=HOUGH_MAX_RADIUS,
#     red_lower_bound=(0, 100, 100),
#     red_upper_bound=(10, 255, 255),
#     red_ratio_threshold=0.05,
#   )

#   cap = cv2.VideoCapture(1)
#   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
#   cv2.namedWindow("frame_roi")
#   while True:
#     ret, frame = cap.read()
#     if not ret:
#       continue
#     frame_roi = frame[0:1080, 420:1500]
#     ChessObjects = ChessModel_Recognizer.Recognize(frame_roi)
#     if ChessObjects is not None:
#       for chessobj in ChessObjects:
#         cx, cy, r, cls_idx, conf = chessobj
#         disp_name = ChessModel_DispLabels[cls_idx]
#         if conf < ChessModel_CONFIDENCE_THRESHOLD:
#           disp_text = f"{disp_name}:{conf:.0%} ?"
#           disp_color = (0,255,255)
#         else:
#           disp_text = f"{disp_name}:{conf:.0%}"
#           disp_color = (255,0,0)
        
#         # 绘制棋子的圆周和圆心
#         cv2.circle(frame_roi, (cx, cy), r, disp_color, 2)
#         cv2.circle(frame_roi, (cx, cy), 2, disp_color, -1)

#         # 绘制棋子的类别和置信度
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         font_scale = 0.6
#         thickness = 2
#         (tw, th), baseline = cv2.getTextSize(disp_text, font, font_scale, thickness)
#         label_x = cx - tw // 2
#         label_y = cy - r - 10
#         if label_y - th - baseline < 0: label_y = cy + r + th + baseline + 10 # 防止标签超出图像边界
#         cv2.rectangle(frame_roi, (label_x-4,label_y-th-baseline), (label_x+tw+4,label_y+baseline), (0,0,0), -1)
#         cv2.putText(frame_roi, disp_text, (label_x,label_y), font, font_scale, disp_color, thickness, cv2.LINE_AA)
#     cv2.imshow("frame_roi", frame_roi)
#     cv2.waitKey(1)
#     pass
