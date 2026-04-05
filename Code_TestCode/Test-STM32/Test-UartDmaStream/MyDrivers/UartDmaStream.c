#include "UartDmaStream.h"

void UartDmaStream_Init(UartDmaStream_t *cThis,
                         UART_HandleTypeDef *huart,
                         DMA_HandleTypeDef *hdmatx,
                         DMA_HandleTypeDef *hdmarx,
                         void (*DelayMS)(uint32_t ms) ) {
  cThis->huart = huart;
  cThis->hdmatx = hdmatx;
  cThis->hdmarx = hdmarx;

  memset(cThis->TranBuf, 0, UART_DMA_STREAM_TX_BUF_SIZE);
  memset(cThis->RecvBuf, 0, UART_DMA_STREAM_RX_BUF_SIZE);
  
  memset(cThis->TxDataQueue, 0, sizeof(UartDmaStream_TxQueue_t)*UART_DMA_STREAM_TX_QUEUE_SIZE);
  cThis->HandleQueueIndex = 0;
  cThis->EnterQueueIndex = 0;
  cThis->DelayMS = DelayMS;
  cThis->IsTxDmaIdle = true;

  cThis->RecvIndex = 0; // 接收指针指向接收缓冲区的起始位置
  cThis->ReadIndex = 0; // 读取指针指向接收缓冲区的起始位置

  __HAL_DMA_ENABLE_IT(cThis->hdmatx, DMA_IT_TC);
  HAL_UART_Receive_DMA(cThis->huart, cThis->RecvBuf, UART_DMA_STREAM_RX_BUF_SIZE); // 启动DMA接收

#ifdef SEND_BYTES_USE_RTOS_MUTEX // 如果是FreeRTOS环境，就会有这个定义
  cThis->SendBytesMutex = osMutexNew(NULL); // 创建互斥锁，NULL表示不使用默认的优先级继承
#endif
}





void UartDmaStream_FuncCalled_InTxCpltCallback(UartDmaStream_t* cThis) {
  cThis->TxDataQueue[cThis->HandleQueueIndex].StartIndex = 0; // 清空已发送的队列
  cThis->TxDataQueue[cThis->HandleQueueIndex].DataLength = 0; // 清空已发送的队列

  cThis->HandleQueueIndex++; // 切换到下一条队列
  if (cThis->HandleQueueIndex >= UART_DMA_STREAM_TX_QUEUE_SIZE) { // 切换到下一条队列后，索引超出范围
    cThis->HandleQueueIndex = 0; // 索引重置为0，从头开始发送
  }
  
  cThis->IsTxDmaIdle = true; // DMA空闲
}

void UartDmaStream_FuncCalled_InInfiniteLoop(UartDmaStream_t* cThis) {
  if (cThis->TxDataQueue[cThis->HandleQueueIndex].DataLength != 0 && cThis->IsTxDmaIdle) { // 有数据待发送且DMA空闲
    HAL_UART_Transmit_DMA(cThis->huart, // 启动DMA传输
      &cThis->TranBuf[ cThis->TxDataQueue[cThis->HandleQueueIndex].StartIndex ], // 传输缓冲区指针
      cThis->TxDataQueue[cThis->HandleQueueIndex].DataLength // 传输数据长度
    );
    cThis->IsTxDmaIdle = false; // DMA非空闲
  }
  // HAL_Delay(5);
  cThis->DelayMS(5); // 这里加一点延时，不然的话写入总是会出现缺失的问题
}





