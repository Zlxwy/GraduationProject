import cv2
import math
import numpy as np
from PlaneMapper import *

mouse_x = 0
mouse_y = 0
LButtonDownFlag = False
MouseMoveFlag = False
LButtonUpFlag = False

def mouse_callback(event, x, y, flags, param):
  global mouse_x, mouse_y, LButtonDownFlag, MouseMoveFlag, LButtonUpFlag
  mouse_x = x
  mouse_y = y
  if event == cv2.EVENT_LBUTTONDOWN: LButtonDownFlag = True # 鼠标左键按下
  if event == cv2.EVENT_MOUSEMOVE: MouseMoveFlag = True # 鼠标移动 
  if event == cv2.EVENT_LBUTTONUP: LButtonUpFlag = True # 鼠标左键释放

# 在画面的CV坐标系中，四边形的四个顶点坐标
CvPlane_Rect_TopLeft = [50,50]
CvPlane_Rect_TopRight = [200,50]
CvPlane_Rect_BottomRight = [200,200]
CvPlane_Rect_BottomLeft = [50,200]
CvPlane_ChangeRef = None
# 在机械臂坐标系中，四边形的四个顶点坐标
ArmPlane_Rect_TopLeft = [0,9]
ArmPlane_Rect_TopRight = [8,9]
ArmPlane_Rect_BottomRight = [8,0]
ArmPlane_Rect_BottomLeft = [0,0]

def DrawIrregularQuad(img, pts, color, thickness):
  """
  绘制不规则四边形（修复了顶点排序逻辑）
  img: 目标图像
  pts: 四个顶点的CV坐标系坐标，按照CV坐标系的左上、右上、右下、左下的顺序排列
  color: 线条颜色
  thickness: 线条粗细
  """
  ptTL, ptTR, ptBR, ptBL = pts # 左上、右上、右下、左下
  cv2.line(img, ptTL, ptTR, color, thickness)
  cv2.line(img, ptTR, ptBR, color, thickness)
  cv2.line(img, ptBR, ptBL, color, thickness)
  cv2.line(img, ptBL, ptTL, color, thickness)

def DrawTablePlus(img, pts, rows, cols, color, thickness):
  """
  绘制带均匀表格的四边形（修复了顶点排序逻辑）
  img: 目标图像
  pts: 四个顶点的CV坐标系坐标，按照CV坐标系的左上、右上、右下、左下的顺序排列
  rows: 表格行数
  cols: 表格列数
  color: 线条颜色
  thickness: 线条粗细
  """
  DrawIrregularQuad(img, pts, color, thickness)
  ptTL, ptTR, ptBR, ptBL = pts # 左上、右上、右下、左下
  ptTL, ptTR, ptBR, ptBL = np.float32([ptTL, ptTR, ptBR, ptBL]) # 将点转换为浮点数以便进行插值计算
  for r in range(1, rows): # 循环绘制内部的行线 (横向分割)
    # 从 1 到 rows-1，因为 0 和 rows 已经是外边框了
    # 计算当前行在左边框和右边框上的位置
    alpha_r = r / float(rows) # alpha_r 是比例因子 (0.0 ~ 1.0)
    pt_left = ptTL + (ptBL - ptTL) * alpha_r # 线性插值：计算左边框上的点 (从TL到BL)
    pt_right = ptTR + (ptBR - ptTR) * alpha_r # 线性插值：计算右边框上的点 (从TR到BR)
    cv2.line(img, tuple(pt_left.astype(int)), tuple(pt_right.astype(int)), color, thickness) # 绘制横线
  for c in range(1, cols): # 循环绘制内部的列线 (纵向分割)
    # 从 1 到 cols-1，因为 0 和 cols 已经是外边框了
    # 计算当前列在上边框和下边框上的位置
    alpha_c = c / float(cols) # alpha_c 是比例因子 (0.0 ~ 1.0)
    pt_top = ptTL + (ptTR - ptTL) * alpha_c # 上边框 (从TL到TR)
    pt_bottom = ptBL + (ptBR - ptBL) * alpha_c # 下边框 (从BL到BR)
    cv2.line(img, tuple(pt_top.astype(int)), tuple(pt_bottom.astype(int)), color, thickness) # 绘制竖线

