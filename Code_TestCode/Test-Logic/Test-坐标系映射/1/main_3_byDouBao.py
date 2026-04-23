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
  if event == cv2.EVENT_LBUTTONDOWN: LButtonDownFlag = True
  if event == cv2.EVENT_MOUSEMOVE: MouseMoveFlag = True
  if event == cv2.EVENT_LBUTTONUP: LButtonUpFlag = True



# 四个角点 顺序：左上TL、右上TR、右下BR、左下BL
CvPlane_Rect_TopLeft = [50,50]
CvPlane_Rect_TopRight = [200,50]
CvPlane_Rect_BottomRight = [200,200]
CvPlane_Rect_BottomLeft = [50,200]
CvPlane_ChangeRef = None

# 机械臂坐标系 顺序严格对应
ArmPlane_Rect_TopLeft = [0,9]
ArmPlane_Rect_TopRight = [8,9]
ArmPlane_Rect_BottomRight = [8,0]
ArmPlane_Rect_BottomLeft = [0,0]

def DrawIrregularQuad(img, pts, color, thickness):
  ptTL, ptTR, ptBR, ptBL = pts
  cv2.line(img, tuple(ptTL), tuple(ptTR), color, thickness)
  cv2.line(img, tuple(ptTR), tuple(ptBR), color, thickness)
  cv2.line(img, tuple(ptBR), tuple(ptBL), color, thickness)
  cv2.line(img, tuple(ptBL), tuple(ptTL), color, thickness)

def DrawTable_WithPerspective(img, pts, rows, cols, color, thickness):
  ptTL, ptTR, ptBR, ptBL = np.float32(pts)
  DrawIrregularQuad(img, pts, color, thickness)

  arm_width = 8
  arm_height = 9
  std_TL = np.float32([0, arm_height])
  std_TR = np.float32([arm_width, arm_height])
  std_BR = np.float32([arm_width, 0])
  std_BL = np.float32([0, 0])

  H_std2img = compute_homography([std_TL, std_TR, std_BR, std_BL], [ptTL, ptTR, ptBR, ptBL])

  # 绘制横线
  for r in range(rows + 1):
    y_arm = rows - r
    p_left_arm = (0, y_arm)
    p_right_arm = (arm_width, y_arm)
    p_left_img = transform_point(p_left_arm, H_std2img)
    p_right_img = transform_point(p_right_arm, H_std2img)
    cv2.line(img, (int(p_left_img[0]), int(p_left_img[1])),
      (int(p_right_img[0]), int(p_right_img[1])), color, thickness)

    # 绘制竖线
  for c in range(cols + 1):
    x_arm = c
    p_top_arm = (x_arm, arm_height)
    p_bottom_arm = (x_arm, 0)
    p_top_img = transform_point(p_top_arm, H_std2img)
    p_bottom_img = transform_point(p_bottom_arm, H_std2img)
    cv2.line(img, (int(p_top_img[0]), int(p_top_img[1])),
      (int(p_bottom_img[0]), int(p_bottom_img[1])), color, thickness)

def main():
  global mouse_x, mouse_y, LButtonDownFlag, MouseMoveFlag, LButtonUpFlag
  global CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft
  global CvPlane_ChangeRef

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

    # 鼠标按下：选择最近角点
    if LButtonDownFlag:
      LButtonDownFlag = False
      is_pressed = True
      mx, my = mouse_x, mouse_y
      EffectiveRadius = 20.0
      dists = [
        math.dist((mx, my), CvPlane_Rect_TopLeft),
        math.dist((mx, my), CvPlane_Rect_TopRight),
        math.dist((mx, my), CvPlane_Rect_BottomRight),
        math.dist((mx, my), CvPlane_Rect_BottomLeft),
      ]
      min_dist = min(dists)
      if min_dist < EffectiveRadius:
        idx = dists.index(min_dist)
        if idx == 0:
          CvPlane_ChangeRef = CvPlane_Rect_TopLeft
        elif idx == 1:
          CvPlane_ChangeRef = CvPlane_Rect_TopRight
        elif idx == 2:
          CvPlane_ChangeRef = CvPlane_Rect_BottomRight
        elif idx == 3:
          CvPlane_ChangeRef = CvPlane_Rect_BottomLeft

    # 鼠标抬起
    elif LButtonUpFlag:
      LButtonUpFlag = False
      is_pressed = False
      CvPlane_ChangeRef = None

    # 鼠标拖动
    if is_pressed and MouseMoveFlag and CvPlane_ChangeRef is not None:
      CvPlane_ChangeRef[0] = mouse_x
      CvPlane_ChangeRef[1] = mouse_y

    # 绘制透视网格
    draw_color = (255, 0, 0)
    text_color = (0, 255, 0)
    DrawTable_WithPerspective(frame, [
      CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight,
      CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft
    ], 9, 8, draw_color, 2)

    # 绘制四个角点
    cv2.circle(frame, tuple(CvPlane_Rect_TopLeft), 10, draw_color, 2)
    cv2.circle(frame, tuple(CvPlane_Rect_TopRight), 10, draw_color, 2)
    cv2.circle(frame, tuple(CvPlane_Rect_BottomRight), 10, draw_color, 2)
    cv2.circle(frame, tuple(CvPlane_Rect_BottomLeft), 10, draw_color, 2)

    cv2.putText(frame, "TL", CvPlane_Rect_TopLeft, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "TR", CvPlane_Rect_TopRight, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "BR", CvPlane_Rect_BottomRight, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "BL", CvPlane_Rect_BottomLeft, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

    # 实时计算映射矩阵
    H_Arm2Cv = compute_homography(
      [ArmPlane_Rect_TopLeft, ArmPlane_Rect_TopRight, ArmPlane_Rect_BottomRight, ArmPlane_Rect_BottomLeft],
      [CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft]
    )
    PointOnArmPlane = [5, 8]
    px, py = transform_point(PointOnArmPlane, H_Arm2Cv)
    cv2.circle(frame, (int(px), int(py)), 10, (0, 0, 255), -1)
    cv2.putText(frame, "(5,8)", (int(px) + 10, int(py)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == 27:
      break

  cap.release()
  cv2.destroyAllWindows()

if __name__ == "__main__":
  main()