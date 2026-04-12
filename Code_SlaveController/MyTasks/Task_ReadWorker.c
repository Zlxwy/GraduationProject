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
DigitalInput_t gKey[4]; // 按键对象
volatile bool KeyPressedFlag[4]; // 按键按下标志位，用于标记按键按下
volatile bool HadKeyPressed[4]; // 按键按下过标志位，用于连带触发KeyReleasedFlag，只有置位了才能触发KeyReleasedFlag
volatile bool KeyReleasedFlag[4]; // 按键释放标志位，用于标记按键释放
DigitalOutput_t gL298nEnableA; // L298n使能A引脚对象
DigitalOutput_t gL298nInput1; // L298n输入1引脚对象
DigitalOutput_t gL298nInput2; // L298n输入2引脚对象
DigitalOutput_t gL298nEnableB; // L298n使能B引脚对象
DigitalOutput_t gL298nInput3; // L298n输入3引脚对象
DigitalOutput_t gL298nInput4; // L298n输入4引脚对象
DigitalInput_t gLimitSwitchVerticalAxis; // 竖轴限位开关对象
volatile bool IsLimitSwitchVerticalAxisExtiEnabled = false; // 竖轴限位开关中断使能标志位







/*包装函数：返回值改为void*/
void MyDelayWrapper(uint32_t ms) {
  osDelay(pdMS_TO_TICKS(ms));
}

void Parse_COMMAND_TYPE_MOTOR_BASIC_MOVE(uint8_t *PayloadData, uint32_t PayloadLen);
void Parse_COMMAND_TYPE_MOTOR_SET_MAGNET_STATUS(uint8_t *PayloadData, uint32_t PayloadLen);
void Parse_COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST(uint8_t *PayloadData, uint32_t PayloadLen);
void Parse_COMMAND_TYPE_MOTOR_VERTICAL_AXIS_MOVE(uint8_t *PayloadData, uint32_t PayloadLen);


/*读取线程函数，是唯一调用UartDmaStream_ReadFrame的地方，解析数据后可通过消息队列分发到其他线程处理*/
void ReadWorkerTaskFunc(void *argument) {
  (void)argument;
  IsAllInitOkay = false; // 标记主通信线程初始化未完成

  /*消息队列创建*/
  gMsgQueueMotorAction = osMessageQueueNew(10, sizeof(Msg_MotorAction_t), NULL);
  if (gMsgQueueMotorAction == NULL) UartDmaStream_DebugPrintf(&gMainStream, "Failed to create message queue for motor action!\n");

  /*硬件对象、标志位初始化*/
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
    GPIO_PIN_RESET // 低电平为正转、即肩关节逆时针转
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
    GPIO_PIN_SET // 高电平为正转，即肘关节逆时针转
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
    GPIO_PIN_RESET // 低电平为正转，即竖轴下降
  );
  DigitalInput_Init(&gKey[0], KEY0_GPIO_Port, KEY0_Pin, GPIO_PIN_RESET);
  DigitalInput_Init(&gKey[1], KEY1_GPIO_Port, KEY1_Pin, GPIO_PIN_RESET);
  DigitalInput_Init(&gKey[2], KEY2_GPIO_Port, KEY2_Pin, GPIO_PIN_RESET);
  DigitalInput_Init(&gKey[3], KEY3_GPIO_Port, KEY3_Pin, GPIO_PIN_RESET);
  for (uint16_t i=0; i<4; i++) {
    KeyPressedFlag[i] = false;
    HadKeyPressed[i] = false;
    KeyReleasedFlag[i] = false;
  }
  DigitalOutput_Init(&gL298nEnableA, L298N_ENA_GPIO_Port, L298N_ENA_Pin, GPIO_PIN_SET);
  DigitalOutput_Init(&gL298nInput1, L298N_IN1_GPIO_Port, L298N_IN1_Pin, GPIO_PIN_SET);
  DigitalOutput_Init(&gL298nInput2, L298N_IN2_GPIO_Port, L298N_IN2_Pin, GPIO_PIN_SET);
  DigitalOutput_Init(&gL298nEnableB, L298N_ENB_GPIO_Port, L298N_ENB_Pin, GPIO_PIN_SET);
  DigitalOutput_Init(&gL298nInput3, L298N_IN3_GPIO_Port, L298N_IN3_Pin, GPIO_PIN_SET);
  DigitalOutput_Init(&gL298nInput4, L298N_IN4_GPIO_Port, L298N_IN4_Pin, GPIO_PIN_SET);
  DigitalInput_Init(&gLimitSwitchVerticalAxis, SIG3_GPIO_Port, SIG3_Pin, GPIO_PIN_RESET);
  LCD_Init(); // 初始化LCD，用的是老版函数，就一条函数初始化完成了
  
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
      UartDmaStream_DebugPrintf(&gMainStream, "Received Frame: %s\n", PrintHexStr);
      
      UartDmaStream_FrameType_e FrameType = UartDmaStream_GetFrameType(&gMainStream, gFrameBuffer); // 获取帧类型（请求帧、应答帧、事件帧）
      uint32_t PayloadLen = UartDmaStream_GetPayloadSize(&gMainStream, gFrameBuffer); // 获取数据长度（只是有效数据部分长度）
      uint8_t *PayloadData = UartDmaStream_GetPayloadData(&gMainStream, gFrameBuffer); // 获取有效数据部分的指针
      uint16_t CommandType = UartDmaStream_GetCommandType(&gMainStream, gFrameBuffer); // 获取命令类型







      if (FrameType == UartDmaStream_FrameType_Req) { // 是请求帧
        if (CommandType == COMMAND_TYPE_MOTOR_BASIC_MOVE) {
          Parse_COMMAND_TYPE_MOTOR_BASIC_MOVE(PayloadData, PayloadLen);
        } // if (CommandType == COMMAND_TYPE_MOTOR_BASIC_MOVE)

        else if (CommandType == COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST) {
          Parse_COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST(PayloadData, PayloadLen);
        } // else if (CommandType == COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST)

        else if (CommandType == COMMAND_TYPE_MOTOR_VERTICAL_AXIS_MOVE) {
          Parse_COMMAND_TYPE_MOTOR_VERTICAL_AXIS_MOVE(PayloadData, PayloadLen);
        } // else if (CommandType == COMMAND_TYPE_MOTOR_VERTICAL_AXIS_MOVE)

        else if (CommandType == COMMAND_TYPE_SET_MAGNET_STATUS) {
          Parse_COMMAND_TYPE_MOTOR_SET_MAGNET_STATUS(PayloadData, PayloadLen);
        } // else if (CommandType == COMMAND_TYPE_SET_MAGNET_STATUS)
        





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
      UartDmaStream_DebugPrintf(&gMainStream, "No Data Received, Timeout!\n");
    } // else if (ReadState == UartDmaStream_ReadState_NoData)

    else if (ReadState == UartDmaStream_ReadState_CrcErr) { // 完整读到了符合格式的数据，但CRC校验错误
      UartDmaStream_DebugPrintf(&gMainStream, "CRC Check Sum Error!\n");
      // uint32_t FrameLen = UartDmaStream_GetFrameSize(&gMainStream, gFrameBuffer); // 获取帧长度（包括有效数据部分）
      // uint8_t PrintHexStr[128];
      // for (size_t i=0; i<FrameLen; i++) sprintf((char*)&PrintHexStr[i*3], "%02X ", gFrameBuffer[i]);
      // UartDmaStream_DebugPrintf(&gMainStream, "CRC Check Sum Error: %s\n", PrintHexStr); // 打印校验码错误的帧数据
    } // else if (ReadState == UartDmaStream_ReadState_CrcErr)

    else if (ReadState == UartDmaStream_ReadState_Timeout) { // 读了一部分符合格式的数据，但中途超时退出了
      UartDmaStream_DebugPrintf(&gMainStream, "Read Timeout!\n");
    } // else if (ReadState == UartDmaStream_ReadState_Timeout)

    else { // 其他未知状态
      UartDmaStream_DebugPrintf(&gMainStream, "Unknown Read State: %d\n", ReadState);
    } // else

    osDelay(pdMS_TO_TICKS(10));
  }
}




