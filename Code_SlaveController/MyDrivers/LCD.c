// 芯片为ILI9341，接口为FSMC的液晶屏
#include "LCD.h"
#include "LCD_font.h"

//LCD的画笔颜色和背景色
uint16_t POINT_COLOR=0x0000;//画笔颜色
uint16_t BACK_COLOR=0xFFFF;//背景色

//管理LCD重要参数
//默认为竖屏
_lcd_dev lcddev;



/***********************************************************************************
***********************************基本读写函数*************************************
***********************************************************************************/

//写命令函数
//cmd:命令值
void LCD_WriteCommand(uint16_t command) {LCD->LCD_REG=command;}
//写LCD数据
//data:要写入的值
void LCD_WriteData(uint16_t data) {LCD->LCD_RAM=data;}

//读LCD数据
//返回值:读到的值
uint16_t LCD_ReadData(void)
{
  uint16_t ram=LCD->LCD_RAM;
  return ram;
}

/**写寄存器**
  *@param    寄存器地址
  *@param    要写入的数据
**/
void LCD_WriteReg(uint16_t index,uint16_t data)
{
  LCD_WriteCommand(index);
  LCD_WriteData(data);         
}

//读寄存器
//LCD_Reg:寄存器地址
//返回值:读到的数据
uint16_t LCD_ReadReg(uint16_t index)
{                       
  LCD_WriteCommand(index);
  // HAL_Delay(1);
  return LCD_ReadData();
}





/***********************************************************************************
***********************************外设初始化函数***********************************
***********************************************************************************/

