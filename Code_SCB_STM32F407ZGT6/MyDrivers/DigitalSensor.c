#include "DigitalSensor.h"

/**
 * @brief 初始化数字传感器
 * @param cThis 数字传感器结构体指针
 * @param port 数字传感器所在的GPIO端口
 * @param pin 数字传感器所在的GPIO引脚
 * @param triglevel 数字传感器触发电平
 */
void DigitalSensor_Init(DigitalSensor_t *cThis, GPIO_TypeDef *port, uint16_t pin, GPIO_PinState triglevel) {
  if (cThis == NULL) return;
  cThis->Port = port;
  cThis->Pin = pin;
  cThis->TrigLevel = triglevel;
}

/**
 * @brief 更改数字传感器触发电平
 * @param cThis 数字传感器结构体指针
 * @param triglevel 触发电平
 */
void DigitalSensor_ChangeTrigLevel(DigitalSensor_t *cThis, GPIO_PinState triglevel) {
  if (cThis == NULL) return;
  cThis->TrigLevel = triglevel;
}

/**
 * @brief 获取数字传感器状态
 * @param cThis 数字传感器结构体指针
 * @return DigitalSensorState_t 类型的数字传感器状态
 *   @arg DigitalSensorState_Released 传感器释放状态（平常状态）
 *   @arg DigitalSensorState_Triggered 传感器触发状态（被触发状态）
 *   @arg DigitalSensorState_Invalid 无效状态
 */
DigitalSensorState_t DigitalSensor_GetState(DigitalSensor_t *cThis) {
  if (cThis == NULL) return DigitalSensorState_Invalid;
  GPIO_PinState gpio_state = HAL_GPIO_ReadPin(cThis->Port, cThis->Pin);
  if (gpio_state == cThis->TrigLevel) return DigitalSensorState_Triggered;
  else return DigitalSensorState_Released;
}

/**
 * @brief 判断数字传感器是否被触发
 * @param cThis 数字传感器结构体指针
 * @return true 传感器被触发，false 传感器未被触发
 */
bool DigitalSensor_IsTriggered(DigitalSensor_t *cThis) {
  if (cThis == NULL) return false;
  return (DigitalSensor_GetState(cThis) == DigitalSensorState_Triggered);
}

/**
 * @brief 判断数字传感器是否释放
 * @param cThis 数字传感器结构体指针
 * @return true 传感器释放，false 传感器未释放
 */
bool DigitalSensor_IsReleased(DigitalSensor_t *cThis) {
  if (cThis == NULL) return false;
  return (DigitalSensor_GetState(cThis) == DigitalSensorState_Released);
}
