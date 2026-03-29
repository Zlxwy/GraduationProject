#ifndef __UART_DEBUG_H__
#define __UART_DEBUG_H__

#include "stm32f4xx_hal.h"
#include "main.h"
#include <stdarg.h>
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

void uart_send_byte_blocking(UART_HandleTypeDef *huart, uint8_t abyte);
void uart_printf(UART_HandleTypeDef *huart, const char *format, ...);

#endif
