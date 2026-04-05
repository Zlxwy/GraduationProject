#include "Task_All.h"

/*这个线程是CubeMX创建的默认线程，用于测试一些东西*/
void StartDefaultTask(void *argument) {
  (void)argument;
  while (!IsAllInitOkay) { osDelay(100); }

  while (true) {
    // static uint32_t count = 0;
    // UartDmaStream_Printf(&gMainStream, "[%015d] Hello, World! From StartDefaultTask!\n", count++);

    /*打印gMainStream的一些状态成员变量*/
    UartDmaStream_Printf(&gMainStream,
      "HandleQueueIndex = %d\nEnterQueueIndex = %d\nIsTxDmaIdle = %s\nRecvIndex = %d\nReadIndex = %d\n\n",
      gMainStream.HandleQueueIndex,
      gMainStream.EnterQueueIndex,
      gMainStream.IsTxDmaIdle ? "true" : "false",
      gMainStream.RecvIndex,
      gMainStream.ReadIndex
    );

    // uint8_t send_array[] = {0x00,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xC8,0x00,0x00,0x02,0x9A};
    // UartDmaStream_WriteFrame(&gMainStream,UartDmaStream_FrameHead2_Req,send_array,sizeof(send_array));

    osDelay(2000);
  }
}
