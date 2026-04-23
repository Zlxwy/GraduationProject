#include "Task_All.h"

void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
  if (huart->Instance == USART3) {
    UartDmaStream_FuncCalled_InTxCpltCallback(&gMainStream);
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
