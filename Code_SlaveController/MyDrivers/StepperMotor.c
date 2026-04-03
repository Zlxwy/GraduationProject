#include "StepperMotor.h"

// STM32CubeMX配置
// Prescaler (PSC - 16 bits value): 14-1
// Counter Mode: Up
// Counter Period (AutoReload Register - 16 bits value): 4000-1
// Internal Clock Division (CKD): No Division
// auto-reload preload: Enable
// Mode: PWM Mode 2
// Pulse (16 bits value): 0
// Output compare preload: Enable
// Fast Mode: Disable
// CH Polarity: High
// 开启中断

/********初始化示例*********/
// StepperMotor_t BoomStepperMotor;
// StepperMotor_Init( // 初始化步进电机
//   &BoomStepperMotor, // 步进电机Object
//   &htim10, // 使用定时器10
//   TIM_CHANNEL_1, // 使用通道1输出PWM
//   168000000, // 内部时钟为168MHz
//   14-1, // 进行预分频，14分频，得到168MHz/14=12MHz的CNT计数频率
//   4000-1, // 设置自动重装载值为4000，得到12MHz/4000=3kHz的PWM频率
//   50, // 高电平占空比50%
//   TestDir_GPIO_Port, // 方向引脚端口
//   TestDir_Pin, // 方向引脚号
//   GPIO_PIN_SET // 高电平为正转
// ); // 在CubeMX配置了PWM引脚为PB8
// StepperMotor_MoveSteps(&BoomStepperMotor, 800, 20000); // 行走800步，以2kHz频率的速度



/**
 * @brief 初始化步进电机
 * @param cThis 步进电机对象指针
 * @param timer 定时器对象指针
 * @param GenerateChannel 定时器的PWM输出通道
 * @param InternalClock 定时器的内部时钟
 * @param PrescalerVal 定时器的预分频值
 * @param AutoReloadVal 定时器的自动重装载值
 * @param HighLevelDutyCycle 高电平占空比
 * @param DirectionPort 方向引脚的端口
 * @param DirectionPin 方向引脚的引脚号
 * @param ForwardState 正向运动时的引脚电平状态
 */
void StepperMotor_Init(StepperMotor_t *cThis,
                       TIM_HandleTypeDef *timer,
                       uint32_t GenerateChannel,
                       uint32_t InternalClock,
                       uint32_t PrescalerVal,
                       uint32_t AutoReloadVal,
                       uint8_t HighLevelDutyCycle,
                       GPIO_TypeDef *DirectionPort,
                       uint16_t DirectionPin,
                       GPIO_PinState ForwardState) {
  /*初始化成员变量*/
  cThis->timer = timer;
  cThis->GenerateChannel = GenerateChannel;
  cThis->InternalClock = InternalClock;
  cThis->PrescalerVal = PrescalerVal;
  cThis->AutoReloadVal = AutoReloadVal;
  cThis->HighLevelDutyCycle = (HighLevelDutyCycle >= 100) ? (50) : (HighLevelDutyCycle);
  cThis->DirectionPort = DirectionPort;
  cThis->DirectionPin = DirectionPin;
  cThis->ForwardState = ForwardState;

  /*初始化状态变量*/
  cThis->RunState = StepperMotor_RunState_Stop;
  cThis->TargetPulsesToOutput = 0;
  cThis->CurrentOutputedPulses = 0;

  /*基本配置*/
  StepperMotor_SetRunState(cThis, StepperMotor_RunState_Stop); // 设置初始运行状态为停止
  StepperMotor_SetDirection(cThis, StepperMotor_Direction_Forward); // 设置初始方向为正向
  StepperMotor_SetPrescaler(cThis, PrescalerVal); // 设置PSC
  StepperMotor_SetAutoReload(cThis, AutoReloadVal); // 设置ARR和CCR
  StepperMotor_ClearOutputPWM(cThis); // 清除PWM输出
}



