#include "Task_All.h"

void BlinkLED0TaskFunc(void *argument) {
  while (!IsMainCmnctTaskInitOkay) osDelay(pdMS_TO_TICKS(10));

  while (true) {
    // HAL_GPIO_TogglePin(LED0_GPIO_Port, LED0_Pin);
    osDelay(pdMS_TO_TICKS(500));
  }
}

void BlinkLED1TaskFunc(void *argument) {
  while (!IsMainCmnctTaskInitOkay) osDelay(pdMS_TO_TICKS(10));

  while (true) {
    // HAL_GPIO_TogglePin(LED1_GPIO_Port, LED1_Pin);
    osDelay(pdMS_TO_TICKS(200));
  }
}
