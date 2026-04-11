#ifndef __TASK_ALL_H__
#define __TASK_ALL_H__

/*C语言标准库头文件*/
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/*芯片平台、FreeRTOS头文件*/
#include "stm32f4xx_hal.h"
#include "FreeRTOS.h"
#include "cmsis_os.h"
#include "queue.h"
#include "task.h"
#include "main.h"

/*自定义头文件*/
#include "UartDmaStream.h"
#include "DigitalInput.h"
#include "DigitalOutput.h"
#include "StepperMotor.h"

extern UART_HandleTypeDef huart3;
extern DMA_HandleTypeDef hdma_usart3_rx;
extern DMA_HandleTypeDef hdma_usart3_tx;
extern TIM_HandleTypeDef htim3;
extern TIM_HandleTypeDef htim10;
extern TIM_HandleTypeDef htim11;





/*每一条对应协议中的命令类型*/
#define COMMAND_TYPE_MOTOR_BASIC_MOVE  0x0000
#define COMMAND_TYPE_MOTOR_MOVE_ON_PLANE  0x0001
#define COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST  0x0003
#define COMMAND_TYPE_MOTOR_VERTICAL_AXIS_MOVE  0x0002
#define COMMAND_TYPE_SET_MAGNET_STATUS  0x0004
#define COMMAND_TYPE_KEY_CLICK  0x0005





typedef enum {
  MotorActionRequestType_BasicMove, // 基础行走
  MotorActionRequestType_MoveOnPlane, // 平面行走
  MotorActionRequestType_VerticalAxisRst, // 竖轴位置重置
  MotorActionRequestType_VerticalAxisMove, // 竖轴位置移动
  MotorActionRequestType_SetMagnetStatus, // 设置磁铁状态
} MotorActionRequestType_e;

typedef struct {
  MotorActionRequestType_e RequestType;

  /*如果RequestType为MotorActionRequestType_BasicMove*/
  uint8_t MotorID; // 标识步进电机ID
  uint8_t ActionType; // 动作类型：0x00停止，0x01旋转指定步数，0x02持续旋转（Steps无效）
  int64_t Steps; // 指定行走步数
  uint32_t Speed; // 指定行走速度

  /*如果RequestType为MotorActionRequestType_MoveOnPlane*/
  float PixelCoordX; // 指定X轴坐标点，单位为像素
  float PixelCoordY; // 指定Y轴坐标点，单位为像素
  bool Side; // 机械臂关节向哪边拐：false左拐，true右拐

  /*如果RequestType为MotorActionRequestType_VerticalAxisMove*/
  float PositionZ; // 指定Z轴下降级数，范围0~100

  /*如果RequestType为MotorActionRequestType_MagnetEnable*/
  uint8_t MagnetStatus; // 磁铁状态：0x00禁用，0x01正向电压使能，0x02反向电压使能
} Msg_MotorAction_t; // 关于电机动作的消息结构体，只在MotorActionTaskFunc线程中执行





extern osMessageQueueId_t gMsgQueueMotorAction; // 电机动作消息队列，用来传递电机动作的执行消息





extern volatile bool IsAllInitOkay;
extern UartDmaStream_t gMainStream; // 主通信流，与上位机进行通信
extern uint8_t gFrameBuffer[256]; // 用来接收一帧一帧数据的缓冲区
extern DigitalOutput_t gLED0;
extern DigitalOutput_t gLED1;
extern StepperMotor_t gStepperMotorShoulder; // 肩部步进电机
extern StepperMotor_t gStepperMotorElbow; // 肘部步进电机
extern StepperMotor_t gStepperMotorLift; // 竖轴步进电机
extern DigitalInput_t gKey[4]; // 按键对象
extern volatile bool KeyPressedFlag[4]; // 按键按下标志位，用于标记按键按下
extern volatile bool HadKeyPressed[4]; // 按键按下过标志位，用于连带触发KeyReleasedFlag，只有置位了才能触发KeyReleasedFlag
extern volatile bool KeyReleasedFlag[4]; // 按键释放标志位，用于标记按键释放
extern DigitalOutput_t gL298nEnableA; // L298n使能A引脚对象
extern DigitalOutput_t gL298nInput1; // L298n输入1引脚对象
extern DigitalOutput_t gL298nInput2; // L298n输入2引脚对象
extern DigitalOutput_t gL298nEnableB; // L298n使能B引脚对象
extern DigitalOutput_t gL298nInput3; // L298n输入3引脚对象
extern DigitalOutput_t gL298nInput4; // L298n输入4引脚对象
extern DigitalInput_t gLimitSwitchVerticalAxis; // 竖轴限位开关对象
extern volatile bool IsLimitSwitchVerticalAxisExtiEnabled; // 竖轴限位开关中断使能标志位







/*以下这些任务线程函数，其实在freertos.c中是声明过的，这里再重复声明一下，是为了方便在其他文件中调用*/
void WriteWorkerTaskFunc(void *argument); // 写入工作线程
void ReadWorkerTaskFunc(void *argument); // 读取工作线程
void MotorActionTaskFunc(void *argument); // 电机动作线程
void KeyScanReadTaskFunc(void *argument); // 按键扫描读取线程







#endif
