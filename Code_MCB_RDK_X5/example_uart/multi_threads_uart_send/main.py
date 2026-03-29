from Timer import Timer
from UartStream import UartStream, UartStream_FrameHead, UartStream_FrameType, UartStream_ParseState, UartStream_ReadState
import time






def send_hello(): # 通过串口发送 Hello! 的函数
  MainCmnct.SendString( f"[{time.strftime('%H:%M:%S')}] Hello!\n" )

def send_hi(): # 通过串口发送 Hi! 的函数
  MainCmnct.SendString( f"[{time.strftime('%H:%M:%S')}] Hi!\n" )

def send_array(): # 通过串口发送数组的函数
  MainCmnct.SendBytes( bytes([0x66, 0x67, 0x68, 0x69, 0x6A, ord('\n')]) ) # 调用 UartStream 实例的 SendBytes 方法发送数组

def send_frame(): # 通过串口发送数据帧的函数
  MainCmnct.WriteFrame(UartStream_FrameHead.FrameHead2_Req, b"Hello World!")





MainCmnct = UartStream(port="/dev/ttyS1", baudrate=115200) # 创建 UartStream 实例
MainCmnct.start() # 启动 UartStream 实例
print("UartStream started") # 打印 UartStream 实例已启动信息

timer_hello = Timer(interval_ms=10000, task=send_hello) # 1000ms间隔调用send_hello
timer_hi = Timer(interval_ms=20000, task=send_hi) # 3000ms间隔调用send_hi
timer_array = Timer(interval_ms=10000, task=send_array) # 5000ms间隔调用send_array
timer_frame = Timer(interval_ms=10000, task=send_frame) # 10000ms间隔调用send_frame
timer_hello.start()  # 启动 timer_hello 定时器
print("timer_hello started")  # 打印 timer_hello 定时器已启动信息
timer_hi.start()  # 启动 timer_hi 定时器
print("timer_hi started")  # 打印 timer_hi 定时器已启动信息
timer_array.start()  # 启动 timer_array 定时器
print("timer_array started")  # 打印 timer_array 定时器已启动信息
timer_frame.start()  # 启动 timer_frame 定时器
print("timer_frame started")  # 打印 timer_frame 定时器已启动信息

try:
  while True: # 一个无限循环，用于持续读取串口数据
    ReadFrameData, ReadState = MainCmnct.ReadFrame(timeout=100000000) # 调用UartStream实例的ReadFrame方法读取数据帧
    match (ReadState): # 根据读取状态进行匹配
      case UartStream_ReadState.NoData: # 一点儿数据都没读到，超时了
        print("NoData") # 打印提示信息
      case UartStream_ReadState.CrcErr: # 完整读到了数据，但CRC校验错误
        print("CrcErr") # 打印提示信息
      case UartStream_ReadState.Timeout: # 读了一部分数据，但中途超时退出了
        print("Timeout") # 打印提示信息
      case UartStream_ReadState.Successful: # 完整读到了数据，CRC校验也通过了
        bytes_print = ''.join([f" {rfd:02X}" for rfd in ReadFrameData])
        print("Successful: " + bytes_print) # 打印提示信息和读取到的数据帧

except KeyboardInterrupt: # 捕获键盘中断异常
  print("\nCaught KeyboardInterrupt, stopping timers...")

finally:
  timer_hello.stop()  # 停止 timer_hello 定时器
  print("timer_hello stopped")  # 打印 timer_hello 定时器已停止信息
  timer_hi.stop()  # 停止 timer_hi 定时器
  print("timer_hi stopped")  # 打印 timer_hi 定时器已停止信息
  timer_array.stop()  # 停止 timer_array 定时器
  print("timer_array stopped")  # 打印 timer_array 定时器已停止信息
  timer_frame.stop()  # 停止 timer_frame 定时器
  print("timer_frame stopped")  # 打印 timer_frame 定时器已停止信息

  MainCmnct.stop()  # 停止 UartStream 实例
  print("UartStream stopped")  # 打印 UartStream 实例已停止信息

  print("\nTimers and UartStream have been stopped!")
  print("Main program has been terminated!")
