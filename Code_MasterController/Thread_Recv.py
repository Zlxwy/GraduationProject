import GlobalVariable as gVar
import time
from MyLibs.Log import Log
from MyLibs.UartStream import *
from MyLibs.BytesConv import BytesToUint16_BigEndian as b2u16
from MyLibs.BytesConv import BytesToUint32_BigEndian as b2u32
from MyLibs.BytesConv import BytesToUint64_BigEndian as b2u64
from MyLibs.BytesConv import BytesToInt16_BigEndian as b2s16
from MyLibs.BytesConv import BytesToInt32_BigEndian as b2s32
from MyLibs.BytesConv import BytesToInt64_BigEndian as b2s64
from MyLibs.BytesConv import BytesToFloat32_BigEndian as b2f32
from MyLibs.BytesConv import Uint16ToBytes_BigEndian as u162b
from MyLibs.BytesConv import Uint32ToBytes_BigEndian as u322b
from MyLibs.BytesConv import Uint64ToBytes_BigEndian as u642b
from MyLibs.BytesConv import Int16ToBytes_BigEndian as s162b
from MyLibs.BytesConv import Int32ToBytes_BigEndian as s322b
from MyLibs.BytesConv import Int64ToBytes_BigEndian as s642b
from MyLibs.BytesConv import Float32ToBytes_BigEndian as f322b


def RecvThreadFunc():
  this_thread_log_enabled = False
  gVar.logger.PrintString("Thread_Recv Info: Log enabled.", enabled=this_thread_log_enabled) # 打印 Thread_Recv 日志已启用信息
  """
  接收线程函数：负责从串口接收数据帧并解析
  """
  gVar.logger.PrintString("Thread_Recv Info: Running.", enabled=this_thread_log_enabled) # 打印 Thread_Recv 正在运行信息

  try:
    gVar.MainStream = UartStream(port="COM9", baudrate=115200) # 创建 UartStream 实例
  except Exception as e:
    gVar.logger.PrintString(f"Thread_Recv Error: UartStream Init failed.", enabled=this_thread_log_enabled)
    gVar.logger.PrintString(f"Thread_Recv Error: {e}", enabled=this_thread_log_enabled)
    gVar.logger.PrintString("Thread_Recv Info: Exit.", enabled=this_thread_log_enabled) # 打印 Thread_Recv 已退出信息
    return

  gVar.MainStream.start() # 启动 UartStream 实例
  gVar.logger.PrintString("Thread_Recv Info: UartStream has started.", enabled=this_thread_log_enabled) # 打印 UartStream 实例已启动信息
  
  while not gVar.exit_flag: # 如果退出标志位还没置起
    ReadFrameBuffer, ReadState = gVar.MainStream.ReadFrame(timeout=1000) # 读取数据帧
    gVar.logger.PrintHexBytes(ReadFrameBuffer, prefix="Thread_Recv Info: ReadFrameBuffer ", suffix="", enabled=this_thread_log_enabled) # 打印读取到的数据帧
    if ReadState == UartStream_ReadState.Successful: # 如果读取成功
      FrameType = ReadFrameBuffer[1] # 获取帧类型
      PayloadLen = b2u32(ReadFrameBuffer[2:2+4]) # 获取有效数据长度
      PayloadData = ReadFrameBuffer[6:6+PayloadLen] # 获取有效数据
      CommandType = b2u16(ReadFrameBuffer[6:6+2]) # 获取命令类型

      if FrameType == UartStream_FrameHead.FrameHead2_Req: # 接收到的是请求帧
        pass

      elif FrameType == UartStream_FrameHead.FrameHead2_Res: # 接收到的是响应帧
        pass

      elif FrameType == UartStream_FrameHead.FrameHead2_Evt: # 接收到的是事件帧
        if CommandType == gVar.COMMAND_TYPE_KEY_CLICK: # 如果是按键点击事件
          Parse_COMMAND_TYPE_KEY_CLICK(PayloadData, PayloadLen) # 调用解析按键点击事件函数解析有效数据
        else: # 其他事件类型
          gVar.logger.PrintString(f"Thread_Recv Info: Unknown Event Type: {CommandType}", enabled=this_thread_log_enabled) # 打印未知事件类型
        pass

      else: # 其他帧类型
        gVar.logger.PrintString("Thread_Recv Info: Unknown Frame Type.", enabled=this_thread_log_enabled)
        pass
      
    else:
      gVar.logger.PrintString("Thread_Recv Info: Receive Timeout~~~", enabled=this_thread_log_enabled)

  gVar.MainStream.stop() # 停止 UartStream 实例
  gVar.logger.PrintString("Thread_Recv Info: UartStream has been stopped.", enabled=this_thread_log_enabled) # 打印 UartStream 实例已停止信息
  gVar.logger.PrintString("Thread_Recv Info: Exit.", enabled=this_thread_log_enabled) # 打印 Thread_Recv 已退出信息







def Parse_COMMAND_TYPE_KEY_CLICK(PayloadData: bytes, PayloadLen: int):
  KeyIndex = b2u16(PayloadData[2:2+2]) # 按键索引
  KeyMotion = PayloadData[4] # 按键动作：0x00按下(Pressed)，0x01松开(Released)
  if KeyMotion == 0x00: # 只处理按下事件
    match KeyIndex:
      case 0x0000:
        gVar.logger.PrintString("Key 0 Pressed.")
      case 0x0001:
        gVar.logger.PrintString("Key 1 Pressed.")
      case 0x0002:
        gVar.logger.PrintString("Key 2 Pressed.")
      case 0x0003:
        gVar.logger.PrintString("Key 3 Pressed.")
      case _:
        gVar.logger.PrintString("Unknown Key Index.")