/**初始化lcd**/
void LCD_Init(void)
{
  
   HAL_Delay(50);//delay50ms
  
  //尝试9341ID的读取
  LCD_WriteCommand(0XD3);
  lcddev.id=LCD_ReadData();//dummy read
  lcddev.id=LCD_ReadData();//读到0X00
  lcddev.id=LCD_ReadData();//读取93
  lcddev.id<<=8;
  lcddev.id|=LCD_ReadData();//读取41
  
  //重新配置写时序控制寄存器的时序
  FSMC_Bank1E->BWTR[6]&=~(0XF<<0);//地址建立时间(ADDSET)清零
  FSMC_Bank1E->BWTR[6]&=~(0XF<<8);//数据保存时间清零
  FSMC_Bank1E->BWTR[6]|=4<<0;//地址建立时间(ADDSET)为3个HCLK =18ns
  FSMC_Bank1E->BWTR[6]|=4<<8;//数据保存时间(DATAST)为6ns*3个HCLK=18ns
  LCD_WriteCommand(0xCF);  
  LCD_WriteData(0x00); 
  LCD_WriteData(0xC1); 
  LCD_WriteData(0X30); 
  LCD_WriteCommand(0xED);  
  LCD_WriteData(0x64); 
  LCD_WriteData(0x03); 
  LCD_WriteData(0X12); 
  LCD_WriteData(0X81); 
  LCD_WriteCommand(0xE8);  
  LCD_WriteData(0x85); 
  LCD_WriteData(0x10); 
  LCD_WriteData(0x7A); 
  LCD_WriteCommand(0xCB);  
  LCD_WriteData(0x39); 
  LCD_WriteData(0x2C); 
  LCD_WriteData(0x00); 
  LCD_WriteData(0x34); 
  LCD_WriteData(0x02); 
  LCD_WriteCommand(0xF7);  
  LCD_WriteData(0x20); 
  LCD_WriteCommand(0xEA);  
  LCD_WriteData(0x00); 
  LCD_WriteData(0x00); 
  LCD_WriteCommand(0xC0);//Power control 
  LCD_WriteData(0x1B);//VRH[5:0] 
  LCD_WriteCommand(0xC1);//Power control 
  LCD_WriteData(0x01);//SAP[2:0];BT[3:0] 
  LCD_WriteCommand(0xC5);//VCM control 
  LCD_WriteData(0x30);//3F
  LCD_WriteData(0x30);//3C
  LCD_WriteCommand(0xC7);//VCM control2 
  LCD_WriteData(0XB7); 
  LCD_WriteCommand(0x36);//Memory Access Control 
  LCD_WriteData(0x48); 
  LCD_WriteCommand(0x3A);   
  LCD_WriteData(0x55); 
  LCD_WriteCommand(0xB1);   
  LCD_WriteData(0x00);   
  LCD_WriteData(0x1A); 
  LCD_WriteCommand(0xB6);//Display Function Control
  LCD_WriteData(0x0A);
  LCD_WriteData(0xA2);
  LCD_WriteCommand(0xF2);//3Gamma Function Disable
  LCD_WriteData(0x00);
  LCD_WriteCommand(0x26);//Gamma curve selected
  LCD_WriteData(0x01); 
  LCD_WriteCommand(0xE0);//Set Gamma
  LCD_WriteData(0x0F); 
  LCD_WriteData(0x2A); 
  LCD_WriteData(0x28); 
  LCD_WriteData(0x08); 
  LCD_WriteData(0x0E); 
  LCD_WriteData(0x08); 
  LCD_WriteData(0x54); 
  LCD_WriteData(0XA9); 
  LCD_WriteData(0x43); 
  LCD_WriteData(0x0A); 
  LCD_WriteData(0x0F); 
  LCD_WriteData(0x00); 
  LCD_WriteData(0x00); 
  LCD_WriteData(0x00); 
  LCD_WriteData(0x00);      
  LCD_WriteCommand(0XE1);//Set Gamma 
  LCD_WriteData(0x00); 
  LCD_WriteData(0x15); 
  LCD_WriteData(0x17); 
  LCD_WriteData(0x07); 
  LCD_WriteData(0x11); 
  LCD_WriteData(0x06); 
  LCD_WriteData(0x2B); 
  LCD_WriteData(0x56); 
  LCD_WriteData(0x3C); 
  LCD_WriteData(0x05); 
  LCD_WriteData(0x10); 
  LCD_WriteData(0x0F); 
  LCD_WriteData(0x3F); 
  LCD_WriteData(0x3F); 
  LCD_WriteData(0x0F); 
  LCD_WriteCommand(0x2B); 
  LCD_WriteData(0x00);
  LCD_WriteData(0x00);
  LCD_WriteData(0x01);
  LCD_WriteData(0x3f);
  LCD_WriteCommand(0x2A); 
  LCD_WriteData(0x00);
  LCD_WriteData(0x00);
  LCD_WriteData(0x00);
  LCD_WriteData(0xef);   
  LCD_WriteCommand(0x11);//Exit Sleep
  // HAL_Delay(120);
  LCD_WriteCommand(0x29);//display on
  
  LCD_SetDisplayDirection(0);//默认为竖屏
  LCD_BL=1;//点亮背光
  LCD_Clear(WHITE);
}







/***********************************************************************************
**********************************液晶屏基本操作函数********************************
***********************************************************************************/

//开始写GRAM
void LCD_WriteRAM_Prepare(void)
{
   LCD_WriteCommand(lcddev.wramcmd);
}

/**LCD写GRAM**
  *@param    颜色值
**/
void LCD_WriteRAM(uint16_t RGB_Code)
{
  LCD_WriteData(RGB_Code);//写十六位GRAM
}

/**从ILI93xx读出的数据为GBR格式，而我们写入的时候为RGB格式。**
  *@param    GBR格式的颜色值
  *@retval  RGB格式的颜色值
**/
uint16_t LCD_BGR2RGB(uint16_t gbr)
{
  uint16_t r,g,b,rgb;
  b=(gbr>>0)&0x1f;
  g=(gbr>>5)&0x3f;
  r=(gbr>>11)&0x1f;
  rgb=(b<<11)+(g<<5)+(r<<0);
  return(rgb);
}

