/*主通信线程，该线程内的程序不应该有阻塞行为*/
#include "MainCmnct.h"
#include "Task_All.h"

volatile bool IsMainCmnctTaskInitOkay;

UartStream_t gMainCmnctStream; // 主通信流对象
uint8_t gMainCmnctBuffer[256]; // 主通信流缓冲区

DigitalOutput_t LED_D1onCoreBoard; // 核心板上的D1灯
DigitalOutput_t LED_D2onCoreBoard; // 核心板上的D2灯

StepperMotor_t BoomStepperMotor;

void MainCmnctTaskFunc(void *argument) {
  IsMainCmnctTaskInitOkay = false; // 标记主通信线程初始化未完成

  UartStream_Init(&gMainCmnctStream, UART_MAINCMNCT); // 初始化主通信流对象
  DigitalOutput_Init(&LED_D1onCoreBoard, LED1_GPIO_Port, LED1_Pin, GPIO_PIN_RESET); // 初始化核心板上的D1灯
  DigitalOutput_Init(&LED_D2onCoreBoard, LED2_GPIO_Port, LED2_Pin, GPIO_PIN_RESET); // 初始化核心板上的D2灯

  StepperMotor_Init( // 初始化步进电机
    &BoomStepperMotor, // 大臂步进电机
    &htim10, // 使用定时器10
    TIM_CHANNEL_1, // 使用通道1输出PWM
    168000000, // 内部时钟为168MHz
    14-1, // 进行预分频，14分频，得到168MHz/14=12MHz的CNT计数频率
    4000-1, // 设置自动重装载值为4000，得到12MHz/4000=3kHz的PWM频率
    50, // 高电平占空比50%
    TestDir_GPIO_Port, // 方向引脚端口
    TestDir_Pin, // 方向引脚号
    GPIO_PIN_SET // 高电平为正转
  ); // 在CubeMX配置了PWM引脚为PB8

  IsMainCmnctTaskInitOkay = true; // 标记主通信线程初始化完成

  while (true) {
    UartStream_ReadState_e status = UartStream_Read(&gMainCmnctStream,
                                                    gMainCmnctBuffer,
                                                    pdMS_TO_TICKS(2000)/* portMAX_DELAY */
                                                   ); // 读取主通信流对象

    // switch (status) { // 根据读取状态进行匹配
    //   case UartStream_ReadState_NoData: // 一点儿数据都没读到，超时了
    //     DigitalOutput_ToggleState(&LED_D1onCoreBoard);
    //     break;
    //   case UartStream_ReadState_CrcErr: // 完整读到了数据，但CRC校验错误
    //     break;
    //   case UartStream_ReadState_Timeout: // 读了一部分数据，但中途超时退出了
    //     DigitalOutput_ToggleState(&LED_D2onCoreBoard);
    //     break;
    //   case UartStream_ReadState_Successful: // 完整读到了数据，CRC校验也通过了
    //     DigitalOutput_ToggleState(&LED_D1onCoreBoard);
    //     DigitalOutput_ToggleState(&LED_D2onCoreBoard);
    //     break;
    // }

    if (status == UartStream_ReadState_Successful) { // 完整读到了数据，CRC校验也通过了
      UartStream_FrameType_e FrameType = UartStream_GetFrameType(&gMainCmnctStream, gMainCmnctBuffer); // 获取帧类型（请求帧、应答帧、事件帧）
      uint32_t PayloadLen = UartStream_GetPayloadSize(&gMainCmnctStream, gMainCmnctBuffer); // 获取数据长度（只是有效数据部分长度）
      uint8_t *PayloadData = UartStream_GetPayloadData(&gMainCmnctStream, gMainCmnctBuffer); // 获取有效数据部分的指针
      
      if (FrameType == UartStream_FrameType_Req) { // 如果是请求帧
        CommandType_e ReqCmdType = (CommandType_e)UartStream_GetCommandType(&gMainCmnctStream, gMainCmnctBuffer);
        if (ReqCmdType == CommandType_MotorAction) { // 如果是电机动作命令
          StepperMotor_MoveSteps(
            &BoomStepperMotor,
            BytesToInt64_BigEndian(PayloadData+4), // 行走步数
            BytesToUint32_BigEndian(PayloadData+12) // 行走速度
          ); // Object, steps, speed
          while (StepperMotor_GetRunState(&BoomStepperMotor) == StepperMotor_RunState_MoveSteps);
        } // if (ReqCmdType == CommandType_MotorAction)
      } // if (FrameType == UartStream_FrameType_Req)

      else if (FrameType == UartStream_FrameType_Res) { // 如果是应答帧
        CommandType_e ResCmdType = (CommandType_e)UartStream_GetCommandType(&gMainCmnctStream, gMainCmnctBuffer);
      } // if (FrameType == UartStream_FrameType_Res)

      else if (FrameType == UartStream_FrameType_Evt) { // 如果是事件帧
        CommandType_e EvtCmdType = (CommandType_e)UartStream_GetCommandType(&gMainCmnctStream, gMainCmnctBuffer);
      } // if (FrameType == UartStream_FrameType_Evt)

      else { // 其他未知帧类型
        ;
      } // if (FrameType == UartStream_FrameType_Unknown)
    }

    osDelay(pdMS_TO_TICKS(10));
  } // while (true)
}
