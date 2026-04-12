#include "Task_All.h"

void ElectronMagnet_SetStatus(uint8_t MagnetStatus) {
  switch (MagnetStatus) {
    case 0x00: // 禁用
      DigitalOutput_SetState(&gL298nEnableA, DigitalOutputState_Inactive);
      DigitalOutput_SetState(&gL298nInput1, DigitalOutputState_Inactive);
      DigitalOutput_SetState(&gL298nInput2, DigitalOutputState_Inactive);
      break;
    case 0x01: // 正向电压使能
      DigitalOutput_SetState(&gL298nEnableA, DigitalOutputState_Active);
      DigitalOutput_SetState(&gL298nInput1, DigitalOutputState_Active);
      DigitalOutput_SetState(&gL298nInput2, DigitalOutputState_Inactive);
      break;
    case 0x02: // 反向电压使能
      DigitalOutput_SetState(&gL298nEnableA, DigitalOutputState_Active);
      DigitalOutput_SetState(&gL298nInput1, DigitalOutputState_Inactive);
      DigitalOutput_SetState(&gL298nInput2, DigitalOutputState_Active);
      break;
    default: break;
  }
}

/*这个线程用来执行所有电机的动作*/
void MotorActionTaskFunc(void *argument) {
  (void)argument;
  while (!IsAllInitOkay) { osDelay(100); }

  while (true) {
    Msg_MotorAction_t msg;
    if ( osMessageQueueGet(gMsgQueueMotorAction, &msg, NULL, 500) == osOK ) {
      if (msg.RequestType == MotorActionRequestType_BasicMove) { // 基础行走
        // StepperMotor_MoveSteps( // 步进电机移动指定步数函数
        //   &gStepperMotorShoulder, // 肩关节步进电机
        //   msg.Steps, // 行走步数
        //   msg.Speed // 行走速度
        // ); // Object, steps, speed
        StepperMotor_t *pStepperMotor = NULL;
        switch (msg.MotorID) { // 根据电机ID选择步进电机对象，进行操作
          case 0x00: pStepperMotor = &gStepperMotorShoulder; break; // 肩关节步进电机
          case 0x01: pStepperMotor = &gStepperMotorElbow; break; // 肘关节步进电机
          case 0x02: pStepperMotor = &gStepperMotorLift; break; // 竖轴步进电机
          default: break;
        }
        if (msg.ActionType == 0x00) { // 动作类型：0x00停止
          StepperMotor_Stop(pStepperMotor); // 步进电机停止
        }
        else if (msg.ActionType == 0x01) { // 动作类型：0x01旋转指定步数
          StepperMotor_MoveSteps(pStepperMotor, msg.Steps, msg.Speed); // 步进电机移动指定步数函数
          while (StepperMotor_GetRunState(pStepperMotor) == StepperMotor_RunState_MoveSteps); // 等待步进电机移动完成
        } 
        else if (msg.ActionType == 0x02) { // 动作类型：0x02持续旋转（Steps为-1则反转，Steps为1则正转）
          StepperMotor_RunContinuous( // 步进电机持续旋转函数
            pStepperMotor, // 步进电机对象
            msg.Steps > 0 ? // 步进电机步数是否为1
            StepperMotor_Direction_Forward : // 步数为1则方向正转
            StepperMotor_Direction_Backward, // 步数为-1则方向反转
            msg.Speed // 步进电机速度
          );
        }
        else if (pStepperMotor == NULL) { // 未知步进电机
          UartDmaStream_DebugPrintf(&gMainStream, "MotorActionTaskFunc: 传入未知的电机[%d]\n", msg.MotorID);
        }
        else { // 未知动作类型
          UartDmaStream_DebugPrintf(&gMainStream, "MotorActionTaskFunc: 传入未知的动作类型[%d]\n", msg.ActionType);
        }
      } // if (msg.RequestType == MotorActionRequestType_BasicMove)



      else if (msg.RequestType == MotorActionRequestType_MoveOnPlane) { // 平面行走
        ;
      } // else if (msg.RequestType == MotorActionRequestType_MoveOnPlane)



      else if (msg.RequestType == MotorActionRequestType_VerticalAxisRst) { // 竖轴位置重置
        if ( DigitalInput_IsTriggered(&gLimitSwitchVerticalAxis) ) { // 如果竖轴限位开关此时被触发着
          StepperMotor_MoveSteps(&gStepperMotorLift, 200, 500); // 竖轴步进电机先往离开限位器方向转200步
          while (StepperMotor_GetRunState(&gStepperMotorLift) == StepperMotor_RunState_MoveSteps); // 等待步进电机移动完成
        }
        IsLimitSwitchVerticalAxisExtiEnabled = true; // 竖轴限位开关中断使能标志位
        StepperMotor_RunContinuous(&gStepperMotorLift, StepperMotor_Direction_Backward, 500); // 竖轴步进电机持续往限位器方向转
      } // else if (msg.RequestType == MotorActionRequestType_VerticalAxisRst)



      else if (msg.RequestType == MotorActionRequestType_VerticalAxisMove) { // 竖轴位置
        int32_t steps = 1225.0f * msg.PositionZ / 100.0f; // 计算出要下降的步数
        StepperMotor_MoveSteps(&gStepperMotorLift, steps, 500); // 竖轴步进电机移动指定步数函数
        while (StepperMotor_GetRunState(&gStepperMotorLift) == StepperMotor_RunState_MoveSteps); // 等待步进电机移动完成
      } // else if (msg.RequestType == MotorActionRequestType_VerticalAxisMove)



      else if (msg.RequestType == MotorActionRequestType_SetMagnetStatus) { // 设置磁铁状态
        ElectronMagnet_SetStatus(msg.MagnetStatus); // 根据传入的磁铁状态设置磁铁
      } // else if (msg.RequestType == MotorActionRequestType_SetMagnetStatus)



      else { // 未知请求
        ;
      } // else



    }

    // 读取队列就已经包含延时操作
  }
}