// SendBytesLen不要超过UART_DMA_STREAM_TX_BUF_SIZE
void UartDmaStream_SendBytes(UartDmaStream_t *cThis, const uint8_t *SendBytes, size_t SendBytesLen) {
#ifdef SEND_BYTES_USE_RTOS_MUTEX // 如果是FreeRTOS环境，就会有这个定义
  osMutexAcquire(cThis->SendBytesMutex, osWaitForever); // 获取互斥锁，阻塞等待直到获取到
#endif

  uint32_t StartIndexMark = cThis->TxDataQueue[cThis->EnterQueueIndex].StartIndex; // 记录当前队列的传输缓冲区起始索引
  uint32_t DataLengthMark; // 这个用来后面来记录数据长度

  /*数据还能填充到传输缓冲区*/
  if (StartIndexMark + SendBytesLen <= UART_DMA_STREAM_TX_BUF_SIZE) {
    cThis->TxDataQueue[cThis->EnterQueueIndex].DataLength = SendBytesLen; // 记录数据长度
    memcpy( // 只需要一次复制
      &cThis->TranBuf[ StartIndexMark ],
      &SendBytes[0],
      cThis->TxDataQueue[cThis->EnterQueueIndex].DataLength
    );

    cThis->EnterQueueIndex++; // 切换到下一条队列
    if (cThis->EnterQueueIndex >= UART_DMA_STREAM_TX_QUEUE_SIZE) {
      cThis->EnterQueueIndex = 0;
    } // 如果下一条队列索引超出范围，则从头开始压入

    cThis->TxDataQueue[cThis->EnterQueueIndex].StartIndex = StartIndexMark + SendBytesLen; // 更新下一条队列的传输缓冲区起始索引
    if (cThis->TxDataQueue[cThis->EnterQueueIndex].StartIndex >= UART_DMA_STREAM_TX_BUF_SIZE) { // 如果下一条队列记录的传输缓冲区起始索引刚好满了
      // 其实进来这里的话，都不会在>UART_DMA_STREAM_TX_BUF_SIZE的情况，只会是=UART_DMA_STREAM_TX_BUF_SIZE的情况，因为上层if已经限制过了>UART_DMA_STREAM_TX_BUF_SIZE的情况
      cThis->TxDataQueue[cThis->EnterQueueIndex].StartIndex -= UART_DMA_STREAM_TX_BUF_SIZE; // 传输缓冲区索引从头开始
    }
  }
  
  /*数据超出传输缓冲区范围，分两次复制进传输缓冲区*/
  else if (StartIndexMark + SendBytesLen > UART_DMA_STREAM_TX_BUF_SIZE) {
    cThis->TxDataQueue[cThis->EnterQueueIndex].DataLength = UART_DMA_STREAM_TX_BUF_SIZE - StartIndexMark; // 记录数据长度
    memcpy( // 复制第一次
      &cThis->TranBuf[ StartIndexMark ],
      &SendBytes[0],
      cThis->TxDataQueue[cThis->EnterQueueIndex].DataLength
    );

    cThis->EnterQueueIndex++; // 切换到下一条队列
    if (cThis->EnterQueueIndex >= UART_DMA_STREAM_TX_QUEUE_SIZE) {
      cThis->EnterQueueIndex = 0;
    } // 如果下一条队列索引超出范围，则从头开始压入

    cThis->TxDataQueue[cThis->EnterQueueIndex].StartIndex = 0; // 传输缓冲区索引从头开始

    cThis->TxDataQueue[cThis->EnterQueueIndex].DataLength = SendBytesLen - (UART_DMA_STREAM_TX_BUF_SIZE - StartIndexMark); // 记录数据长度
    memcpy( // 复制第二次
      &cThis->TranBuf[ 0 ],
      &SendBytes[UART_DMA_STREAM_TX_BUF_SIZE - StartIndexMark],
      cThis->TxDataQueue[cThis->EnterQueueIndex].DataLength
    );

    StartIndexMark = cThis->TxDataQueue[cThis->EnterQueueIndex].StartIndex;
    DataLengthMark = cThis->TxDataQueue[cThis->EnterQueueIndex].DataLength;

    cThis->EnterQueueIndex++; // 切换到下一条队列
    if (cThis->EnterQueueIndex >= UART_DMA_STREAM_TX_QUEUE_SIZE) {
      cThis->EnterQueueIndex = 0;
    } // 如果下一条队列索引超出范围，则从头开始压入

    cThis->TxDataQueue[cThis->EnterQueueIndex].StartIndex = StartIndexMark + DataLengthMark;
    // 这个不会超出范围，因为已经分两次复制过了
  }
#ifdef SEND_BYTES_USE_RTOS_MUTEX // 如果是FreeRTOS环境，就会有这个定义
    osMutexRelease(cThis->SendBytesMutex); // 释放互斥锁
#endif
}

