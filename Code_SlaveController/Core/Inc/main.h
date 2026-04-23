/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
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

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f4xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define LCD_TOUCH_CS_Pin GPIO_PIN_13
#define LCD_TOUCH_CS_GPIO_Port GPIOC
#define SIG0_Pin GPIO_PIN_0
#define SIG0_GPIO_Port GPIOF
#define SIG0_EXTI_IRQn EXTI0_IRQn
#define SIG1_Pin GPIO_PIN_1
#define SIG1_GPIO_Port GPIOF
#define SIG1_EXTI_IRQn EXTI1_IRQn
#define SIG2_Pin GPIO_PIN_2
#define SIG2_GPIO_Port GPIOF
#define SIG2_EXTI_IRQn EXTI2_IRQn
#define SIG3_Pin GPIO_PIN_3
#define SIG3_GPIO_Port GPIOF
#define SIG3_EXTI_IRQn EXTI3_IRQn
#define KEY0_Pin GPIO_PIN_4
#define KEY0_GPIO_Port GPIOF
#define KEY1_Pin GPIO_PIN_5
#define KEY1_GPIO_Port GPIOF
#define KEY2_Pin GPIO_PIN_6
#define KEY2_GPIO_Port GPIOF
#define KEY3_Pin GPIO_PIN_7
#define KEY3_GPIO_Port GPIOF
#define LED0_Pin GPIO_PIN_9
#define LED0_GPIO_Port GPIOF
#define LED1_Pin GPIO_PIN_10
#define LED1_GPIO_Port GPIOF
#define L298N_IN1_Pin GPIO_PIN_4
#define L298N_IN1_GPIO_Port GPIOA
#define L298N_ENA_Pin GPIO_PIN_5
#define L298N_ENA_GPIO_Port GPIOA
#define L298N_ENB_Pin GPIO_PIN_6
#define L298N_ENB_GPIO_Port GPIOA
#define L298N_IN2_Pin GPIO_PIN_7
#define L298N_IN2_GPIO_Port GPIOA
#define L298N_IN3_Pin GPIO_PIN_4
#define L298N_IN3_GPIO_Port GPIOC
#define L298N_IN4_Pin GPIO_PIN_5
#define L298N_IN4_GPIO_Port GPIOC
#define LCD_TOUCH_SCK_Pin GPIO_PIN_0
#define LCD_TOUCH_SCK_GPIO_Port GPIOB
#define LCD_TOUCH_PEN_Pin GPIO_PIN_1
#define LCD_TOUCH_PEN_GPIO_Port GPIOB
#define LCD_TOUCH_MISO_Pin GPIO_PIN_2
#define LCD_TOUCH_MISO_GPIO_Port GPIOB
#define LCD_TOUCH_MOSI_Pin GPIO_PIN_11
#define LCD_TOUCH_MOSI_GPIO_Port GPIOF
#define LCD_FSMC_A6_Pin GPIO_PIN_12
#define LCD_FSMC_A6_GPIO_Port GPIOF
#define LCD_FSMC_D4_Pin GPIO_PIN_7
#define LCD_FSMC_D4_GPIO_Port GPIOE
#define LCD_FSMC_D5_Pin GPIO_PIN_8
#define LCD_FSMC_D5_GPIO_Port GPIOE
#define LCD_FSMC_D6_Pin GPIO_PIN_9
#define LCD_FSMC_D6_GPIO_Port GPIOE
#define LCD_FSMC_D7_Pin GPIO_PIN_10
#define LCD_FSMC_D7_GPIO_Port GPIOE
#define LCD_FSMC_D8_Pin GPIO_PIN_11
#define LCD_FSMC_D8_GPIO_Port GPIOE
#define LCD_FSMC_D9_Pin GPIO_PIN_12
#define LCD_FSMC_D9_GPIO_Port GPIOE
#define LCD_FSMC_D10_Pin GPIO_PIN_13
#define LCD_FSMC_D10_GPIO_Port GPIOE
#define LCD_FSMC_D11_Pin GPIO_PIN_14
#define LCD_FSMC_D11_GPIO_Port GPIOE
#define LCD_FSMC_D12_Pin GPIO_PIN_15
#define LCD_FSMC_D12_GPIO_Port GPIOE
#define MainStream_TX_Pin GPIO_PIN_10
#define MainStream_TX_GPIO_Port GPIOB
#define MainStream_RX_Pin GPIO_PIN_11
#define MainStream_RX_GPIO_Port GPIOB
#define LCD_BL_Pin GPIO_PIN_15
#define LCD_BL_GPIO_Port GPIOB
#define LCD_FSMC_D13_Pin GPIO_PIN_8
#define LCD_FSMC_D13_GPIO_Port GPIOD
#define LCD_FSMC_D14_Pin GPIO_PIN_9
#define LCD_FSMC_D14_GPIO_Port GPIOD
#define LCD_FSMC_D15_Pin GPIO_PIN_10
#define LCD_FSMC_D15_GPIO_Port GPIOD
#define LCD_FSMC_D0_Pin GPIO_PIN_14
#define LCD_FSMC_D0_GPIO_Port GPIOD
#define LCD_FSMC_D1_Pin GPIO_PIN_15
#define LCD_FSMC_D1_GPIO_Port GPIOD
#define LCD_FSMC_D2_Pin GPIO_PIN_0
#define LCD_FSMC_D2_GPIO_Port GPIOD
#define LCD_FSMC_D3_Pin GPIO_PIN_1
#define LCD_FSMC_D3_GPIO_Port GPIOD
#define LCD_FSMC_NOE_Pin GPIO_PIN_4
#define LCD_FSMC_NOE_GPIO_Port GPIOD
#define LCD_FSMC_NWE_Pin GPIO_PIN_5
#define LCD_FSMC_NWE_GPIO_Port GPIOD
#define LCD_FSMC_NE4_Pin GPIO_PIN_12
#define LCD_FSMC_NE4_GPIO_Port GPIOG
#define StepperMotorShoulder_Pul_Pin GPIO_PIN_4
#define StepperMotorShoulder_Pul_GPIO_Port GPIOB
#define StepperMotorShoulder_Dir_Pin GPIO_PIN_5
#define StepperMotorShoulder_Dir_GPIO_Port GPIOB
#define StepperMotorElbow_Dir_Pin GPIO_PIN_6
#define StepperMotorElbow_Dir_GPIO_Port GPIOB
#define StepperMotorLift_Dir_Pin GPIO_PIN_7
#define StepperMotorLift_Dir_GPIO_Port GPIOB
#define StepperMotorElbow_Pul_Pin GPIO_PIN_8
#define StepperMotorElbow_Pul_GPIO_Port GPIOB
#define StepperMotorLift_Pul_Pin GPIO_PIN_9
#define StepperMotorLift_Pul_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