def main():
  global mouse_x, mouse_y, LButtonDownFlag, MouseMoveFlag, LButtonUpFlag
  global CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft
  global CvPlane_ChangeRef
  global ArmPlane_Rect_TopLeft, ArmPlane_Rect_TopRight, ArmPlane_Rect_BottomRight, ArmPlane_Rect_BottomLeft

  cap = cv2.VideoCapture(1)
  if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()
  cv2.namedWindow("Frame")
  cv2.setMouseCallback("Frame", mouse_callback)


  is_pressed = False
  while True:
    ret, frame = cap.read()
    if not ret:
      print("Error: Could not read frame.")
      break

    if LButtonDownFlag:
      LButtonDownFlag = False
      is_pressed = True
      mx = mouse_x
      my = mouse_y
      DisRefToTopLeft = math.dist((mx,my), CvPlane_Rect_TopLeft)
      DisRefToTopRight = math.dist((mx,my), CvPlane_Rect_TopRight)
      DisRefToBottomRight = math.dist((mx,my), CvPlane_Rect_BottomRight)
      DisRefToBottomLeft = math.dist((mx,my), CvPlane_Rect_BottomLeft)
      EffectiveRadius = 20.0 # 有效半径
      if DisRefToTopLeft < EffectiveRadius: CvPlane_ChangeRef = CvPlane_Rect_TopLeft
      if DisRefToTopRight <= DisRefToTopLeft and DisRefToTopRight < EffectiveRadius: CvPlane_ChangeRef = CvPlane_Rect_TopRight
      if DisRefToBottomRight <= DisRefToTopRight and DisRefToBottomRight < EffectiveRadius: CvPlane_ChangeRef = CvPlane_Rect_BottomRight
      if DisRefToBottomLeft <= DisRefToBottomRight and DisRefToBottomLeft < EffectiveRadius: CvPlane_ChangeRef = CvPlane_Rect_BottomLeft
    elif LButtonUpFlag:
      LButtonUpFlag = False
      is_pressed = False
      CvPlane_ChangeRef = None
    else: pass

    if is_pressed and MouseMoveFlag:
      if CvPlane_ChangeRef is not None:
        CvPlane_ChangeRef[0] = mouse_x
        CvPlane_ChangeRef[1] = mouse_y
    
    draw_color = (255,0,0)
    text_color = (0,255,0)
    DrawTablePlus(frame, [CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft], 9, 8, draw_color, 2)
    cv2.circle(frame, CvPlane_Rect_TopLeft, 10, draw_color, 2)
    cv2.circle(frame, CvPlane_Rect_TopRight, 10, draw_color, 2)
    cv2.circle(frame, CvPlane_Rect_BottomRight, 10, draw_color, 2)
    cv2.circle(frame, CvPlane_Rect_BottomLeft, 10, draw_color, 2)
    cv2.putText(frame, "TL", CvPlane_Rect_TopLeft, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "TR", CvPlane_Rect_TopRight, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "BR", CvPlane_Rect_BottomRight, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "BL", CvPlane_Rect_BottomLeft, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

    # # 调用坐标映射器，方法1
    # PlaneMapper_Arm2Cv = PlaneMapper(
    #   [ArmPlane_Rect_TopLeft, ArmPlane_Rect_TopRight, ArmPlane_Rect_BottomRight, ArmPlane_Rect_BottomLeft], # a plane: ArmPlane
    #   [CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft] # b plane: CvPlane
    # )
    # PointOnArmPlane = [5, 8] # ArmPlane
    # PointOnCvPlane = PlaneMapper_Arm2Cv.a_to_b(PointOnArmPlane) # ArmPlane -> CvPlane
    # cv2.circle(frame, (int(PointOnCvPlane[0]), int(PointOnCvPlane[1])), 10, draw_color, 2)

    # 调用坐标映射器，方法2
    PointOnArmPlane = [5, 8]
    H_Arm2Cv = compute_homography(
      [ArmPlane_Rect_TopLeft, ArmPlane_Rect_TopRight, ArmPlane_Rect_BottomRight, ArmPlane_Rect_BottomLeft], # ArmPlane
      [CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft] # CvPlane
    )
    PointOnCvPlane = transform_point(PointOnArmPlane, H_Arm2Cv) # ArmPlane -> CvPlane
    cv2.circle(frame, (int(PointOnCvPlane[0]), int(PointOnCvPlane[1])), 10, draw_color, 2)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == ord('\x1b'):
      break

if __name__ == "__main__":
  main()