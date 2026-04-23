#ifndef __UART_QUEUE_DMA_TX_H__
#define __UART_QUEUE_DMA_TX_H__

#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include "stm32f4xx_hal.h"
#include "main.h"

#define UART_TX_BUF_SIZE 50
#define UART_TX_QUEUE_SIZE 32

typedef struct {
  size_t StartIndex;
  size_t DataLength;
} UartDmaQueueTx_Queue_t;

typedef struct {
  UART_HandleTypeDef *huart; // UART句柄
  DMA_HandleTypeDef *hdmatx; // DMA句柄
  uint8_t TranBuf[UART_TX_BUF_SIZE]; // 传输缓冲区

  UartDmaQueueTx_Queue_t TxDataQueue[UART_TX_QUEUE_SIZE]; // 待发送数据队列
  uint32_t HandleQueueIndex; // 处理待发送数据队列的索引（实际发送的索引）
  uint32_t EnterQueueIndex; // 进入待发送数据队列的索引（压入队列的索引）
  void (*DelayMS)(uint32_t ms);
  bool IsTxDmaIdle; // DMA是否空闲
} UartDmaQueueTx_t;

void UartDmaQueueTx_Init(UartDmaQueueTx_t *cThis,
                        UART_HandleTypeDef *huart,
                        DMA_HandleTypeDef *hdmatx,
                        void (*DelayMS)(uint32_t ms) );
void UartDmaQueueTx_FuncCalled_InTxCpltCallback(UartDmaQueueTx_t* cThis);
void UartDmaQueueTx_FuncCalled_InInfiniteLoop(UartDmaQueueTx_t* cThis);

void UartDmaQueueTx_SendArray(UartDmaQueueTx_t *cThis, const uint8_t *SendArray, size_t SendArrayLen);
void UartDmaQueueTx_SendString(UartDmaQueueTx_t *cThis, const char *SendString);
void UartDmaQueueTx_Printf(UartDmaQueueTx_t *cThis, const char *format, ...);

#endif
