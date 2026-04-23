#include "DigitalOutput.h"

/**
 * @brief 初始化数字输出
 * @param cThis 数字输出对象指针
 * @param port 数字输出连接的GPIO端口
 * @param pin 数字输出连接的GPIO引脚
 * @param activelevel 数字输出激活时的GPIO电平
 */
void DigitalOutput_Init(DigitalOutput_t *cThis, GPIO_TypeDef *port, uint16_t pin, GPIO_PinState activelevel) {
  if (cThis == NULL) return;
  cThis->Port = port;
  cThis->Pin = pin;
  cThis->ActiveLevel = activelevel;
}

/**
 * @brief 设置数字输出状态
 * @param cThis 数字输出对象指针
 * @param state 数字输出状态
 */
void DigitalOutput_SetState(DigitalOutput_t *cThis, DigitalOutputState_t state) {
  if (cThis == NULL) return;
  GPIO_PinState ActiveLevel = cThis->ActiveLevel;
  GPIO_PinState InactiveLevel = (ActiveLevel == GPIO_PIN_RESET) ? (GPIO_PIN_SET) : (GPIO_PIN_RESET);
  HAL_GPIO_WritePin(
    cThis->Port, cThis->Pin,
    (state == DigitalOutputState_Active) ? (ActiveLevel) : (InactiveLevel)
  );
}

void DigitalOutput_ToggleState(DigitalOutput_t *cThis) {
  if (cThis == NULL) return;
  HAL_GPIO_TogglePin(cThis->Port, cThis->Pin);
}
