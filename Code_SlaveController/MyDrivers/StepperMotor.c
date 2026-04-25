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

#define ARR_CLAMP(val, min, max)  ( (val < min) ? min : ( (val > max) ? max : val ) )
#define ABS(val) ( (val < 0) ? (-val) : (val) )
#define MIN(a, b) ( (a) < (b) ? (a) : (b) )
#define MAX(a, b) ( (a) > (b) ? (a) : (b) )
static uint32_t cal_arr(StepperMotor_t *cThis, uint32_t speed) {
  return ( (float)cThis->InternalClock /
           (float)(cThis->PrescalerVal+1) /
           (float)speed
          ) - 1;
} // 返回值单位为ARR

static float cal_freq(StepperMotor_t *cThis, uint32_t arr) {
  return (float)cThis->InternalClock /
         (float)(cThis->PrescalerVal+1) /
         (float)(arr+1);
} // 返回值单位为Hz

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
                       GPIO_TypeDef *DirectionPort,
                       uint16_t DirectionPin,
                       GPIO_PinState ForwardState) {
  /*初始化成员变量*/
  cThis->timer = timer;
  cThis->GenerateChannel = GenerateChannel;
  cThis->InternalClock = InternalClock;
  cThis->PrescalerVal = PrescalerVal;
  cThis->AutoReloadVal = AutoReloadVal;
  cThis->DirectionPort = DirectionPort;
  cThis->DirectionPin = DirectionPin;
  cThis->ForwardState = ForwardState;

  /*初始化状态变量*/
  cThis->RunState = StepperMotor_RunState_Stop;
  cThis->TargetPulsesToOutput = 0;
  cThis->CurrentOutputedPulses = 0;
  
  /*以下这些成员用于步进电机的缓启停功能*/
  cThis->TargetArrValue = 0; // 目标ARR值，初始值为0
  cThis->ArrAtMaxSpeed = 4; // 最大的速度对应着最小的ARR，为2，小于这个的ARR都不可设置
  cThis->ArrAtMinSpeed = 65535; // 最小的速度对应着最大的ARR，为65535，大于这个的ARR都不可设置
  // 因为STM32手册里面也没有明确说明，在PWM Mode 2模式下，CCR到底是<ARR有效还是≤ARR有效，
  // 因此至少将ARR设置为2，也就是0,1,2,0,1,2,...地计数，CRR取个1能够保证50%占空比输出
  cThis->MaxSingleFadeSteps = 50; // 单段缓冲最大用步50步
  cThis->UsedSingleFadeSteps = 0; // 初始化使用的单段缓冲步数为0
  cThis->FadeState = StepperMotor_FadeState_Idle; // 初始缓启停状态为空闲
  
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

  arr = ARR_CLAMP(arr, cThis->ArrAtMaxSpeed, cThis->ArrAtMinSpeed); // 对ARR值进行限制，确保在最大速度和最小速度之间
  cThis->AutoReloadVal = arr; // 设置自动重装载值
  uint32_t ccr = arr / 2; // 固定占空比为一半

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

    if (cThis->FadeState == StepperMotor_FadeState_Accel) { // 如果是加速状态
      float now_speed = cal_freq(cThis, cThis->timer->Instance->ARR); // 根据当前ARR计算当前速度
      float tar_speed = cal_freq(cThis, cThis->TargetArrValue); // 根据目标ARR计算目标速度
      float min_speed = cal_freq(cThis, cThis->ArrAtMinSpeed); // 根据最小速度ARR计算最小速度
      float accel = (tar_speed - min_speed) / cThis->UsedSingleFadeSteps; // 计算加速率
      float next_speed = now_speed + accel; // 计算下一个速度
      if (next_speed >= tar_speed || cThis->CurrentOutputedPulses >= cThis->UsedSingleFadeSteps) { // 如果下一个速度达到目标速度，或者加速段结束
        cThis->FadeState = StepperMotor_FadeState_Keep; // 切换到保持状态
        StepperMotor_SetAutoReload(cThis, cThis->TargetArrValue); // 设置自动重装载值为目标ARR值
      } else {
        StepperMotor_SetAutoReload(cThis, cal_arr(cThis, next_speed)); // 设置自动重装载值为下一个速度的ARR值
      }
    }

    else if (cThis->FadeState == StepperMotor_FadeState_Keep) { // 如果是保持状态
      StepperMotor_SetAutoReload(cThis, cThis->TargetArrValue); // 设置自动重装载值为目标ARR值
      if (cThis->CurrentOutputedPulses >= cThis->TargetPulsesToOutput - cThis->UsedSingleFadeSteps - 1) {
        cThis->FadeState = StepperMotor_FadeState_Decel; // 切换到减速状态
      }
    }

    else if (cThis->FadeState == StepperMotor_FadeState_Decel) { // 如果是减速状态
      float now_speed = cal_freq(cThis, cThis->timer->Instance->ARR); // 根据当前ARR计算当前速度
      float tar_speed = cal_freq(cThis, cThis->TargetArrValue); // 根据目标ARR计算目标速度
      float min_speed = cal_freq(cThis, cThis->ArrAtMinSpeed); // 根据最小速度ARR计算最小速度
      float decel = (tar_speed - min_speed) / cThis->UsedSingleFadeSteps; // 计算减速率
      float next_speed = now_speed - decel; // 计算下一个速度
      if (next_speed <= min_speed || cThis->CurrentOutputedPulses >= cThis->TargetPulsesToOutput) { // 如果下一个速度已经达到最小速度，或者减速段结束
        cThis->FadeState = StepperMotor_FadeState_Idle; // 切换到空闲状态
        StepperMotor_SetAutoReload(cThis, cThis->ArrAtMinSpeed); // 设置自动重装载值为最小速度ARR值
      } else {
        StepperMotor_SetAutoReload(cThis, cal_arr(cThis, next_speed)); // 设置自动重装载值为下一个速度的ARR值
      }
    }
  }

  /*如果是连续运行状态，一直输出PWM*/
  else if (RunState == StepperMotor_RunState_RunContinuous) {
    cThis->CurrentOutputedPulses++; // 输出脉冲数计数增加
    if (cThis->FadeState == StepperMotor_FadeState_Accel) {
      float now_speed = cal_freq(cThis, cThis->timer->Instance->ARR); // 根据当前ARR计算当前速度
      float tar_speed = cal_freq(cThis, cThis->TargetArrValue); // 根据目标ARR计算目标速度
      float min_speed = cal_freq(cThis, cThis->ArrAtMinSpeed); // 根据最小速度ARR计算最小速度
      float accel = (tar_speed - min_speed) / cThis->UsedSingleFadeSteps; // 计算加速率
      float next_speed = now_speed + accel; // 计算下一个速度
      if (next_speed >= tar_speed || cThis->CurrentOutputedPulses >= cThis->UsedSingleFadeSteps) {
        cThis->FadeState = StepperMotor_FadeState_Keep; // 切换到保持状态
        StepperMotor_SetAutoReload(cThis, cThis->TargetArrValue); // 设置自动重装载值为目标ARR值
      } else {
        StepperMotor_SetAutoReload(cThis, cal_arr(cThis, next_speed)); // 设置自动重装载值为下一个速度的ARR值
      }
    }
  }

}

















