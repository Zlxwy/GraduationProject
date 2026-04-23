#ifndef __POTENTIONMETER_H__
#define __POTENTIONMETER_H__

#include "stm32f4xx_hal.h"
#include "main.h"

extern uint32_t ADC_ConvValue[4];

typedef struct {
  uint32_t* ConvValueAddr; // 转换值的指针，随时随地可读取
  float RefVoltage; // 参考电压
  uint32_t ConvValueMax; // 转换最大值
  uint32_t ConvValueMin; // 转换最小值
  uint32_t CenterValueDriftMax; // 中心值最大漂移，该值需要在电位器回中时调用Potentionmeter_GetCenterValueRange函数获取
  uint32_t CenterValueDriftMin; // 中心值最小漂移，该值需要在电位器回中时调用Potentionmeter_GetCenterValueRange函数获取
} Potentionmeter_t;

void Potentionmeter_Init(Potentionmeter_t *cThis,
                        uint32_t ConvValueIndex,
                        float RefVoltage,
                        uint32_t ConvValueMin,
                        uint32_t ConvValueMax,
                        uint32_t CenterValueDriftMin,
                        uint32_t CenterValueDriftMax );
void Potentionmeter_AutoCenterValueRange(Potentionmeter_t *cThis);
void Potentionmeter_SetCenterValueRange(Potentionmeter_t *cThis, uint32_t CenterValueDriftMin, uint32_t CenterValueDriftMax);

uint32_t Potentionmeter_GetConvValue(Potentionmeter_t *cThis);
float Potentionmeter_GetVoltage(Potentionmeter_t *cThis);
float Potentionmeter_GetPosition(Potentionmeter_t *cThis);

#endif