/**读取个某点的颜色值**
  *@param    横坐标
  *@param    纵坐标
  *@retval  此点的颜色
**/
uint16_t LCD_ReadPoint(uint16_t x,uint16_t y)
{
  uint16_t r=0,g=0,b=0;
  if(x>=lcddev.width||y>=lcddev.height)return 0;//超过了范围,直接返回
  LCD_SetCursor(x,y);
  LCD_WriteCommand(0X2E);
  r = LCD_ReadData();//假读  
  r = LCD_ReadData();//实际坐标颜色
  //9341/5310/5510/7789/9806 要分2次读出
  b = LCD_ReadData();
  g = r & 0XFF;//对于 9341/5310/5510/7789, 第一次读取的是RG的值,R在前,G在后,各占8位
  g <<= 8;
  return (r | (g>>5) | (b>>11));//9341/5310/5510/7789/9806需要公式转换一下
}

/**LCD开启显示**/
void LCD_OpenDisplay(void)
{
  //9341/5310/1963/7789/7796/9806 等发送开启显示指令
  LCD_WriteCommand(0X29);//开启显示
}
/**LCD关闭显示**/
void LCD_CloseDisplay(void)
{
  //9341/5310/1963/7789/7796/9806 等发送关闭显示指令
  LCD_WriteCommand(0X28);//关闭显示
}

/**设置光标位置**
  *@param    横坐标
  *@param    纵坐标
**/
void LCD_SetCursor(uint16_t Xpos,uint16_t Ypos)
{
  //9341/5310/7789/7796/9806等设置坐标
  LCD_WriteCommand(lcddev.setxcmd);
  LCD_WriteData(Xpos >> 8);
  LCD_WriteData(Xpos & 0XFF);
  LCD_WriteCommand(lcddev.setycmd);
  LCD_WriteData(Ypos >> 8);
  LCD_WriteData(Ypos & 0XFF);
}

//设置LCD的自动扫描方向
//dir:0~7,代表8个方向(具体定义见lcd.h)
//9341/5310/5510/1963/7789等IC已经实际测试
//注意:其他函数可能会受到此函数设置的影响(尤其是9341),
//所以,一般设置为L2R_U2D即可,如果设置为其他扫描方式,可能导致显示不正常.
void LCD_SetScanDirection(uint8_t dir)
{
  uint16_t regval=0;
  uint16_t dirreg=0;
  uint16_t temp;
  //横屏时，对1963不改变扫描方向, 其他IC改变扫描方向！竖屏时1963改变方向, 其他IC不改变扫描方向
  if (lcddev.dir == 1)
  {
    switch(dir)//方向转换
    {
      case 0: dir=6;break;
      case 1: dir=7;break;
      case 2: dir=4;break;
      case 3: dir=5;break;
      case 4: dir=1;break;
      case 5: dir=0;break;
      case 6: dir=3;break;
      case 7: dir=2;break;
    }
  }
  
  switch (dir)
  {
    case L2R_U2D://从左到右,从上到下
      regval |= (0 << 7) | (0 << 6) | (0 << 5);
      break;
    case L2R_D2U://从左到右,从下到上
      regval |= (1 << 7) | (0 << 6) | (0 << 5);
      break;
    case R2L_U2D://从右到左,从上到下
      regval |= (0 << 7) | (1 << 6) | (0 << 5);
      break;
    case R2L_D2U://从右到左,从下到上
      regval |= (1 << 7) | (1 << 6) | (0 << 5);
      break;
    case U2D_L2R://从上到下,从左到右
      regval |= (0 << 7) | (0 << 6) | (1 << 5);
      break;
    case U2D_R2L://从上到下,从右到左
      regval |= (0 << 7) | (1 << 6) | (1 << 5);
      break;
    case D2U_L2R://从下到上,从左到右
      regval |= (1 << 7) | (0 << 6) | (1 << 5);
      break;
    case D2U_R2L://从下到上,从右到左
      regval |= (1 << 7) | (1 << 6) | (1 << 5);
      break;
  }
  dirreg = 0X36;
  //9341 & 7789 要设置BGR位
  regval |= 0X08;
  LCD_WriteReg(dirreg, regval);
  if (regval & 0X20)
  {
    if (lcddev.width < lcddev.height)   //交换X,Y
    {
      temp = lcddev.width;
      lcddev.width = lcddev.height;
      lcddev.height = temp;
    }
  }
  else
  {
    if (lcddev.width > lcddev.height)   //交换X,Y
    {
      temp = lcddev.width;
      lcddev.width = lcddev.height;
      lcddev.height = temp;
    }
  }
  
  //设置显示区域(开窗)大小
  LCD_WriteCommand(lcddev.setxcmd);
  LCD_WriteData(0);
  LCD_WriteData(0);
  LCD_WriteData((lcddev.width - 1) >> 8);
  LCD_WriteData((lcddev.width - 1) & 0XFF);
  LCD_WriteCommand(lcddev.setycmd);
  LCD_WriteData(0);
  LCD_WriteData(0);
  LCD_WriteData((lcddev.height - 1) >> 8);
  LCD_WriteData((lcddev.height - 1) & 0XFF);
}

