#include "Task_All.h"

osMessageQueueId_t gMsgQueueMotorAction; // 电机动作消息队列，用来传递电机动作的执行消息

volatile bool IsAllInitOkay = false;
UartDmaStream_t gMainStream; // 主通信流，与上位机进行通信
uint8_t gFrameBuffer[256]; // 用来接收一帧一帧数据的缓冲区
DigitalOutput_t gLED0;
DigitalOutput_t gLED1;
StepperMotor_t gStepperMotorShoulder; // 肩关节步进电机，ID为0x0001
StepperMotor_t gStepperMotorElbow; // 肘关节步进电机，ID为0x0002
StepperMotor_t gStepperMotorLift; // 竖轴步进电机，ID为0x0003

/*包装函数：返回值改为void*/
void MyDelayWrapper(uint32_t ms) {
  osDelay(pdMS_TO_TICKS(ms));
}

void Parse_COMMAND_TYPE_MOTOR_BASIC_MOVE(uint8_t *PayloadData, uint32_t PayloadLen);

/*读取线程函数，是唯一调用UartDmaStream_ReadFrame的地方，解析数据后可通过消息队列分发到其他线程处理*/
void ReadWorkerTaskFunc(void *argument) {
  (void)argument;
  IsAllInitOkay = false; // 标记主通信线程初始化未完成

  gMsgQueueMotorAction = osMessageQueueNew(10, sizeof(Msg_MotorAction_t), NULL);
  if (gMsgQueueMotorAction == NULL) UartDmaStream_Printf(&gMainStream, "Failed to create message queue for motor action!\n");

  UartDmaStream_Init(&gMainStream, &huart3, &hdma_usart3_tx, &hdma_usart3_rx, MyDelayWrapper);
  DigitalOutput_Init(&gLED0, LED0_GPIO_Port, LED0_Pin, GPIO_PIN_RESET); // 初始化核心板上的D0灯
  DigitalOutput_Init(&gLED1, LED1_GPIO_Port, LED1_Pin, GPIO_PIN_RESET); // 初始化核心板上的D1灯
  StepperMotor_Init( // 初始化步进电机gStepperMotorShoulder
    &gStepperMotorShoulder, // 肩关节步进电机
    &htim3, // 使用TIM3定时器
    TIM_CHANNEL_1, // 使用通道1输出PWM
    84000000, // 内部时钟为84MHz
    7-1, // 进行预分频，7分频，得到84MHz/7=12MHz的CNT计数频率
    4000-1, // 设置自动重装载值为4000，得到12MHz/4000=3kHz的PWM频率
    50, // 高电平占空比50%
    StepperMotorShoulder_Dir_GPIO_Port, // 方向引脚端口
    StepperMotorShoulder_Dir_Pin, // 方向引脚引脚
    GPIO_PIN_SET // 高电平为正转
  );
  StepperMotor_Init( // 初始化步进电机gStepperMotorElbow
    &gStepperMotorElbow, // 肘关节步进电机
    &htim10, // 使用TIM10定时器
    TIM_CHANNEL_1, // 使用通道1输出PWM
    168000000, // 内部时钟为168MHz
    14-1, // 进行预分频，14分频，得到168MHz/14=12MHz的CNT计数频率
    4000-1, // 设置自动重装载值为4000，得到12MHz/4000=3kHz的PWM频率
    50, // 高电平占空比50%
    StepperMotorElbow_Dir_GPIO_Port, // 方向引脚端口
    StepperMotorElbow_Dir_Pin, // 方向引脚引脚
    GPIO_PIN_SET // 高电平为正转
  );
  StepperMotor_Init( // 初始化步进电机gStepperMotorLift
    &gStepperMotorLift, // 竖轴步进电机
    &htim11, // 使用TIM11定时器
    TIM_CHANNEL_1, // 使用通道1输出PWM
    168000000, // 内部时钟为168MHz
    14-1, // 进行预分频，14分频，得到168MHz/14=12MHz的CNT计数频率
    4000-1, // 设置自动重装载值为4000，得到12MHz/4000=3kHz的PWM频率
    50, // 高电平占空比50%
    StepperMotorLift_Dir_GPIO_Port, // 方向引脚端口
    StepperMotorLift_Dir_Pin, // 方向引脚引脚
    GPIO_PIN_SET // 高电平为正转
  );
  
  IsAllInitOkay = true;

  while (true) {
    UartDmaStream_ReadState_e ReadState =
      UartDmaStream_ReadFrame( // 读取一帧数据
        &gMainStream, // 主通信流
        gFrameBuffer, // 接收一帧数据的缓冲区
        osWaitForever // 等待一帧数据，超时时间无限等待
      );
    
    if (ReadState == UartDmaStream_ReadState_Successful) { // 成功接收到一帧数据
      uint32_t FrameLen = UartDmaStream_GetFrameSize(&gMainStream, gFrameBuffer); // 获取帧长度（包括有效数据部分）
      uint8_t PrintHexStr[128];
      for (size_t i=0; i<FrameLen; i++) sprintf((char*)&PrintHexStr[i*3], "%02X ", gFrameBuffer[i]);
      UartDmaStream_Printf(&gMainStream, "Received Frame: %s\n", PrintHexStr);
      
      UartDmaStream_FrameType_e FrameType = UartDmaStream_GetFrameType(&gMainStream, gFrameBuffer); // 获取帧类型（请求帧、应答帧、事件帧）
      uint32_t PayloadLen = UartDmaStream_GetPayloadSize(&gMainStream, gFrameBuffer); // 获取数据长度（只是有效数据部分长度）
      uint8_t *PayloadData = UartDmaStream_GetPayloadData(&gMainStream, gFrameBuffer); // 获取有效数据部分的指针
      uint16_t CommandType = UartDmaStream_GetCommandType(&gMainStream, gFrameBuffer); // 获取命令类型
      
      if (FrameType == UartDmaStream_FrameType_Req) { // 是请求帧
        if (CommandType == COMMAND_TYPE_MOTOR_BASIC_MOVE) {
          Parse_COMMAND_TYPE_MOTOR_BASIC_MOVE(PayloadData, PayloadLen);
        } // if (CommandType == COMMAND_TYPE_MOTOR_BASIC_MOVE)
        else if (CommandType == COMMAND_TYPE_LED_BLINK) {
          DigitalOutput_ToggleState(&gLED0);
          DigitalOutput_ToggleState(&gLED1);
        } // if (CommandType == COMMAND_TYPE_LED_BLINK)
      } // if (FrameType == UartDmaStream_FrameType_Req)

      else if (FrameType == UartDmaStream_FrameType_Res) { // 是应答帧
        ;
      } // else if (FrameType == UartDmaStream_FrameType_Res)

      else if (FrameType == UartDmaStream_FrameType_Evt) { // 是事件帧
        ;
      } // else if (FrameType == UartDmaStream_FrameType_Evt)

      else { // 其他未知帧类型
        ;
      } // else
    } // if (ReadState == UartDmaStream_ReadState_Successful)

    else if (ReadState == UartDmaStream_ReadState_NoData) { // 一点数据都没读到，超时了
      UartDmaStream_Printf(&gMainStream, "No Data Received, Timeout!\n");
    } // else if (ReadState == UartDmaStream_ReadState_NoData)

    else if (ReadState == UartDmaStream_ReadState_CrcErr) { // 完整读到了符合格式的数据，但CRC校验错误
      UartDmaStream_Printf(&gMainStream, "CRC Check Sum Error!\n");
      // uint32_t FrameLen = UartDmaStream_GetFrameSize(&gMainStream, gFrameBuffer); // 获取帧长度（包括有效数据部分）
      // uint8_t PrintHexStr[128];
      // for (size_t i=0; i<FrameLen; i++) sprintf((char*)&PrintHexStr[i*3], "%02X ", gFrameBuffer[i]);
      // UartDmaStream_Printf(&gMainStream, "CRC Check Sum Error: %s\n", PrintHexStr); // 打印校验码错误的帧数据
    } // else if (ReadState == UartDmaStream_ReadState_CrcErr)

    else if (ReadState == UartDmaStream_ReadState_Timeout) { // 读了一部分符合格式的数据，但中途超时退出了
      UartDmaStream_Printf(&gMainStream, "Read Timeout!\n");
    } // else if (ReadState == UartDmaStream_ReadState_Timeout)

    else { // 其他未知状态
      UartDmaStream_Printf(&gMainStream, "Unknown Read State: %d\n", ReadState);
    } // else

    DigitalOutput_ToggleState(&gLED0);
    DigitalOutput_ToggleState(&gLED1);
    osDelay(pdMS_TO_TICKS(10));
  }
}

void Parse_COMMAND_TYPE_MOTOR_BASIC_MOVE(uint8_t *PayloadData, uint32_t PayloadLen) {
  Msg_MotorAction_t msg;
  msg.RequestType = MotorActionRequestType_BasicMove;
  msg.MotorID = 0x0001;
  msg.ActionType = 0x01;
  msg.Steps = BytesToInt64_BigEndian(PayloadData+4);
  msg.Speed = BytesToUint32_BigEndian(PayloadData+12);
  if ( osMessageQueuePut(gMsgQueueMotorAction, &msg, 0U, 0) == osOK ) {
    UartDmaStream_Printf(&gMainStream, "[COMMAND_TYPE_MOTOR_BASIC_MOVE] Parse Success!!!\n\n");
  } else {
    UartDmaStream_Printf(&gMainStream, "[COMMAND_TYPE_MOTOR_BASIC_MOVE] Parse Failed~~~\n\n");
  }
}