/**
 * @brief 设置步进电机的运行状态
 * @param cThis 步进电机对象指针
 * @param RunState 运行状态
 *   @arg StepperMotor_RunState_Stop 停止
 *   @arg StepperMotor_RunState_MoveSteps 移动步数
 *   @arg StepperMotor_RunState_RunContinuous 连续运行
 */
void StepperMotor_SetRunState(StepperMotor_t *cThis, StepperMotor_RunState_t RunState) {
  cThis->RunState = RunState; // 设置运行状态
}



/**
 * @brief 获取步进电机的运行状态
 * @param cThis 步进电机对象指针
 * @return StepperMotor_RunState_t 运行状态
 *   @arg StepperMotor_RunState_Stop 停止
 *   @arg StepperMotor_RunState_MoveSteps 移动步数
 *   @arg StepperMotor_RunState_RunContinuous 连续运行
 */
StepperMotor_RunState_t StepperMotor_GetRunState(StepperMotor_t *cThis) {
  return cThis->RunState; // 返回运行状态
}



/**
 * @brief 设置步进电机的方向
 * @param cThis 步进电机对象指针
 * @param dir 方向（前向或后向）
 *   @arg StepperMotor_Direction_Forward 正向
 *   @arg StepperMotor_Direction_Backward 反向
 */
void StepperMotor_SetDirection(StepperMotor_t *cThis, StepperMotor_Direction_t dir) {
  cThis->Direction = dir; // 设置方向状态

  GPIO_PinState ForwardState = cThis->ForwardState;
  GPIO_PinState BackwardState = (ForwardState == GPIO_PIN_RESET) ? (GPIO_PIN_SET) : (GPIO_PIN_RESET);

  HAL_GPIO_WritePin(
    cThis->DirectionPort, cThis->DirectionPin,
    (dir == StepperMotor_Direction_Forward) ? (ForwardState) : (BackwardState)
  );
}



/**
 * @brief 设置步进电机的预分频值(TIM->PSC)
 * @param cThis 步进电机对象指针
 * @param prescaler 预分频值
 */
void StepperMotor_SetPrescaler(StepperMotor_t *cThis, uint32_t prescaler) {
  if (prescaler == 0) return;
  cThis->PrescalerVal = prescaler; // 设置预分频值

  __HAL_TIM_SET_PRESCALER(cThis->timer, prescaler); // 设置预分频值
}



/**
 * @brief 设置步进电机的周期(TIM->ARR, TIM->CCR)
 * @note 这个函数不仅会设置ARR，还会根据占空比参数设置CCR
 * @param cThis 步进电机对象指针
 * @param arr 自动重装载值（周期）
 */
void StepperMotor_SetAutoReload(StepperMotor_t *cThis, uint32_t arr) {
  if (arr == 0) return;
  cThis->AutoReloadVal = arr; // 设置自动重装载值
  uint16_t ccr = arr - arr*(cThis->HighLevelDutyCycle/100.0f);

  __HAL_TIM_SET_AUTORELOAD(cThis->timer, arr); // 设置自动重装载值
  __HAL_TIM_SET_COMPARE(cThis->timer, cThis->GenerateChannel, ccr); // 设置比较值（占空比50%）
}



/**
 * @brief 启动步进电机输出PWM
 * @note 这个函数是为了硬件使能PWM输出，并且要保证定时器刚启动的时候不会意外进入中断，
 *       先配好时基单元，再使能PWM输出，确保波形完整完美
 * @param cThis 步进电机对象指针
 */
void StepperMotor_StartOutputPWM(StepperMotor_t *cThis) {
  /*使能定时器时基单元*/
  __HAL_TIM_SET_COUNTER(cThis->timer, 0); // 设置计数器值为0
  __HAL_TIM_CLEAR_FLAG(cThis->timer, TIM_FLAG_UPDATE); // 清除更新中断标志位，防止刚启动时意外进入中断
  __HAL_TIM_ENABLE_IT(cThis->timer, TIM_IT_UPDATE); // 启用更新中断
  __HAL_TIM_ENABLE(cThis->timer); // 启用定时器

  /*把相应的通道使能（相应的位置1）*/
  SET_BIT(cThis->timer->Instance->CCER, (uint32_t)(TIM_CCER_CC1E << (cThis->GenerateChannel & 0x1FU)));
  // 参考自TIM_CCxChannelCmd(cThis->timer->Instance, cThis->GenerateChannel, TIM_CCx_ENABLE);
}