/**设置LCD显示方向**
  *@param    0,竖屏；1,横屏
**/
void LCD_SetDisplayDirection(uint8_t dir)
{
  lcddev.dir = dir;//竖屏/横屏
  
  if (dir == 0)//竖屏
  {
    lcddev.width = 240;
    lcddev.height = 320;
    
    //其他IC, 包括: 9341 / 5310 / 7789/7796/9806等IC
    lcddev.wramcmd = 0X2C;
    lcddev.setxcmd = 0X2A;
    lcddev.setycmd = 0X2B;
  }
  else//横屏
  {
    lcddev.width = 320;
    lcddev.height = 240;
    
    //其他IC, 包括: 9341 / 5310 / 7789/7796等IC
    lcddev.wramcmd = 0X2C;
    lcddev.setxcmd = 0X2A;
    lcddev.setycmd = 0X2B;
  }
  LCD_SetScanDirection(DFT_SCAN_DIR);     //默认扫描方向
}

/**设置窗口,并自动设置画点坐标到窗口左上角(sx,sy)**
  *@param    窗口的起始横坐标
  *@param    窗口的起始纵坐标
  *@param    窗口宽度，必须大于0
  *@param    窗口高度，必须大于0
**/
void LCD_SetWindow(uint16_t sx, uint16_t sy, uint16_t width, uint16_t height)
{
  uint16_t twidth, theight;
  twidth = sx + width - 1;
  theight = sy + height - 1;
  
  //9341/5310/7789/1963/7796/9806横屏 等 设置窗口
  LCD_WriteCommand(lcddev.setxcmd);
  LCD_WriteData(sx >> 8);
  LCD_WriteData(sx & 0XFF);
  LCD_WriteData(twidth >> 8);
  LCD_WriteData(twidth & 0XFF);
  LCD_WriteCommand(lcddev.setycmd);
  LCD_WriteData(sy >> 8);
  LCD_WriteData(sy & 0XFF);
  LCD_WriteData(theight >> 8);
  LCD_WriteData(theight & 0XFF);
}












/***********************************************************************************
**********************************液晶屏显示操作函数********************************
***********************************************************************************/

/**用指定颜色清屏**
  *@param    要清屏的填充色
**/
void LCD_Clear(uint16_t color)
{
  uint32_t index = 0;
  uint32_t totalpoint = lcddev.width;
  totalpoint *= lcddev.height;    //得到总点数
  
  LCD_SetCursor(0x00, 0x0000);    //设置光标位置
  LCD_WriteRAM_Prepare();         //开始写入GRAM
  
  for (index = 0; index < totalpoint; index++)
  {
    LCD_WriteRAM(color);
  }
}

/**画点**
  *@param    横坐标
  *@param    纵坐标
**/
void LCD_DrawPoint(uint16_t x,uint16_t y)
{
  LCD_SetCursor(x,y);    //设置光标位置
  LCD_WriteRAM_Prepare();  //开始写入GRAM
  LCD_WriteRAM(POINT_COLOR);
}

