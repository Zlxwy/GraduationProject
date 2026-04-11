# 霍夫圆检测，实时检测摄像头画面中的圆并标记
import cv2
import numpy as np

CAM_INDEX = 1 # 摄像头索引，0表示默认摄像头

cap_width = 1920 # 摄像头分辨率宽度
cap_height = 1080 # 摄像头分辨率高度

roi_width = cap_height
roi_height = cap_height

HOUGH_PARAM1 = 80 # 边缘检测时的高阈值
HOUGH_PARAM2 = 25 # 圆心检测的阈值
HOUGH_MIN_RADIUS = 20 # 圆的最小半径 (直径40像素)
HOUGH_MAX_RADIUS = 35 # 圆的最大半径 (直径60像素)
HOUGH_MIN_DIST = 30 # 圆心之间的最小距离

def main():
  cam = cv2.VideoCapture(CAM_INDEX) # 创建摄像头捕获对象，0表示默认摄像头
  if not cam.isOpened(): # 如果摄像头未成功打开
    print("无法打开摄像头") # 打印错误信息
    return # 退出程序

  cam.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width) # 设置摄像头分辨率宽度
  cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height) # 设置摄像头分辨率高度
  
  cv2.namedWindow('cam_gray_blur') # 创建名为"cam_gray_blur"的窗口
  cv2.namedWindow('cam_hough_circle') # 创建名为"cam_hough_circle"的窗口
  print("按ESC键退出程序")

  while True:
    ret, frame_origin = cam.read() # 读取摄像头帧
    if not ret: # 如果帧读取失败
      print("无法读取摄像头帧")  # 打印错误信息
      break # 退出循环
    
    frame_origin_height, frame_origin_width = frame_origin.shape[0:2] # 获取帧的宽度和高度
    x = (frame_origin_width - roi_width) // 2 # 计算裁剪区域的左上角x坐标
    y = (frame_origin_height - roi_height) // 2 # 计算裁剪区域的左上角y坐标
    frame_roi = frame_origin[y:y+roi_height, x:x+roi_width] # 裁剪图像
    
    frame_roi_gray = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY) # 将彩色图像转换为灰度图
    frame_roi_gray_blur = cv2.GaussianBlur(frame_roi_gray, (19,19), 2.5) # 高斯模糊去噪
    
    circles = cv2.HoughCircles(
      frame_roi_gray_blur,
      cv2.HOUGH_GRADIENT,
      dp=1,
      minDist=HOUGH_MIN_DIST,
      param1=HOUGH_PARAM1,
      param2=HOUGH_PARAM2,
      minRadius=HOUGH_MIN_RADIUS,
      maxRadius=HOUGH_MAX_RADIUS
    )
    
    if circles is not None: # 如果检测到圆
      circles = np.uint16(np.around(circles)) # 将浮点数转换为整数
      for circle in circles[0, :]: # 遍历每一个圆
        center_x, center_y, radius = circle # 提取圆心坐标和半径
        cv2.circle(frame_roi, (center_x, center_y), 1, (0, 100, 255), 3) # 绘制圆心
        cv2.circle(frame_roi, (center_x, center_y), radius, (255, 0, 255), 2) # 绘制圆周
    
    cv2.imshow('cam_gray_blur', frame_roi_gray_blur) # 在窗口中显示灰度图模糊后的结果
    cv2.imshow('cam_hough_circle', frame_roi) # 在窗口中显示帧
    
    if cv2.waitKey(1) & 0xFF == 27: # 如果按下ESC键
      break # 退出循环
    
  cam.release() # 释放摄像头
  print("相机资源已释放")
  cv2.destroyAllWindows() # 关闭所有窗口
  print("所有窗口已关闭")

if __name__ == "__main__":
  main()
