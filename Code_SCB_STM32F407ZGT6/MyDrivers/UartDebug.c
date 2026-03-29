#include "UartDebug.h"

/**
 * @brief  串口发送一个字节，阻塞方式。
 * @note   等待发送缓冲区为空，再发送。
 * @param  huart USART handle
 * @param  abyte 待发送的字节
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
 * @param  huart USART handle
 * @param  array 待发送的字节数组
 * @param  len 待发送的字节数组长度
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
 * @param  huart USART handle
 * @param  string 待发送的字符串
 * @retval None
 */
void uart_send_string(UART_HandleTypeDef *huart, char *string) {
  uart_send_array(huart, (uint8_t *)string, strlen(string));
}

/**
 * @brief  串口printf函数，用于向串口发送格式化字符串信息。
 * @note   最大长度为256字节。
 * @attention 这个函数不可以发送带有'\0'(0x00)的字节串
 * @param  huart USART handle
 * @param  format format string
 * @param  ... arguments list
 * @retval None
 */
#define USART_DATALEN_MAX  256
void uart_printf(UART_HandleTypeDef *huart, const char *format, ...) {
  if (huart == NULL || format == NULL) return;
  char SendBuf[USART_DATALEN_MAX];
  va_list args;
  va_start(args, format);
  int len = vsnprintf(SendBuf, sizeof(SendBuf), format, args);
  va_end(args);
  if (len < 0) return; // 检查是否发生截断

  // 发送格式化后的字符串
  uart_send_array(huart, (uint8_t *)SendBuf, (size_t)len);
}
