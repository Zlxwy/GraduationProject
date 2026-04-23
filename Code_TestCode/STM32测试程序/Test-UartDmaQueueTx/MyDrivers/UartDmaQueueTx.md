- [STM32CubeMX配置](#stm32cubemx配置)
- [代码使用示例](#代码使用示例)

## STM32CubeMX配置

- Pinout & Configuration
  - Connectivity: <u>USARTx</u>
    - Mode
      * Mode: <u>Asynchronous</u>
      * Hardware Flow Control (RS232): <u>Disable</u>
    - Configuration
      - Parameter Settings
        - Basic Parameters
          * Baud Rate: <u>115200 Bits/s</u>
          * Word Length: <u>8 Bits (including Parity)</u>
          * Parity: <u>None</u>
          * Stop Bits: <u>1</u>
        - Advanced Parameters
          * Data Direction: <u>Receive and Transmit</u>
          * Over Sampling: <u>16 Samples</u>
      - NVIC Settings
        * USARTx global interrupt: <u>Enabled</u>
      - DMA Settings
        * DMA Request: <u>USARTx_TX</u>
        * Stream: <u>DMAx Stream x</u>
        * Direction: <u>Memory To Peripheral</u>
        * Priority: <u>Medium</u>
        - DMA Request Settings
          * Mode: <u>Normal</u>
          * Peripheral Increment: <u>Unchecked</u>
          * Memory Increment: <u>Checked</u>
          * Use Fifo: <u>Unchecked</u>
          * Peripheral Data Width: <u>Byte</u>
          * Memory Data Width: <u>Byte</u>



## 代码使用示例
```c
#include <stdio.h>
#include "UartDmaIdleRx.h"

extern UART_HandleTypeDef huartx;
extern DMA_HandleTypeDef hdma_usartx_tx;
UartDmaQueueTx_t ttUQDT;

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
  if (huart->Instance == USARTx) {
    UartDmaQueueTx_FuncCalled_InTxCpltCallback(&ttUQDT);
  }
}

int main(void) {
  UartDmaQueueTx_Init(&ttUQDT, &huartx, &hdma_usartx_tx, HAL_Delay); // 初始化
  UartDmaQueueTx_Printf(&ttUQDT, "Hello, World!\n");
  UartDmaQueueTx_Printf(&ttUQDT, "Hello, STM32!\n");
  UartDmaQueueTx_Printf(&ttUQDT, "Hello, F407ZGT6!\n");
  UartDmaQueueTx_Printf(&ttUQDT, "\r\n");

  uint64_t cnt = 0;
  uint32_t a = 0;
  while (1) {
    UartDmaQueueTx_FuncCalled_InInfiniteLoop(&ttUQDT);

    if (a++ >= 1) {
      UartDmaQueueTx_Printf(&ttUQDT, "[%010llu] Hello, World!\n", cnt++);
      a = 0;
    }
  }
}
```