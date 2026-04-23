import threading
import serial
import queue
import time
from enum import IntEnum
from enum import auto

# CRC-16/CCITT-FALSE 查找表
CRC16_TABLE = (
  0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7,
  0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
  0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6,
  0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
  0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485,
  0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
  0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4,
  0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
  0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823,
  0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
  0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12,
  0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
  0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41,
  0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
  0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70,
  0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
  0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F,
  0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
  0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E,
  0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
  0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D,
  0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
  0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C,
  0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
  0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB,
  0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
  0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A,
  0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
  0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9,
  0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
  0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8,
  0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0
)

class UartStream_FrameHead(IntEnum):
  FrameHead1 = 0x53 # 帧头1
  FrameHead2_Req = 0xCA # 帧头2 请求帧
  FrameHead2_Res = 0x35 # 帧头2 应答帧
  FrameHead2_Evt = 0x96 # 帧头2 事件帧

class UartStream_FrameType(IntEnum):
  Req = auto() # 请求帧
  Res = auto() # 应答帧
  Evt = auto() # 事件帧
  Unknown = auto() # 未知帧类型

class UartStream_ParseState(IntEnum):
  WaitFrameHead1 = auto() # 等待帧头1
  WaitFrameHead2 = auto() # 等待帧头2
  WaitPayloadLen = auto() # 等待数据长度
  WaitPayloadData = auto() # 等待数据
  WaitCrcCheckSum = auto() # 等待校验和
  FrameOverflow = auto() # 帧溢出

class UartStream_ReadState(IntEnum):
  NoData = auto() # 一点儿数据都没读到，超时了
  CrcErr = auto() # 完整读到了数据，但CRC校验错误
  Timeout = auto() # 读了一部分数据，但中途超时退出了
  Successful = auto() # 完整读到了数据，CRC校验也通过了


