#ifndef __STEPPER_MOTOR_H__
#define __STEPPER_MOTOR_H__

#include "stm32f4xx_hal.h"
#include "main.h"
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

// __HAL_TIM_SET_PRESCALER // 设置预分频值
// __HAL_TIM_SET_AUTORELOAD // 设置自动重装载值
// __HAL_TIM_SET_COUNTER // 设置计数器值
// __HAL_TIM_SET_COMPARE // 设置比较值（用于PWM输出）

typedef enum {
  /*停止*/StepperMotor_RunState_Stop = 0,
  /*正在指定步数旋转*/StepperMotor_RunState_MoveSteps = 1,
  /*正在连续旋转*/StepperMotor_RunState_RunContinuous = 2,
} StepperMotor_RunState_t;

typedef enum {
  /*正转*/StepperMotor_Direction_Forward = 0,
  /*反转*/StepperMotor_Direction_Backward = 1,
} StepperMotor_Direction_t;

typedef enum {
  /*未设置*/StepperMotor_FadeState_Unset = 0,
  /*加速*/StepperMotor_FadeState_Accel = 1,
  /*保持速度*/StepperMotor_FadeState_Keep = 2,
  /*减速*/StepperMotor_FadeState_Decel = 3,
} StepperMotor_FadeState_t;

typedef struct {
  /*定时器句柄*/TIM_HandleTypeDef *timer;
  /*PWM输出通道*/uint32_t GenerateChannel; // 大多数定时器会有多个通道，但每个步进电机只使用一个通道
  /*内部时钟频率*/uint32_t InternalClock; // 对于STM32F407ZGT6，TIM10,11的时钟源为168MHz，TIM13,14的时钟源为84MHz，需要注意这个
  /*预分频值*/uint32_t PrescalerVal; // CNT的计数频率由内部时钟频率和预分频值决定，推荐12MHz，根据ARR范围[1,65535]，此时PWM频率范围[183.11,6M]Hz
  /*自动重装载值*/uint32_t AutoReloadVal; // 无论什么时候，比较值都应该是这个值的一半（比较值也要跟随其实时变化）

  /*方向引脚端口*/GPIO_TypeDef *DirectionPort;
  /*方向引脚*/uint16_t DirectionPin;
  /*方向引脚正转状态*/GPIO_PinState ForwardState;
  /*方向状态*/StepperMotor_Direction_t Direction; // （实时变化）

  /*电机是否正在转动*/StepperMotor_RunState_t RunState; // 用于获取电机状态（实时变化）
  /*本轮输出总脉冲数*/uint64_t TargetPulsesToOutput; // 用于指定步数旋转
  /*当前已输出脉冲数*/uint64_t CurrentOutputedPulses; // 用于指定步数旋转

  /*以下这些成员用于步进电机的缓启停功能*/
  /*目标输出PWM速度对应的ARR*/uint32_t TargetArr; // 输出一系列脉冲时所需的速度，对应的ARR值，用于电机的缓启停功能
  /*最大可输出PWM频率对应的ARR*/uint32_t ArrAtMaxSpeed; // 最大的速度对应着最小的ARR，为2，小于这个的ARR都不可设置
  /*最小可输出PWM频率对应的ARR*/uint32_t ArrAtMinSpeed; // 最小的速度对应着最大的ARR，为65535，大于这个的ARR都不可设置
  /*最大单段缓冲最大用时*/uint16_t MaxSingleFadeTime; // 单位：ms
  /*实际单段缓冲最大用时*/uint16_t UsedSingleFadeTime; // 单位：ms
  /*缓冲状态*/StepperMotor_FadeState_t FadeState; // （实时变化）
  /*速度保持计数器*/uint32_t FreqHoldTimeCnt; // 在速度保持的时候开始递增，输出脉冲超过一半后递减，用以定位减速的区间
  /*速度保持计数器计数方向*/bool IsFreqHoldTimeCntIncreasing; // 为true时速度保持计数器递增，为false时递减，用以定位减速的区间
} StepperMotor_t;

void StepperMotor_Init(StepperMotor_t *cThis,
                       TIM_HandleTypeDef *timer,
                       uint32_t GenerateChannel,
                       uint32_t InternalClock,
                       uint32_t PrescalerVal,
                       uint32_t AutoReloadVal,
                       GPIO_TypeDef *DirectionPort,
                       uint16_t DirectionPin,
                       GPIO_PinState ForwardState);
void StepperMotor_SetRunState(StepperMotor_t *cThis, StepperMotor_RunState_t RunState);
StepperMotor_RunState_t StepperMotor_GetRunState(StepperMotor_t *cThis);
void StepperMotor_SetDirection(StepperMotor_t *cThis, StepperMotor_Direction_t dir);
void StepperMotor_SetPrescaler(StepperMotor_t *cThis, uint32_t prescaler);
void StepperMotor_SetAutoReload(StepperMotor_t *cThis, uint32_t arr);

void StepperMotor_StartOutputPWM(StepperMotor_t *cThis);
void StepperMotor_ClearOutputPWM(StepperMotor_t *cThis);

void StepperMotor_FuncCalled_InTimerInterrupt(StepperMotor_t *cThis);

void StepperMotor_Stop(StepperMotor_t *cThis);
void StepperMotor_MoveSteps(StepperMotor_t *cThis, int64_t steps, uint32_t speed);
void StepperMotor_RunContinuous(StepperMotor_t *cThis, StepperMotor_Direction_t dir, uint32_t speed);
// uint32_t StepperMotor_SetSpeed(StepperMotor_t *cThis, uint32_t speed);
// void StepperMotor_SetSpeedWithoutCheck(StepperMotor_t *cThis, uint32_t speed);

#endif // #ifndef __STEPPER_MOTOR_H__
