# 创建一个黑色的帧
import numpy as np
import cv2

frame_width = 1080
frame_height = 1080



def main():
  cv2.namedWindow('black_frame') # 创建名为"black_frame"的窗口
  print("按ESC键退出程序")

  while True:
    black_frame = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

    cv2.imshow('black_frame', black_frame) # 在窗口中显示黑色帧

    PressKey = cv2.waitKey(10) & 0xFF
    if PressKey & 0xFF == 27: # 如果按下ESC键
      break # 退出循环

  cv2.destroyAllWindows() # 关闭所有窗口
  print("程序退出")



if __name__ == '__main__':
  main()