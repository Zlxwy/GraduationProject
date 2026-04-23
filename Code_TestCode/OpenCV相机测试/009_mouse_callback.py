import cv2
import numpy as np

mouse_x = 0
mouse_y = 0
LButtonDownFlag = False
MouseMoveFlag = False
LButtonUpFlag = False

def mouse_callback(event, x, y, flags, param):
  global mouse_x
  global mouse_y
  global LButtonDownFlag
  global MouseMoveFlag
  global LButtonUpFlag

  mouse_x = x
  mouse_y = y

  if event == cv2.EVENT_LBUTTONDOWN: LButtonDownFlag = True # 鼠标左键按下
  if event == cv2.EVENT_MOUSEMOVE: MouseMoveFlag = True # 鼠标移动 
  if event == cv2.EVENT_LBUTTONUP: LButtonUpFlag = True # 鼠标左键释放

img = np.zeros((500, 500, 3), np.uint8) # 黑色画布
cv2.namedWindow('Drag Demo')
cv2.setMouseCallback('Drag Demo', mouse_callback)

is_pressed = False
mark_point = (0, 0)

# 3. 主循环
while True:
  if LButtonDownFlag: # 如果左键按下标志位触发
    LButtonDownFlag = False # 清除左键按下标志位
    is_pressed = True # 设置按下状态
    mark_point = (mouse_x, mouse_y) # 记录当前鼠标位置
  elif LButtonUpFlag: # 如果左键释放标志位触发
    LButtonUpFlag = False # 清除左键释放标志位
    is_pressed = False # 清除按下状态
  else: pass

  if is_pressed and MouseMoveFlag: # 如果在按下状态，且鼠标移动标志位触发
    cv2.line(img, mark_point, (mouse_x,mouse_y), (0,255,0), 5) # 画线
    mark_point = (mouse_x, mouse_y) # 更新起始点
  
  cv2.imshow('Drag Demo', img)
  if cv2.waitKey(1) & 0xFF == 27: # 按ESC退出
    break

cv2.destroyAllWindows()