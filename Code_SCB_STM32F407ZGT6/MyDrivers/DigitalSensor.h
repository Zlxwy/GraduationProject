#ifndef __DIGITAL_SENSOR_H__
#define __DIGITAL_SENSOR_H__

#include "stm32f4xx_hal.h"
#include "main.h"
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
  DigitalSensorState_Released, // 传感器释放状态（平常状态）
  DigitalSensorState_Triggered, // 传感器触发状态（被触发状态）
  DigitalSensorState_Invalid, // 无效状态
} DigitalSensorState_t;

typedef struct {
  GPIO_TypeDef *Port; // 传感器连接的GPIO端口
  uint16_t Pin; // 传感器连接的GPIO引脚
  GPIO_PinState TrigLevel; // 传感器被触发时的GPIO电平
} DigitalSensor_t;

void DigitalSensor_Init(DigitalSensor_t *cThis, GPIO_TypeDef *port, uint16_t pin, GPIO_PinState triglevel); // 初始化传感器
void DigitalSensor_ChangeTrigLevel(DigitalSensor_t *cThis, GPIO_PinState triglevel); // 改变传感器触发电平
DigitalSensorState_t DigitalSensor_GetState(DigitalSensor_t *cThis); // 获取传感器状态

bool DigitalSensor_IsTriggered(DigitalSensor_t *cThis); // 判断传感器是否被触发
bool DigitalSensor_IsReleased(DigitalSensor_t *cThis); // 判断传感器是否释放

#endif // #ifndef __DIGITAL_SENSOR_H__