void UartDmaStream_SendString(UartDmaStream_t *cThis, const char *SendString) {
  UartDmaStream_SendBytes(cThis, (const uint8_t *)SendString, strlen(SendString));
}

void UartDmaStream_Printf(UartDmaStream_t *cThis, const char *format, ...) {
  char SendBuf[256];
  va_list args;
  va_start(args, format);
  vsnprintf(SendBuf, sizeof(SendBuf), format, args);
  va_end(args);
  UartDmaStream_SendString(cThis, SendBuf);
}




















// CRC-16/CCITT-FALSE 的预计算查找表（多项式: x^16 + x^12 + x^5 + 1 => 0x1021）
static const uint16_t CRC16_TABLE[256] = {
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
};

/**
 * @brief 计算 CRC-16 (CCITT-FALSE) 校验值
 * @param data 字节串起始地址
 * @param len  字节串长度（字节数）
 * @return CRC-16 校验值（16位）
 */
uint16_t UartDmaStream_CRC16Cal(const uint8_t *bytes, size_t len) {
  uint16_t crc = 0xFFFF;  // 初始值为 0xFFFF
  for (size_t i=0; i<len; i++) {
    uint8_t index = (crc >> 8) ^ bytes[i]; // 高8位与当前字节异或，得到查表索引
    crc = (crc << 8) ^ CRC16_TABLE[index]; // 更新 CRC：低8位左移8位，再与查表结果异或
  }
  return crc;
}

/**
 * @brief 获取当前接收指针位置
 * @param cThis UartDmaStream对象指针
 * @return size_t 当前接收指针位置
 */
size_t UartDmaStream_GetRecvIndex(UartDmaStream_t *cThis) {
  cThis->RecvIndex = (UART_DMA_STREAM_RX_BUF_SIZE - __HAL_DMA_GET_COUNTER(cThis->hdmarx));
  return cThis->RecvIndex;
}





/**
 * @brief 以指定数据帧格式发送一帧数据包
 * @param cThis 指向UartDmaStream_t结构体的指针
 * @param fh2 是请求帧，还是响应帧，还是事件帧
 *   @arg UartDmaStream_FrameHead2_Req 请求帧
 *   @arg UartDmaStream_FrameHead2_Res 响应帧
 *   @arg UartDmaStream_FrameHead2_Evt 事件帧
 * @param WriteFrameData 指向要发送的数据包的指针，只是有效数据即可，最大(TEMP_SEND_BUF_SIZE-8)字节
 * @param WriteFrameDataLen 要发送的数据包的长度，有效数据的长度，最大(TEMP_SEND_BUF_SIZE-8)
 * @return 无
 */
#define TEMP_SEND_BUF_SIZE  256 // 临时发送缓冲区的大小
void UartDmaStream_WriteFrame(UartDmaStream_t *cThis, UartDmaStream_FrameHead_e fh2, uint8_t *WriteFrameData, size_t WriteFrameDataLen) {
  uint8_t SendBuf[TEMP_SEND_BUF_SIZE]; // 临时发送缓冲区
  SendBuf[0] = UartDmaStream_FrameHead1; // 帧头1
  SendBuf[1] = fh2; // 帧头2
  SendBuf[2] = (WriteFrameDataLen >> 24) & 0xFF;
  SendBuf[3] = (WriteFrameDataLen >> 16) & 0xFF;
  SendBuf[4] = (WriteFrameDataLen >> 8) & 0xFF;
  SendBuf[5] = (WriteFrameDataLen >> 0) & 0xFF;
  memcpy(&SendBuf[6], WriteFrameData, WriteFrameDataLen); // 有效数据
  uint16_t crc = UartDmaStream_CRC16Cal(SendBuf, 6+WriteFrameDataLen); // 计算校验和
  SendBuf[6+WriteFrameDataLen] = (crc >> 8) & 0xFF; // 校验和高8位
  SendBuf[6+WriteFrameDataLen+1] = (crc >> 0) & 0xFF; // 校验和低8位
  UartDmaStream_SendBytes(cThis, SendBuf, 6+WriteFrameDataLen+2); // 发送数据包
}