/**快速画点**
  *@param    横坐标
  *@param    纵坐标
  *@param    颜色
**/
void LCD_Fast_DrawPoint(uint16_t x,uint16_t y,uint16_t color)
{     
  //9341/5310/7789等设置坐标
  LCD_WriteCommand(lcddev.setxcmd);
  LCD_WriteData(x >> 8);
  LCD_WriteData(x & 0XFF);
  LCD_WriteCommand(lcddev.setycmd);
  LCD_WriteData(y >> 8);
  LCD_WriteData(y & 0XFF);
  LCD_WriteReg(lcddev.wramcmd,color); 
}

/**在指定矩形区域内填充指定颜色**
**区域大小:(xend-xsta+1)*(yend-ysta+1)**
  *@param    起始横坐标
  *@param    起始纵坐标
  *@param    结束横坐标
  *@param    结束纵坐标
  *@param    要填充的颜色
**/
void LCD_FillRectangle(uint16_t sx, uint16_t sy, uint16_t ex, uint16_t ey)
{
  uint16_t
    i,j,
    xlen = ex - sx + 1,
    ylen = ey - sy + 1;
  
  for (i = 0; i < ylen; i++)
  {
    LCD_SetCursor(sx, sy+i);//设置光标位置
    LCD_WriteRAM_Prepare();//开始写入GRAM
    
    for (j = 0; j < xlen; j++)
    {
      LCD->LCD_RAM=POINT_COLOR;//设置光标位置
    }
  }
}

/**在指定区域内填充指定颜色序列，即显示图片**
**(sx,sy),(ex,ey):填充矩形对角坐标,区域大小为:(ex-sx+1)*(ey-sy+1)**
  *@param    起始横坐标
  *@param    起始纵坐标
  *@param    结束横坐标
  *@param    结束纵坐标
  *@param    要填充的颜色序列，从左到右从上到下
**/
void LCD_FillPicture(uint16_t sx, uint16_t sy, uint16_t ex, uint16_t ey, uint16_t *color)
{
  uint16_t
    i,j,
    width = ex - sx + 1,//填充宽度
    height = ey - sy + 1;//填充高度
  
  for (i=0;i<height;i++)
  {
    LCD_SetCursor(sx,sy + i);//设置光标位置
    LCD_WriteRAM_Prepare();//开始写入GRAM
    
    for (j=0;j<width;j++)
    {
      LCD_WriteRAM(color[i*width+j]);  //写入数据
    }
  }
}

/**画直线**
  *@param    起始横坐标
  *@param    起始纵坐标
  *@param    结束横坐标
  *@param    结束纵坐标
  *@param    要填充的颜色
**/
void LCD_DrawLine(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2)
{
  uint16_t t;
  int xerr = 0, yerr = 0, delta_x, delta_y, distance;
  int incx, incy, uRow, uCol;
  delta_x = x2 - x1;              //计算坐标增量
  delta_y = y2 - y1;
  uRow = x1;
  uCol = y1;
  
  if (delta_x > 0)incx = 1;       //设置单步方向
  else if (delta_x == 0)incx = 0; //垂直线
  else
  {
    incx = -1;
    delta_x = -delta_x;
  }
  
  if (delta_y > 0)incy = 1;
  else if (delta_y == 0)incy = 0; //水平线
  else
  {
    incy = -1;
    delta_y = -delta_y;
  }
  
  if ( delta_x > delta_y)distance = delta_x; //选取基本增量坐标轴
  else distance = delta_y;
  
  for (t = 0; t <= distance + 1; t++ )    //画线输出
  {
    LCD_DrawPoint(uRow, uCol); //画点
    xerr += delta_x ;
    yerr += delta_y ;
    
    if (xerr > distance)
    {
      xerr -= distance;
      uRow += incx;
    }
    
    if (yerr > distance)
    {
      yerr -= distance;
      uCol += incy;
    }
  }
}