/**
 * @brief 清除步进电机输出PWM
 * @note 先关闭PWM输出，再关闭定时器时基单元
 * @param cThis 步进电机对象指针
 */
void StepperMotor_ClearOutputPWM(StepperMotor_t *cThis) {
  /*把相应的通道失能（相应的位置0）*/
  CLEAR_BIT(cThis->timer->Instance->CCER, (uint32_t)(TIM_CCER_CC1E << (cThis->GenerateChannel & 0x1FU)));
  // 参考自TIM_CCxChannelCmd(cThis->timer->Instance, cThis->GenerateChannel, TIM_CCx_DISABLE);

  /*先禁用定时器*/
  __HAL_TIM_DISABLE(cThis->timer); // 禁用定时器
  __HAL_TIM_DISABLE_IT(cThis->timer, TIM_IT_UPDATE); // 禁用更新中断
  __HAL_TIM_SET_COUNTER(cThis->timer, 0); // 设置计数器值为0
}













/**
 * @brief 在对应定时器的中断ISR中，调用这个函数
 * @param cThis 步进电机对象指针
 */
void StepperMotor_FuncCalled_InTimerInterrupt(StepperMotor_t *cThis) {
  
    /*如果是移动步数状态，直到输出脉冲数达到目标脉冲数，停止输出PWM*/
    StepperMotor_RunState_t RunState = StepperMotor_GetRunState(cThis);
    if (RunState == StepperMotor_RunState_MoveSteps) {
      cThis->CurrentOutputedPulses++; // 输出脉冲数增加
      if (cThis->CurrentOutputedPulses >= cThis->TargetPulsesToOutput) {
        StepperMotor_Stop(cThis); // 输出脉冲数达到目标脉冲数，停止电机
      }
    }

    /*如果是连续运行状态，一直输出PWM*/
    else if (RunState == StepperMotor_RunState_RunContinuous) {
      
    }

}

















/**
 * @brief 停止步进电机旋转
 * @note 调用此函数后，步进电机将停止旋转
 * @param cThis 步进电机对象指针
 */
void StepperMotor_Stop(StepperMotor_t *cThis) {
  StepperMotor_SetRunState(cThis, StepperMotor_RunState_Stop); // 设置运行状态

  cThis->TargetPulsesToOutput = 0; // 重置目标脉冲数
  cThis->CurrentOutputedPulses = 0; // 重置输出脉冲数

  StepperMotor_ClearOutputPWM(cThis); // 清除PWM输出
}



/**
 * @brief 运行步进电机指定步数
 * @note 调用此函数后，要确保ARR和CCR已经加载好，否则输出的第一个波形会有点奇怪（占空比不是50%）
 * @param cThis 步进电机对象指针
 * @param Steps 步数，正负值对应正反转，范围int32_t
 * @param speed 速度，单位Hz，范围[SYSCLK/(PSC+1)/(65536), SYSCLK/(PSC+1)/2]
 */
void StepperMotor_MoveSteps(StepperMotor_t *cThis, int32_t Steps, uint32_t speed) {
  /*如果步数为0，直接停止电机*/
  if (Steps == 0) {
    StepperMotor_Stop(cThis);
    return;
  }

  /*根据步数设置方向*/
  StepperMotor_Direction_t dir = (Steps > 0) ? (StepperMotor_Direction_Forward) : (StepperMotor_Direction_Backward);
  StepperMotor_SetDirection(cThis, dir);

  /*设置PWM频率*/
  StepperMotor_SetSpeed(cThis, speed);
  SET_BIT(cThis->timer->Instance->EGR, TIM_EGR_UG);
  // 手动触发一次定时器更新，让预分频器、自动重装值、比较值等配置立即生效
  // 因为如果第一次不更新一下ARR和CCR的话，第一个波形会有点奇怪（占空比不是50%）

  /*设置目标脉冲数*/
  cThis->TargetPulsesToOutput = (Steps > 0) ? (Steps) : (-Steps);
  cThis->CurrentOutputedPulses = 0;

  /*启动定时器*/
  StepperMotor_SetRunState(cThis, StepperMotor_RunState_MoveSteps); // 设置运行状态
  StepperMotor_StartOutputPWM(cThis); // 启动PWM输出
}



