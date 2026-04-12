# 创建一个黑色的帧
import GlobalVariable as gv
import numpy as np
import cv2






def draw_table(img, pt1, pt2, rows, cols, color, thickness):
  """
  绘制带均匀表格的矩形
  :param img: 要绘制的图像
  :param pt1: 左上角 (x1, y1)
  :param pt2: 右下角 (x2, y2)
  :param rows: 表格行数
  :param cols: 表格列数
  :param color: BGR 颜色
  :param thickness: 线条粗细
  """
  cv2.rectangle(img, pt1, pt2, color, thickness) # 先画外框矩形
  x1, y1 = pt1 # 取出矩形的左上角坐标
  x2, y2 = pt2 # 取出矩形的右下角坐标

  cell_w = (x2 - x1) / cols # 计算每一格的宽度
  cell_h = (y2 - y1) / rows # 计算每一格的高度

  for i in range(1, cols): # 遍历每一列
    x = int(x1 + i*cell_w) # 计算当前列的x坐标
    cv2.line(img, (x,y1), (x,y2), color, thickness) # 画竖线

  for i in range(1, rows): # 遍历每一行
    y = int(y1 + i*cell_h) # 计算当前行的y坐标
    cv2.line(img, (x1,y), (x2,y), color, thickness) # 画横线



def CamThreadFunc():

  cap = cv2.VideoCapture(gv.CamIndex) # 打开摄像头
  if not cap.isOpened(): # 如果摄像头未成功打开
    gv.logger.PrintString("Thread_Cam Error: Camera not found.")
    return
  cap.set(cv2.CAP_PROP_FRAME_WIDTH, gv.CapWidth) # 设置视频帧宽度
  cap.set(cv2.CAP_PROP_FRAME_HEIGHT, gv.CapHeight) # 设置视频帧高度

  cv2.namedWindow('cam_roi') # 创建名为"cam_roi"的窗口
  while not gv.exit_flag:
    ret, frame_origin = cap.read() # 读取一帧图像
    if not ret: # 如果读取到的帧为空
      gv.logger.PrintString("Thread_Cam Error: Failed to read frame from camera.")
      break
    frame_origin_height, frame_origin_width = frame_origin.shape[0:2]
    x = (frame_origin_width - gv.RoiWidth) // 2 # 计算裁剪区域的左上角x坐标
    y = (frame_origin_height - gv.RoiHeight) // 2 # 计算裁剪区域的左上角y坐标
    frame_roi = frame_origin[y:y+gv.RoiHeight, x:x+gv.RoiWidth] # 裁剪图像

    if gv.draw_table_flag:
      draw_table(frame_roi,
        pt1=(20,10),
        pt2=(1050,1070),
        rows=9, cols=8,
        color=(0,0,255),
        thickness=2
      )

    cv2.imshow('cam_roi', frame_roi) # 在窗口中显示裁剪后的图像
    PressKey = cv2.waitKey(10) & 0xFF
    if PressKey & 0xFF == 27: # 如果按下ESC键
      break # 退出循环

  cap.release() # 释放摄像头资源
  gv.logger.PrintString("Thread_Cam Info: Camera resource released.")
  cv2.destroyAllWindows() # 关闭所有窗口
  gv.logger.PrintString("Thread_Cam Info: All windows closed.")

  gv.logger.PrintString("Thread_Cam Info: Exit.") # 打印 Thread_Cam 已退出信息