/*使用xxx消息队列，在xxx任务中处理*/
void Parse_COMMAND_TYPE_MOTOR_BASIC_MOVE(uint8_t *PayloadData, uint32_t PayloadLen) {
  Msg_MotorAction_t msg;
  msg.RequestType = MotorActionRequestType_BasicMove;
  msg.MotorID = PayloadData[2];
  msg.ActionType = PayloadData[3];
  msg.Steps = BytesToInt64_BigEndian(&PayloadData[4]);
  msg.Speed = BytesToUint32_BigEndian(&PayloadData[12]);
  if ( osMessageQueuePut(gMsgQueueMotorAction, &msg, 0U, 0) == osOK ) {
    UartDmaStream_LogPrintf(&gMainStream, "[COMMAND_TYPE_MOTOR_BASIC_MOVE] Parse Success!!!\n\n");
  } else {
    UartDmaStream_LogPrintf(&gMainStream, "[COMMAND_TYPE_MOTOR_BASIC_MOVE] Parse Failed~~~\n\n");
  }
}

void Parse_COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST(uint8_t *PayloadData, uint32_t PayloadLen) {
  Msg_MotorAction_t msg;
  msg.RequestType = MotorActionRequestType_VerticalAxisRst;
  if ( osMessageQueuePut(gMsgQueueMotorAction, &msg, 0U, 0) == osOK ) {
    UartDmaStream_LogPrintf(&gMainStream, "[COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST] Parse Success!!!\n\n");
  } else {
    UartDmaStream_LogPrintf(&gMainStream, "[COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST] Parse Failed~~~\n\n");
  }
}

void Parse_COMMAND_TYPE_MOTOR_VERTICAL_AXIS_MOVE(uint8_t *PayloadData, uint32_t PayloadLen) {
  Msg_MotorAction_t msg;
  msg.RequestType = MotorActionRequestType_VerticalAxisMove;
  msg.PositionZ = BytesToFloat32_BigEndian(&PayloadData[2]);
  if ( osMessageQueuePut(gMsgQueueMotorAction, &msg, 0U, 0) == osOK ) {
    UartDmaStream_LogPrintf(&gMainStream, "[COMMAND_TYPE_MOTOR_VERTICAL_AXIS_MOVE] Parse Success!!!\n\n");
  } else {
    UartDmaStream_LogPrintf(&gMainStream, "[COMMAND_TYPE_MOTOR_VERTICAL_AXIS_MOVE] Parse Failed~~~\n\n");
  }
}

void Parse_COMMAND_TYPE_MOTOR_SET_MAGNET_STATUS(uint8_t *PayloadData, uint32_t PayloadLen) {
  Msg_MotorAction_t msg;
  msg.RequestType = MotorActionRequestType_SetMagnetStatus;
  msg.MagnetStatus = PayloadData[2];
  if ( osMessageQueuePut(gMsgQueueMotorAction, &msg, 0U, 0) == osOK ) {
    UartDmaStream_LogPrintf(&gMainStream, "[COMMAND_TYPE_SET_MAGNET_STATUS] Parse Success!!!\n\n");
  } else {
    UartDmaStream_LogPrintf(&gMainStream, "[COMMAND_TYPE_SET_MAGNET_STATUS] Parse Failed~~~\n\n");
  }
}
