#include "Task_All.h"

/*这个线程用来执行所有电机的动作*/
void MotorActionTaskFunc(void *argument) {
  (void)argument;
  while (!IsAllInitOkay) { osDelay(100); }
  while (true) {
    Msg_MotorAction_t msg;
    if ( osMessageQueueGet(gMsgQueueMotorAction, &msg, NULL, 500) == osOK ) {
      if (msg.RequestType == MotorActionRequestType_BasicMove) { // 基础行走
        StepperMotor_MoveSteps( // 步进电机移动指定步数函数
          &gStepperMotorShoulder, // 肩关节步进电机
          msg.Steps, // 行走步数
          msg.Speed // 行走速度
        ); // Object, steps, speed
        StepperMotor_MoveSteps( // 步进电机移动指定步数函数
          &gStepperMotorElbow, // 肘关节步进电机
          msg.Steps, // 行走步数
          msg.Speed // 行走速度
        ); // Object, steps, speed
        StepperMotor_MoveSteps( // 步进电机移动指定步数函数
          &gStepperMotorLift, // 竖轴步进电机
          msg.Steps, // 行走步数
          msg.Speed // 行走速度
        ); // Object, steps, speed
        while (StepperMotor_GetRunState(&gStepperMotorShoulder) == StepperMotor_RunState_MoveSteps);
        while (StepperMotor_GetRunState(&gStepperMotorElbow) == StepperMotor_RunState_MoveSteps);
        while (StepperMotor_GetRunState(&gStepperMotorLift) == StepperMotor_RunState_MoveSteps);
      } // if (msg.RequestType == MotorActionRequestType_BasicMove)

      else if (msg.RequestType == MotorActionRequestType_MoveOnPlane) { // 平面行走
        ;
      } // else if (msg.RequestType == MotorActionRequestType_MoveOnPlane)

      else if (msg.RequestType == MotorActionRequestType_VerticalAxis) { // 竖轴位置
        ;
      } // else if (msg.RequestType == MotorActionRequestType_VerticalAxis)

      else { // 未知请求
        ;
      } // else
    }
    
  }
}
