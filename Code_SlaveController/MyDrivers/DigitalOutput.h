#ifndef __DIGITAL_OUTPUT_H__
#define __DIGITAL_OUTPUT_H__

#include "stm32f4xx_hal.h"
#include "main.h"
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct {
  GPIO_TypeDef *Port; // 数字输出连接的GPIO端口
  uint16_t Pin; // 数字输出连接的GPIO引脚
  GPIO_PinState ActiveLevel; // 数字输出激活时的GPIO电平
} DigitalOutput_t;

typedef enum {
  DigitalOutputState_Active, // 数字输出激活状态
  DigitalOutputState_Inactive, // 数字输出非激活状态
  DigitalOutputState_Invalid, // 无效状态
} DigitalOutputState_t;

void DigitalOutput_Init(DigitalOutput_t *cThis, GPIO_TypeDef *port, uint16_t pin, GPIO_PinState activelevel); // 初始化数字输出
void DigitalOutput_SetState(DigitalOutput_t *cThis, DigitalOutputState_t state); // 设置数字输出状态
void DigitalOutput_ToggleState(DigitalOutput_t *cThis); // 切换数字输出状态

#endif // #ifndef __DIGITAL_OUTPUT_H__
