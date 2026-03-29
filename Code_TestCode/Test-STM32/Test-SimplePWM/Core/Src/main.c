/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
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
#include "main.h"
#include "tim.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "StepperMotor.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
StepperMotor_t BoomStepperMotor;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM10_Init();
  MX_TIM11_Init();
  MX_TIM13_Init();
  MX_TIM14_Init();
  /* USER CODE BEGIN 2 */
  StepperMotor_Init( // 初始化步进电机
    &BoomStepperMotor, // 大臂步进电机
    &htim10, // 使用定时器10
    TIM_CHANNEL_1, // 使用通道1输出PWM
    168000000, // 内部时钟为168MHz
    14-1, // 进行预分频，14分频，得到168MHz/14=12MHz的CNT计数频率
    4000-1, // 设置自动重装载值为4000，得到12MHz/4000=3kHz的PWM频率
    50, // 高电平占空比50%
    TestDir_GPIO_Port, // 方向引脚端口
    TestDir_Pin, // 方向引脚号
    GPIO_PIN_SET // 高电平为正转
  ); // 在CubeMX配置了PWM引脚为PB8
  HAL_Delay(1000);
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  // int32_t pulses = 200;
  // uint32_t tone[] = {523, 587, 659, 698, 784, 880, 988, 1047};
  while (1)
  {
    // for (int i=0; i<sizeof(tone)/sizeof(tone[0]); i++) {
    //   StepperMotor_MoveSteps(&BoomStepperMotor, pulses, tone[i]); // Object, steps, speed
    //   while (StepperMotor_GetRunState(&BoomStepperMotor) == StepperMotor_RunState_MoveSteps);
    //   HAL_Delay(500); // 等待1秒
    //   HAL_GPIO_TogglePin(TestLED_GPIO_Port, TestLED_Pin);
    // }
    StepperMotor_MoveSteps(&BoomStepperMotor, 800, 1555); // Object, steps, speed
    while (StepperMotor_GetRunState(&BoomStepperMotor) == StepperMotor_RunState_MoveSteps);
    HAL_Delay(500); // 等待1秒
    StepperMotor_MoveSteps(&BoomStepperMotor, -200, 999); // Object, steps, speed
    while (StepperMotor_GetRunState(&BoomStepperMotor) == StepperMotor_RunState_MoveSteps);
    HAL_Delay(500); // 等待1秒

    StepperMotor_RunContinuous(&BoomStepperMotor, StepperMotor_Direction_Forward, 600); // 以999Hz的频率持续转动，方向为正方向
    HAL_Delay(1000); // 延时1秒
    StepperMotor_Stop(&BoomStepperMotor); // 停止电机
    HAL_Delay(1000); // 延时1秒

    StepperMotor_RunContinuous(&BoomStepperMotor, StepperMotor_Direction_Backward, 999); // 以999Hz的频率持续转动，方向为反方向
    HAL_Delay(1000); // 延时1秒
    StepperMotor_Stop(&BoomStepperMotor); // 停止电机
    HAL_Delay(1000); // 延时1秒
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 4;
  RCC_OscInitStruct.PLL.PLLN = 168;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
