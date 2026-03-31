#include "UartDmaQueueTx.h"

void UartDmaQueueTx_Init(UartDmaQueueTx_t *cThis,
                        UART_HandleTypeDef *huart,
                        DMA_HandleTypeDef *hdmatx ) {
  cThis->huart = huart;
  cThis->hdmatx = hdmatx;
  memset(cThis->TranBuf, DATA_NULL, UART_TX_BUF_SIZE);
  memset(cThis->DataQueue, DATA_NULL, sizeof(UartDmaQueueTx_DataToBeSent_t)*UART_TX_QUEUE_SIZE);
  cThis->HandleQueueIndex = 0;
  cThis->EnterQueueIndex = 0;
  cThis->IsTxDmaIdle = true;

  __HAL_DMA_ENABLE_IT(cThis->hdmatx, DMA_IT_TC);
}





void UartDmaQueueTx_FuncCalled_InCpltInterrupt(UartDmaQueueTx_t* cThis) {
  cThis->DataQueue[cThis->HandleQueueIndex].StartIndex = 0; // 清空已发送的队列
  cThis->DataQueue[cThis->HandleQueueIndex].DataLength = 0; // 清空已发送的队列

  cThis->HandleQueueIndex++; // 切换到下一条队列
  if (cThis->HandleQueueIndex >= UART_TX_QUEUE_SIZE) { // 切换到下一条队列后，索引超出范围
    cThis->HandleQueueIndex = 0; // 索引重置为0，从头开始发送
  }
  
  cThis->IsTxDmaIdle = true; // DMA空闲
}

void UartDmaQueueTx_FuncCalled_InInfiniteLoop(UartDmaQueueTx_t* cThis) {
  if (cThis->DataQueue[cThis->HandleQueueIndex].DataLength != 0 && cThis->IsTxDmaIdle) { // 有数据待发送且DMA空闲
    // HAL_DMA_Start_IT(cThis->hdmatx, // 启动DMA传输
    //   (uint32_t)&cThis->TranBuf[ cThis->DataQueue[cThis->HandleQueueIndex].StartIndex ], // 传输缓冲区指针
    //   (uint32_t)&(cThis->huart->Instance->DR), // DMA目的地址指针

    HAL_UART_Transmit_DMA(cThis->huart, // 启动DMA传输
      &cThis->TranBuf[ cThis->DataQueue[cThis->HandleQueueIndex].StartIndex ], // 传输缓冲区指针

      cThis->DataQueue[cThis->HandleQueueIndex].DataLength // 传输数据长度
    );
    cThis->IsTxDmaIdle = false; // DMA非空闲
  }
  HAL_Delay(10);
}





// SendArrayLen不要超过UART_TX_BUF_SIZE
void UartDmaQueueTx_SendArray(UartDmaQueueTx_t *cThis, const uint8_t *SendArray, size_t SendArrayLen) {
  uint32_t StartIndexMark = cThis->DataQueue[cThis->EnterQueueIndex].StartIndex; // 记录当前队列的传输缓冲区起始索引
  uint32_t DataLengthMark; // 这个用来后面来记录数据长度

  /*数据还能填充到传输缓冲区*/
  if (StartIndexMark + SendArrayLen <= UART_TX_BUF_SIZE) {
    cThis->DataQueue[cThis->EnterQueueIndex].DataLength = SendArrayLen; // 记录数据长度
    memcpy( // 只需要一次复制
      &cThis->TranBuf[ StartIndexMark ],
      &SendArray[0],
      cThis->DataQueue[cThis->EnterQueueIndex].DataLength
    );

    cThis->EnterQueueIndex++; // 切换到下一条队列
    if (cThis->EnterQueueIndex >= UART_TX_QUEUE_SIZE) {
      cThis->EnterQueueIndex = 0;
    } // 如果下一条队列索引超出范围，则从头开始压入

    cThis->DataQueue[cThis->EnterQueueIndex].StartIndex = StartIndexMark + SendArrayLen; // 更新下一条队列的传输缓冲区起始索引
    if (cThis->DataQueue[cThis->EnterQueueIndex].StartIndex >= UART_TX_BUF_SIZE) { // 如果下一条队列记录的传输缓冲区起始索引刚好满了
      // 其实进来这里的话，都不会在>UART_TX_BUF_SIZE的情况，只会是=UART_TX_BUF_SIZE的情况，因为上层if已经限制过了>UART_TX_BUF_SIZE的情况
      cThis->DataQueue[cThis->EnterQueueIndex].StartIndex -= UART_TX_BUF_SIZE; // 传输缓冲区索引从头开始
    }
  }
  
  /*数据超出传输缓冲区范围，分两次复制进传输缓冲区*/
  else if (StartIndexMark + SendArrayLen > UART_TX_BUF_SIZE) {
    cThis->DataQueue[cThis->EnterQueueIndex].DataLength = UART_TX_BUF_SIZE - StartIndexMark; // 记录数据长度
    memcpy( // 复制第一次
      &cThis->TranBuf[ StartIndexMark ],
      &SendArray[0],
      cThis->DataQueue[cThis->EnterQueueIndex].DataLength
    );

    cThis->EnterQueueIndex++; // 切换到下一条队列
    if (cThis->EnterQueueIndex >= UART_TX_QUEUE_SIZE) {
      cThis->EnterQueueIndex = 0;
    } // 如果下一条队列索引超出范围，则从头开始压入

    cThis->DataQueue[cThis->EnterQueueIndex].StartIndex = 0; // 传输缓冲区索引从头开始
    cThis->DataQueue[cThis->EnterQueueIndex].DataLength = SendArrayLen - (UART_TX_BUF_SIZE - StartIndexMark); // 记录数据长度

    memcpy( // 复制第二次
      &cThis->TranBuf[ 0 ],
      &SendArray[UART_TX_BUF_SIZE - StartIndexMark],
      cThis->DataQueue[cThis->EnterQueueIndex].DataLength
    );

    StartIndexMark = cThis->DataQueue[cThis->EnterQueueIndex].StartIndex;
    DataLengthMark = cThis->DataQueue[cThis->EnterQueueIndex].DataLength;

    cThis->EnterQueueIndex++; // 切换到下一条队列
    if (cThis->EnterQueueIndex >= UART_TX_QUEUE_SIZE) {
      cThis->EnterQueueIndex = 0;
    } // 如果下一条队列索引超出范围，则从头开始压入

    cThis->DataQueue[cThis->EnterQueueIndex].StartIndex = StartIndexMark + DataLengthMark;
    // 这个不会超出范围，因为已经分两次复制过了
  }
  else return;

}





void UartDmaQueueTx_SendString(UartDmaQueueTx_t *cThis, const char *SendString) {
  UartDmaQueueTx_SendArray(cThis, (const uint8_t *)SendString, strlen(SendString));
}





void UartDmaQueueTx_Printf(UartDmaQueueTx_t *cThis, const char *format, ...) {
  char SendBuf[256];
  va_list args;
  va_start(args, format);
  vsnprintf(SendBuf, sizeof(SendBuf), format, args);
  va_end(args);
  UartDmaQueueTx_SendString(cThis, SendBuf);
}
 
