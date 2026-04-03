#ifndef __UART_DMA_STREAM_H__
#define __UART_DMA_STREAM_H__

#include "stm32f4xx_hal.h"
#include "main.h"
#include "string.h"
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include "FreeRTOS.h" // 如果不是FreeRTOS环境，直接注释掉这一行就行了，其他条件编译代码都不用管





#ifdef FREERTOS_CONFIG_H // 如果是 FreeRTOS 环境，自动启用互斥锁
  #include "cmsis_os2.h" // 包含互斥锁相关的头文件
  #define SEND_BYTES_USE_RTOS_MUTEX // 启用FreeRTOS互斥锁保护发送操作，避免并发访问问题
#endif





#define UART_DMA_STREAM_TX_BUF_SIZE        512
#define UART_DMA_STREAM_TX_QUEUE_SIZE      32
#define UART_DMA_STREAM_RX_BUF_SIZE        256





// # 第1,2个字节
//   - 0x53 0xCA为请求帧帧头
//   - 0x53 0x35为应答帧帧头
//   - 0x53 0x96为事件帧帧头
// # 第3,4,5,6个字节
//   - 有效数据部分长度，大端顺序
// # 在7个字节开始
//   - 有效数据部分
// # 最后2个字节
//   - 从第一个字节开始，到有效数据的最后一个字节，所有字节的CRC16校验码，大端顺序
// （都是以正确的两个帧头、数据长度，这两部分来判定一帧数据的完整性的。）

typedef enum {
  UartDmaStream_FrameHead1 = 0x53, // 帧头1
  UartDmaStream_FrameHead2_Req = 0xCA, // 帧头2 请求帧
  UartDmaStream_FrameHead2_Res = 0x35, // 帧头2 应答帧
  UartDmaStream_FrameHead2_Evt = 0x96, // 帧头2 事件帧
} UartDmaStream_FrameHead_e;

typedef enum {
  UartDmaStream_FrameType_Req, // 请求帧
  UartDmaStream_FrameType_Res, // 应答帧
  UartDmaStream_FrameType_Evt, // 事件帧
  UartDmaStream_FrameType_Unknown, // 未知帧类型
} UartDmaStream_FrameType_e;

typedef enum {
  UartDmaStream_ParseState_WaitFrameHead1, // 等待帧头1
  UartDmaStream_ParseState_WaitFrameHead2, // 等待帧头2
  UartDmaStream_ParseState_WaitPayloadLen, // 等待数据长度
  UartDmaStream_ParseState_WaitPayloadData,// 等待数据
  UartDmaStream_ParseState_WaitCrcCheckSum, // 等待校验和
  UartDmaStream_ParseState_FrameOverflow, // 帧溢出
} UartDmaStream_ParseState_e;

typedef enum {
  UartDmaStream_ReadState_NoData, // 一点儿符合格式的数据都没读到，超时了
  UartDmaStream_ReadState_CrcErr, // 完整读到了符合格式的数据，但CRC校验错误
  UartDmaStream_ReadState_Timeout, // 读了一部分符合格式的数据，但中途超时退出了
  UartDmaStream_ReadState_Successful, // 完整读到了符合格式的数据，CRC校验也通过了
} UartDmaStream_ReadState_e;

typedef struct {
  volatile size_t StartIndex;
  volatile size_t DataLength;
} UartDmaStream_TxQueue_t;





typedef struct {
  UART_HandleTypeDef *huart; // UART句柄
  DMA_HandleTypeDef *hdmatx; // DMA发送句柄
  DMA_HandleTypeDef *hdmarx; // DMA接收句柄

  uint8_t TranBuf[UART_DMA_STREAM_TX_BUF_SIZE]; // 传输缓冲区
  uint8_t RecvBuf[UART_DMA_STREAM_RX_BUF_SIZE]; // 接收缓冲区

  UartDmaStream_TxQueue_t TxDataQueue[UART_DMA_STREAM_TX_QUEUE_SIZE]; // 待发送数据队列
  volatile uint32_t HandleQueueIndex; // 处理待发送数据队列的索引（实际发送的索引）
  volatile uint32_t EnterQueueIndex; // 进入待发送数据队列的索引（压入队列的索引）
  void (*DelayMS)(uint32_t ms); // 延时函数指针
  volatile bool IsTxDmaIdle; // DMA是否空闲

  volatile size_t RecvIndex; // 接收指针，指向当前接收字节的位置
  volatile size_t ReadIndex; // 读取指针，指向当前读取字节的位置
  // 以上这两个变量必须要加volatile，否则出现丢包的bug，CRC校验错误的bug
  // 因为这个问题，在2026.4.3这天，找了半天bug，才发现这里解决掉

#ifdef SEND_BYTES_USE_RTOS_MUTEX
  osMutexId_t SendBytesMutex; // 发送数据互斥锁
#endif
} UartDmaStream_t;





void UartDmaStream_Init(UartDmaStream_t *cThis,
                         UART_HandleTypeDef *huart,
                         DMA_HandleTypeDef *hdmatx,
                         DMA_HandleTypeDef *hdmarx,
                         void (*DelayMS)(uint32_t ms) );

void UartDmaStream_FuncCalled_InTxCpltCallback(UartDmaStream_t* cThis);
void UartDmaStream_FuncCalled_InInfiniteLoop(UartDmaStream_t* cThis);

void UartDmaStream_SendBytes(UartDmaStream_t *cThis, const uint8_t *SendBytes, size_t SendBytesLen);
void UartDmaStream_SendString(UartDmaStream_t *cThis, const char *SendString);
void UartDmaStream_Printf(UartDmaStream_t *cThis, const char *format, ...);

uint16_t UartDmaStream_CRC16Cal(const uint8_t *bytes, size_t len);
size_t UartDmaStream_GetRecvIndex(UartDmaStream_t *cThis);

void UartDmaStream_WriteFrame(UartDmaStream_t *cThis, UartDmaStream_FrameHead_e fh2, uint8_t *WriteFrameData, size_t WriteFrameDataLen);
UartDmaStream_ReadState_e UartDmaStream_ReadFrame(UartDmaStream_t *cThis, uint8_t *ReadFrameData, uint32_t Timeout);

uint16_t BytesToUint16_BigEndian(uint8_t *HandleBytes);
uint32_t BytesToUint32_BigEndian(uint8_t *HandleBytes);
uint64_t BytesToUint64_BigEndian(uint8_t *HandleBytes);
int16_t BytesToInt16_BigEndian(uint8_t *HandleBytes);
int32_t BytesToInt32_BigEndian(uint8_t *HandleBytes);
int64_t BytesToInt64_BigEndian(uint8_t *HandleBytes);

UartDmaStream_FrameType_e UartDmaStream_GetFrameType(UartDmaStream_t *cThis, uint8_t *RecvBuf);
size_t UartDmaStream_GetPayloadSize(UartDmaStream_t *cThis, uint8_t *RecvBuf);
size_t UartDmaStream_GetFrameSize(UartDmaStream_t *cThis, uint8_t *RecvBuf);
uint8_t* UartDmaStream_GetPayloadData(UartDmaStream_t *cThis, uint8_t *RecvBuf);
uint16_t UartDmaStream_GetCommandType(UartDmaStream_t *cThis, uint8_t *RecvBuf);

#endif // __UART_DMA_STREAM_H__
