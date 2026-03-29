# 按s按键拍照并保存为jpg文件
import os
import cv2

CAM_INDEX = 1 # 摄像头索引，0表示默认摄像头

cap_width = 1920 # 摄像头分辨率宽度
cap_height = 1080 # 摄像头分辨率高度

roi_width = cap_height
roi_height = cap_height

KEY_ESC = 27
KEY_s = ord('s')
KEY_S = ord('S')

jpg_save_index = 129

def main():
  cam = cv2.VideoCapture(CAM_INDEX) # 创建摄像头捕获对象，0表示默认摄像头
  if not cam.isOpened(): # 如果摄像头未成功打开
    print("无法打开摄像头") # 打印错误信息
    return # 退出程序

  cam.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width) # 设置摄像头分辨率宽度
  cam.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height) # 设置摄像头分辨率高度
  
  cv2.namedWindow('cam_roi') # 创建名为"cam_roi"的窗口，显示裁剪后的图像
  print("按ESC键退出程序")

  # 定义保存目录 (放在循环外)
  jpg_save_dir = "train_images"
  if not os.path.exists(jpg_save_dir):
      os.makedirs(jpg_save_dir)


  while True:
    ret, frame_origin = cam.read() # 读取摄像头帧
    if not ret: # 如果帧读取失败
      print("无法读取摄像头帧")  # 打印错误信息
      break # 退出循环
    
    frame_origin_height, frame_origin_width = frame_origin.shape[0:2] # 获取帧的宽度和高度
    x = (frame_origin_width - roi_width) // 2 # 计算裁剪区域的左上角x坐标
    y = (frame_origin_height - roi_height) // 2 # 计算裁剪区域的左上角y坐标
    frame_roi = frame_origin[y:y+roi_height, x:x+roi_width] # 裁剪图像

    cv2.imshow('cam_roi', frame_roi) # 在窗口中显示裁剪后的图像

    key_get = cv2.waitKey(1) & 0xFF # 等待按键输入
    if key_get == 27: # 如果按下ESC键
      break # 退出循环
    elif key_get == KEY_s or key_get == KEY_S: # 如果按下s/S键
      global jpg_save_index # 标注这是一个全局变量，用于保存jpg文件名的索引
      jpg_name = f"train_{jpg_save_index:05d}.jpg" # 设置保存的图片文件名
      jpg_save_index += 1 # 增加jpg文件名的索引，确保每个文件都有唯一的文件名
      jpg_full_path = os.path.join(jpg_save_dir, jpg_name) # 拼接jpg文件的完整路径
      compression_params = [cv2.IMWRITE_JPEG_QUALITY, 95] # 设置JPEG压缩质量，100是最好质量，95能在画质和文件大小之间取得平衡
      cv2.imwrite(jpg_full_path, frame_roi, compression_params) # 保存裁剪后的图像
      print(f"已保存图像: {jpg_full_path}") # 打印保存的图像路径


  cam.release() # 释放摄像头
  print("相机资源已释放")
  cv2.destroyAllWindows() # 关闭所有窗口
  print("所有窗口已关闭")

if __name__ == "__main__":
  main()
