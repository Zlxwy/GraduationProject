#include "Task_All.h"

/*这个线程用来扫描读取按键状态*/
void KeyScanReadTaskFunc(void *argument) {
  (void)argument;
  while (!IsAllInitOkay) { osDelay(100); }
  uint8_t key_click_event_send_array[5];
  key_click_event_send_array[0] = (COMMAND_TYPE_KEY_CLICK >> 8) & 0xFF;
  key_click_event_send_array[1] = COMMAND_TYPE_KEY_CLICK & 0xFF;
  while (true) {
    for (uint16_t i=0; i<4; i++) {
      key_click_event_send_array[2] = (i<<8) & 0xFF;
      key_click_event_send_array[3] = i & 0xFF;
      if ( !HadKeyPressed[i] && DigitalInput_IsTriggered(&gKey[i]) ) { // 按键被按下
        HadKeyPressed[i] = true;

        key_click_event_send_array[4] = 0x00; // 按键按下指示字节
        UartDmaStream_WriteFrame(&gMainStream, UartDmaStream_FrameHead2_Evt, key_click_event_send_array, 5);
        UartDmaStream_LogPrintf(&gMainStream, "Key[%d] Pressed!\n", i);

        // /*用按键控制电磁铁的测试代码*/
        // if ( i == 0 ) {
        //   Msg_MotorAction_t msg;
        //   msg.RequestType = MotorActionRequestType_SetMagnetStatus;
        //   msg.MagnetStatus = 0x00;
        //   osMessageQueuePut(gMsgQueueMotorAction, &msg, 0U, 0);
        // } else if (i==1) {
        //   Msg_MotorAction_t msg;
        //   msg.RequestType = MotorActionRequestType_SetMagnetStatus;
        //   msg.MagnetStatus = 0x01;
        //   osMessageQueuePut(gMsgQueueMotorAction, &msg, 0U, 0);
        // }
      }
      else if ( HadKeyPressed[i] && DigitalInput_IsReleased(&gKey[i]) ) { // 按键被释放
        HadKeyPressed[i] = false;

        key_click_event_send_array[4] = 0x01; // 按键释放指示字节
        UartDmaStream_WriteFrame(&gMainStream, UartDmaStream_FrameHead2_Evt, key_click_event_send_array, 5);
        UartDmaStream_LogPrintf(&gMainStream, "Key[%d] Released!\n", i);
      }
    }

    osDelay(20);
  }
}
