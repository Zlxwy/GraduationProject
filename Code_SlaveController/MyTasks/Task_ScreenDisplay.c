#include "Task_All.h"

void ScreenDisplayTaskFunc(void *argument) {
  (void)argument;
  while (!IsAllInitOkay) { osDelay(100); }

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
  uint16_t color[9] = {WHITE,BLACK,RED,ORANGE,YELLOW,GREEN,BLUE,INDIGO,PURPLE};
  for(uint8_t i=0; i<9; i++) {
    if(i==0) {
      POINT_COLOR=BLACK;
      LCD_DrawRectangle(5+i*25,220,25+i*25,240);//因为背景色是白色，填充白色是看不见的，所以如果填充色是白色，就画一个黑色的矩形框就行
    }
    else {
      POINT_COLOR=color[i];
      LCD_FillRectangle(5+i*25,220,25+i*25,240);//如果填充色是其他颜色，就直接填充一个矩形显示出来
    }
  }

  // /**汉字显示测试**/
  POINT_COLOR=RED;
  LCD_ShowString(5,243,12,"/******Display Chinese Test******/");
  POINT_COLOR=BLACK;
  LCD_CNSTRING40(5,257,"杨登杰");
  LCD_CNSTRING16(125,259,"细雪飘落长街");
  LCD_CNSTRING16(125,277,"枫叶红透又一年");

  while (true) {
    osDelay(100);
  }
}
