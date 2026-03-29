/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * File Name          : freertos.c
  * Description        : Code for freertos applications
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
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
/* Definitions for BlinkLED0Task */
osThreadId_t BlinkLED0TaskHandle;
uint32_t BlinkLED0TaskBuffer[ 128 ];
osStaticThreadDef_t BlinkLED0TaskControlBlock;
const osThreadAttr_t BlinkLED0Task_attributes = {
  .name = "BlinkLED0Task",
  .cb_mem = &BlinkLED0TaskControlBlock,
  .cb_size = sizeof(BlinkLED0TaskControlBlock),
  .stack_mem = &BlinkLED0TaskBuffer[0],
  .stack_size = sizeof(BlinkLED0TaskBuffer),
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for BlinkLED1Task */
osThreadId_t BlinkLED1TaskHandle;
uint32_t BlinkLED1TaskBuffer[ 128 ];
osStaticThreadDef_t BlinkLED1TaskControlBlock;
const osThreadAttr_t BlinkLED1Task_attributes = {
  .name = "BlinkLED1Task",
  .cb_mem = &BlinkLED1TaskControlBlock,
  .cb_size = sizeof(BlinkLED1TaskControlBlock),
  .stack_mem = &BlinkLED1TaskBuffer[0],
  .stack_size = sizeof(BlinkLED1TaskBuffer),
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for UartTestTask */
osThreadId_t UartTestTaskHandle;
uint32_t UartTestTaskBuffer[ 128 ];
osStaticThreadDef_t UartTestTaskControlBlock;
const osThreadAttr_t UartTestTask_attributes = {
  .name = "UartTestTask",
  .cb_mem = &UartTestTaskControlBlock,
  .cb_size = sizeof(UartTestTaskControlBlock),
  .stack_mem = &UartTestTaskBuffer[0],
  .stack_size = sizeof(UartTestTaskBuffer),
  .priority = (osPriority_t) osPriorityNormal,
};

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN FunctionPrototypes */

/* USER CODE END FunctionPrototypes */

void MainCmnctTaskFunc(void *argument);
void BlinkLED0TaskFunc(void *argument);
void BlinkLED1TaskFunc(void *argument);
void UartTestTaskFunc(void *argument);

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
  defaultTaskHandle = osThreadNew(MainCmnctTaskFunc, NULL, &defaultTask_attributes);

  /* creation of BlinkLED0Task */
  BlinkLED0TaskHandle = osThreadNew(BlinkLED0TaskFunc, NULL, &BlinkLED0Task_attributes);

  /* creation of BlinkLED1Task */
  BlinkLED1TaskHandle = osThreadNew(BlinkLED1TaskFunc, NULL, &BlinkLED1Task_attributes);

  /* creation of UartTestTask */
  UartTestTaskHandle = osThreadNew(UartTestTaskFunc, NULL, &UartTestTask_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

}

/* USER CODE BEGIN Header_MainCmnctTaskFunc */
/**
  * @brief  Function implementing the defaultTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_MainCmnctTaskFunc */
__weak void MainCmnctTaskFunc(void *argument)
{
  /* USER CODE BEGIN MainCmnctTaskFunc */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END MainCmnctTaskFunc */
}

/* USER CODE BEGIN Header_BlinkLED0TaskFunc */
/**
* @brief Function implementing the BlinkLED0Task thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_BlinkLED0TaskFunc */
__weak void BlinkLED0TaskFunc(void *argument)
{
  /* USER CODE BEGIN BlinkLED0TaskFunc */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END BlinkLED0TaskFunc */
}

/* USER CODE BEGIN Header_BlinkLED1TaskFunc */
/**
* @brief Function implementing the BlinkLED1Task thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_BlinkLED1TaskFunc */
__weak void BlinkLED1TaskFunc(void *argument)
{
  /* USER CODE BEGIN BlinkLED1TaskFunc */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END BlinkLED1TaskFunc */
}

/* USER CODE BEGIN Header_UartTestTaskFunc */
/**
* @brief Function implementing the UartTestTask thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_UartTestTaskFunc */
__weak void UartTestTaskFunc(void *argument)
{
  /* USER CODE BEGIN UartTestTaskFunc */
  /* Infinite loop */
  for(;;)
  {
    osDelay(1);
  }
  /* USER CODE END UartTestTaskFunc */
}

/* Private application code --------------------------------------------------*/
/* USER CODE BEGIN Application */

/* USER CODE END Application */

