#ifndef __DIGITAL_SENSOR_H__
#define __DIGITAL_SENSOR_H__

#include "stm32f4xx_hal.h"
#include "main.h"
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

typedef enum {
  DigitalInputState_Released, // 传感器释放状态（平常状态）
  DigitalInputState_Triggered, // 传感器触发状态（被触发状态）
  DigitalInputState_Invalid, // 无效状态
} DigitalInputState_t;

typedef struct {
  GPIO_TypeDef *Port; // 传感器连接的GPIO端口
  uint16_t Pin; // 传感器连接的GPIO引脚
  GPIO_PinState TrigLevel; // 传感器被触发时的GPIO电平
} DigitalInput_t;

void DigitalInput_Init(DigitalInput_t *cThis, GPIO_TypeDef *port, uint16_t pin, GPIO_PinState triglevel); // 初始化传感器
void DigitalInput_ChangeTrigLevel(DigitalInput_t *cThis, GPIO_PinState triglevel); // 改变传感器触发电平
DigitalInputState_t DigitalInput_GetState(DigitalInput_t *cThis); // 获取传感器状态
bool DigitalInput_IsTriggered(DigitalInput_t *cThis); // 判断传感器是否被触发
bool DigitalInput_IsReleased(DigitalInput_t *cThis); // 判断传感器是否释放

#endif // #ifndef __DIGITAL_SENSOR_H__