/**
 * @brief  从接收流缓冲区中读取一帧数据，并返回对应的状态
 * @param  cThis UartDmaStream对象指针
 * @param  ReadFrameData 接收一帧数据的指针
 * @param  Timeout 超时时间
 * @return UartDmaStream_ReadState_e枚举类型
 *   @arg UartDmaStream_ReadState_NoData 一点儿数据都没读到，超时了
 *   @arg UartDmaStream_ReadState_CrcErr 完整读到了数据，但CRC校验错误
 *   @arg UartDmaStream_ReadState_Timeout 读了一部分数据，但中途超时退出了
 *   @arg UartDmaStream_ReadState_Successful 完整读到了数据，CRC校验也通过了
 */
UartDmaStream_ReadState_e UartDmaStream_ReadFrame(UartDmaStream_t *cThis, uint8_t *ReadFrameData, uint32_t Timeout) {
  UartDmaStream_ParseState_e state = UartDmaStream_ParseState_WaitFrameHead1; // 解析状态机初始状态，等待帧头1
  UartDmaStream_ReadState_e ReadState = UartDmaStream_ReadState_NoData; // 读取状态机初始状态，等待数据读取
  bool HasEverFoundData = false; // 是否曾经找到过数据
                                 // - 如果没找到过数据就直接退出了的话，返回的是UartDmaStream_ReadState_NoData
                                 // - 如果找到过数据但中途超时退出了，返回的是UartDmaStream_ReadState_Timeout
  bool ShouldBreakTheInfiniteLoop = false; // 是否应该跳出无限循环，如果置true的话，则会跳出while(1)循环

  uint8_t tempHead1 = 0; // 用来暂存帧头1
  uint8_t tempHead2 = 0; // 用来暂存帧头2
  uint32_t tempLen = 0; // 用来暂存数据长度
  uint16_t tempCrc = 0; // 用来暂存校验和

  uint8_t LenCnt = 0; // 数据长度接收计数器，最大为4
  uint32_t DataCnt = 0; // 数据接收计数器，最大值不确定
  uint8_t CrcCnt = 0; // 校验和接收计数器，最大为2

  uint32_t TimeMark; // 记录时间戳的变量

  while (true) { // 是要依次往下读取的，设置为死循环，通过return和break退出循环
    /*检测接收缓冲区的读指针和接收指针是否重合，如果重合则表示无数据可读*/
    TimeMark = HAL_GetTick(); // 获取当前时间，作为起始
    while ( cThis->ReadIndex == UartDmaStream_GetRecvIndex(cThis) ) { // 当接收指针与读取指针相等时，则无数据可读
      if (HAL_GetTick()-TimeMark >= Timeout) { // 超时没检测到数据可读
        if (HasEverFoundData) ReadState = UartDmaStream_ReadState_Timeout; // 如果之前曾经找到过数据，则表示中途超时
        else                  ReadState = UartDmaStream_ReadState_NoData; // 如果之前从来没找到过数据，则表示超时读取
        return ReadState; // 受不了这气，直接return超时读取，退出整个函数，也不用再继续往下执行，包括读指针自增
      }
      // cThis->DelayMS(5);
    }
    HasEverFoundData = true; // 执行到这里了，表示有数据可读，标记曾经找到过数据
    
    uint8_t ReadByte = cThis->RecvBuf[cThis->ReadIndex]; // 通过接收缓冲区的读指针读取一个字节
    switch (state) { // 根据当前状态进行判断
      /*如果在等待帧头1状态，接收到了正确的帧头1，则切换下一个状态：等待帧头2*/
      case UartDmaStream_ParseState_WaitFrameHead1: // 如果此时是等待帧头1
        if (ReadByte == UartDmaStream_FrameHead1) { // 确实接收到了帧头1
          state = UartDmaStream_ParseState_WaitFrameHead2; // 切换到等待帧头2状态
          tempHead1 = ReadByte; // 暂存帧头1
        } else { // 接收到的不是帧头1
          state = UartDmaStream_ParseState_WaitFrameHead1; // 重新进入等待帧头1状态
          tempHead1 = 0; // 清空帧头1
          tempHead2 = 0; // 清空帧头2
          tempLen = 0; // 清空数据长度
          tempCrc = 0; // 清空校验和
        }
        break;

      /*如果在等待帧头2状态，接收到了正确的帧头2，则切换下一个状态：等待数据长度*/
      case UartDmaStream_ParseState_WaitFrameHead2: // 如果此时是等待帧头2
        if ( ReadByte == UartDmaStream_FrameHead2_Req // 确实是接收到了请求帧的帧头2
          || ReadByte == UartDmaStream_FrameHead2_Res // 确实是接收到了响应帧的帧头2
          || ReadByte == UartDmaStream_FrameHead2_Evt ) { // 确实是接收到了事件帧的帧头2
          state = UartDmaStream_ParseState_WaitPayloadLen; // 进入等待数据长度状态
          tempHead2 = ReadByte; // 暂存帧头2
          ReadFrameData[0] = tempHead1; // 保存帧头1到ReadFrameData
          ReadFrameData[1] = tempHead2; // 保存帧头2到ReadFrameData
        } else { // 接收到的不是帧头2
          state = UartDmaStream_ParseState_WaitFrameHead1; // 重新进入等待帧头1状态
          tempHead1 = 0; // 清空帧头1
          tempHead2 = 0; // 清空帧头2
          ReadFrameData[0] = 0; // 清空ReadFrameData[0]
          ReadFrameData[1] = 0; // 清空ReadFrameData[1]
        }
        break;

      /*如果此时是等待数据长度，接收到了数据长度，则切换下一个状态：等待数据*/
      case UartDmaStream_ParseState_WaitPayloadLen: // 如果此时是等待数据长度
        tempLen |= ReadByte << ((3-LenCnt)*8); // 保存数据长度
        ReadFrameData[2+LenCnt] = ReadByte; // 保存数据长度到FrameData[2~5]
        LenCnt++; // 数据长度计数器自增1
        if (LenCnt >= 4) { // 数据长度计数器达到4，表示数据长度已经接收完毕
          state = UartDmaStream_ParseState_WaitPayloadData; // 进入等待数据状态
        }
        break;

      /*如果此时是等待数据，接收到了数据，则切换下一个状态：等待校验和*/
      case UartDmaStream_ParseState_WaitPayloadData: // 如果此时是等待数据
        ReadFrameData[6+DataCnt] = ReadByte; // 保存数据到FrameData[6~]
        DataCnt++; // 数据计数器自增1
        if (DataCnt >= tempLen) { // 数据计数器达到数据长度，表示数据已经接收完毕
          state = UartDmaStream_ParseState_WaitCrcCheckSum; // 进入等待校验和状态
        }
        break;

      /*如果此时是等待校验和，接收到了校验和，则恢复到初始状态：等待帧头1*/
      case UartDmaStream_ParseState_WaitCrcCheckSum: // 如果此时是等待校验和
        tempCrc |= ReadByte << ((1-CrcCnt)*8); // 保存校验和
        ReadFrameData[6+tempLen+CrcCnt] = ReadByte; // 保存校验和到FrameData[6+len~]
        CrcCnt++; // 校验和计数器自增1
        if (CrcCnt >= 2) { // 校验和计数器达到2，表示校验和已经接收完毕
          state = UartDmaStream_ParseState_WaitFrameHead1; // 重新进入等待帧头1状态
          ReadState = (tempCrc == UartDmaStream_CRC16Cal(ReadFrameData, 6+tempLen)) ? // 判断校验和是否正确
                      UartDmaStream_ReadState_Successful : // 如果校验和正确，则标记读取成功
                      UartDmaStream_ReadState_CrcErr ; // 如果校验和不正确，则标记校验和错误
          ShouldBreakTheInfiniteLoop = true; // 标记退出无限循环
        }
        break;

      default: break;
    }

    cThis->ReadIndex++; // 读取指针自增1
    if (cThis->ReadIndex >= UART_DMA_STREAM_RX_BUF_SIZE) { // 读取指针已经到达接收缓冲区的末尾
      cThis->ReadIndex = 0; // 读取指针回到接收缓冲区的起始位置
    }

    if (ShouldBreakTheInfiniteLoop) { // 如果需要退出循环
      break; // 退出循环
    }
  }

  return ReadState;
}





