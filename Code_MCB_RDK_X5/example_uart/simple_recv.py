import serial
import serial.tools.list_ports
import time
import signal
import sys
import os

"""
@brief 处理中断信号
@param signal 信号
@param frame 帧信息
"""
def signal_handler(signal, frame):
  print("\n程序已退出")
  sys.exit(0)

"""
@brief 简单的串口测试
@param ser 串口对象
"""
def uart_simple_test(ser):
  count = 0

  while True:
    count += 1
    print(f"[{count}] ", end="")

    # 当作字符串接收
    # （这样接收不太安全，因为当接收到含有中英文混合的字符串时，会引发"UnicodeEncodeError"错误）
    try: recv_data = uart1.read(3).decode('utf-8')
    except Exception as e: print(e.args)
    print("Recv String", f"\"{recv_data}\"")

    # # 当作字节串接收
    # recv_data = uart1.read(3)
    # print("Recv 3 bytes: ", list(recv_data))

"""
@brief 串口空闲接收测试
@param ser 串口对象
"""
def uart_idle_test(ser):
  is_idle = bool(True) # 是否处于空闲状态
  idle_trig = bool(False) # 空闲触发标志
  in_waiting_mark = ser.in_waiting # 记录上一次的接收缓冲区大小
  count = 0 # 接收计数
  while True:
    if ser.in_waiting == in_waiting_mark: # 如果接收缓冲区大小没有变化
      if is_idle == False: # 如果上一次处在非空闲状态
        idle_trig = True # 触发空闲标志
        is_idle = True # 回归空闲状态
    else: # 如果接收缓冲区大小发生变化
      is_idle = False # 置非空闲状态
      in_waiting_mark = ser.in_waiting # 更新接收缓冲区大小
      time.sleep(0.01) # 等待一段时间，这是空闲判定的时间间隔

    if idle_trig: # 如果空闲标志触发
      count = count + 1 # 接收计数加一
      print(f"[{count}] recv data: ", ser.read(ser.in_waiting).decode('utf-8'))
      in_waiting_mark = 0 # 重置接收缓冲区大小记录
      idle_trig = False # 清除空闲标志

"""
@brief 主函数
"""
if __name__ == '__main__':
  signal.signal(signal.SIGINT, signal_handler)
  uart1 = serial.Serial(
    port = "/dev/ttyS1", # UART1
    baudrate = 115200, # 115200波特率
    bytesize = serial.EIGHTBITS, # 8位数据位
    parity = serial.PARITY_NONE, # 无校验位
    stopbits = serial.STOPBITS_ONE, # 1位停止位
    timeout = 1 # 1秒钟
  )

  os.system("clear")
  print("按Ctrl+C退出")

  # uart_simple_test(uart1)
  uart_idle_test(uart1)