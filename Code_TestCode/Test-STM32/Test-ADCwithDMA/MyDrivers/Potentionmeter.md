* [STM32CubeMX配置](#stm32cubemx配置)
* [代码使用示例](#代码使用示例)

## STM32CubeMX配置

- Pinout & Configuration
  - Analog: <u>ADC1</u>
    - Mode
      * IN0: <u>Checked</u>
      * IN1: <u>Checked</u>
      * IN2: <u>Checked</u>
      * IN3: <u>Checked</u>
    - Configuration
      - Parameter Settings
        - ADCs_Common_Settings
          * Mode: <u>Independent mode</u>
        - ADCC_Settings
          * Clock Prescaler: <u>PCLK2 divided by 4</u>
          * Resolution: <u>12 bits (15 ADC Clock cycles)</u>
          * Data Alignment: <u>Right alignment</u>
          * Scan Conversion Mode: <u>Enabled</u>
          * Continuous Conversion Mode: <u>Enabled</u>
          * Discontinuous Conversion Mode: <u>Disabled</u>
          * DMA Continuous Request: <u>Enabled</u>
          * End Of Conversion Selection: <u>EOC flag at the end of single channel conversion</u>
        - ADC_Regular_ConversionMode
          * Number Of Conversion: <u>4</u>
          * External Trigger Conversion Source: <u>Regular Conversion launched by software</u>
          * External Trigger Conversion Edge: <u>None</u>
          - Rank: <u>1</u>
            * Channel: <u>Channel 0</u>
            * Sampling Time: <u>3 Cycles</u>
          - Rank: <u>2</u>
            * Channel: <u>Channel 1</u>
            * Sampling Time: <u>3 Cycles</u>
          - Rank: <u>3</u>
            * Channel: <u>Channel 2</u>
            * Sampling Time: <u>3 Cycles</u>
          - Rank: <u>4</u>
            * Channel: <u>Channel 3</u>
            * Sampling Time: <u>3 Cycles</u>
        - ADC_Injected_ConversionMode
          * Number Of Conversion: <u>0</u>
        - WatchDog
          * Enable Analog Watchdog Mode: <u>Unchecked</u>
      - DMA Settings
        * DMA Request: <u>ADC1</u>
        * Stream: <u>DMA2 Stream 0</u>
        * Direction: <u>Peripheral To Memory</u>
        * Priority: <u>Medium</u>
        - DMA Request Settings
          * Mode: <u>Circular</u>
          * Peripheral Increment: <u>Unchecked</u>
          * Memory Increment: <u>Checked</u>
          * Use Fifo: <u>Unchecked</u>
          * Peripheral Data Width: <u>Word</u>
          * Memory Data Width: <u>Word</u>



## 代码使用示例
```c
#include "Potentionmeter.h"

Potentionmeter_t LeftStick_Y; // 这个方向上的摇杆连接了PA0(ADC1_IN0)
Potentionmeter_t LeftStick_X; // 这个方向上的摇杆连接了PA1(ADC1_IN1)
Potentionmeter_t RightStick_Y; // 这个方向上的摇杆连接了PA2(ADC1_IN2)
Potentionmeter_t RightStick_X; // 这个方向上的摇杆连接了PA3(ADC1_IN3)

int main(void) {
  HAL_ADC_Start_DMA(&hadc1, (uint32_t*)ADC_ConvValue, 4); // 第一步必须要先把这个打开，打开后才能初始化

  /*电位器对象，ADC数组索引，参考电压，转换最小值，转换最大值，回中飘动最小值，回中飘动最大值*/
  Potentionmeter_Init(&LeftStick_Y, 0, 3.3f, 0, 4095, 1900, 2200);
  Potentionmeter_Init(&LeftStick_X, 1, 3.3f, 0, 4095, 1900, 2200);
  Potentionmeter_Init(&RightStick_Y, 2, 3.3f, 0, 4095, 1900, 2200);
  Potentionmeter_Init(&RightStick_X, 3, 3.3f, 0, 4095, 1900, 2200);

  while (1) {
    printf("LeftStick_Y: %4d, LeftStick_X: %4d, RightStick_Y: %4d, RightStick_X: %4d\n",
      Potentionmeter_GetConvValue(&LeftStick_Y), 
      Potentionmeter_GetConvValue(&LeftStick_X), 
      Potentionmeter_GetConvValue(&RightStick_Y), 
      Potentionmeter_GetConvValue(&RightStick_X)
    ); // 显示原始转换值，范围[0,4095]

    printf("LeftStick_Y: %1.2fV, LeftStick_X: %1.2fV, RightStick_Y: %1.2fV, RightStick_X: %1.2fV\n",
      Potentionmeter_GetVoltage(&LeftStick_Y), 
      Potentionmeter_GetVoltage(&LeftStick_X), 
      Potentionmeter_GetVoltage(&RightStick_Y), 
      Potentionmeter_GetVoltage(&RightStick_X)
    ); // 显示电压值，范围[0,3.3]

    printf("LeftStick_Y: %3.2f%%, LeftStick_X: %3.2f%%, RightStick_Y: %3.2f%%, RightStick_X: %3.2f%%\n",
      Potentionmeter_GetPosition(&LeftStick_Y) * 100.0f, 
      Potentionmeter_GetPosition(&LeftStick_X) * 100.0f, 
      Potentionmeter_GetPosition(&RightStick_Y) * 100.0f, 
      Potentionmeter_GetPosition(&RightStick_X) * 100.0f
    ); // 显示比例值，范围[-1,1]

    printf("\r\n");
    HAL_Delay(200);
  }
}
```