/**画矩形框**
**(x1,y1),(x2,y2):矩形的对角坐标**
  *@param    矩形左上角横坐标
  *@param    矩形左上角纵坐标
  *@param    矩形右下角横坐标
  *@param    矩形右下角纵坐标
  *@param    要填充的颜色
**/
void LCD_DrawRectangle(uint16_t x1, uint16_t y1, uint16_t x2, uint16_t y2)
{
  LCD_DrawLine(x1,y1,x2,y1);
  LCD_DrawLine(x1,y1,x1,y2);
  LCD_DrawLine(x1,y2,x2,y2);
  LCD_DrawLine(x2,y1,x2,y2);
}

/**在指定位置画一个指定大小的圆**
  *@param    圆心横坐标
  *@param    圆心纵坐标
  *@param    圆半径
**/
void LCD_DrawCircle(uint16_t x0,uint16_t y0,uint16_t r)
{
  int a, b;
  int di;
  a = 0;
  b = r;
  di = 3 - (r << 1);       //判断下个点位置的标志
  
  while (a <= b)
  {
    LCD_DrawPoint(x0 + a, y0 - b);        //5
    LCD_DrawPoint(x0 + b, y0 - a);        //0
    LCD_DrawPoint(x0 + b, y0 + a);        //4
    LCD_DrawPoint(x0 + a, y0 + b);        //6
    LCD_DrawPoint(x0 - a, y0 + b);        //1
    LCD_DrawPoint(x0 - b, y0 + a);
    LCD_DrawPoint(x0 - a, y0 - b);        //2
    LCD_DrawPoint(x0 - b, y0 - a);        //7
    a++;
    
    //使用Bresenham算法画圆
    if (di < 0)di += 4 * a + 6;
    else
    {
      di += 10 + 4 * (a - b);
      b--;
    }
  }
}

/**显示一个16×16大小的中文字符**
  *@param    显示的起始横坐标
  *@param    显示的起始纵坐标
  *@param    一个中文字符（要用英文双引号括起来）
**/
void LCD_CNCHAR16(uint16_t x,uint16_t y,char *cn)
{
  uint16_t
    x0=x,
    temp,i,j,
    CharNum=32,size=16,
    CNnum=sizeof(CNchar16x16)/sizeof(GBCNchar16x16);
  
  for(i=0;i<CNnum;i++)
    if(CNchar16x16[i].Index[0]==cn[0])
      if(CNchar16x16[i].Index[1]==cn[1])
        if(CNchar16x16[i].Index[2]==cn[2])
        break;
  CNnum=i;
  for(i=0;i<CharNum;i++)
  {
    temp=CNchar16x16[CNnum].Msk[i];
    for(j=0;j<8;j++)
    {
      if(temp&0x80)LCD_Fast_DrawPoint(x,y,POINT_COLOR);
      else LCD_Fast_DrawPoint(x,y,BACK_COLOR);
      temp<<=1;
      x++;
      if((x-x0)==size)
      {
        x=x0;
        y++;
      }
    }
  }
}

/**显示一个24×24大小的中文字符**
  *@param    显示的起始横坐标
  *@param    显示的起始纵坐标
  *@param    一个中文字符（要用英文双引号括起来）
**/
void LCD_CNCHAR24(uint16_t x,uint16_t y,char *cn)
{
  uint16_t
    x0=x,
    temp,i,j,
    CharNum=72,size=24,
    CNnum=sizeof(CNchar24x24)/sizeof(GBCNchar24x24);
  
  for(i=0;i<CNnum;i++)
    if(CNchar24x24[i].Index[0]==cn[0])
      if(CNchar24x24[i].Index[1]==cn[1])
        if(CNchar24x24[i].Index[2]==cn[2])
        break;
  CNnum=i;
  for(i=0;i<CharNum;i++)
  {
    temp=CNchar24x24[CNnum].Msk[i];
    for(j=0;j<8;j++)
    {
      if(temp&0x80)LCD_Fast_DrawPoint(x,y,POINT_COLOR);
      else LCD_Fast_DrawPoint(x,y,BACK_COLOR);
      temp<<=1;
      x++;
      if((x-x0)==size)
      {
        x=x0;
        y++;
      }
    }
  }
}

