#ifndef __TASK_ALL_H__
#define __TASK_ALL_H__

/*C语言标准库头文件*/
#include <stdio.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/*芯片平台、FreeRTOS头文件*/
#include "stm32f4xx_hal.h"
#include "FreeRTOS.h"
#include "cmsis_os.h"
#include "queue.h"
#include "task.h"
#include "main.h"

/*自定义头文件*/
#include "UartDmaStream.h"

extern UART_HandleTypeDef huart3;
extern DMA_HandleTypeDef hdma_usart3_rx;
extern DMA_HandleTypeDef hdma_usart3_tx;

extern volatile bool IsAllInitOkay;
extern UartDmaStream_t gMainStream;
extern uint8_t gFrameBuffer[256]; // 用来接收一帧一帧数据的缓冲区

/*以下这些任务线程函数，其实在freertos.c中是声明过的，这里再重复声明一下，是为了方便在其他文件中调用*/
void WriteWorkerTaskFunc(void *argument); // 写入工作线程
void ReadWorkerTaskFunc(void *argument); // 读取工作线程

#endif
