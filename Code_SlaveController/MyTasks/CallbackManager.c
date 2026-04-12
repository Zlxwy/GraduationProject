#include "Task_All.h"

/*UART发送完成回调函数*/
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart) {
  if (huart->Instance == USART3) {
    UartDmaStream_FuncCalled_InTxCpltCallback(&gMainStream);
  }
}

void OnSignal0FallingEdge(void);
void OnSignal1FallingEdge(void);
void OnSignal2FallingEdge(void);
void OnSignal3FallingEdge(void);

/*GPIO中断回调函数*/
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
  switch (GPIO_Pin) {
    case SIG0_Pin: OnSignal0FallingEdge(); break;
    case SIG1_Pin: OnSignal1FallingEdge(); break;
    case SIG2_Pin: OnSignal2FallingEdge(); break;
    case SIG3_Pin: OnSignal3FallingEdge(); break;
  }
}





void OnSignal0FallingEdge(void) {
  ;
}

void OnSignal1FallingEdge(void) {
  ;
}

void OnSignal2FallingEdge(void) {
  ;
}

void OnSignal3FallingEdge(void) {
  if (IsLimitSwitchVerticalAxisExtiEnabled) { // 如果竖轴限位开关中断使能标志位为true
    StepperMotor_Stop(&gStepperMotorLift); // 竖轴步进电机停止持续运动
    IsLimitSwitchVerticalAxisExtiEnabled = false; // 竖轴限位开关中断使能标志位
  } // 这样做是为了防止电机在限位器处时意外被截停，只有使能了这个标志位，才允许电机被截停
}
