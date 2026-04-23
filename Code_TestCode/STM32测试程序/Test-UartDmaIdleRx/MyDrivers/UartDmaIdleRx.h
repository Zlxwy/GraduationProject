#ifndef __UART_DMA_IDLE_RX_H__
#define __UART_DMA_IDLE_RX_H__

#include "stm32f4xx_hal.h"
#include "main.h"
#include "string.h"
#include <stdlib.h>
#include <stdbool.h>

#define UART_RX_BUF_SIZE  256

typedef struct {
  UART_HandleTypeDef *huart; // UART句柄
  DMA_HandleTypeDef *hdmarx; // DMA句柄
  uint8_t RecvBuf[UART_RX_BUF_SIZE]; // 接收缓冲区
  size_t RecvLen; // 接收数据长度
  bool RecvFlag; // 接收数据标志位
} UartDmaIdleRx_t;

void UartDmaIdleRx_Init(UartDmaIdleRx_t* cThis,
                        UART_HandleTypeDef *huart,
                        DMA_HandleTypeDef *hdmarx);
void UartDmaIdleRx_FuncCalled_InIdleInterrupt(UartDmaIdleRx_t* cThis);

bool UartDmaIdleRx_GetRecvFlag(UartDmaIdleRx_t* cThis);
uint8_t* UartDmaIdleRx_GetRecvBuf(UartDmaIdleRx_t* cThis);
size_t UartDmaIdleRx_GetRecvLen(UartDmaIdleRx_t* cThis);



#endif // __UART_IDLE_DMA_RX_H__
