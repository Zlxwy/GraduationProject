#include "UartIdleDmaRx.h"

// 在使用之前，必须按照 UartIdleDmaRx.md 中配置好 UART 和 DMA_RX

void UartIdleDmaRx_Init(UartIdleDmaRx_t* cThis,
                         UART_HandleTypeDef *huart,
                         DMA_HandleTypeDef *hdmarx) {
  cThis->huart = huart;
  cThis->hdmarx = hdmarx;
  memset(cThis->RecvBuf, 0, UART_RX_BUF_SIZE);
  cThis->RecvLen = 0;
  cThis->RecvFlag = false;

  __HAL_UART_ENABLE_IT(cThis->huart, UART_IT_IDLE); // 使能串口空闲中断
  HAL_UART_Receive_DMA(cThis->huart, cThis->RecvBuf, UART_RX_BUF_SIZE); // 启动DMA接收
}





void UartIdleDmaRx_FuncCalled_InIdleInterrupt(UartIdleDmaRx_t* cThis) {
  cThis->RecvLen = UART_RX_BUF_SIZE - __HAL_DMA_GET_COUNTER(cThis->hdmarx); // 接收到的字节数
  cThis->RecvBuf[cThis->RecvLen] = '\0'; // 补一个结束符
  cThis->RecvFlag = true; // 挂起接收数据标志位

  HAL_UART_DMAStop(cThis->huart); // 停止DMA接收
  __HAL_DMA_SET_COUNTER(cThis->hdmarx, UART_RX_BUF_SIZE); // 重置DMA计数器
  HAL_UART_Receive_DMA(cThis->huart, cThis->RecvBuf, UART_RX_BUF_SIZE); // 重新启动DMA传输
}





bool UartIdleDmaRx_GetRecvFlag(UartIdleDmaRx_t* cThis) {
  if (cThis->RecvFlag) {
    cThis->RecvFlag = false;
    return true;
  } else {
    return false;
  }

  /*以下代码可能会造成一些时序问题，虽然看起来和上面的代码相同，但绝对不能用*/
  // bool ret = cThis->RecvFlag;
  // cThis->RecvFlag = false;
  // return ret;
}

uint8_t* UartIdleDmaRx_GetRecvBuf(UartIdleDmaRx_t* cThis) {
  return cThis->RecvBuf;
}

size_t UartIdleDmaRx_GetRecvLen(UartIdleDmaRx_t* cThis) {
  return cThis->RecvLen;
}