uint16_t BytesToUint16_BigEndian(uint8_t *HandleBytes) {
  return ( (HandleBytes[0] << 8)
         | (HandleBytes[1] << 0) );
}

uint32_t BytesToUint32_BigEndian(uint8_t *HandleBytes) {
  return ( (HandleBytes[0] << 24)
         | (HandleBytes[1] << 16)
         | (HandleBytes[2] << 8)
         | (HandleBytes[3] << 0) );
}

uint64_t BytesToUint64_BigEndian(uint8_t *HandleBytes) {
  return ( (HandleBytes[0] << 56) // May Trigger Warning But Runs Normally
         | (HandleBytes[1] << 48) // May Trigger Warning But Runs Normally
         | (HandleBytes[2] << 40) // May Trigger Warning But Runs Normally
         | (HandleBytes[3] << 32) // May Trigger Warning But Runs Normally
         | (HandleBytes[4] << 24)
         | (HandleBytes[5] << 16)
         | (HandleBytes[6] << 8)
         | (HandleBytes[7] << 0) );
}

int16_t BytesToInt16_BigEndian(uint8_t *HandleBytes) {
  return ( (HandleBytes[0] << 8)
         | (HandleBytes[1] << 0) );
}

int32_t BytesToInt32_BigEndian(uint8_t *HandleBytes) {
  return ( (HandleBytes[0] << 24)
         | (HandleBytes[1] << 16)
         | (HandleBytes[2] << 8)
         | (HandleBytes[3] << 0) );
}

