#ifndef __UART_STREAM_H__
#define __UART_STREAM_H__

#include "stm32f4xx_hal.h"
#include "main.h"
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

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
  UartStream_FrameHead1 = 0x53, // 帧头1
  UartStream_FrameHead2_Req = 0xCA, // 帧头2 请求帧
  UartStream_FrameHead2_Res = 0x35, // 帧头2 应答帧
  UartStream_FrameHead2_Evt = 0x96, // 帧头2 事件帧
} UartStream_FrameHead_e;

typedef enum {
  UartStream_FrameType_Req, // 请求帧
  UartStream_FrameType_Res, // 应答帧
  UartStream_FrameType_Evt, // 事件帧
  UartStream_FrameType_Unknown, // 未知帧类型
} UartStream_FrameType_e;

typedef enum {
  UartStream_ParseState_WaitFrameHead1, // 等待帧头1
  UartStream_ParseState_WaitFrameHead2, // 等待帧头2
  UartStream_ParseState_WaitPayloadLen, // 等待数据长度
  UartStream_ParseState_WaitPayloadData,// 等待数据
  UartStream_ParseState_WaitCrcCheckSum, // 等待校验和
  UartStream_ParseState_FrameOverflow, // 帧溢出
} UartStream_ParseState_e;

typedef enum {
  UartStream_ReadState_NoData, // 一点儿数据都没读到，超时了
  UartStream_ReadState_CrcErr, // 完整读到了数据，但CRC校验错误
  UartStream_ReadState_Timeout, // 读了一部分数据，但中途超时退出了
  UartStream_ReadState_Successful, // 完整读到了数据，CRC校验也通过了
} UartStream_ReadState_e;

#define UART_STREAM_WRITE_BUFFER_SIZE 256
#define UART_STREAM_RECV_BUFFER_SIZE 256

typedef struct {
  UART_HandleTypeDef *huart; // 串口句柄
  uint8_t RecvBuffer[UART_STREAM_RECV_BUFFER_SIZE];
  size_t RecvIndex; // 接收指针，指向当前接收字节的位置
  size_t ReadIndex; // 读取指针，指向当前读取字节的位置
} UartStream_t;



void UartStream_Init(UartStream_t *cThis, UART_HandleTypeDef *huart);
void UartStream_FuncCalled_InUartRecvInterrupt(UartStream_t *cThis);

void UartStream_SendOneByteBlocking(UartStream_t *cThis, uint8_t abyte);
void UartStream_SendBytesBlocking(UartStream_t *cThis, uint8_t *bytes, size_t len);
uint16_t UartStream_CRC16Cal(const uint8_t *bytes, size_t len);

UartStream_ReadState_e UartStream_Read(UartStream_t *cThis, uint8_t *ReadFrameData, uint32_t Timeout);
void UartStream_Write(UartStream_t *cThis, UartStream_FrameHead_e fh2, uint8_t *WriteFrameData, size_t WriteFrameDataLen);

uint16_t BytesToUint16_BigEndian(uint8_t *bytes);
uint32_t BytesToUint32_BigEndian(uint8_t *bytes);
uint64_t BytesToUint64_BigEndian(uint8_t *bytes);
int16_t BytesToInt16_BigEndian(uint8_t *bytes);
int32_t BytesToInt32_BigEndian(uint8_t *bytes);
int64_t BytesToInt64_BigEndian(uint8_t *bytes);


UartStream_FrameType_e UartStream_GetFrameType(UartStream_t *cThis, uint8_t *RecvBuf);
size_t UartStream_GetPayloadSize(UartStream_t *cThis, uint8_t *RecvBuf);
uint8_t* UartStream_GetPayloadData(UartStream_t *cThis, uint8_t *RecvBuf);
uint16_t UartStream_GetCommandType(UartStream_t *cThis, uint8_t *RecvBuf);

#endif
