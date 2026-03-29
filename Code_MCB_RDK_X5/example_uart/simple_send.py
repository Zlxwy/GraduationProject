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
@brief 主函数
"""
if __name__ == '__main__':
  signal.signal(signal.SIGINT, signal_handler)
  uart1 = serial.Serial(
    port="/dev/ttyS1", # UART1
    baudrate=115200, # 115200波特率
    bytesize=serial.EIGHTBITS, # 8位数据位
    parity=serial.PARITY_NONE, # 无校验位
    stopbits=serial.STOPBITS_ONE # 1位停止位
  )
  print("按Ctrl+C退出")
  
  while True:
    # 发送字符串
    send_data = "hello world\n"
    uart1.write(send_data.encode('UTF-8'))

    # 发送字节数组
    # send_data = bytearray([0xAA,0x55])
    # uart1.write(send_data)

    time.sleep(0.1)