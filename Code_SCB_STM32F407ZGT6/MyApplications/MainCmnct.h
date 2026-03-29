#ifndef __MAIN_CMNCT_H__
#define __MAIN_CMNCT_H__

#include "stm32f4xx_hal.h"
#include "main.h"
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#include "UartStream.h"
#include "DigitalOutput.h"
#include "StepperMotor.h"

extern TIM_HandleTypeDef htim10;

extern volatile bool IsMainCmnctTaskInitOkay;

extern UartStream_t gMainCmnctStream; // 主通信流对象

typedef enum {
  CommandType_MotorAction = 0x0000
} CommandType_e;

#endif
