# 创建一个黑色的帧
import math
import numpy as np
import cv2


frame_width = 1080
frame_height = 1080

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






def DrawTablePlus(img, pts, rows, cols, color, thickness):
  """
  绘制带均匀表格的四边形（修复了顶点排序逻辑）
  img: 目标图像
  pts: 四个顶点坐标，按照左上、右上、右下、左下的顺序排列
  rows: 表格行数
  cols: 表格列数
  color: 线条颜色
  thickness: 线条粗细
  """
  ptTL, ptTR, ptBR, ptBL = pts # 左上、右上、右下、左下
  cv2.line(img, ptTL, ptTR, color, thickness)
  cv2.line(img, ptTR, ptBR, color, thickness)
  cv2.line(img, ptBR, ptBL, color, thickness)
  cv2.line(img, ptBL, ptTL, color, thickness)

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



def get_intersection_point(line1, line2) -> tuple[int,int]:
  """
  计算两条直线的交点
  line1: 第一个线段，格式为 ((x1, y1), (x2, y2))
  line2: 第二个线段，格式为 ((x3, y3), (x4, y4))
  返回值: 交点坐标 ix, iy，如果两条线平行则返回 None,None
  """
  x1, y1 = line1[0]
  x2, y2 = line1[1]
  x3, y3 = line2[0]
  x4, y4 = line2[1]
  denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
  if abs(denom) < 1e-9: return None,None # 用极小值判断，避免浮点数精度问题
  det1 = (x1 * y2 - y1 * x2)
  det2 = (x3 * y4 - y3 * x4)
  ix = (det1 * (x3 - x4) - (x1 - x2) * det2) / denom
  iy = (det1 * (y3 - y4) - (y1 - y2) * det2) / denom
  return int(ix), int(iy)

def DrawTablePlus_DrawIntersectionPoint(img, pts, rows, cols, color, radius, thickness):
  """
  绘制带均匀表格的四边形（修复了顶点排序逻辑）
  img: 目标图像
  pts: 四个顶点坐标，按照左上、右上、右下、左下的顺序排列
  rows: 表格行数
  cols: 表格列数
  color: 线条颜色
  thickness: 线条粗细
  """
  ptTL, ptTR, ptBR, ptBL = pts # 左上、右上、右下、左下

  ptTL, ptTR, ptBR, ptBL = np.float32([ptTL, ptTR, ptBR, ptBL]) # 将点转换为浮点数以便进行插值计算
  for r in range(0, rows+1): # 循环绘制内部的行线 (横向分割)
    alpha_r = r / float(rows) # alpha_r 是比例因子 (0.0 ~ 1.0)
    pt_left = ptTL + (ptBL - ptTL) * alpha_r # 线性插值：计算左边框上的点 (从TL到BL)
    pt_right = ptTR + (ptBR - ptTR) * alpha_r # 线性插值：计算右边框上的点 (从TR到BR)

    for c in range(0, cols+1): # 循环绘制内部的列线 (纵向分割)
      alpha_c = c / float(cols) # alpha_c 是比例因子 (0.0 ~ 1.0)
      pt_top = ptTL + (ptTR - ptTL) * alpha_c # 上边框 (从TL到TR)
      pt_bottom = ptBL + (ptBR - ptBL) * alpha_c # 下边框 (从BL到BR)

      line1 = (tuple(pt_left.astype(int)), tuple(pt_right.astype(int)))
      line2 = (tuple(pt_top.astype(int)), tuple(pt_bottom.astype(int)))
      ix, iy = get_intersection_point(line1, line2)
      if ix is not None and iy is not None:
        cv2.circle(img, (ix,iy), radius, color, thickness)


def main():
  global mouse_x
  global mouse_y
  global LButtonDownFlag
  global MouseMoveFlag
  global LButtonUpFlag
  is_pressed = False

  cv2.namedWindow('black_frame') # 创建名为"black_frame"的窗口
  cv2.setMouseCallback("black_frame", mouse_callback)
  print("按ESC键退出程序")

  while True:
    black_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

    if LButtonDownFlag: # 如果左键按下标志位触发
      LButtonDownFlag = False # 清除左键按下标志位
      is_pressed = True # 设置按下状态
      mark_point = (mouse_x, mouse_y) # 记录当前鼠标位置
    elif LButtonUpFlag: # 如果左键释放标志位触发
      LButtonUpFlag = False # 清除左键释放标志位
      is_pressed = False # 清除按下状态
    else: pass

    if is_pressed:
      pts = (
        (100, 200),
        (666, 250),
        (666, 800),
        (mouse_x, mouse_y)
      )
      DrawTablePlus(
        black_frame, # 黑板底图
        pts,
        rows=9, cols=8, 
        color=(0,255,0),
        thickness=2
      ) # 调用函数绘制带均匀表格的矩形
      DrawTablePlus_DrawIntersectionPoint(
        black_frame, # 黑板底图
        pts,
        rows=9, cols=8,
        color=(0,255,0),
        radius=10,
        thickness=2
      )

    cv2.imshow('black_frame', black_frame) # 在窗口中显示黑色帧

    PressKey = cv2.waitKey(10) & 0xFF
    if PressKey & 0xFF == 27: # 如果按下ESC键
      break # 退出循环

  cv2.destroyAllWindows() # 关闭所有窗口
  print("程序退出")



if __name__ == '__main__':
  main()