int64_t BytesToInt64_BigEndian(uint8_t *HandleBytes) {
  return ( (HandleBytes[0] << 56) // May Trigger Warning But Runs Normally
         | (HandleBytes[1] << 48) // May Trigger Warning But Runs Normally
         | (HandleBytes[2] << 40) // May Trigger Warning But Runs Normally
         | (HandleBytes[3] << 32) // May Trigger Warning But Runs Normally
         | (HandleBytes[4] << 24)
         | (HandleBytes[5] << 16)
         | (HandleBytes[6] << 8)
         | (HandleBytes[7] << 0) );
}





/**
 * @brief 获取一帧数据包的帧类型
 * @param cThis 指向UartDmaStream_t结构体的指针
 * @param RecvBuf 指向接收缓冲区的指针
 * @return 帧类型
 */
UartDmaStream_FrameType_e UartDmaStream_GetFrameType(UartDmaStream_t *cThis, uint8_t *RecvBuf) {
  switch (RecvBuf[1]) {
    case UartDmaStream_FrameHead2_Req: return UartDmaStream_FrameType_Req;
    case UartDmaStream_FrameHead2_Res: return UartDmaStream_FrameType_Res;
    case UartDmaStream_FrameHead2_Evt: return UartDmaStream_FrameType_Evt;
    default: return UartDmaStream_FrameType_Unknown;
  }
}

/**
 * @brief 获取一帧数据包的有效数据长度
 * @param cThis 指向UartDmaStream_t结构体的指针
 * @param RecvBuf 指向接收缓冲区的指针
 * @return 有效数据长度
 */
size_t UartDmaStream_GetPayloadSize(UartDmaStream_t *cThis, uint8_t *RecvBuf) {
  return BytesToUint32_BigEndian(RecvBuf+2);
}

/**
 * @brief 获取一帧数据包的总长度
 * @param cThis 指向UartDmaStream_t结构体的指针
 * @param RecvBuf 指向接收缓冲区的指针
 * @return 帧总长度
 */
size_t UartDmaStream_GetFrameSize(UartDmaStream_t *cThis, uint8_t *RecvBuf) {
  return UartDmaStream_GetPayloadSize(cThis, RecvBuf) + 8;
  // 8字节是帧头1(1)、帧头2(1)、有效数据长度(4)、校验和(2)
}

/**
 * @brief 获取一帧数据包的有效数据指针
 * @param cThis 指向UartDmaStream_t结构体的指针
 * @param RecvBuf 指向接收缓冲区的指针
 * @return 有效数据指针
 */
uint8_t* UartDmaStream_GetPayloadData(UartDmaStream_t *cThis, uint8_t *RecvBuf) {
  return (RecvBuf+6);
}

uint16_t UartDmaStream_GetCommandType(UartDmaStream_t *cThis, uint8_t *RecvBuf) {
  return BytesToUint16_BigEndian(RecvBuf+6);
}
