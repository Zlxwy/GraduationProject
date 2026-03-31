* [STM32CubeMX配置](#stm32cubemx配置)
* [代码使用示例](#代码使用示例)

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
      - DMA Settings
        * DMA Request: <u>USARTx_RX</u>
        * Stream: <u>DMAx Stream x</u>
        * Direction: <u>Peripheral To Memory</u>
        * Priority: <u>Medium</u>
        - DMA Request Settings
          * Mode: <u>Circular</u>
          * Peripheral Increment: <u>Unchecked</u>
          * Memory Increment: <u>Checked</u>
          * Use Fifo: <u>Unchecked</u>
          * Peripheral Data Width: <u>Byte</u>
          * Memory Data Width: <u>Byte</u>



## 代码使用示例
```c
#include "UartIdleDmaRx.h"

extern UART_HandleTypeDef huartx;
extern DMA_HandleTypeDef hdma_usartx_rx;
UartIdleDmaRx_t ttUIDR; // 串口空闲中断DMA接收的结构体实例

/*需要在USARTx空闲中断中调用一条函数，用于处理接收完的一帧不定长数据*/
void USARTx_IRQHandler(void) {
  /* USER CODE BEGIN USARTx_IRQn 0 */
  if ( __HAL_UART_GET_FLAG(&huartx, UART_FLAG_IDLE) ) { // 确实是RXNE中断触发
    __HAL_UART_CLEAR_IDLEFLAG(&huartx); // 清除IDLE标志位
    __HAL_UART_CLEAR_FLAG(&huartx, UART_FLAG_IDLE); // 清除IDLE标志位
    UartIdleDmaRx_FuncCalled_InIdleInterrupt(&ttUIDR); // 在空闲中断调用这个函数
    return;
  }
  /* USER CODE END USARTx_IRQn 0 */
  // ......
}

int main(void) {
  HUartIdleDmaRx_Init(&ttUIDR, &huartx, &hdma_usartx_rx); // 初始化

  while (1) {
    if ( UartIdleDmaRx_GetRecvFlag(&ttUIDR) ) { // 获取是否接收数据标志位
      printf( "rx_count: %d\r\nrx_data: %s",
        UartIdleDmaRx_GetRecvLen(&ttUIDR), // 获取接收的字节数
        UartIdleDmaRx_GetRecvBuf(&ttUIDR) // 获取接收的字节数组
      ); // 因为在接收完成后，补了个结束符'\0'，所以可以直接打印字符串
      printf("\r\n");
    }
  }
}
```