#ifndef __GPIO_BIT_BANDING_H__
#define __GPIO_BIT_BANDING_H__

#include "stm32f4xx_hal.h"

// 位带操作，实现51类似的GPIO控制功能
// 具体实现思想，参考<<CM3权威指南>>第五章(87页~92页)，M4同M3类似，只是寄存器地址变了
// IO口操作宏定义
#define  BITBAND(addr, bitnum)    ((addr & 0xF0000000)+0x2000000+((addr &0xFFFFF)<<5)+(bitnum<<2))
#define  MEM_ADDR(addr)           *( (volatile unsigned long*)(addr) )
#define  BIT_ADDR(addr, bitnum)   MEM_ADDR(BITBAND(addr, bitnum))

// IO口地址映射
#define  GPIOA_ODR_Addr    (GPIOA_BASE+20) // 0x40020014
#define  GPIOB_ODR_Addr    (GPIOB_BASE+20) // 0x40020414
#define  GPIOC_ODR_Addr    (GPIOC_BASE+20) // 0x40020814
#define  GPIOD_ODR_Addr    (GPIOD_BASE+20) // 0x40020C14
#define  GPIOE_ODR_Addr    (GPIOE_BASE+20) // 0x40021014
#define  GPIOF_ODR_Addr    (GPIOF_BASE+20) // 0x40021414
#define  GPIOG_ODR_Addr    (GPIOG_BASE+20) // 0x40021814
#define  GPIOH_ODR_Addr    (GPIOH_BASE+20) // 0x40021C14
#define  GPIOI_ODR_Addr    (GPIOI_BASE+20) // 0x40022014

#define  GPIOA_IDR_Addr    (GPIOA_BASE+16) // 0x40020010
#define  GPIOB_IDR_Addr    (GPIOB_BASE+16) // 0x40020410
#define  GPIOC_IDR_Addr    (GPIOC_BASE+16) // 0x40020810
#define  GPIOD_IDR_Addr    (GPIOD_BASE+16) // 0x40020C10
#define  GPIOE_IDR_Addr    (GPIOE_BASE+16) // 0x40021010
#define  GPIOF_IDR_Addr    (GPIOF_BASE+16) // 0x40021410
#define  GPIOG_IDR_Addr    (GPIOG_BASE+16) // 0x40021810
#define  GPIOH_IDR_Addr    (GPIOH_BASE+16) // 0x40021C10
#define  GPIOI_IDR_Addr    (GPIOI_BASE+16) // 0x40022010
 
// IO口操作，只对单一的IO口!
// 确保n的值小于16!
#define  OutputPA(n)    BIT_ADDR(GPIOA_ODR_Addr,n)  //输出
#define  OutputPB(n)    BIT_ADDR(GPIOB_ODR_Addr,n)  //输出
#define  OutputPC(n)    BIT_ADDR(GPIOC_ODR_Addr,n)  //输出
#define  OutputPD(n)    BIT_ADDR(GPIOD_ODR_Addr,n)  //输出
#define  OutputPE(n)    BIT_ADDR(GPIOE_ODR_Addr,n)  //输出
#define  OutputPF(n)    BIT_ADDR(GPIOF_ODR_Addr,n)  //输出
#define  OutputPG(n)    BIT_ADDR(GPIOG_ODR_Addr,n)  //输出
#define  OutputPH(n)    BIT_ADDR(GPIOH_ODR_Addr,n)  //输出
#define  OutputPI(n)    BIT_ADDR(GPIOI_ODR_Addr,n)  //输出

#define  InputPA(n)     BIT_ADDR(GPIOA_IDR_Addr,n)  //输入
#define  InputPB(n)     BIT_ADDR(GPIOB_IDR_Addr,n)  //输入
#define  InputPC(n)     BIT_ADDR(GPIOC_IDR_Addr,n)  //输入
#define  InputPD(n)     BIT_ADDR(GPIOD_IDR_Addr,n)  //输入
#define  InputPE(n)     BIT_ADDR(GPIOE_IDR_Addr,n)  //输入
#define  InputPF(n)     BIT_ADDR(GPIOF_IDR_Addr,n)  //输入
#define  InputPG(n)     BIT_ADDR(GPIOG_IDR_Addr,n)  //输入
#define  InputPH(n)     BIT_ADDR(GPIOH_IDR_Addr,n)  //输入
#define  InputPI(n)     BIT_ADDR(GPIOI_IDR_Addr,n)  //输入