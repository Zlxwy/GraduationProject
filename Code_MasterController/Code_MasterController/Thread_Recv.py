import GlobalVariable as gv
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
  gMainStream = UartStream(port="COM9", baudrate=115200) # 创建 UartStream 实例
  gMainStream.start() # 启动 UartStream 实例
  gv.logger.PrintString("Thread_Recv Info: UartStream has started.") # 打印 UartStream 实例已启动信息

  while not gv.exit_flag:
    ReadFrameBuffer, ReadState = gMainStream.ReadFrame(timeout=1000) # 读取数据帧
    if ReadState == UartStream_ReadState.Successful:
      FrameType = ReadFrameBuffer[1]
      PayloadLen = b2u32(ReadFrameBuffer[2:2+4])
      PayloadData = ReadFrameBuffer[6:6+PayloadLen]
      CommandType = b2u16(ReadFrameBuffer[6:6+2])

      if FrameType == UartStream_FrameHead.FrameHead2_Req: # 接收到的是请求帧
        pass

      elif FrameType == UartStream_FrameHead.FrameHead2_Res: # 接收到的是响应帧
        pass

      elif FrameType == UartStream_FrameHead.FrameHead2_Evt: # 接收到的是事件帧
        if CommandType == gv.COMMAND_TYPE_KEY_CLICK:
          Parse_COMMAND_TYPE_KEY_CLICK(PayloadData, PayloadLen)
        pass

      else: # 其他帧类型
        gv.logger.PrintString("Thread_Recv Info: Unknown Frame Type.")
        pass
      
    else:
      gv.logger.PrintString("Thread_Recv Info: Receive Timeout~~~")

  gMainStream.stop() # 停止 UartStream 实例
  gv.logger.PrintString("Thread_Recv Info: UartStream has been stopped.") # 打印 UartStream 实例已停止信息
  gv.logger.PrintString("Thread_Recv Info: Exit.") # 打印 Thread_Recv 已退出信息







def Parse_COMMAND_TYPE_KEY_CLICK(PayloadData: bytes, PayloadLen: int):
  KeyIndex = b2u16(PayloadData[2:2+2]) # 按键索引
  KeyMotion = PayloadData[4] # 按键动作：0x00按下(Pressed)，0x01松开(Released)
  if KeyMotion == 0x00: # 只处理按下事件
    match KeyIndex:
      case 0x0000:
        gv.draw_table_flag = not gv.draw_table_flag
        gv.logger.PrintString("Key 0 Pressed.")
      case 0x0001:
        gv.draw_table_flag = not gv.draw_table_flag
        gv.logger.PrintString("Key 1 Pressed.")
      case 0x0002:
        gv.draw_table_flag = not gv.draw_table_flag
        gv.logger.PrintString("Key 2 Pressed.")
      case 0x0003:
        gv.draw_table_flag = not gv.draw_table_flag
        gv.logger.PrintString("Key 3 Pressed.")
      case _:
        gv.logger.PrintString("Unknown Key Index.")


