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
#include "gpio.h"
#include "fsmc.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "LCD.h"
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
  MX_FSMC_Init();
  /* USER CODE BEGIN 2 */
  LCD_Init();//初始化LCD FSMC接口
  
  //行间隔像素：
  //12->12（14像素）、12->16（14像素）、12->24（12像素）
  //16->12（18像素）、16->16（18像素）、16->24（16像素）
  //24->12（26像素）、24->16（24像素）、24->24（26像素）
  
  /**字符串显示测试**/
  POINT_COLOR=RED;//画笔颜色
  LCD_ShowString(5,9,12,"/******Display String Test*******/");
  POINT_COLOR=BLACK;
  LCD_ShowString(5,21,24,"STM32F407ZGT6");
  LCD_ShowString(5,45,16,"TFTLCD TEST");
  
  
  /**数字显示测试**/
  POINT_COLOR=RED;
  LCD_ShowString(5,63,12,"/******Display Number Test*******/");
  POINT_COLOR=PURPLE;
  LCD_ShowxNum(5,77,16,12345678,12);
  LCD_ShowNum(5,95,16,12345678,12);
  LCD_ShowHexNum(5,113,16,0x6735,5);
  LCD_ShowBinNum(5,131,16,0x567/*0101 0110 0111*/,15);
  LCD_ShowSignedNum(5,149,16,-1269,6);
  LCD_ShowSignedNum(5,167,16,+12,6);
  LCD_ShowSignedNum(5,185,16,0,6);
  
  
  /**颜色填充测试**/
  POINT_COLOR=RED;
  LCD_ShowString(5,203,12,"/******Display Color Test*******/");
  uint16_t color[9]={WHITE,BLACK,RED,ORANGE,YELLOW,GREEN,BLUE,INDIGO,PURPLE};
  for(uint8_t i=0;i<9;i++)
  {
    if(i==0)
      POINT_COLOR=BLACK,
      LCD_DrawRectangle(5+i*25,220,25+i*25,240);//因为背景色是白色，填充白色是看不见的，所以如果填充色是白色，就画一个黑色的矩形框就行
    else
      POINT_COLOR=color[i],
      LCD_FillRectangle(5+i*25,220,25+i*25,240);//如果填充色是其他颜色，就直接填充一个矩形显示出来
  }
  
  
  // /**汉字显示测试**/
  POINT_COLOR=RED;
  LCD_ShowString(5,243,12,"/******Display Chinese Test******/");
  POINT_COLOR=BLACK;
  LCD_CNSTRING40(5,257,"杨登杰");
  LCD_CNSTRING16(125,259,"细雪飘落长街");
  LCD_CNSTRING16(125,277,"枫叶红透又一年");
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  OutputPF(9) = GPIO_PIN_RESET;
  OutputPF(10) = GPIO_PIN_RESET;
  OutputPB(15) = GPIO_PIN_RESET;

  while (1)
  {
    #include "GpioBitBanding.h"
    OutputPF(9) = !OutputPF(9);
    OutputPF(10) = !OutputPF(10);
    OutputPB(15) = !OutputPB(15);
    HAL_Delay(200);
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
