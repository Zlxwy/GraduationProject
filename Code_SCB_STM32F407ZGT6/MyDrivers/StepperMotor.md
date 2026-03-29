* [STM32CubeMX配置](#stm32cubemx配置)
* [代码使用示例](#代码使用示例)

## STM32CubeMX配置

- Pinout & Configuration
  - Timer: <u>TIM10</u>
    - Mode
      * Activated: <u>Checked</u>
      * Channel1: <u>PWM Generation CH1</u>
    - Configuration
      - Parameter Settings
        - Counter Settings
          * Prescaler (PSC - 16 bits value): <u>0</u>
          * Counter Mode: <u>Up</u>
          * Counter Period (ARR - 16 bits value): <u>65535</u>
          * Internal Clock Division (CKD): <u>No Division</u>
          * Auto-Reload Preload: <u>Enabled</u>
        - PWM Generation Channel 1
          * Mode: <u>PWM mode 2</u>
          * Pulse (16 bits value): <u>0</u>
          * Output compare preload: <u>Enabled</u>
          * Fast Mode: <u>Disabled</u>
          * CH Polarity: <u>High</u>
      - NVIC Settings
        | NVIC Interrupt Table | Enabled | Preemption Priority | Sub Priority |
        | --- | --- | --- | --- |
        | TIM update global interrupt | &#x2611; | x | x |
      - GPIO Settings
        GPIO Pull-up/Pull-down: <u>Pull-down</u>
        Maximum output speed: <u>Very High</u>

## 代码使用示例
```c
#define Dir_GPIO_Port  GPIOB
#define Dir_Pin  GPIO_PIN_8
StepperMotor_t BoomStepperMotor;


void TIMx_IRQHandler(void) {
  if ( __HAL_TIM_GET_FLAG(&htimx, TIM_FLAG_UPDATE) ) {
    StepperMotor_FuncCalled_InTimerInterrupt(&BoomStepperMotor);
    __HAL_TIM_CLEAR_FLAG(&htimx, TIM_FLAG_UPDATE); // 清除更新中断标志位
    return;
  }
}


int main(void) {
  StepperMotor_Init( // 初始化步进电机
    &BoomStepperMotor, // 大臂步进电机
    &htimx, // 使用定时器x
    TIM_CHANNEL_X, // 使用通道x输出PWM
    168000000, // 内部时钟为168MHz
    14-1, // 进行预分频，14分频，得到168MHz/14=12MHz的CNT计数频率
    4000-1, // 设置自动重装载值为4000，得到12MHz/4000=3kHz的PWM频率
    50, // 高电平占空比50%
    Dir_GPIO_Port, // 方向引脚端口
    Dir_Pin, // 方向引脚号
    GPIO_PIN_SET // 高电平为正转
  ); // 在CubeMX配置了PWM引脚为PB8

  while (1) {
    StepperMotor_MoveSteps(&BoomStepperMotor, -32, 20000); // 以20kHz的频率输出32个脉冲，转动方向为反方向
    while (StepperMotor_GetRunState(&BoomStepperMotor) == StepperMotor_RunState_MoveSteps); // 等待电机转动完成
    Delay_ms(1000); // 延时1秒

    StepperMotor_MoveSteps(&BoomStepperMotor, 20, 999); // 以999Hz的频率输出20个脉冲，转动方向为正方向
    while (StepperMotor_GetRunState(&BoomStepperMotor) == StepperMotor_RunState_MoveSteps); // 等待电机转动完成
    Delay_ms(1000); // 延时1秒

    StepperMotor_RunContinuous(&BoomStepperMotor, StepperMotor_Direction_Forward, 999); // 以999Hz的频率持续转动，方向为正方向
    Delay_ms(1000); // 延时1秒
    StepperMotor_Stop(&BoomStepperMotor); // 停止电机
    Delay_ms(1000); // 延时1秒

    StepperMotor_RunContinuous(&BoomStepperMotor, StepperMotor_Direction_Backward, 999); // 以999Hz的频率持续转动，方向为反方向
    Delay_ms(1000); // 延时1秒
    StepperMotor_Stop(&BoomStepperMotor); // 停止电机
    Delay_ms(1000); // 延时1秒
  }
}





```