"""
一个用于异步串口通信的类，支持多线程安全的发送和接收。
"""
class UartStream:

  """
  初始化串口连接和内部组件。
  Args:
      port (str): 串口设备路径，例如 "/dev/ttyS1"。
      baudrate (int, optional): 波特率，默认 115200。
      bytesize (int, optional): 数据位，默认 8 位。
      parity (str, optional): 校验位，默认无校验。
      stopbits (int, optional): 停止位，默认 1 位。
  """
  def __init__(self,
              port="/dev/ttyS1", 
              baudrate=115200,
              bytesize=serial.EIGHTBITS, 
              parity=serial.PARITY_NONE,
              stopbits=serial.STOPBITS_ONE):
    self._uart = serial.Serial(
      port=port,
      baudrate=baudrate,
      bytesize=bytesize,
      parity=parity,
      stopbits=stopbits
    )

    self._send_queue = queue.Queue() # 发送队列，用于多线程安全地传递待发送数据
    self._writer_thread = None # 发送线程，负责从队列中获取数据并发送
    self._reader_thread = None # 接收线程，负责从串口接收数据并处理
    self._serial_lock = threading.Lock() # 接收缓冲区锁，用于多线程安全访问
    self._running = False # 运行标志，用于控制发送接收线程是否继续运行

    self._RECV_BUFFER_SIZE = 256 # 接收缓冲区大小，用于限制接收数据的最大长度
    self._SEND_BUFFER_SIZE = 256 # 发送缓冲区大小，用于限制发送数据的最大长度
    self._RecvIndex = 0 # 接收指针，指向当前接收字节的位置
    self._ReadIndex = 0 # 读取指针，指向当前读取字节的位置
    self._RecvBuffer = bytearray(self._RECV_BUFFER_SIZE) # 接收缓冲区，占位256个元素



  """
  启动内部的发送线程，开始处理发送队列。
  """
  def start(self):
    if self._running: # 如果线程已经在运行（可能是因为重复调用了）
      return # 直接返回，避免重复启动线程
    self._running = True # 设置运行标志为 True，开始运行发送线程
    self._writer_thread = threading.Thread(  # 创建专门的发送线程对象
      target=self._serial_writer_worker,  # 设置目标函数为_serial_writer_worker
      daemon=True # 设置为守护线程，确保在主线程退出时自动结束
    )
    self._reader_thread = threading.Thread(  # 创建专门的接收线程对象
      target=self._serial_reader_worker,  # 设置目标函数为_serial_reader_worker
      daemon=True # 设置为守护线程，确保在主线程退出时自动结束
    )
    self._writer_thread.start()  # 启动发送线程
    self._reader_thread.start()  # 启动接收线程



  """
  停止串口流，关闭线程和串口连接。
  # Args:
    timeout (float, optional): 等待线程结束的超时时间（秒）。
  """
  def stop(self, timeout=5):
    if not self._running: # 如果线程不在运行（可能是因为没有调用 start()）
      return # 直接返回，避免重复停止线程
    self._running = False # 设置运行标志为 False，停止发送线程
    self._send_queue.put(None) # 发送退出信号(None)给发送线程

    if self._writer_thread and self._writer_thread.is_alive(): # 如果发送线程还存在，并且还在运行
      self._writer_thread.join(timeout=timeout) # 等待线程结束，最多等待 timeout 秒
    if self._reader_thread and self._reader_thread.is_alive(): # 如果接收线程还存在，并且还在运行
      self._reader_thread.join(timeout=timeout) # 等待线程结束，最多等待 timeout 秒

    self._uart.close() # 关闭串口连接
  


  """
  专门的接收线程工作函数，是唯一调用 ser.read() 的地方。
  作用：只要收到数据，就将数据存储到接收缓冲区中。
  """
  def _serial_reader_worker(self):
    while self._running:
      if self._uart.in_waiting > 0: # 如果接收缓冲区有数据等待读取
        recv_bytes = self._uart.read(self._uart.in_waiting) # 读取所有可用数据，这是一个bytes类型的对象

        for rb in recv_bytes: # 遍历读取到的每个字节
          self._RecvBuffer[self._RecvIndex] = rb & 0xFF # 存储到接收缓冲区
          self._RecvIndex = self._RecvIndex + 1
          if self._RecvIndex >= self._RECV_BUFFER_SIZE: # 如果接收指针超过了缓冲区大小
            self._RecvIndex = 0 # 重置接收指针，循环利用缓冲区空间



  """
  专门的发送线程工作函数，是唯一调用 ser.write() 的地方。
  """
  def _serial_writer_worker(self):
    while self._running:
      try:
        data_to_send = self._send_queue.get(timeout=1) # 从队列中获取要发送的数据 (阻塞式)
        if data_to_send is None: # 如果收到退出信号(None)
          self._send_queue.task_done() # 标记任务完成
          break # 退出循环，结束发送线程
        bytes_written = self._uart.write(data_to_send) # 执行实际的串口发送
        self._uart.flush() # 确保数据被发送出去
        print(f"UART: Sent {bytes_written} bytes: {repr(data_to_send)}") # 打印发送信息
        self._send_queue.task_done() # 标记队列中的这个任务已经完成
          
      except queue.Empty: # 超时没检测到队列数据
        continue # 队列为空，继续循环检查 self._running 状态

      except Exception as e: # 其他异常
        print(f"Error in UART writer thread: {e}") # 打印异常信息
        if data_to_send is not None: # 如果队列中还有数据
          self._send_queue.task_done() # 发生错误时也应标记任务完成，以防队列卡住



  """
  将数据加入发送队列，由后台线程异步发送。
  这个方法是线程安全的，可以被多个线程同时调用。
  Args:
    data (str): 要发送的字符串数据。
  """
  def SendString(self, strdata: str):
    if not self._running:  # 如果线程不在运行（可能是因为没有调用 start()）
      raise RuntimeError("UART Stream is not running. Cannot send data.") # 抛出运行时错误，提示用户先启动 UartStream
    self._send_queue.put(strdata.encode('utf-8')) # 将字符串放入队列，由发送线程处理

  def SendBytes(self, arrdata: bytes):
    if not self._running:  # 如果线程不在运行（可能是因为没有调用 start()）
      raise RuntimeError("UART Stream is not running. Cannot send data.") # 抛出运行时错误，提示用户先启动 UartStream
    self._send_queue.put(arrdata) # 将字符串放入队列，由发送线程处理


  """
  从接收缓冲区读取一帧数据。
  Args:
    timeout: 等待数据的超时时间(ms)。
  Returns:
    bytes: 一帧完整的字节流数据。
  """
  def ReadFrame(self, timeout: int) -> (bytes, UartStream_ReadState):
    with self._serial_lock: # 加锁，虽说这个函数原则上不应该被多个线程同时调用，还是加锁确保多线程安全
      ReadFrameData = bytearray(self._SEND_BUFFER_SIZE) # 用来暂存一帧数据的字节数组
      state = UartStream_ParseState.WaitFrameHead1 # 解析状态机初始状态，等待帧头1
      ReadState = UartStream_ReadState.NoData # 读取状态机初始状态，等待数据读取
      HasEverFoundData = False # 是否曾经找到过数据
                              # - 如果没找到过数据就直接退出了的话，返回的是UartStream_ReadState.NoData
                              # - 如果找到过数据但中途超时退出了，返回的是UartStream_ReadState.Timeout
      ShouldBreakTheInfiniteLoop = False # 是否应该跳出无限循环，如果置true的话，则会跳出while(1)循环

      tempHead1 = 0; # 用作uint8类型，用来暂存帧头1
      tempHead2 = 0; # 用作uint8类型，用来暂存帧头2
      tempLen = 0; # 用作uint32类型，用来暂存数据长度
      tempCrc = 0; # 用作uint16类型，用来暂存校验和

      LenCnt = 0; # 用作uint8类型，数据长度接收计数器，最大为4
      DataCnt = 0; # 用作uint32类型，数据接收计数器，最大值不确定
      CrcCnt = 0; # 用作uint8类型，校验和接收计数器，最大为2

      TimeMark = 0; # 记录消耗时间的变量，单位为毫秒

      while True: # 是要依次往下读取的，设置为死循环，通过return和break退出
        # 检测接收缓冲区的读指针和接收指针是否重合，如果重合则表示无数据可读
        TimeMark = int(time.monotonic() * 1000) # 获取当前时间，作为起始
        while self._ReadIndex == self._RecvIndex: # 当接收指针与读取指针相等时，则无数据可读
          if ( int(time.monotonic()*1000) - TimeMark ) >= timeout: # 超时没检测到数据可读
            if HasEverFoundData: ReadState = UartStream_ReadState.Timeout # 如果之前曾经找到过数据，则表示中途超时
            else:                ReadState = UartStream_ReadState.NoData # 如果之前从来没找到过数据，则表示超时读取
            return b"", ReadState # 受不了这气，直接return超时读取，退出整个函数，也不用再继续往下执行，包括读指针自增
        HasEverFoundData = True # 执行到这里了，表示有数据可读，标记曾经找到过数据

        ReadByte = self._RecvBuffer[self._ReadIndex] & 0xFF # 通过接收缓冲区的读指针读取一个字节
        match state: # 根据当前状态进行判断
          # 如果在等待帧头1状态，接收到了正确的帧头1，则切换下一个状态：等待帧头2
          case UartStream_ParseState.WaitFrameHead1: # 如果此时是等待帧头1
            if ReadByte == UartStream_FrameHead.FrameHead1: # 确实接收到了帧头1
              state = UartStream_ParseState.WaitFrameHead2 # 切换到等待帧头2状态
              tempHead1 = ReadByte & 0xFF # 暂存帧头1
            else: # 接收到的不是帧头1
              state = UartStream_ParseState.WaitFrameHead1 # 重新进入等待帧头1状态
              tempHead1 = 0; # 清空帧头1
              tempHead2 = 0; # 清空帧头2
              tempLen = 0; # 清空数据长度
              tempCrc = 0; # 清空校验和
          
          # 如果在等待帧头2状态，接收到了正确的帧头2，则切换下一个状态：等待数据长度
          case UartStream_ParseState.WaitFrameHead2: # 如果此时是等待帧头2
            if ( (ReadByte == UartStream_FrameHead.FrameHead2_Req) # 确实是接收到了请求帧的帧头2
              or (ReadByte == UartStream_FrameHead.FrameHead2_Res) # 确实是接收到了响应帧的帧头2
              or (ReadByte == UartStream_FrameHead.FrameHead2_Evt) ): # 确实是接收到了事件帧的帧头2
              state = UartStream_ParseState.WaitPayloadLen # 进入等待数据长度状态
              tempHead2 = ReadByte & 0xFF # 暂存帧头2
              ReadFrameData[0] = tempHead1 & 0xFF # 保存帧头1到ReadFrameData
              ReadFrameData[1] = tempHead2 & 0xFF # 保存帧头2到ReadFrameData
            else: # 接收到的不是帧头2
              state = UartStream_ParseState.WaitFrameHead1 # 重新进入等待帧头1状态
              tempHead1 = 0 # 清空帧头1
              tempHead2 = 0 # 清空帧头2
              ReadFrameData[0] = 0 # 清空ReadFrameData[0]
              ReadFrameData[1] = 0 # 清空ReadFrameData[1]

          # 如果此时是等待数据长度，接收到了数据长度，则切换下一个状态：等待数据
          case UartStream_ParseState.WaitPayloadLen: # 如果此时是等待数据长度
            tempLen |= ( ReadByte << ((3-LenCnt)*8) ) & 0xFFFFFFFF # 保存数据长度
            ReadFrameData[2+LenCnt] = ReadByte & 0xFF # 保存数据长度到FrameData[2~5]
            LenCnt += 1 # 数据长度计数器自增1
            if (LenCnt >= 4): # 数据长度计数器达到4，表示数据长度已经接收完毕
              state = UartStream_ParseState.WaitPayloadData # 进入等待数据状态
          
          # 如果此时是等待数据，接收到了数据，则切换下一个状态：等待校验和
          case UartStream_ParseState.WaitPayloadData: # 如果此时是等待数据
            ReadFrameData[6+DataCnt] = ReadByte & 0xFF # 保存数据到FrameData[6~]
            DataCnt += 1 # 数据计数器自增1
            if (DataCnt >= tempLen): # 数据计数器达到数据长度，表示数据已经接收完毕
              state = UartStream_ParseState.WaitCrcCheckSum # 进入等待校验和状态

          # 如果此时是等待校验和，接收到了校验和，则恢复到初始状态：等待帧头1
          case UartStream_ParseState.WaitCrcCheckSum: # 如果此时是等待校验和
            tempCrc |= ( ReadByte << ((1-CrcCnt)*8) ) & 0xFFFF # 保存校验和
            ReadFrameData[6+tempLen+CrcCnt] = ReadByte & 0xFF # 保存校验和到FrameData[6+len~]
            CrcCnt += 1 # 校验和计数器自增1
            if CrcCnt >= 2: # 校验和计数器达到2，表示校验和已经接收完毕
              state = UartStream_ParseState.WaitFrameHead1 # 重新进入等待帧头1状态
              if ( tempCrc == self._CRC16_Cal(ReadFrameData[:6+tempLen]) & 0xFFFF ): # 判断校验和是否正确
                ReadState = UartStream_ReadState.Successful # 如果校验和正确，则标记读取成功
              else: # 如果校验和不正确
                ReadState =  UartStream_ReadState.CrcErr # 如果校验和不正确，则标记校验和错误
              ShouldBreakTheInfiniteLoop = True # 标记退出无限循环

        self._ReadIndex += 1 # 读取指针自增1
        if self._ReadIndex >= self._RECV_BUFFER_SIZE: # 读取指针已经到达接收缓冲区的末尾
          self._ReadIndex = 0 # 重置读取指针到接收缓冲区的开头

        if ShouldBreakTheInfiniteLoop: # 如果需要退出循环
          break # 退出循环

      return ReadFrameData[0:6+tempLen+2], ReadState # 返回数据帧（2帧头4数长n数据2校验）、获取状态



  def WriteFrame(self, fh2:UartStream_FrameHead, WriteFrameData:bytes):
    SendBuf = bytearray(self._SEND_BUFFER_SIZE) # 创建一个256长度的字节数组，用于存储要发送的数据帧
    SendBuf[0] = UartStream_FrameHead.FrameHead1 & 0xFF # 帧头1
    SendBuf[1] = fh2 & 0xFF # 帧头2
    SendBuf[2] = (len(WriteFrameData) >> 24) & 0xFF # 数据长度高8位
    SendBuf[3] = (len(WriteFrameData) >> 16) & 0xFF # 数据长度中8位
    SendBuf[4] = (len(WriteFrameData) >> 8) & 0xFF # 数据长度低8位
    SendBuf[5] = (len(WriteFrameData) >> 0) & 0xFF # 数据长度低8位
    SendBuf[6 : 6+len(WriteFrameData)] = WriteFrameData # 有效数据
    crc = self._CRC16_Cal(SendBuf[0:6+len(WriteFrameData)]) & 0xFFFF # 计算校验和
    SendBuf[6+len(WriteFrameData)] = (crc >> 8) & 0xFF; # 校验和高8位
    SendBuf[6+len(WriteFrameData)+1] = (crc >> 0) & 0xFF; # 校验和低8位
    self.SendBytes(SendBuf[0:6+len(WriteFrameData)+2]) # 发送数据包



  def _CRC16_Cal(self, bytes_caled:bytes) ->int:
    crc = 0xFFFF # 初始值为 0xFFFF
    for bc in bytes_caled: # 遍历每个字节
      index = ((crc>>8) ^ bc) & 0xFFFF # 高8位与当前字节异或，得到查表索引
      crc = ( (crc<<8) ^ CRC16_TABLE[index] ) & 0xFFFF # 更新 CRC：低8位左移8位，再与查表结果异或
    return crc