/**
 * @brief 停止步进电机旋转
 * @note 调用此函数后，步进电机将停止旋转
 * @param cThis 步进电机对象指针
 */
void StepperMotor_Stop(StepperMotor_t *cThis) {
  StepperMotor_SetRunState(cThis, StepperMotor_RunState_Stop); // 设置运行状态

  /*恢复缓启停状态机*/
  cThis->UsedSingleFadeSteps = 0; // 重置缓启停使用步数为0
  cThis->FadeState = StepperMotor_FadeState_Idle; // 重置缓启停状态为空闲

  /*重置目标脉冲数和输出脉冲数*/
  cThis->TargetPulsesToOutput = 0; // 重置目标脉冲数
  cThis->CurrentOutputedPulses = 0; // 重置输出脉冲数

  StepperMotor_ClearOutputPWM(cThis); // 清除PWM输出
}



/**
 * @brief 运行步进电机指定步数
 * @note 调用此函数后，要确保ARR和CCR已经加载好，否则输出的第一个波形会有点奇怪（占空比不是50%）
 * @param cThis 步进电机对象指针
 * @param steps 步数，正负值对应正反转，范围int64_t
 * @param speed 速度，单位Hz，范围[SYSCLK/(PSC+1)/(65536), SYSCLK/(PSC+1)/2]
 */
