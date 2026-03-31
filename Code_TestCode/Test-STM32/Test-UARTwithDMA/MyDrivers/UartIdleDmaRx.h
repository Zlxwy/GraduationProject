#ifndef __UART_IDLE_DMA_RX_H__
#define __UART_IDLE_DMA_RX_H__

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
} UartIdleDmaRx_t;

void UartIdleDmaRx_Init(UartIdleDmaRx_t* cThis,
                        UART_HandleTypeDef *huart,
                        DMA_HandleTypeDef *hdmarx);
void UartIdleDmaRx_FuncCalled_InIdleInterrupt(UartIdleDmaRx_t* cThis);

bool UartIdleDmaRx_GetRecvFlag(UartIdleDmaRx_t* cThis);
uint8_t* UartIdleDmaRx_GetRecvBuf(UartIdleDmaRx_t* cThis);
size_t UartIdleDmaRx_GetRecvLen(UartIdleDmaRx_t* cThis);



#endif // __UART_IDLE_DMA_RX_H__
