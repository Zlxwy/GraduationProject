# AprilTag 识别，实时检测摄像头画面中的 AprilTag 标签
import cv2
import numpy as np
import apriltag

CAM_INDEX = 0 # 摄像头索引，0 表示默认摄像头

cap_width = 1920 # 摄像头分辨率宽度
cap_height = 1080 # 摄像头分辨率高度

roi_width = cap_height
roi_height = cap_height

def main():
  cam = cv2.VideoCapture(CAM_INDEX) # 创建摄像头捕获对象，0 表示默认摄像头
  if not cam.isOpened(): # 如果摄像头未成功打开
    print("无法打开摄像头") # 打印错误信息
    return # 退出程序

  cam.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width) # 设置摄像头分辨率宽度
  cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height) # 设置摄像头分辨率高度
  
  AprilTagDetector = apriltag.Detector(apriltag.DetectorOptions(families="tag36h11")) # 创建AprilTag检测器
  
  cv2.namedWindow('cam_apriltag') # 创建名为"cam_apriltag"的窗口
  print("按 ESC 键退出程序")

  while True:
    ret, frame_origin = cam.read() # 读取摄像头帧
    if not ret: # 如果帧读取失败
      print("无法读取摄像头帧")  # 打印错误信息
      break # 退出循环
    
    frame_origin_height, frame_origin_width = frame_origin.shape[0:2] # 获取帧的宽度和高度
    x = (frame_origin_width - roi_width) // 2 # 计算裁剪区域的左上角 x 坐标
    y = (frame_origin_height - roi_height) // 2 # 计算裁剪区域的左上角 y 坐标
    frame_roi = frame_origin[y:y+roi_height, x:x+roi_width] # 裁剪图像
    
    frame_roi_gray = cv2.cvtColor(frame_roi, cv2.COLOR_BGR2GRAY) # 将彩色图像转换为灰度图
    results = AprilTagDetector.detect(frame_roi_gray) # 检测 AprilTag
    
    for result in results: # 遍历每一个AprilTag检测结果
      tag_id = result.tag_id # 获取标签 ID
      corners = result.corners # 获取四个角点坐标
      center = result.center # 获取中心点坐标
      print(tag_id) # 打印标签ID
      print(corners) # 打印角点坐标，其格式为[ [x1, y1], [x2, y2], [x3, y3], [x4, y4] ]
      print(center) # 打印中心点坐标，其格式为[ x, y ]
      
      # 显示标签 ID
      label_text = f"ID: {tag_id}"
      cv2.putText(frame_roi, label_text, (int(corners[0][0]), int(corners[0][1])-10),
                  cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2) # 显示标签 ID
      
      # 绘制四边形的四条边
      for i in range(4): # 遍历角点绘制四条边框
        pt1 = tuple(corners[i].astype(int)) # 将角点坐标转换为整数，并转换为元组
        pt2 = tuple(corners[(i+1) % 4].astype(int)) # 将下一个角点坐标转换为整数，并转换为元组
        cv2.line(frame_roi, pt1, pt2, (0, 255, 0), 3) # 绘制绿色边框
      
      # 绘制红色中心点
      center_pt = tuple(center.astype(int)) # 将中心点坐标转换为整数，并转换为元组
      cv2.circle(frame_roi, center_pt, 5, (0,0,255), -1) # 绘制红色中心点
    
    cv2.imshow('cam_apriltag', frame_roi) # 在窗口中显示帧
    
    if cv2.waitKey(1) & 0xFF == 27: # 如果按下 ESC 键
      break # 退出循环
    
  cam.release() # 释放摄像头
  print("相机资源已释放")
  cv2.destroyAllWindows() # 关闭所有窗口
  print("所有窗口已关闭")

if __name__ == "__main__":
  main()