/**
 * @brief 使步进电机旋转
 * @note 会一直旋转，直到调用StepperMotor_Stop()停止旋转
 * @param cThis 步进电机对象指针
 * @param dir 方向（前向或后向）
 *   @arg StepperMotor_Direction_Forward 正向
 *   @arg StepperMotor_Direction_Backward 反向
 */
void StepperMotor_RunContinuous(StepperMotor_t *cThis, StepperMotor_Direction_t dir, uint32_t speed) {
  StepperMotor_SetDirection(cThis, dir); // 设置方向
  StepperMotor_SetSpeed(cThis, speed); // 设置PWM频率
  SET_BIT(cThis->timer->Instance->EGR, TIM_EGR_UG);
  // 手动触发一次定时器更新，让预分频器、自动重装值、比较值等配置立即生效
  // 因为如果第一次不更新一下ARR和CCR的话，第一个波形会有点奇怪（占空比不是50%）
  
  StepperMotor_SetRunState(cThis, StepperMotor_RunState_RunContinuous); // 设置运行状态
  StepperMotor_StartOutputPWM(cThis); // 启动PWM输出
}



/**
 * @brief 设置步进电机的速度（实际是PWM频率）
 * @note 这个函数会检查参数范围，如果传入的参数不合法，会设置为合法的最小或最大频率
 * @param cThis 步进电机对象指针
 * @param freq 频率，单位是Hz，范围在[SYSCLK/(PSC+1)/(65536), SYSCLK/(PSC+1)/2]之间
 */
void StepperMotor_SetSpeed(StepperMotor_t *cThis, uint32_t Speed) {
  /*计算出合法的最小频率和最大频率*/
  uint32_t MinFreq, MaxFreq; // 最小频率，最大频率
  MinFreq = cThis->InternalClock / (cThis->PrescalerVal+1);
  MinFreq = MinFreq / (65535+1); // 有可能会是0
  MaxFreq = cThis->InternalClock / (cThis->PrescalerVal+1);
  MaxFreq = MaxFreq / (1+1); // 二分频作为最大频率

  /*根据频率计算自动重装载值*/
  uint32_t arr;
  if (Speed < MinFreq) arr = 65536-1; // 如果频率小于最小频率，设置为合法的最小频率（65536分频）
  else if (Speed > MaxFreq) arr = 2-1; // 如果频率大于最大频率，设置为合法最大频率（2分频）
  else arr = ( cThis->InternalClock / (cThis->PrescalerVal+1) / Speed ) - 1; // 自动重装载值

  /*设置自动重装载值*/
  StepperMotor_SetAutoReload(cThis, arr); // 这个函数不仅会设置ARR，还会根据占空比参数设置CCR
}



/**
 * @brief 设置步进电机的速度（实际是PWM频率），不检查参数范围
 * @note 不检查参数范围，这个函数相比于StepperMotor_SetSpeed可以节省一些时间，
 *       如果传入的参数不合法，可能会导致定时器无法正常工作
 * @param cThis 步进电机对象指针
 * @param freq 频率，单位是Hz
 */
void StepperMotor_SetSpeedWithoutCheck(StepperMotor_t *cThis, uint32_t Speed) {
  uint32_t arr = ( cThis->InternalClock / (cThis->PrescalerVal+1) / Speed ) - 1; // 自动重装载值
  StepperMotor_SetAutoReload(cThis, arr); // 这个函数不仅会设置ARR，还会根据占空比参数设置CCR
}