void StepperMotor_MoveSteps(StepperMotor_t *cThis, int64_t steps, uint32_t speed) {
  /*如果步数为0，直接停止电机*/
  if (steps == 0) {
    StepperMotor_Stop(cThis);
    return;
  }

  /*根据步数设置方向*/
  StepperMotor_Direction_t dir = (steps > 0) ? (StepperMotor_Direction_Forward) : (StepperMotor_Direction_Backward);
  StepperMotor_SetDirection(cThis, dir);

  /*设置目标的PWM频率*/
  cThis->TargetArrValue = cal_arr(cThis, speed);
  cThis->TargetArrValue = ARR_CLAMP(cThis->TargetArrValue, cThis->ArrAtMaxSpeed, cThis->ArrAtMinSpeed); // 对ARR值进行限制，确保在最大速度和最小速度之间
  StepperMotor_SetAutoReload(cThis, cThis->ArrAtMinSpeed);
  SET_BIT(cThis->timer->Instance->EGR, TIM_EGR_UG);
  // 手动触发一次定时器更新，让预分频器、自动重装值、比较值等配置立即生效
  // 因为如果第一次不更新一下ARR和CCR的话，第一个波形会有点奇怪（占空比不是50%）

  /*计算实际使用的单段缓冲步数*/
  uint64_t ValidSingleFadeSteps = (float)ABS(steps) * 5.0f / 16.0f; // 取八分之五的步数进行缓启停，单段则为十六分之五的步数
  cThis->UsedSingleFadeSteps = MIN(ValidSingleFadeSteps, cThis->MaxSingleFadeSteps); // 取较小值作为单段缓冲使用的步数
  cThis->FadeState = StepperMotor_FadeState_Accel; // 设置缓启停状态为加速状态

  /*设置目标脉冲数*/
  cThis->TargetPulsesToOutput = ABS(steps);
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

  /*设置目标的PWM频率*/
  cThis->TargetArrValue = cal_arr(cThis, speed);
  cThis->TargetArrValue = ARR_CLAMP(cThis->TargetArrValue, cThis->ArrAtMaxSpeed, cThis->ArrAtMinSpeed); // 对ARR值进行限制，确保在最大速度和最小速度之间
  StepperMotor_SetAutoReload(cThis, cThis->ArrAtMinSpeed);
  SET_BIT(cThis->timer->Instance->EGR, TIM_EGR_UG);
  // 手动触发一次定时器更新，让预分频器、自动重装值、比较值等配置立即生效
  // 因为如果第一次不更新一下ARR和CCR的话，第一个波形会有点奇怪（占空比不是50%）

  /*因为是持续运动，不是指定步数运行，因此设置成最大的单段缓冲使用步数即可*/
  cThis->UsedSingleFadeSteps = cThis->MaxSingleFadeSteps;
  cThis->FadeState = StepperMotor_FadeState_Accel; // 设置缓启停状态为加速状态

  /*清零脉冲数就行*/
  cThis->TargetPulsesToOutput = 0;
  cThis->CurrentOutputedPulses = 0;
  
  StepperMotor_SetRunState(cThis, StepperMotor_RunState_RunContinuous); // 设置运行状态
  StepperMotor_StartOutputPWM(cThis); // 启动PWM输出
}




