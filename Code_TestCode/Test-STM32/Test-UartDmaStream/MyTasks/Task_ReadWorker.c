#include "Task_All.h"

volatile bool IsAllInitOkay = false;

UartDmaStream_t gMainStream;
uint8_t gFrameBuffer[256]; // 用来接收一帧一帧数据的缓冲区

/*包装函数：返回值改为void*/
void MyDelayWrapper(uint32_t ms) {
  osDelay(ms);
}

/*读取线程函数，是唯一调用UartDmaStream_ReadFrame的地方，解析数据后可通过消息队列分发到其他线程处理*/
void ReadWorkerTaskFunc(void *argument) {
  (void)argument;
  UartDmaStream_Init(&gMainStream, &huart3, &hdma_usart3_tx, &hdma_usart3_rx, MyDelayWrapper);
  IsAllInitOkay = true;

  while (true) {
    // static uint32_t count = 0;
    // UartDmaStream_Printf(&gMainStream, "[%010d] Hello, World! From ReadWorkerTask!\n", count++);
    // osDelay(50);

    UartDmaStream_ReadState_e rs = UartDmaStream_ReadFrame(&gMainStream, gFrameBuffer, pdMS_TO_TICKS(2000));
    switch (rs) {
      case UartDmaStream_ReadState_NoData: // 一点儿符合格式的数据都没读到，超时了
        UartDmaStream_Printf(&gMainStream, "【【一点儿符合格式的数据都没读到，超时了】】\n\n");
        break;

      case UartDmaStream_ReadState_CrcErr: // 完整读到了符合格式的数据，但CRC校验错误
      UartDmaStream_Printf(&gMainStream, "【【完整读到了符合格式的数据，但CRC校验错误】】\n\n");
      break;

      case UartDmaStream_ReadState_Timeout: // 读了一部分符合格式的数据，但中途超时退出了
      UartDmaStream_Printf(&gMainStream, "【【读了一部分符合格式的数据，但中途超时退出了】】\n\n");
      break;

      case UartDmaStream_ReadState_Successful: // 完整读到了符合格式的数据，CRC校验也通过了
        UartDmaStream_Printf(&gMainStream, "|-|-完整读到了符合格式的数据，CRC校验也通过了！！！！！！\n");
        uint8_t recv_size, print_hex_string[256];
        recv_size = UartDmaStream_GetFrameSize(&gMainStream, gFrameBuffer);
        for (size_t i=0; i<recv_size; i++) sprintf((char*)&print_hex_string[i*3], "%02X ", gFrameBuffer[i]);
        UartDmaStream_Printf(&gMainStream, "|-|-接收数据为: %s\n", print_hex_string);
        UartDmaStream_Printf(&gMainStream, "|-|-接收长度为: %d Bytes\n\n", recv_size);
        break;
    }
  }
}
