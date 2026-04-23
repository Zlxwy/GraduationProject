import numpy as np
import cv2
import math
import numpy as np
from DrawFuncWithPerspective import *



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
    DrawTable_Perspective(frame, [CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft], 9, 8, draw_color, 2)
    DrawIntersectionPointOfTable_Perspective(frame, [CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft], 9, 8, draw_color, 6, 2)
    point_grid = GetAllIntersectionPointOfTable_Perspective([CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft], 9, 8)
    for i,row in enumerate(point_grid):
      for j,pt in enumerate(row):
        cv2.circle(frame, pt, 3, draw_color, 2)
        cv2.putText(frame, f"{i*len(row)+j}", pt, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

    cv2.circle(frame, CvPlane_Rect_TopLeft, 10, draw_color, 2)
    cv2.circle(frame, CvPlane_Rect_TopRight, 10, draw_color, 2)
    cv2.circle(frame, CvPlane_Rect_BottomRight, 10, draw_color, 2)
    cv2.circle(frame, CvPlane_Rect_BottomLeft, 10, draw_color, 2)
    cv2.putText(frame, "TL", CvPlane_Rect_TopLeft, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "TR", CvPlane_Rect_TopRight, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "BR", CvPlane_Rect_BottomRight, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "BL", CvPlane_Rect_BottomLeft, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == ord('\x1b'):
      break

if __name__ == "__main__":
  main()