# 将图片裁剪出感兴趣区，以便之后给YOLO训练能得到32倍数的像素点
import cv2

CAM_INDEX = 1 # 摄像头索引，0表示默认摄像头

cap_width = 1920 # 摄像头分辨率宽度
cap_height = 1080 # 摄像头分辨率高度

roi_width = cap_height
roi_height = cap_height

def main():
  cam = cv2.VideoCapture(CAM_INDEX) # 创建摄像头捕获对象，0表示默认摄像头
  if not cam.isOpened(): # 如果摄像头未成功打开
    print("无法打开摄像头") # 打印错误信息
    return # 退出程序

  cam.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width) # 设置摄像头分辨率宽度
  cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height) # 设置摄像头分辨率高度
  
#   cv2.namedWindow('cam_origin') # 创建名为"cam"的窗口，显示原始图像
  cv2.namedWindow('cam_roi') # 创建名为"cam_roi"的窗口，显示裁剪后的图像
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

    # cv2.imshow('cam_origin', frame_origin) # 在窗口中显示帧
    cv2.imshow('cam_roi', frame_roi) # 在窗口中显示裁剪后的图像

    if cv2.waitKey(1) & 0xFF == 27: # 如果按下ESC键
      break # 退出循环
    
  cam.release() # 释放摄像头
  print("相机资源已释放")
  cv2.destroyAllWindows() # 关闭所有窗口
  print("所有窗口已关闭")

if __name__ == "__main__":
  main()