/**显示一个40×40大小的中文字符**
  *@param    显示的起始横坐标
  *@param    显示的起始纵坐标
  *@param    一个中文字符（要用英文双引号括起来）
**/
void LCD_CNCHAR40(uint16_t x,uint16_t y,char *cn)
{
  uint16_t
    x0=x,
    temp,i,j,
    CharNum=200,size=40,
    CNnum=sizeof(CNchar40x40)/sizeof(GBCNchar40x40);
  
  for(i=0;i<CNnum;i++)
    if(CNchar40x40[i].Index[0]==cn[0])
      if(CNchar40x40[i].Index[1]==cn[1])
        if(CNchar40x40[i].Index[2]==cn[2])
        break;
  CNnum=i;
  for(i=0;i<CharNum;i++)
  {
    temp=CNchar40x40[CNnum].Msk[i];
    for(j=0;j<8;j++)
    {
      if(temp&0x80)LCD_Fast_DrawPoint(x,y,POINT_COLOR);
      else LCD_Fast_DrawPoint(x,y,BACK_COLOR);
      temp<<=1;
      x++;
      if((x-x0)==size)
      {
        x=x0;
        y++;
      }
    }
  }
}

/**显示16×16大小的中文字符串**
  *@param    显示的起始横坐标
  *@param    显示的起始纵坐标
  *@param    中文字符串
**/
void LCD_CNSTRING16(uint16_t x,uint16_t y,char *cn)
{
  while(*cn!=0)
  {
    LCD_CNCHAR16(x,y,cn);
    x+=16;
    cn+=3;
  }
}

/**显示24×24大小的中文字符串**
  *@param    显示的起始横坐标
  *@param    显示的起始纵坐标
  *@param    中文字符串
**/
void LCD_CNSTRING24(uint16_t x,uint16_t y,char *cn)
{
  while(*cn!=0)
  {
    LCD_CNCHAR24(x,y,cn);
    x+=24;
    cn+=3;
  }
}

/**显示40×40大小的中文字符串**
  *@param    显示的起始横坐标
  *@param    显示的起始纵坐标
  *@param    中文字符串
**/
void LCD_CNSTRING40(uint16_t x,uint16_t y,char *cn)
{
  while(*cn!=0)
  {
    LCD_CNCHAR40(x,y,cn);
    x+=40;
    cn+=3;
  }
}

/**在指定位置显示一个字符**
  *@param    显示起始横坐标
  *@param    显示起始纵坐标
  *@param    显示字符的字体大小：12、16、24
  *@param    显示的字符
**/
void LCD_ShowChar(uint16_t x,uint16_t y,uint8_t size,char character)
{                  
  uint8_t temp,t1;
  uint16_t y0=y,t,csize;
//  csize = (size/8+((size%8)?1:0))*(size/2);//得到字体一个字符对应点阵集所占的字节数  
  switch(size)
  {
    case 12: csize=12;break;
    case 16: csize=16;break;
    case 24: csize=36;break;
    default: break;
  }
   character = character-' ';//得到偏移后的值（ASCII字库是从空格开始取模，所以-' '就是对应字符的字库）
  for(t=0;t<csize;t++)
  {   
    if(size==12)temp=asc2_1206[character][t];//调用1206字体
    else if(size==16)temp=asc2_1608[character][t];//调用1608字体
    else if(size==24)temp=asc2_2412[character][t];//调用2412字体
    else return;//没有的字库
    for(t1=0;t1<8;t1++)
    {
      if(temp&0x80)LCD_Fast_DrawPoint(x,y,POINT_COLOR);
      else LCD_Fast_DrawPoint(x,y,BACK_COLOR);
      temp<<=1;
      y++;
      if((y-y0)==size)
      {
        y=y0;
        x++;
        break;
      }
    }
  }
}

