#include "Task_All.h"

/*UART发送完成回调函数*/
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
  if (huart->Instance == USART3) {
    UartDmaStream_FuncCalled_InTxCpltCallback(&gMainStream);
  }
}

void OnLimitSwitchSignal0Trigger(void);
void OnLimitSwitchSignal1Trigger(void);
void OnLimitSwitchSignal2Trigger(void);
void OnLimitSwitchSignal3Trigger(void);

/*GPIO中断回调函数*/
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
  switch (GPIO_Pin) {
    case SIG0_Pin: OnLimitSwitchSignal0Trigger(); break;
    case SIG1_Pin: OnLimitSwitchSignal1Trigger(); break;
    case SIG2_Pin: OnLimitSwitchSignal2Trigger(); break;
    case SIG3_Pin: OnLimitSwitchSignal3Trigger(); break;
  }
}

void OnLimitSwitchSignal0Trigger(void) {
  ;
}

void OnLimitSwitchSignal1Trigger(void) {
  ;
}

void OnLimitSwitchSignal2Trigger(void) {
  ;
}

void OnLimitSwitchSignal3Trigger(void) {
  // DigitalOutput_ToggleState(&gLED0);
  // DigitalOutput_ToggleState(&gLED1);
  if (IsLimitSwitchVerticalAxisExtiEnabled) { // 如果竖轴限位开关中断使能标志位为true
    StepperMotor_Stop(&gStepperMotorLift); // 竖轴步进电机停止持续运动
    IsLimitSwitchVerticalAxisExtiEnabled = false; // 竖轴限位开关中断使能标志位
  }
}
