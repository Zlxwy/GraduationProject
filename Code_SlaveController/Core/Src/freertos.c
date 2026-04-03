/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * File Name          : freertos.c
  * Description        : Code for freertos applications
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
typedef StaticTask_t osStaticThreadDef_t;
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN Variables */

/* USER CODE END Variables */
/* Definitions for defaultTask */
osThreadId_t defaultTaskHandle;
uint32_t defaultTaskBuffer[ 128 ];
osStaticThreadDef_t defaultTaskControlBlock;
const osThreadAttr_t defaultTask_attributes = {
  .name = "defaultTask",
  .cb_mem = &defaultTaskControlBlock,
  .cb_size = sizeof(defaultTaskControlBlock),
  .stack_mem = &defaultTaskBuffer[0],
  .stack_size = sizeof(defaultTaskBuffer),
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for WriteWorkerTask */
osThreadId_t WriteWorkerTaskHandle;
uint32_t WriteWorkerTaskBuffer[ 256 ];
osStaticThreadDef_t WriteWorkerTaskControlBlock;
const osThreadAttr_t WriteWorkerTask_attributes = {
  .name = "WriteWorkerTask",
  .cb_mem = &WriteWorkerTaskControlBlock,
  .cb_size = sizeof(WriteWorkerTaskControlBlock),
  .stack_mem = &WriteWorkerTaskBuffer[0],
  .stack_size = sizeof(WriteWorkerTaskBuffer),
  .priority = (osPriority_t) osPriorityBelowNormal,
};
/* Definitions for ReadWorkerTask */
osThreadId_t ReadWorkerTaskHandle;
uint32_t ReadWorkerTaskBuffer[ 256 ];
osStaticThreadDef_t ReadWorkerTaskControlBlock;
const osThreadAttr_t ReadWorkerTask_attributes = {
  .name = "ReadWorkerTask",
  .cb_mem = &ReadWorkerTaskControlBlock,
  .cb_size = sizeof(ReadWorkerTaskControlBlock),
  .stack_mem = &ReadWorkerTaskBuffer[0],
  .stack_size = sizeof(ReadWorkerTaskBuffer),
  .priority = (osPriority_t) osPriorityBelowNormal,
};
/* Definitions for MotorActionTask */
osThreadId_t MotorActionTaskHandle;
uint32_t MotorActionTaskBuffer[ 256 ];
osStaticThreadDef_t MotorActionTaskControlBlock;
const osThreadAttr_t MotorActionTask_attributes = {
  .name = "MotorActionTask",
  .cb_mem = &MotorActionTaskControlBlock,
  .cb_size = sizeof(MotorActionTaskControlBlock),
  .stack_mem = &MotorActionTaskBuffer[0],
  .stack_size = sizeof(MotorActionTaskBuffer),
  .priority = (osPriority_t) osPriorityBelowNormal,
};

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN FunctionPrototypes */

/* USER CODE END FunctionPrototypes */

void StartDefaultTask(void *argument);
void WriteWorkerTaskFunc(void *argument);
void ReadWorkerTaskFunc(void *argument);
void MotorActionTaskFunc(void *argument);

void MX_FREERTOS_Init(void); /* (MISRA C 2004 rule 8.1) */

/**
  * @brief  FreeRTOS initialization
  * @param  None
  * @retval None
  */
void MX_FREERTOS_Init(void) {
  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of defaultTask */
  defaultTaskHandle = osThreadNew(StartDefaultTask, NULL, &defaultTask_attributes);

  /* creation of WriteWorkerTask */
  WriteWorkerTaskHandle = osThreadNew(WriteWorkerTaskFunc, NULL, &WriteWorkerTask_attributes);

  /* creation of ReadWorkerTask */
  ReadWorkerTaskHandle = osThreadNew(ReadWorkerTaskFunc, NULL, &ReadWorkerTask_attributes);

  /* creation of MotorActionTask */
  MotorActionTaskHandle = osThreadNew(MotorActionTaskFunc, NULL, &MotorActionTask_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

}

/* USER CODE BEGIN Header_StartDefaultTask */
/**
  * @brief  Function implementing the defaultTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_StartDefaultTask */
__weak void StartDefaultTask(void *argument)
{
  /* USER CODE BEGIN StartDefaultTask */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END StartDefaultTask */
}

/* USER CODE BEGIN Header_WriteWorkerTaskFunc */
/**
* @brief Function implementing the WriteWorkerTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_WriteWorkerTaskFunc */
__weak void WriteWorkerTaskFunc(void *argument)
{
  /* USER CODE BEGIN WriteWorkerTaskFunc */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END WriteWorkerTaskFunc */
}

/* USER CODE BEGIN Header_ReadWorkerTaskFunc */
/**
* @brief Function implementing the ReadWorkerTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_ReadWorkerTaskFunc */
__weak void ReadWorkerTaskFunc(void *argument)
{
  /* USER CODE BEGIN ReadWorkerTaskFunc */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END ReadWorkerTaskFunc */
}

/* USER CODE BEGIN Header_MotorActionTaskFunc */
/**
* @brief Function implementing the MotorActionTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_MotorActionTaskFunc */
__weak void MotorActionTaskFunc(void *argument)
{
  /* USER CODE BEGIN MotorActionTaskFunc */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END MotorActionTaskFunc */
}

/* Private application code --------------------------------------------------*/
/* USER CODE BEGIN Application */

/* USER CODE END Application */

