#include "Potentionmeter.h"

uint32_t ADC_ConvValue[4];

void Potentionmeter_Init(Potentionmeter_t *cThis,
                        uint32_t ConvValueIndex,
                        float RefVoltage,
                        uint32_t ConvValueMin,
                        uint32_t ConvValueMax,
                        uint32_t CenterValueDriftMin,
                        uint32_t CenterValueDriftMax ) {
  cThis->ConvValueAddr = &ADC_ConvValue[ConvValueIndex];
  cThis->RefVoltage = RefVoltage;
  cThis->ConvValueMin = ConvValueMin;
  cThis->ConvValueMax = ConvValueMax;
  cThis->CenterValueDriftMax = CenterValueDriftMax;
  cThis->CenterValueDriftMin = CenterValueDriftMin;
}



uint32_t Potentionmeter_GetConvValue(Potentionmeter_t *cThis) {
  return *(cThis->ConvValueAddr);
}



float Potentionmeter_GetVoltage(Potentionmeter_t *cThis) {
  uint32_t ConvValue = Potentionmeter_GetConvValue(cThis);
  float Voltage = (ConvValue - cThis->ConvValueMin) * cThis->RefVoltage / (cThis->ConvValueMax - cThis->ConvValueMin);
  return Voltage;
}



float Potentionmeter_GetPosition(Potentionmeter_t *cThis) {
  uint32_t ConvValue = Potentionmeter_GetConvValue(cThis);

  if (ConvValue >= cThis->CenterValueDriftMax)
    return 0.0f +
           (float)(ConvValue-cThis->CenterValueDriftMax) /
           (float)(cThis->ConvValueMax - cThis->CenterValueDriftMax);

  else if (ConvValue < cThis->CenterValueDriftMin)
    return 0.0f -
           (float)(cThis->CenterValueDriftMin - ConvValue) /
           (float)(cThis->CenterValueDriftMin - cThis->ConvValueMin);

  else return 0.0f;
}





void Potentionmeter_AutoCenterValueRange(Potentionmeter_t *cThis) {
  uint32_t RecordValue;
  uint32_t RecordValueMax = 0;
  uint32_t RecordValueMin = 0xFFFF;
  for (uint32_t i=0; i<10000; i++) {
    RecordValue = Potentionmeter_GetConvValue(cThis);
    // uart_printf(&huart3, "RecordValue: %d\n", RecordValue);
    if (RecordValue > RecordValueMax) {
      RecordValueMax = RecordValue;
      // uart_printf(&huart3, "获得的值比RecordValueMax大，更新RecordValueMax: %d\n", RecordValueMax);
    }
    if (RecordValue < RecordValueMin) {
      RecordValueMin = RecordValue;
      // uart_printf(&huart3, "获得的值比RecordValueMin小，更新RecordValueMin: %d\n", RecordValueMin);
    }
    
    // uart_printf(&huart3, "当前RecordValueMax: %d\n", RecordValueMax);
    // uart_printf(&huart3, "当前RecordValueMin: %d\n", RecordValueMin);
    // uart_printf(&huart3, "\r\n\r\n");
    HAL_Delay(1);
  }

  cThis->CenterValueDriftMax = RecordValueMax;
  cThis->CenterValueDriftMin = RecordValueMin;
}



void Potentionmeter_SetCenterValueRange(Potentionmeter_t *cThis, uint32_t CenterValueDriftMin, uint32_t CenterValueDriftMax) {
  cThis->CenterValueDriftMax = CenterValueDriftMax;
  cThis->CenterValueDriftMin = CenterValueDriftMin;
}


