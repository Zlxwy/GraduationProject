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
#include "dma.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */

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
/**
 * @brief  串口发送一个字节，阻塞方式。
 * @note   等待发送缓冲区为空，再发送。
 * @param  huart: USART handle
 * @param  abyte: 待发送的字节
 * @retval None
 */
void uart_send_byte_blocking(UART_HandleTypeDef *huart, uint8_t abyte) {
  while ( !__HAL_UART_GET_FLAG(huart, UART_FLAG_TXE) ); // TX不为空，则持续循环
  huart->Instance->DR = abyte; // TX为空了，则跳出以上while循环发送字节
}

/**
 * @brief  串口发送一个字节数组，阻塞方式。
 * @note   等待发送缓冲区为空，再发送。
 * @attention 这个函数可以发送带有'\0'(0x00)的字节串
 * @param  huart: USART handle
 * @param  array: 待发送的字节数组
 * @param  len: 待发送的字节数组长度
 * @retval None
 */
void uart_send_array(UART_HandleTypeDef *huart, uint8_t *array, size_t len) {
  for (size_t i=0; i<len; i++) {
    uart_send_byte_blocking(huart, array[i]);
  }
}

/**
 * @brief  串口发送一个字符串，阻塞方式。
 * @note   等待发送缓冲区为空，再发送。
 * @attention 这个函数不可以发送带有'\0'(0x00)的字节串
 * @param  huart: USART handle
 * @param  string: 待发送的字符串
 * @retval None
 */
void uart_send_string(UART_HandleTypeDef *huart, char *string) {
  uart_send_array(huart, (uint8_t *)string, strlen(string));
}

/**
 * @brief  串口printf函数，用于向串口发送格式化字符串信息。
 * @note   最大长度为128字节。
 * @attention 这个函数不可以发送带有'\0'(0x00)的字节串
 * @param  huart: USART handle
 * @param  format: format string
 * @param  ...: arguments list
 * @retval None
 */
#define USART_DATALEN_MAX  256
void uart_printf(UART_HandleTypeDef *huart, char *format, ...) {
  char SendBuf[USART_DATALEN_MAX];
  va_list args;
  va_start(args, format);
  vsnprintf(SendBuf, sizeof(SendBuf), format, args);
  va_end(args);
  for (uint16_t i=0; SendBuf[i]!='\0'; i++) {
    uart_send_byte_blocking(huart, SendBuf[i]);
  }
}

UartIdleDmaRx_t ttUIDR; // 串口空闲中断DMA接收的结构体实例
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
  MX_DMA_Init();
  MX_USART3_UART_Init();
  /* USER CODE BEGIN 2 */
  UartIdleDmaRx_Init(&ttUIDR, &huart3, &hdma_usart3_rx); // 初始化串口空闲中断DMA接收
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1) {
    if ( UartIdleDmaRx_GetRecvFlag(&ttUIDR) ) { // 获取是否接收数据标志位
      uart_printf(&huart3, "rx_count: %d\r\nrx_data: %s",
        UartIdleDmaRx_GetRecvLen(&ttUIDR), // 获取接收的字节数
        UartIdleDmaRx_GetRecvBuf(&ttUIDR) // 获取接收的字节数组
      ); // 因为在接收完成后，补了个结束符'\0'，所以可以直接打印字符串
      uart_printf(&huart3, "\r\n");
    }
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