/**显示字符串，可自动换行**
  *@param    显示起始横坐标
  *@param    显示起始纵坐标
  *@param    显示宽度限制
  *@param    显示高度限制
  *@param    显示字符的字体大小：12、16、24
  *@param    显示的字符串
**/
void LCD_ShowString(uint16_t x, uint16_t y, uint16_t size, char *p)
{
  while ((*p >= ' ') && (*p <= '~'))//判断是不是非法字符!
  {
    LCD_ShowChar(x, y, size, *p);
    x += size / 2;
    p++;
  }  
}

/**返回m的n次方**/
uint32_t LCD_Pow(uint8_t m,uint8_t n)
{
  uint32_t result=1;   
  while(n--)result*=m;    
  return result;
}

/**显示无符号数字,高位为0则显示空格**
  *@param    显示起始横坐标
  *@param    显示起始纵坐标
  *@param    显示字符的字体大小：12、16、24
  *@param    显示的数，范围：0~4294967295
  *@param    显示数的长度
**/
void LCD_ShowxNum(uint16_t x, uint16_t y, uint16_t size, uint32_t num, uint16_t len)
{
  uint16_t i,temp;
  for(i=0;i<len;i++)
  {
    temp=num/LCD_Pow(10,len-i-1)%10+'0';
    if(temp=='0')
      LCD_ShowChar(x+(size/2)*i,y,size,' ');
    else break;
  }
  for(;i<len;i++)
  {
    LCD_ShowChar(x+(size/2)*i,y,size,num/LCD_Pow(10,len-i-1)%10+'0');
  }
}

/**显示无符号数字**
  *@param    显示起始横坐标
  *@param    显示起始纵坐标
  *@param    显示字符的字体大小：12、16、24
  *@param    显示的数，范围：0~4294967295
  *@param    显示数的长度
**/
void LCD_ShowNum(uint16_t x, uint16_t y, uint16_t size, uint32_t num, uint16_t len)
{
  for(uint16_t i=0;i<len;i++)
    LCD_ShowChar(x+(size/2)*i,y,size,num/LCD_Pow(10,len-i-1)%10+'0');
}

/**显示有符号数字**
  *@param    显示的起始行
  *@param    显示的起始列
  *@param    显示的数字
  *@param    显示长度
  *@param    显示颜色
**/
void LCD_ShowSignedNum(uint16_t x,uint16_t y,uint16_t size,int32_t num,uint16_t len)
{
  uint32_t AbsNum;
  if(num>=0)
  {LCD_ShowChar(x,y,size,'+');AbsNum=num;}
  else
  {LCD_ShowChar(x,y,size,'-');AbsNum=-num;}
  x+=size/2;
  for (uint16_t i=0;i<len;i++)
    LCD_ShowChar(x+(size/2)*i,y,size,AbsNum/LCD_Pow(10,len-i-1)%10+'0');
}

/**显示无符号十六进制数**
  *@param    显示的起始横坐标
  *@param    显示的起始纵坐标
  *@param    显示字符的字体大小：12、16、24
  *@param    显示的数字
  *@param    显示长度
**/
void LCD_ShowHexNum(uint16_t x,uint16_t y,uint16_t size,uint32_t num,uint16_t len)
{
  uint8_t SingleNum;
  for(uint16_t i=0;i<len;i++)
  {
    SingleNum = num / LCD_Pow(16,len-i-1)%16;
    if(SingleNum<10)
      LCD_ShowChar(x+(size/2)*i,y,size,SingleNum+'0');
    else
      LCD_ShowChar(x+(size/2)*i,y,size,SingleNum-10+'A');
  }
}

/**显示无符号二进制数**
  *@param    显示的起始横坐标
  *@param    显示的起始纵坐标
  *@param    显示字符的字体大小：12、16、24
  *@param    显示的数字
  *@param    显示长度
**/
void LCD_ShowBinNum(uint16_t x,uint16_t y,uint16_t size,uint32_t num,uint16_t len)
{
  for(uint16_t i=0;i<len;i++)
    LCD_ShowChar(x+(size/2)*i,y,size,num/LCD_Pow(2,len-i-1)%2+'0');
}
