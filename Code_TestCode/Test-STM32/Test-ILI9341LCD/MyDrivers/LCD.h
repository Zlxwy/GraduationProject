#ifndef __LCD_H__
#define __LCD_H__

#include "stm32f4xx_hal.h"
#include "GpioBitBanding.h"

//行间推荐间隔像素：
//12->12（14像素）、12->16（14像素）、12->24（12像素）
//16->12（18像素）、16->16（18像素）、16->24（16像素）
//24->12（26像素）、24->16（24像素）、24->24（26像素）

//LCD重要参数集
typedef struct
{
  uint16_t width;//LCD 宽度
  uint16_t height;//LCD 高度
  uint16_t id;//LCD ID
  uint8_t  dir;//横屏还是竖屏控制：0，竖屏；1，横屏。  
  uint16_t  wramcmd;//开始写gram指令
  uint16_t  setxcmd;//设置x坐标指令
  uint16_t  setycmd;//设置y坐标指令 
}_lcd_dev;     

//LCD参数
extern _lcd_dev lcddev;  //管理LCD重要参数
//LCD的画笔颜色和背景色     
extern uint16_t  POINT_COLOR;//默认红色    
extern uint16_t  BACK_COLOR; //背景颜色.默认为白色

 
/********************LCD端口定义*********************/ 
#define  LCD_BL OutputPB(15)      //LCD背光         PB15       
//LCD地址结构体
typedef struct
{
  vu16 LCD_REG;
  vu16 LCD_RAM;
}LCD_TypeDef;


//使用NOR/SRAM的 Bank1.sector4,地址位HADDR[27,26]=11 A6作为数据命令区分线
//注意设置时STM32内部会右移一位对其! 111 1110=0X7E
#define LCD_BASE        ((uint32_t)(0x6C000000 | 0x0000007E))
#define LCD             ((LCD_TypeDef *) LCD_BASE)
   
/***************************扫描方向定义*******************************/
#define L2R_U2D  0 //从左到右,从上到下
#define L2R_D2U  1 //从左到右,从下到上
#define R2L_U2D  2 //从右到左,从上到下
#define R2L_D2U  3 //从右到左,从下到上
#define U2D_L2R  4 //从上到下,从左到右
#define U2D_R2L  5 //从上到下,从右到左
#define D2U_L2R  6 //从下到上,从左到右
#define D2U_R2L  7 //从下到上,从右到左
#define DFT_SCAN_DIR  L2R_U2D  //默认的扫描方向

/********************************画笔颜色**********************************/
#define WHITE   0xFFFF//白色(255,255,255)(31,63,31) 1111 1111 1111 1111
#define BLACK   0x0000//黑色(000,000,000)(00,00,00) 0000 0000 0000 0000
#define RED     0xF800//红色(255,000,000)(31,00,00) 1111 1000 0000 0000
#define ORANGE  0xFA80//橙色(255,125,000)(31,20,00) 1111 1010 1000 0000
#define YELLOW  0xFFE0//黄色(255,255,000)(31,63,00) 1111 1111 1110 0000
#define GREEN   0x07E0//绿色(000,255,000)(00,63,00) 0000 0111 1110 0000
#define BLUE    0x001F//蓝色(000,000,255)(00,00,31) 0000 0000 0001 1111
#define INDIGO  0x07FF//靛色(000,255,255)(00,63,31) 0000 0111 1111 1111
#define PURPLE  0x780F//紫色(123,000,123)(15,00,15) 0111 1000 0000 1111


void LCD_WriteCommand(uint16_t command);//写指令
void LCD_WriteData(uint16_t data);//写数据
uint16_t LCD_ReadData(void);//读数据
void LCD_WriteReg(uint16_t index,uint16_t data);//往寄存器写数据
uint16_t LCD_ReadReg(uint16_t index);//往寄存器读数据

void LCD_Init(void);

void LCD_WriteRAM_Prepare(void);//准备写GRAM
void LCD_WriteRAM(uint16_t RGB_Code);//写GRAM
uint16_t LCD_BGR2RGB(uint16_t gbr);//颜色值格式转换
uint16_t LCD_ReadPoint(uint16_t x,uint16_t y);//读像素点的颜色

