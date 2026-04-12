import GlobalVariable as gv
import time
import threading
from MyLibs.Log import Log
from Thread_Recv import RecvThreadFunc
from Thread_Cam import CamThreadFunc

if __name__ == "__main__":
  gv.logger = Log() # 创建Log实例
  gv.logger.PrintString("Log has Initialized.") # 打印Log已初始化信息

  recv_thread = threading.Thread(target=RecvThreadFunc) # 接收线程，非守护线程，通过exit_flag通知退出
  gv.logger.PrintString("Thread_Recv has created.") # 打印 Thread_Recv 已创建信息
  cam_thread = threading.Thread(target=CamThreadFunc) # 相机线程，非守护线程，通过exit_flag通知退出
  gv.logger.PrintString("Thread_Cam has created.") # 打印 Thread_Cam 已创建信息

  recv_thread.start() # 启动接收线程
  gv.logger.PrintString("Thread_Recv has started.") # 打印 Thread_Recv 已启动信息
  cam_thread.start() # 启动相机线程
  gv.logger.PrintString("Thread_Cam has started.") # 打印 Thread_Cam 已启动信息

  try:
    while True: # 无限循环，直到收到信号
      time.sleep(0.5)
  except KeyboardInterrupt:
    gv.exit_flag = True
    gv.logger.PrintString("Program has been stopped by user.")
  finally:
    recv_thread.join()
    cam_thread.join()
    time.sleep(0.5) # 延时是为了能把最后一点点数据也打印出来
  
