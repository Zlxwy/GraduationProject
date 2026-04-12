import Shared as gVar
import time
import threading
from MyLibs.Log import Log
from Thread_Recv import RecvThreadFunc
from Thread_Cam import CamThreadFunc

if __name__ == "__main__":
  gVar.logger = Log() # 创建Log实例
  gVar.logger.PrintString("Log has Initialized.") # 打印Log已初始化信息

  recv_thread = threading.Thread(target=RecvThreadFunc) # 接收线程，非守护线程，通过exit_flag通知退出
  gVar.logger.PrintString("RecvThread has created.") # 打印 RecvThread 已创建信息
  cam_thread = threading.Thread(target=CamThreadFunc) # 相机线程，非守护线程，通过exit_flag通知退出
  gVar.logger.PrintString("CamThread has created.") # 打印 CamThread 已创建信息
  
  recv_thread.start() # 启动接收线程
  gVar.logger.PrintString("RecvThread has started.") # 打印 RecvThread 已启动信息
  cam_thread.start() # 启动相机线程
  gVar.logger.PrintString("CamThread has started.") # 打印 CamThread 已启动信息

  try:
    while True: # 无限循环，直到收到信号
      time.sleep(0.5)
  except KeyboardInterrupt:
    gVar.exit_flag = True
    gVar.logger.PrintString("Program has been stopped by user.")
  finally:
    recv_thread.join()
    cam_thread.join()
    time.sleep(0.5)
  