void LCD_OpenDisplay(void);//打开显示
void LCD_CloseDisplay(void);//关闭显示

void LCD_SetCursor(uint16_t Xpos,uint16_t Ypos);//设置光标位置
void LCD_SetScanDirection(uint8_t dir);//设置扫描方向
void LCD_SetDisplayDirection(uint8_t dir);//设置显示方向
void LCD_SetWindow(uint16_t sx, uint16_t sy, uint16_t width, uint16_t height);//开窗

void LCD_Clear(uint16_t color);//指定颜色清屏
void LCD_DrawPoint(uint16_t x,uint16_t y);//画点
void LCD_Fast_DrawPoint(uint16_t x,uint16_t y,uint16_t color);//快速画点
void LCD_FillRectangle(uint16_t sx, uint16_t sy, uint16_t ex, uint16_t ey);//指定颜色填充一个矩形
void LCD_FillPicture(uint16_t sx, uint16_t sy, uint16_t ex, uint16_t ey, uint16_t *color);//用一个颜色数组填充出一个图片
void LCD_DrawLine(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2);//画线
void LCD_DrawRectangle(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2);//画矩形框
void LCD_DrawCircle(uint16_t x0,uint16_t y0,uint16_t r);//画圆

void LCD_CNCHAR16(uint16_t x,uint16_t y,char *cn);//显示16×16大小的汉字字符
void LCD_CNCHAR24(uint16_t x,uint16_t y,char *cn);//显示24×24大小的汉字字符
void LCD_CNCHAR40(uint16_t x,uint16_t y,char *cn);//显示40×40大小的汉字字符
void LCD_CNSTRING16(uint16_t x,uint16_t y,char *cn);//显示16×16大小的汉字字符串
void LCD_CNSTRING24(uint16_t x,uint16_t y,char *cn);//显示24×24大小的汉字字符串
void LCD_CNSTRING40(uint16_t x,uint16_t y,char *cn);//显示40×40大小的汉字字符串

void LCD_ShowChar(uint16_t x,uint16_t y,uint8_t size,char character);//显示英文字符
void LCD_ShowString(uint16_t x, uint16_t y, uint16_t size, char *p);//显示字符串，可自动换行
void LCD_ShowxNum(uint16_t x, uint16_t y, uint16_t size, uint32_t num, uint16_t len);//显示无符号十进制数，高位为0则显示空格
void LCD_ShowNum(uint16_t x, uint16_t y, uint16_t size, uint32_t num, uint16_t len);//显示无符号十进制数，高位为0则补0
void LCD_ShowSignedNum(uint16_t x,uint16_t y,uint16_t size,int32_t num,uint16_t len);//显示有符号十进制数
void LCD_ShowHexNum(uint16_t x,uint16_t y,uint16_t size,uint32_t num,uint16_t len);//显示无符号十六进制数
void LCD_ShowBinNum(uint16_t x,uint16_t y,uint16_t size,uint32_t num,uint16_t len);//显示无符号二进制数



//LCD分辨率设置
#define SSD_HOR_RESOLUTION    800    //LCD水平分辨率
#define SSD_VER_RESOLUTION    480    //LCD垂直分辨率
//LCD驱动参数设置
#define SSD_HOR_PULSE_WIDTH    1    //水平脉宽
#define SSD_HOR_BACK_PORCH    46    //水平前廊
#define SSD_HOR_FRONT_PORCH    210    //水平后廊

#define SSD_VER_PULSE_WIDTH    1    //垂直脉宽
#define SSD_VER_BACK_PORCH    23    //垂直前廊
#define SSD_VER_FRONT_PORCH    22    //垂直前廊
//如下几个参数，自动计算
#define SSD_HT  (SSD_HOR_RESOLUTION+SSD_HOR_BACK_PORCH+SSD_HOR_FRONT_PORCH)
#define SSD_HPS  (SSD_HOR_BACK_PORCH)
#define SSD_VT   (SSD_VER_RESOLUTION+SSD_VER_BACK_PORCH+SSD_VER_FRONT_PORCH)
#define SSD_VPS (SSD_VER_BACK_PORCH)

#endif // __LCD_H__
