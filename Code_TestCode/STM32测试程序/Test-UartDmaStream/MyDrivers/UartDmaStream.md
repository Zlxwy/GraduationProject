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
      - DMA Settings (USARTx_TX)
        * DMA Request: <u>USARTx_TX</u>
        * Stream: <u>DMAx Stream x</u>
        * Direction: <u>Memory To Peripheral</u>
        * Priority: <u>Low</u>
        - DMA Request Settings
          * Mode: <u>Normal</u>
          * Peripheral Increment: <u>Unchecked</u>
          * Memory Increment: <u>Checked</u>
          * Use Fifo: <u>Unchecked</u>
          * Peripheral Data Width: <u>Byte</u>
          * Memory Data Width: <u>Byte</u>
      - DMA Settings (USARTx_RX)
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
#include "main.h"
#include "FreeRTOS.h"
#include "task.h"
#include "UartDmaStream.h"

extern UART_HandleTypeDef huartx;
extern DMA_HandleTypeDef hdma_usartx_rx;
extern DMA_HandleTypeDef hdma_usartx_tx;

volatile bool IsAllInitOkay; // 其他线程while等待此标志位为true
UartDmaStream_t gMainStream; // 主串口流实例

/*读取线程函数，是唯一调用UartDmaStream_ReadFrame的地方*/
/*解析数据后可通过消息队列分发到其他线程处理*/
void ReadWorkerTaskFunc(void *argument) {
  (void)argument;
  UartDmaStream_Init(&gMainStream, &huartx, &hdma_usartx_tx, &hdma_usartx_rx, osDelay);
  IsAllInitOkay = true;
  while (true) {
    UartDmaStream_ReadState_e rs = UartDmaStream_ReadFrame(&gMainStream, gFrameBuffer, pdMS_TO_TICKS(2000));
    switch (rs) {
      case UartDmaStream_ReadState_NoData: /*do sth.*/ break; // 一点儿符合格式的数据都没读到，超时了
      case UartDmaStream_ReadState_CrcErr: /*do sth.*/ break; // 完整读到了符合格式的数据，但CRC校验错误
      case UartDmaStream_ReadState_Timeout: /*do sth.*/ break; // 读了一部分符合格式的数据，但中途超时退出了
      case UartDmaStream_ReadState_Successful: /*do sth.*/ break; // 完整读到了符合格式的数据，CRC校验也通过了
    }
  }
}

/*专门的发送线程工作函数，调用UartDmaStream_FuncCalled_InInfiniteLoop*/
/*是唯一操作串口硬件的地方，其他线程调用的发送函数，实际只是将数据写入发送队列*/
/*如果是裸机程序，这个UartDmaStream_FuncCalled_InInfiniteLoop也可以在定时中断中调用*/
void WriteWorkerTaskFunc(void *argument) {
  (void)argument;
  while (!IsAllInitOkay) { osDelay(100); }
  while (true) {
    UartDmaStream_FuncCalled_InInfiniteLoop(&gMainStream);
    osDelay(10); // 其实UartDmaStream_FuncCalled_InInfiniteLoop里边已经有了个5ms的延时
  }
}

/*在HAL库提供的发送完成回调函数中，调用UartDmaStream_FuncCalled_InTxCpltCallback*/
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
  if (huart->Instance == USARTx) {
    UartDmaStream_FuncCalled_InTxCpltCallback(&gMainStream);
  }
}





/*实际应用任务函数1*/
void UserTaskFunc_1(void *argument) {
  (void)argument;
  while (true) {
    static uint32_t cnt = 0;
    UartDmaStream_DebugPrintf(&gMainStream, "[%010llu] Hello, World! From Task_1!\n", cnt++);
    osDelay(200);
  }
}

/*实际应用任务函数2*/
void UserTaskFunc_2(void *argument) {
  (void)argument;
  while (true) {
    static uint32_t cnt = 0;
    UartDmaStream_DebugPrintf(&gMainStream, "[%010llu] Hello, STM32! From Task_2!\n", cnt++);
    osDelay(500);
  }
}


```