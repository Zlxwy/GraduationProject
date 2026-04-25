# import threading
# from Thread_Recv import RecvThreadFunc
# from Thread_Cam import CamThreadFunc
# from Thread_Main import MainThreadFunc
import os
import cv2
import time
import math
import copy
import queue
import torch
import numpy as np
from torchvision import transforms

import GlobalVariable as gVar
from MyLibs.Log import Log
from MyLibs.UartStream import *
from MyLibs.SomeFunc import *
from MyLibs.ThreeStepperMotor import *
from MyLibs.BytesConv import BytesToUint16_BigEndian as b2u16
from MyLibs.BytesConv import BytesToUint32_BigEndian as b2u32
from MyLibs.BytesConv import BytesToUint64_BigEndian as b2u64
from MyLibs.BytesConv import BytesToInt16_BigEndian as b2s16
from MyLibs.BytesConv import BytesToInt32_BigEndian as b2s32
from MyLibs.BytesConv import BytesToInt64_BigEndian as b2s64
from MyLibs.BytesConv import BytesToFloat32_BigEndian as b2f32
from MyLibs.BytesConv import Uint16ToBytes_BigEndian as u162b
from MyLibs.BytesConv import Uint32ToBytes_BigEndian as u322b
from MyLibs.BytesConv import Uint64ToBytes_BigEndian as u642b
from MyLibs.BytesConv import Int16ToBytes_BigEndian as s162b
from MyLibs.BytesConv import Int32ToBytes_BigEndian as s322b
from MyLibs.BytesConv import Int64ToBytes_BigEndian as s642b
from MyLibs.BytesConv import Float32ToBytes_BigEndian as f322b
from MyLibs.ChessRecognition.ChessRecognizer import ChessRecognizer
from MyLibs.ChessEngine.ElephantFish import *
from MyLibs.ChessEngine.ChessInterface import *
from MyLibs.PlaneMapper import PlaneMapper





def MyDrawDoubleConnectingRod(img,
                              line1_length, line1_angle_deg,
                              line2_length, line2_angle_deg,
                              color=(0,255,0) ):
  """
  brief:
    绘制双连杆，直接输入机械臂坐标系中自身的角度就行，不是画面中的角度
  params:
    img: 要绘制的图像
    line1_length: 连杆A的长度
    line1_angle_deg: 连杆A的角度（度），极坐标系，0度为x轴正方向，顺时针旋转0度为正方向
    line2_length: 连杆B的长度
    line2_angle_deg: 连杆B的角度（度）
  """
  def calculate_dx_dy(pt_start, length, angle_deg):
    """
    brief:
      计算从点pt_start出发，长度为length，角度为angle_deg的线段，在XY方向上跨越的距离
    params:
      pt_start: 起始点 (x1, y1)
      length: 线段长度
      angle_deg: 角度（度）
    return:
      移动距离 (dx, dy)
    """
    # 三角函数就那么几个，都是循环周期函数，不需要检验其范围
    angle_rad = math.radians(angle_deg) # 将角度转换为弧度
    dx = length * math.cos(angle_rad) # 计算x方向上的移动距离
    dy = length * math.sin(angle_rad) # 计算y方向上的移动距离
    return dx, dy

  line1_pt_start = (0,0)
  line1_dx, line1_dy = calculate_dx_dy(line1_pt_start, line1_length, line1_angle_deg)
  line1_dx = round(line1_dx) # 四舍五入到最近的整数
  line1_dy = round(line1_dy) # 四舍五入到最近的整数
  line1_pt_end = ( line1_pt_start[0]+line1_dx, line1_pt_start[1]+line1_dy ) # 计算结束点
  
  line2_pt_start = line1_pt_end
  line2_dx, line2_dy = calculate_dx_dy(line2_pt_start, line2_length, line2_angle_deg)
  line2_dx = round(line2_dx) # 四舍五入到最近的整数
  line2_dy = round(line2_dy) # 四舍五入到最近的整数
  line2_pt_end = ( line2_pt_start[0]+line2_dx, line2_pt_start[1]+line2_dy ) # 计算结束点

  try:
    # 机械臂坐标系平面坐标 → cv2坐标系平面坐标，以便在画面中绘制箭头线段
    line1_pt_start = gVar.PlaneMapper_Arm2Cv.transform(line1_pt_start)
    line1_pt_end = gVar.PlaneMapper_Arm2Cv.transform(line1_pt_end)
    line2_pt_start = gVar.PlaneMapper_Arm2Cv.transform(line2_pt_start)
    line2_pt_end = gVar.PlaneMapper_Arm2Cv.transform(line2_pt_end)
    # 四舍五入到最近的整数，并转换成列表
    line1_pt_start = [round(x) for x in line1_pt_start]
    line1_pt_end   = [round(x) for x in line1_pt_end]
    line2_pt_start = [round(x) for x in line2_pt_start]
    line2_pt_end   = [round(x) for x in line2_pt_end]
  except Exception as e:
    gVar.logger.PrintString(f"Error: PlaneMapper_Arm2Cv 未初始化，错误信息：{e}")
    return

  cv2.arrowedLine(img, line1_pt_start, line1_pt_end, color, 5) # 绘制线段1
  cv2.arrowedLine(img, line2_pt_start, line2_pt_end, color, 5) # 绘制线段2





def mouse_callback(event, x, y, flags, param):
  """鼠标回调函数"""
  gVar.mouse_x = x
  gVar.mouse_y = y
  if event == cv2.EVENT_LBUTTONDOWN: gVar.LButtonDownFlag = True # 鼠标左键按下
  if event == cv2.EVENT_MOUSEMOVE: gVar.MouseMoveFlag = True # 鼠标移动 
  if event == cv2.EVENT_LBUTTONUP: gVar.LButtonUpFlag = True # 鼠标左键释放





def CreateCommand_VerticalAxisRst():
  """按照通信协议，构建垂直轴重置命令"""
  Bytes_CommandType = u162b(gVar.COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST)
  Bytes_VerticalAxisRst = Bytes_CommandType
  return Bytes_VerticalAxisRst

def CreateCommand_BasicMove(MotorId, ActionType, Steps, Speed):
  """按照通信协议，构建基本运动命令"""
  Bytes_CommandType = u162b(gVar.COMMAND_TYPE_MOTOR_BASIC_MOVE)
  Bytes_MotorId = bytes([MotorId & 0xFF])
  Bytes_ActionType = bytes([ActionType & 0xFF])
  Bytes_Steps = s642b(Steps)
  Bytes_Speed = u322b(Speed)
  Bytes_BasicMove = Bytes_CommandType + Bytes_MotorId + Bytes_ActionType + Bytes_Steps + Bytes_Speed
  return Bytes_BasicMove

def CreateCommand_SetElectroMagnet(status):
  """按照通信协议，构建设置电磁铁状态命令：0x00-禁用，0x01-正向电压使能，0x02-反向电压使能"""
  Bytes_CommandType = u162b(gVar.COMMAND_TYPE_SET_MAGNET_STATUS)
  Bytes_Status = bytes([status & 0xFF])
  Bytes_Electromagnet = Bytes_CommandType + Bytes_Status
  return Bytes_Electromagnet

def allocate_two_motor_time(dStepShoulder, dStepElbow, deg_per_sec):
  """
  brief:
    分配平面两轴速度，使得机械臂在need_time_ms内，移动dStepShoulder和dStepElbow步数
  params:
    dStepShoulder: 大臂步数
    dStepElbow: 小臂步数
    deg_per_sec: 1秒旋转的角度
  return:
    speed_shoulder: 大臂速度
    speed_elbow: 小臂速度
  """
  deg_angle_shoulder = abs(gVar.tsm.StepToPosition("Shoulder", dStepShoulder)) # 大臂需要旋转的角度
  deg_angle_elbow = abs(gVar.tsm.StepToPosition("Elbow", dStepElbow)) # 小臂需要旋转的角度
  deg_angle_max = max(deg_angle_shoulder, deg_angle_elbow) # 获取旋转角度最大的那个
  need_time = deg_angle_max / deg_per_sec # 以旋转角度最大的那个为准，计算需要旋转的时间
  speed_shoulder = abs(dStepShoulder) / need_time # 以得到的旋转时间计算大臂的速度
  speed_elbow = abs(dStepElbow) / need_time # 以得到的旋转时间计算小臂的速度
  gVar.logger.PrintString(f"deg_angle_shoulder: {deg_angle_shoulder}")
  gVar.logger.PrintString(f"deg_angle_elbow: {deg_angle_elbow}")
  gVar.logger.PrintString(f"deg_angle_max: {deg_angle_max}")
  gVar.logger.PrintString(f"need_time: {need_time}")
  gVar.logger.PrintString(f"speed_shoulder: {speed_shoulder}")
  gVar.logger.PrintString(f"speed_elbow: {speed_elbow}")
  return int(speed_shoulder), int(speed_elbow) # 以整数形式返回

# CreateCommandList_DriveMotor_XXXXXXXXXX(
#   StartPosIndex=[ord(gVar.PcMoveAgainstUser[0])-ord('a'), ord(gVar.PcMoveAgainstUser[1])-ord('0')],
#   TargetPosIndex=[ord(gVar.PcMoveAgainstUser[2])-ord('a'), ord(gVar.PcMoveAgainstUser[3])-ord('0')]
# ) # 调用示例
def CreateCommandList_DriveMotor_DropSelfPiece(StartPosIndex, TargetPosIndex):
  """
  brief:
    按照通信协议，构建一个指令列表，驱动机械臂执行【落子操作】，指令共12条。
    - 1.移动大臂到起始位置的指定角度
    - 2.移动小臂到起始位置的指定角度
    - 3.竖轴下降
    - 4.电磁铁通电
    - 5.竖轴上升
    - 6.移动大臂到目标位置的指定角度
    - 7.移动小臂到目标位置的指定角度
    - 8.竖轴下降
    - 9.电磁铁断电
    - 10.竖轴上升
    - 11.移动大臂到待机位置的指定角度
    - 12.移动小臂到待机位置的指定角度
  params:
    StartPosIndex: 起始位置CV坐标的索引
    TargetPosIndex: 目标位置CV坐标的索引
  """
  deg_per_sec = 60.0 # 1秒旋转90度
  speed_lift = 1500 # 竖轴速度

  # 计算起点位置时，两个机械臂的角度
  CvPlane_StartPos = gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ StartPosIndex[0] ] [ StartPosIndex[1] ] # 以棋盘交点的位置
  try:
    ArmPlane_StartPos = gVar.PlaneMapper_Cv2Arm.transform(CvPlane_StartPos) # 转换为机械臂的平面坐标系
    DegAngle_StartPos_Shoulder, DegAngle_StartPos_Elbow = decompose_vector( # 矢量分解，计算双连杆角度
      gVar.LengthOfShoulder, # 大臂长度
      gVar.LengthOfElbow, # 小臂长度
      ArmPlane_StartPos[0], # 起始位置的X坐标
      ArmPlane_StartPos[1] # 起始位置的Y坐标
    )
  except Exception as e:
    gVar.logger.PrintString(f"Error: 执行落子操作中，计算[起始点]的双连杆角度失败 {e}")

  # 此时获得了DegAngle_StartPos_Shoulder, DegAngle_StartPos_Elbow，开始组合指令
  dStepShoulder, dStepElbow, dStepLift = gVar.tsm.DRIVE_MOTOR(DegAngle_StartPos_Shoulder, DegAngle_StartPos_Elbow, 100.0) # 更新三轴的位置，并获取转动步数
  speed_shoulder, speed_elbow = allocate_two_motor_time(dStepShoulder, dStepElbow, deg_per_sec) # 分配平面两轴速度
  cmd1 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorShoulder_Index, ActionType=0x01, Steps=dStepShoulder, Speed=speed_shoulder) # 指令1：移动大臂到起始位置的指定角度
  cmd2 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorElbow_Index, ActionType=0x01, Steps=dStepElbow, Speed=speed_elbow) # 指令2：移动小臂到起始位置的指定角度
  cmd3 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=speed_lift) # 指令3：竖轴下降
  cmd4 = CreateCommand_SetElectroMagnet(status=0x01) # 指令4：电磁铁通电

  _, _, dStepLift = gVar.tsm.DRIVE_MOTOR(gVar.tsm.PositionShoulder, gVar.tsm.PositionElbow, 0.0) # 只更新竖轴位置为0.0
  cmd5 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=speed_lift) # 指令5：竖轴上升

  # 计算目标位置时，两个机械臂的角度
  CvPlane_TargetPos = gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ TargetPosIndex[0] ] [ TargetPosIndex[1] ] # 目标点是肯定没有棋子，所以要以棋盘交点的位置为准
  try:
    ArmPlane_TargetPos = gVar.PlaneMapper_Cv2Arm.transform(CvPlane_TargetPos) # 转换为机械臂的平面坐标系
    DegAngle_TargetPos_Shoulder, DegAngle_TargetPos_Elbow = decompose_vector( # 矢量分解，计算双连杆角度
      gVar.LengthOfShoulder, # 大臂长度
      gVar.LengthOfElbow, # 小臂长度
      ArmPlane_TargetPos[0], # 目标位置的X坐标
      ArmPlane_TargetPos[1] # 目标位置的Y坐标
    )
  except Exception as e:
    gVar.logger.PrintString(f"Error: 执行落子操作中，计算[目标点]的双连杆角度失败 {e}")

  # 此时获得了DegAngle_TargetPos_Shoulder, DegAngle_TargetPos_Elbow，开始组合指令
  dStepShoulder, dStepElbow, dStepLift = gVar.tsm.DRIVE_MOTOR(DegAngle_TargetPos_Shoulder, DegAngle_TargetPos_Elbow, 100.0) # 更新三轴的位置，并获取转动步数
  speed_shoulder, speed_elbow = allocate_two_motor_time(dStepShoulder, dStepElbow, deg_per_sec) # 分配平面两轴速度
  cmd6 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorShoulder_Index, ActionType=0x01, Steps=dStepShoulder, Speed=speed_shoulder) # 指令6：移动大臂到目标位置的指定角度
  cmd7 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorElbow_Index, ActionType=0x01, Steps=dStepElbow, Speed=speed_elbow) # 指令7：移动小臂到目标位置的指定角度
  cmd8 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=speed_lift) # 指令8：竖轴下降
  cmd9 = CreateCommand_SetElectroMagnet(status=0x00) # 指令9：电磁铁断电

  _, _, dStepLift = gVar.tsm.DRIVE_MOTOR(gVar.tsm.PositionShoulder, gVar.tsm.PositionElbow, 0.0) # 只更新竖轴位置为0.0
  # cmd10 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=200) # 指令10：竖轴上升
  cmd10 = CreateCommand_VerticalAxisRst() # 指令10：竖轴重置（其实也就是上升到顶点了，这最后一步就调用竖轴复位指令吧）

  # 组合向待机位移动的指令
  dStepShoulder, dStepElbow, dStepLift = gVar.tsm.DRIVE_MOTOR(gVar.DegAngle_StandByPos_Shoulder, gVar.DegAngle_StandByPos_Ebow, gVar.DegAngle_StandByPos_Lift) # 更新三轴的位置，并获取转动步数
  speed_shoulder, speed_elbow = allocate_two_motor_time(dStepShoulder, dStepElbow, deg_per_sec) # 分配平面两轴速度
  cmd11 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorShoulder_Index, ActionType=0x01, Steps=dStepShoulder, Speed=speed_shoulder) # 指令11：移动大臂到待机位置的指定角度
  cmd12 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorElbow_Index, ActionType=0x01, Steps=dStepElbow, Speed=speed_elbow) # 指令12：移动小臂到待机位置的指定角度
  
  return [cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7, cmd8, cmd9, cmd10, cmd11, cmd12] # 指令列表，每个元素都是一个字节数组

def CreateCommandList_DriveMotor_CapOppoPiece(StartPosIndex, TargetPosIndex):
  """
  brief:
    创建一个指令列表，驱动机械臂执行【捕获对方棋子操作】，指令共12条。
    - 1.移动大臂到吃子位置的指定角度
    - 2.移动小臂到吃子位置的指定角度
    - 3.竖轴下降
    - 4.电磁铁通电
    - 5.竖轴上升
    - 6.移动大臂到吃子盒位置的指定角度
    - 7.移动小臂到吃子盒位置的指定角度
    - 8.竖轴下降20%
    - 9.电磁铁断电
    - 10.竖轴上升
    - 11.移动大臂到起始位置的指定角度
    - 12.移动小臂到起始位置的指定角度
    - 13.竖轴下降
    - 14.电磁铁通电
    - 15.竖轴上升
    - 16.移动大臂到目标位置的指定角度
    - 17.移动小臂到目标位置的指定角度
    - 18.竖轴下降
    - 19.电磁铁断电
    - 20.竖轴上升
    - 21.移动大臂到待机位置的指定角度
    - 22.移动小臂到待机位置的指定角度
  Args:
    StartPosIndex: 起始位置CV坐标的索引
    TargetPosIndex: 目标位置CV坐标的索引
  """
  deg_per_sec = 60.0 # 1秒旋转90度
  speed_lift = 1500 # 竖轴速度

  # 计算被吃子位置时，两个机械臂的角度
  CvPlane_EatedPiece = gVar.ChessBoard_ChessPiecePointsGrid_CvPlane [ TargetPosIndex[0] ] [ TargetPosIndex[1] ] # 被吃棋子的位置，要以棋子实际位置为准，而不是棋盘交点的位置
  try:
    ArmPlane_EatedPiecePos = gVar.PlaneMapper_Cv2Arm.transform(CvPlane_EatedPiece) # 转换为机械臂的平面坐标系
    DegAngle_EatedPiecePos_Shoulder, DegAngle_EatedPiecePos_Elbow = decompose_vector( # 矢量分解，计算双连杆角度
      gVar.LengthOfShoulder, # 大臂长度
      gVar.LengthOfElbow, # 小臂长度
      ArmPlane_EatedPiecePos[0], # 被吃棋子位置的X坐标
      ArmPlane_EatedPiecePos[1] # 被吃棋子位置的Y坐标
    )
  except Exception as e:
    gVar.logger.PrintString(f"Error: 执行吃子操作中，计算[被吃棋子]的双连杆角度失败 {e}")
  
  # 此时获得了DegAngle_EatedPiecePos_Shoulder, DegAngle_EatedPiecePos_Elbow，开始组合指令
  dStepShoulder, dStepElbow, dStepLift = gVar.tsm.DRIVE_MOTOR(DegAngle_EatedPiecePos_Shoulder, DegAngle_EatedPiecePos_Elbow, 100.0) # 更新三轴的位置，并获取转动步数
  speed_shoulder, speed_elbow = allocate_two_motor_time(dStepShoulder, dStepElbow, deg_per_sec) # 分配平面两轴速度
  cmd1 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorShoulder_Index, ActionType=0x01, Steps=dStepShoulder, Speed=speed_shoulder) # 指令1：移动大臂到吃子位置的指定角度
  cmd2 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorElbow_Index, ActionType=0x01, Steps=dStepElbow, Speed=speed_elbow) # 指令2：移动小臂到吃子位置的指定角度
  cmd3 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=speed_lift) # 指令3：竖轴下降
  cmd4 = CreateCommand_SetElectroMagnet(status=0x01) # 指令4：电磁铁通电
  
  _, _, dStepLift = gVar.tsm.DRIVE_MOTOR(gVar.tsm.PositionShoulder, gVar.tsm.PositionElbow, 0.0) # 只更新竖轴位置为0.0
  cmd5 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=800) # 指令5：竖轴上升

  try:
    DegAngle_CapBoxPos_Shoulder, DegAngle_CapBoxPos_Elbow = decompose_vector( # 矢量分解，计算双连杆角度
      gVar.LengthOfShoulder, # 大臂长度
      gVar.LengthOfElbow, # 小臂长度
      gVar.ChessBoard_CapBox_ArmPlane[0], # 吃子盒位置的X坐标
      gVar.ChessBoard_CapBox_ArmPlane[1] # 吃子盒位置的Y坐标
    )
  except Exception as e:
    gVar.logger.PrintString(f"Error: 执行【吃子操作】中，计算【吃子盒】的双连杆角度失败 {e}")
  
  dStepShoulder, dStepElbow, dStepLift = gVar.tsm.DRIVE_MOTOR(DegAngle_CapBoxPos_Shoulder, DegAngle_CapBoxPos_Elbow, 20.0) # 更新三轴的位置，并获取转动步数
  speed_shoulder, speed_elbow = allocate_two_motor_time(dStepShoulder, dStepElbow, deg_per_sec) # 分配平面两轴速度
  cmd6 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorShoulder_Index, ActionType=0x01, Steps=dStepShoulder, Speed=speed_shoulder) # 指令6：移动大臂到吃子盒位置的指定角度
  cmd7 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorElbow_Index, ActionType=0x01, Steps=dStepElbow, Speed=speed_elbow) # 指令7：移动小臂到吃子盒位置的指定角度
  cmd8 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=speed_lift) # 指令8：竖轴下降20%
  cmd9 = CreateCommand_SetElectroMagnet(status=0x00) # 指令9：电磁铁断电

  _, _, dStepLift = gVar.tsm.DRIVE_MOTOR(gVar.tsm.PositionShoulder, gVar.tsm.PositionElbow, 0.0) # 只更新竖轴位置为0.0
  cmd10 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=speed_lift) # 指令10：竖轴上升

  # 计算起点位置时，两个机械臂的角度
  CvPlane_StartPos = gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ StartPosIndex[0] ] [ StartPosIndex[1] ] # 以棋盘交点的位置
  try:
    ArmPlane_StartPos = gVar.PlaneMapper_Cv2Arm.transform(CvPlane_StartPos) # 转换为机械臂的平面坐标系
    DegAngle_StartPos_Shoulder, DegAngle_StartPos_Elbow = decompose_vector( # 矢量分解，计算双连杆角度
      gVar.LengthOfShoulder, # 大臂长度
      gVar.LengthOfElbow, # 小臂长度
      ArmPlane_StartPos[0], # 起始位置的X坐标
      ArmPlane_StartPos[1] # 起始位置的Y坐标
    )
  except Exception as e:
    gVar.logger.PrintString(f"Error: 执行【吃子操作】中，计算【起始位置】的双连杆角度失败 {e}")

  # 此时获得了DegAngle_StartPos_Shoulder, DegAngle_StartPos_Elbow，开始组合指令
  dStepShoulder, dStepElbow, dStepLift = gVar.tsm.DRIVE_MOTOR(DegAngle_StartPos_Shoulder, DegAngle_StartPos_Elbow, 100.0) # 更新三轴的位置，并获取转动步数
  speed_shoulder, speed_elbow = allocate_two_motor_time(dStepShoulder, dStepElbow, deg_per_sec) # 分配平面两轴速度
  cmd11 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorShoulder_Index, ActionType=0x01, Steps=dStepShoulder, Speed=speed_shoulder) # 指令11：移动大臂到起始位置的指定角度
  cmd12 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorElbow_Index, ActionType=0x01, Steps=dStepElbow, Speed=speed_elbow) # 指令12：移动小臂到起始位置的指定角度
  cmd13 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=speed_lift) # 指令13：竖轴下降
  cmd14 = CreateCommand_SetElectroMagnet(status=0x01) # 指令14：电磁铁通电

  _, _, dStepLift = gVar.tsm.DRIVE_MOTOR(gVar.tsm.PositionShoulder, gVar.tsm.PositionElbow, 0.0) # 只更新竖轴位置为0.0
  cmd15 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=speed_lift) # 指令15：竖轴上升

  # 计算目标位置时，两个机械臂的角度
  CvPlane_TargetPos = gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ TargetPosIndex[0] ] [ TargetPosIndex[1] ] # 目标点是肯定没有棋子，所以要以棋盘交点的位置为准
  try:
    ArmPlane_TargetPos = gVar.PlaneMapper_Cv2Arm.transform(CvPlane_TargetPos) # 转换为机械臂的平面坐标系
    DegAngle_TargetPos_Shoulder, DegAngle_TargetPos_Elbow = decompose_vector( # 矢量分解，计算双连杆角度
      gVar.LengthOfShoulder, # 大臂长度
      gVar.LengthOfElbow, # 小臂长度
      ArmPlane_TargetPos[0], # 目标位置的X坐标
      ArmPlane_TargetPos[1] # 目标位置的Y坐标
    )
  except Exception as e:
    gVar.logger.PrintString(f"Error: 执行吃子操作中，计算[目标位置]的双连杆角度失败 {e}")

  # 此时获得了DegAngle_TargetPos_Shoulder, DegAngle_TargetPos_Elbow，开始组合指令
  dStepShoulder, dStepElbow, dStepLift = gVar.tsm.DRIVE_MOTOR(DegAngle_TargetPos_Shoulder, DegAngle_TargetPos_Elbow, 100.0) # 更新三轴的位置，并获取转动步数
  speed_shoulder, speed_elbow = allocate_two_motor_time(dStepShoulder, dStepElbow, deg_per_sec) # 分配平面两轴速度
  cmd16 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorShoulder_Index, ActionType=0x01, Steps=dStepShoulder, Speed=speed_shoulder) # 指令16：移动大臂到目标位置的指定角度
  cmd17 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorElbow_Index, ActionType=0x01, Steps=dStepElbow, Speed=speed_elbow) # 指令17：移动小臂到目标位置的指定角度
  cmd18 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=speed_lift) # 指令18：竖轴下降
  cmd19 = CreateCommand_SetElectroMagnet(status=0x00) # 指令19：电磁铁断电

  _, _, dStepLift = gVar.tsm.DRIVE_MOTOR(gVar.tsm.PositionShoulder, gVar.tsm.PositionElbow, 0.0) # 只更新竖轴位置为0.0
  # cmd20 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorLift_Index, ActionType=0x01, Steps=dStepLift, Speed=200) # 指令20：竖轴上升
  cmd20 = CreateCommand_VerticalAxisRst() # 指令20：竖轴重置（其实也就是上升到顶点了，这最后一步就调用竖轴复位指令吧）

  # 组合向待机位移动的指令
  dStepShoulder, dStepElbow, dStepLift = gVar.tsm.DRIVE_MOTOR(gVar.DegAngle_StandByPos_Shoulder, gVar.DegAngle_StandByPos_Ebow, gVar.DegAngle_StandByPos_Lift) # 更新三轴的位置，并获取转动步数
  speed_shoulder, speed_elbow = allocate_two_motor_time(dStepShoulder, dStepElbow, deg_per_sec) # 分配平面两轴速度
  cmd21 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorShoulder_Index, ActionType=0x01, Steps=dStepShoulder, Speed=speed_shoulder) # 指令21：移动大臂到待机位置的指定角度
  cmd22 = CreateCommand_BasicMove(MotorId=gVar.StepperMotorElbow_Index, ActionType=0x01, Steps=dStepElbow, Speed=speed_elbow) # 指令22：移动小臂到待机位置的指定角度

  return [cmd1, cmd2, cmd3, cmd4, cmd5, cmd6, cmd7, cmd8, cmd9, cmd10, cmd11, cmd12, cmd13, cmd14, cmd15, cmd16, cmd17, cmd18, cmd19, cmd20, cmd21, cmd22] # 指令列表，每个元素都是一个字节数组





def ChessEngine_CallFunc():
  """象棋引擎调用函数，将会用于主线程中创建子线程进行异步调用"""
  try:
    gVar.ChessEngine_Result = ElephantFishChessSE(gVar.UserMove)
  except Exception as e:
    gVar.logger.PrintString(f"ChessEngine_CallThread Info: 调用象棋引擎失败，错误信息：{e}")
  finally:
    gVar.ChessEngine_IsRunning = False
    gVar.ChessEngine_ResultFinished = True















if __name__ == "__main__":
  if gVar.MyDevice == "Linux": # 如果是Linux系统，全局限制线程数为1，避免多线程导致的性能问题
    os.environ["OMP_NUM_THREADS"] = "1" # 设置OMP线程数为1
    os.environ["MKL_NUM_THREADS"] = "1" # 设置MKL线程数为1
    os.environ["OPENBLAS_NUM_THREADS"] = "1" # 设置OpenBLAS线程数为1





  gVar.logger = Log() # 创建Log实例
  gVar.logger.PrintString("Info: 日志打印对象已初始化，可前往./Logs/目录下查看") # 打印Log已初始化信息





  # recv_thread = threading.Thread(target=RecvThreadFunc) # 接收线程，非守护线程，通过exit_flag通知退出
  # gVar.logger.PrintString("Main Info: Thread_Recv has created.") # 打印 Thread_Recv 已创建信息
  # recv_thread.start() # 启动接收线程
  # gVar.logger.PrintString("Main Info: Thread_Recv has started.") # 打印 Thread_Recv 已启动信息





  gVar.PlaneMapper_Cv2Arm = PlaneMapper(gVar.ChessBoard_InnerCorners_CvPlane, gVar.ChessBoard_InnerCorners_ArmPlane) # 平面映射对象，通过单应性变换将CV坐标转换为机械臂坐标
  gVar.PlaneMapper_Arm2Cv = PlaneMapper(gVar.ChessBoard_InnerCorners_ArmPlane, gVar.ChessBoard_InnerCorners_CvPlane) # 平面映射对象，通过单应性变换将机械臂坐标转换为CV坐标
  gVar.ChessBoard_OuterCorner_TopLeft_CvPlane  = gVar.PlaneMapper_Arm2Cv.transform(gVar.ChessBoard_OuterCorner_TopLeft_ArmPlane) # 将现实世界的外部角点坐标，映射到画面坐标
  gVar.ChessBoard_OuterCorner_TopRight_CvPlane = gVar.PlaneMapper_Arm2Cv.transform(gVar.ChessBoard_OuterCorner_TopRight_ArmPlane) # 将现实世界的外部角点坐标，映射到画面坐标
  gVar.ChessBoard_OuterCorner_BotRight_CvPlane = gVar.PlaneMapper_Arm2Cv.transform(gVar.ChessBoard_OuterCorner_BotRight_ArmPlane) # 将现实世界的外部角点坐标，映射到画面坐标
  gVar.ChessBoard_OuterCorner_BotLeft_CvPlane  = gVar.PlaneMapper_Arm2Cv.transform(gVar.ChessBoard_OuterCorner_BotLeft_ArmPlane) # 将现实世界的外部角点坐标，映射到画面坐标
  gVar.ChessBoard_OuterCorner_TopLeft_CvPlane  = [round(x) for x in gVar.ChessBoard_OuterCorner_TopLeft_CvPlane  ] # 四舍五入并转为列表
  gVar.ChessBoard_OuterCorner_TopRight_CvPlane = [round(x) for x in gVar.ChessBoard_OuterCorner_TopRight_CvPlane ] # 四舍五入并转为列表
  gVar.ChessBoard_OuterCorner_BotRight_CvPlane = [round(x) for x in gVar.ChessBoard_OuterCorner_BotRight_CvPlane ] # 四舍五入并转为列表
  gVar.ChessBoard_OuterCorner_BotLeft_CvPlane  = [round(x) for x in gVar.ChessBoard_OuterCorner_BotLeft_CvPlane  ] # 四舍五入并转为列表
  gVar.ChessBoard_OuterCorners_CvPlane = [ # 棋盘外部角点阵列，为一个(4,2)的二维列表
    gVar.ChessBoard_OuterCorner_TopLeft_CvPlane, # 左上角点
    gVar.ChessBoard_OuterCorner_TopRight_CvPlane, # 右上角点
    gVar.ChessBoard_OuterCorner_BotRight_CvPlane, # 右下角点
    gVar.ChessBoard_OuterCorner_BotLeft_CvPlane, # 左下角点
  ]





  try:
    UartDevice = None # 初始为None
    match gVar.MyDevice: # 根据不同设备选择不同的串口设备
      case "Windows": UartDevice = "COM9"
      case "Linux": UartDevice = "/dev/ttyS1"
      case _: UartDevice = None
    gVar.MainStream = UartStream(port=UartDevice, baudrate=115200) # 创建 UartStream 实例
    gVar.MainStream.start() # 启动 UartStream 实例
    gVar.logger.PrintString("Info: 串口流已成功启动") # 打印 UartStream 实例已启动信息
  except Exception as e:
    gVar.logger.PrintString(f"Error: 串口流初始化失败")
    gVar.logger.PrintString(f"Error: {e}")
    exit(0) # 如果串口启动失败，直接退出程序





  # 因为在多线程中运行模型识别太慢了，所以把运行模型识别的代码放到主线程中
  gVar.ChessModel_Recognizer = ChessRecognizer( # 棋子识别器封装成了一个类，实例化
    chess_model_path=os.path.join( # 模型文件路径
      os.path.dirname(os.path.abspath(__file__)), # 获取当前文件所在目录的绝对路径
      "MyLibs/ChessRecognition/chess_mobilenetv3.pt" # 模型文件相对于当前文件所在目录的路径
    ),
    chess_model_val_transform=transforms.Compose([ # 模型输入数据预处理流程
      transforms.ToPILImage(), # 将输入数据转换为PIL图像
      transforms.Resize((gVar.ChessModel_InputSize, gVar.ChessModel_InputSize)), # 将图像缩放到指定大小
      transforms.ToTensor(), # 将图像转换为张量
      transforms.Normalize([0.5] * 3, [0.5] * 3), # 对图像进行归一化处理
    ]),
    hough_minDist=gVar.HOUGH_MIN_DIST, # 霍夫圆变换参数：圆心之间的最小距离
    hough_param1=gVar.HOUGH_PARAM1, # 霍夫圆变换参数：圆心检测的累加器阈值
    hough_param2=gVar.HOUGH_PARAM2, # 霍夫圆变换参数：圆心检测的累加器阈值
    hough_minRadius=gVar.HOUGH_MIN_RADIUS, # 霍夫圆变换参数：圆的最小半径
    hough_maxRadius=gVar.HOUGH_MAX_RADIUS, # 霍夫圆变换参数：圆的最大半径
    lower_red1=np.array([0, 43, 46]), # 棋子红黑色检测参数：红色1下界
    upper_red1=np.array([10, 255, 255]), # 棋子红黑色检测参数：红色1上界
    lower_red2=np.array([170, 43, 46]), # 棋子红黑色检测参数：红色2下界
    upper_red2=np.array([180, 255, 255]), # 棋子红黑色检测参数：红色2上界
    # 因为红色在 HSV 颜色环里分成两段，所以必须用两组上下界才能完整检测到所有红色
    red_ratio_threshold=0.05 # 棋子红黑色检测参数：红色占比阈值
  )





  gVar.ChessBoard_IntersectionPointsGrid_CvPlane = GetAllIntersectionPointOfTable_Perspective( # 获取棋盘表格的所有交点坐标，符合透视变换标准
    pts=gVar.ChessBoard_InnerCorners_CvPlane, # 棋盘内部角点坐标阵列，是一个(4,2)的二维列表
    rows=gVar.ChessBoard_Rows, # 棋盘行数：9，这是表格空格的行数，而不是横线的行数
    cols=gVar.ChessBoard_Cols # 棋盘列数：8，这是表格空格的列数，而不是竖线的列数
  ) # 返回值是一个(10,9,2)的三维列表
  gVar.ChessBoard_ChessSituation_ForChessEngine = [list(row) for row in INIT_CHESSBOARD] # 初始化棋盘状态为初始状态，这个的数据是和棋盘引擎绑定的

  gVar.ChessBoard_ChessPiecePointsGrid_CvPlane = GetAllIntersectionPointOfTable_Perspective( # 获取棋盘表格的所有交点坐标，符合透视变换标准
    pts=gVar.ChessBoard_InnerCorners_CvPlane, # 棋盘内部角点坐标阵列，是一个(4,2)的二维列表
    rows=gVar.ChessBoard_Rows, # 棋盘行数：9，这是表格空格的行数，而不是横线的行数
    cols=gVar.ChessBoard_Cols # 棋盘列数：8，这是表格空格的列数，而不是竖线的列数
  ) # 返回值是一个(10,9,2)的三维列表，也初始化为棋盘的所有交点坐标，如果交点附近有棋子则更新为棋子坐标，这个的数据来源将会是棋盘识别器
  gVar.ChessBoard_ChessSituation_FromRecognizer = [ [NOCHESS for _ in range (gVar.ChessBoard_Cols+1)] for _ in range(gVar.ChessBoard_Rows+1) ] # 初始化棋盘状态为无棋子，这个的数据来源将会是棋盘识别器





  cam_index = None # 摄像头索引
  match gVar.MyDevice:
    case "Windows": cam_index = 1 # Windows原本有一个摄像头，所以接入的这个摄像头索引为1了
    case "Linux": cam_index = 0 # Linux默认有一个摄像头，所以接入的这个摄像头索引为0了
    case _: cam_index = None # 其他设备默认不接入摄像头
  gVar.Cap = cv2.VideoCapture(cam_index) # 打开摄像头
  if not gVar.Cap.isOpened(): # 如果摄像头未成功打开
    gVar.logger.PrintString("Info: 打开摄像头失败~~~")
    exit(0) # 直接退出程序
  else:
    gVar.logger.PrintString("Info: 打开摄像头成功！！！") # 打印成功信息
  
  gVar.Cap.set(cv2.CAP_PROP_FRAME_WIDTH, gVar.CapWidth) # 设置捕获图像宽度
  gVar.Cap.set(cv2.CAP_PROP_FRAME_HEIGHT, gVar.CapHeight) # 设置捕获图像高度
  gVar.logger.PrintString(f"Info: 摄像头分辨率为 {gVar.CapWidth}*{gVar.CapHeight}") # 打印成功信息

  cv2.namedWindow("frame_roi", cv2.WINDOW_NORMAL) # 创建名为"frame_roi"的窗口
  cv2.resizeWindow("frame_roi", 1000, 1000) # 调整窗口大小
  cv2.setMouseCallback("frame_roi", mouse_callback) # 设置鼠标回调函数





  gVar.tsm = ThreeStepperMotor() # 初始化三轴步进电机对象，用于维护其角度位置信息
  gVar.CurrMode = gVar.MODE_STANDBY # 初始化系统模式为待机模式
  gVar.IsDrawTwoLine = False # 是否显示双连杆线段
  gVar.IsAnchorVisible = False # 是否显示棋盘表格
  gVar.IsArranged = False # 棋子是否整理完成
  gVar.IsGameRunning = False # 是否正在对弈中
  gVar.IsGameOver = False # 当前对局是否结束
  gVar.IsUserTurn = False  # True用户回合，False电脑回合
  gVar.UserMove = "" # 用户的移动
  gVar.PcMoveAgainstUser = "" # 电脑的移动
  gVar.IsUserWin = False # 用户是否赢了
  gVar.IsPcWin = False # 电脑是否赢了





  gVar.ChessEngine_IsRunning = False # 象棋引擎是否正在运行
  gVar.ChessEngine_ResultFinished = False # 象棋引擎是否计算完成





  while 1: # 如果退出标志位还没置起



    ret, frame_origin = gVar.Cap.read() # 读取一帧图像
    if not ret: # 如果读取失败
      gVar.logger.PrintString("Error: 读取图像失败")
      continue # 跳过当前循环，继续下一次循环
    frame_roi = frame_origin[ # 只截取中间1080*1080的区域，可以直接把整张图像放进去
      gVar.RoiStartY : gVar.RoiStartY + gVar.RoiHeight,
      gVar.RoiStartX : gVar.RoiStartX + gVar.RoiWidth
    ] # 提取ROI区域
    frame_roi_cp = frame_roi.copy() # 复制ROI区域，一张纯净的图像帧，用来进行一些识别操作
    cv2.putText(frame_roi, f"{gVar.CurrMode}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)





    if gVar.IsDrawTwoLine: # 如果需要绘制双连杆线段（按q键切换显示）
      # 根据标定线的角度，绘制双连杆线段
      MyDrawDoubleConnectingRod( # 这个函数是以笛卡尔坐标系来绘制双连杆线段的
        frame_roi, # 输入的图像帧
        gVar.LengthOfShoulder, # 肩关节长度
        gVar.DegAngle_Runtime_Shoulder, # 肩关节角度
        gVar.LengthOfElbow, # 肘关节长度
        gVar.DegAngle_Runtime_Elbow, # 肘关节实时角度
      )
    if gVar.IsAnchorVisible: # 如果棋盘表格显示（按w键切换显示）
      DrawTable_Perspective(frame_roi, gVar.ChessBoard_InnerCorners_CvPlane, gVar.ChessBoard_Rows, gVar.ChessBoard_Cols, (0,255,0), 2)
      DrawIrregularQuad(frame_roi, gVar.ChessBoard_OuterCorners_CvPlane, (0,255,0), 2) # 绘制棋盘外部范围四边形
      # 绘制棋盘表格的所有交点
      for i, row in enumerate(gVar.ChessBoard_IntersectionPointsGrid_CvPlane): # 遍历棋盘表格的第1维度
        for j, (x, y) in enumerate(row): # 遍历棋盘表格的第2维度
          cv2.circle(frame_roi, (x, y), 10, [255,255,0], 2) # 圈一下交点
          cv2.putText(frame_roi, f"{i*len(row)+j}", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, [255,0,0], 3) # 绘制交点的索引，观察顺序
      # 读取鼠标的坐标，找到此时距离鼠标坐标最近的交点，用红色圆圈标记出来
      nearest_point, min_dist, nearest_row, nearest_col = find_nearest_intersection((gVar.mouse_x, gVar.mouse_y), gVar.ChessBoard_IntersectionPointsGrid_CvPlane)
      if nearest_point != None: # 如果最近的交点不是None，则绘制最近的交点
        cv2.circle(frame_roi, gVar.ChessBoard_IntersectionPointsGrid_CvPlane[nearest_row][nearest_col], 10, [0,0,255], 2)
      # 读取鼠标的坐标，如果鼠标的坐标在棋盘范围内，则用红色重绘表格，这样效果就是，鼠标移动到棋盘范围内，棋盘表格就会变成红色
      if is_point_in_quad((gVar.mouse_x, gVar.mouse_y), gVar.ChessBoard_InnerCorners_CvPlane): # 如果鼠标坐标在棋盘内角点的范围内
        DrawTable_Perspective(frame_roi, gVar.ChessBoard_InnerCorners_CvPlane, gVar.ChessBoard_Rows, gVar.ChessBoard_Cols, (0,0,255), 2) # 用红色绘制棋盘表格
      if is_point_in_quad((gVar.mouse_x, gVar.mouse_y), gVar.ChessBoard_OuterCorners_CvPlane): # 如果鼠标坐标在棋盘外角点的范围内
        DrawIrregularQuad(frame_roi, gVar.ChessBoard_OuterCorners_CvPlane, (0,0,255), 2) # 用红色绘制棋盘外部范围四边形





    if gVar.CurrMode == gVar.MODE_STANDBY: # 如果当前模式是待机模式，需要干什么
      ArmPlane_YouXia = gVar.PlaneMapper_Cv2Arm.transform(gVar.ChessBoard_IntersectionPointsGrid_CvPlane[9][8])
      try:
        DegAngle_Shoulder, DegAngle_Elbow = decompose_vector(
          gVar.LengthOfShoulder, # 肩关节长度
          gVar.LengthOfElbow, # 腕关节长度
          ArmPlane_YouXia[0], # 目标点的x坐标
          ArmPlane_YouXia[1] # 目标点的y坐标
        )
        # gVar.logger.PrintString(f"Info: DegAngle_Runtime_Shoulder = {DegAngle_Runtime_Shoulder}")
        # gVar.logger.PrintString(f"Info: DegAngle_Elbow = {DegAngle_Elbow}")
        MyDrawDoubleConnectingRod(
          frame_roi, # 输入的图像帧
          gVar.LengthOfShoulder, # 肩关节长度
          DegAngle_Shoulder, # 标定线1的角度，也就是肩关节角度
          gVar.LengthOfElbow, # 腕关节长度
          DegAngle_Elbow, # 标定线2的角度，也就是肘关节角度
        )
      except ValueError as e: # 如果分解角度失败
        gVar.logger.PrintString(f"MainThread Info: Failed to decompose vector.")
        gVar.logger.PrintString(f"Decompose Vector: {e}")
      pass



    elif gVar.CurrMode == gVar.MODE_CALIBRATION: # 如果当前模式是机械臂标定模式，需要干什么
      # 提示用户按Enter键返回待机模式，且会重置两个机械臂的角度；按Esc键不进行任何操作，按空格键确认标定
      text_color = [0, 255, 0]
      cv2.putText(frame_roi, "If press ENTER to return to standby mode,", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
      cv2.putText(frame_roi, "it will execute calibration operation!!!", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
      cv2.putText(frame_roi, "If press 'Esc' to return to standby mode,", (10,130), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
      cv2.putText(frame_roi, "it will not do any operation.", (10,160), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
      if gVar.IsCalibrateChessBoard: # 如果正在标定棋盘模式
        # 在画面中拖拽棋盘內部的四个角点，使其与棋盘表格的四个角点对齐，实现棋盘的标定操作
        if gVar.LButtonDownFlag: # 如果左键按下标志位触发
          gVar.LButtonDownFlag = False # 清除左键按下标志位
          gVar.is_pressed = True # 设置按下状态
          mx = gVar.mouse_x # 存定鼠标x坐标
          my = gVar.mouse_y # 存定鼠标y坐标
          # 在鼠标按下时，判断鼠标离哪一个点最近，然后将其引用为CvPlane_ChangeReference，之后这个点会跟随鼠标移动
          DisRefToInnerTopLeft = math.dist((mx,my), gVar.ChessBoard_InnerCorner_TopLeft_CvPlane)
          DisRefToInnerTopRight = math.dist((mx,my), gVar.ChessBoard_InnerCorner_TopRight_CvPlane)
          DisRefToInnerBotRight = math.dist((mx,my), gVar.ChessBoard_InnerCorner_BotRight_CvPlane)
          DisRefToInnerBotLeft = math.dist((mx,my), gVar.ChessBoard_InnerCorner_BotLeft_CvPlane)
          gVar.logger.PrintString(f"Info: -------------------------------------")
          gVar.logger.PrintString(f"Info:  DisRefToInnerTopLeft  | {DisRefToInnerTopLeft:.2f} px")
          gVar.logger.PrintString(f"Info:  DisRefToInnerTopRight | {DisRefToInnerTopRight:.2f} px")
          gVar.logger.PrintString(f"Info:  DisRefToInnerBotRight | {DisRefToInnerBotRight:.2f} px")
          gVar.logger.PrintString(f"Info:  DisRefToInnerBotLeft  | {DisRefToInnerBotLeft:.2f} px")
          gVar.logger.PrintString(f"Info: -------------------------------------")
          EffectiveRadius = 20.0 # 有效半径
          # 如果鼠标和这个点的距离在有效半径内，就引用为这个点
          if DisRefToInnerTopLeft < EffectiveRadius: gVar.CvPlane_ChangeReference = gVar.ChessBoard_InnerCorner_TopLeft_CvPlane
          if DisRefToInnerTopRight <= DisRefToInnerTopLeft and DisRefToInnerTopRight < EffectiveRadius: gVar.CvPlane_ChangeReference = gVar.ChessBoard_InnerCorner_TopRight_CvPlane
          if DisRefToInnerBotRight <= DisRefToInnerTopRight and DisRefToInnerBotRight < EffectiveRadius: gVar.CvPlane_ChangeReference = gVar.ChessBoard_InnerCorner_BotRight_CvPlane
          if DisRefToInnerBotLeft <= DisRefToInnerBotRight and DisRefToInnerBotLeft < EffectiveRadius: gVar.CvPlane_ChangeReference = gVar.ChessBoard_InnerCorner_BotLeft_CvPlane
          gVar.logger.PrintString(f"Info: 鼠标左键按下")
        elif gVar.LButtonUpFlag: # 如果左键释放标志位触发
          gVar.LButtonUpFlag = False # 清除左键释放标志位
          gVar.is_pressed = False # 清除按下状态
          gVar.CvPlane_ChangeReference = None # 清除引用
          gVar.logger.PrintString(f"Info: 鼠标左键释放")
        else: pass
        if gVar.is_pressed and gVar.MouseMoveFlag: # 如果在按下状态，且鼠标移动标志位触发
          if gVar.CvPlane_ChangeReference is not None:
            # 更新引用点的坐标
            gVar.CvPlane_ChangeReference[0] = gVar.mouse_x # 更新引用点的x坐标
            gVar.CvPlane_ChangeReference[1] = gVar.mouse_y # 更新引用点的y坐标
            gVar.ChessBoard_InnerCorners_CvPlane = [ # 更新棋盘內部的四个角点坐标
              gVar.ChessBoard_InnerCorner_TopLeft_CvPlane,
              gVar.ChessBoard_InnerCorner_TopRight_CvPlane,
              gVar.ChessBoard_InnerCorner_BotRight_CvPlane,
              gVar.ChessBoard_InnerCorner_BotLeft_CvPlane ]
            # 还要更新棋盘外围的四个角点相关的参数
            gVar.PlaneMapper_Arm2Cv.update(gVar.ChessBoard_InnerCorners_ArmPlane, gVar.ChessBoard_InnerCorners_CvPlane) # 更新机械臂坐标系转CV坐标系的单应矩阵
            gVar.PlaneMapper_Cv2Arm.update(gVar.ChessBoard_InnerCorners_CvPlane, gVar.ChessBoard_InnerCorners_ArmPlane) # 更新CV坐标系转机械臂坐标系的单应矩阵
            gVar.ChessBoard_OuterCorner_TopLeft_CvPlane = gVar.PlaneMapper_Arm2Cv.transform(gVar.ChessBoard_OuterCorner_TopLeft_ArmPlane)
            gVar.ChessBoard_OuterCorner_TopRight_CvPlane = gVar.PlaneMapper_Arm2Cv.transform(gVar.ChessBoard_OuterCorner_TopRight_ArmPlane)
            gVar.ChessBoard_OuterCorner_BotRight_CvPlane = gVar.PlaneMapper_Arm2Cv.transform(gVar.ChessBoard_OuterCorner_BotRight_ArmPlane)
            gVar.ChessBoard_OuterCorner_BotLeft_CvPlane = gVar.PlaneMapper_Arm2Cv.transform(gVar.ChessBoard_OuterCorner_BotLeft_ArmPlane)
            gVar.ChessBoard_OuterCorner_TopLeft_CvPlane = [round(x) for x in gVar.ChessBoard_OuterCorner_TopLeft_CvPlane]
            gVar.ChessBoard_OuterCorner_TopRight_CvPlane = [round(x) for x in gVar.ChessBoard_OuterCorner_TopRight_CvPlane]
            gVar.ChessBoard_OuterCorner_BotRight_CvPlane = [round(x) for x in gVar.ChessBoard_OuterCorner_BotRight_CvPlane]
            gVar.ChessBoard_OuterCorner_BotLeft_CvPlane = [round(x) for x in gVar.ChessBoard_OuterCorner_BotLeft_CvPlane]
            gVar.ChessBoard_OuterCorners_CvPlane = [
              gVar.ChessBoard_OuterCorner_TopLeft_CvPlane,
              gVar.ChessBoard_OuterCorner_TopRight_CvPlane,
              gVar.ChessBoard_OuterCorner_BotRight_CvPlane,
              gVar.ChessBoard_OuterCorner_BotLeft_CvPlane ]
            # 还要更新棋盘表格直线交点的信息
            gVar.ChessBoard_IntersectionPointsGrid_CvPlane = GetAllIntersectionPointOfTable_Perspective(gVar.ChessBoard_InnerCorners_CvPlane, gVar.ChessBoard_Rows, gVar.ChessBoard_Cols) # 获取棋盘的所有交点坐标
            gVar.ChessBoard_ChessPiecePointsGrid_CvPlane = GetAllIntersectionPointOfTable_Perspective(gVar.ChessBoard_InnerCorners_CvPlane, gVar.ChessBoard_Rows, gVar.ChessBoard_Cols) # 也初始化为棋盘的所有交点坐标，如果交点附近有棋子则更新为棋子坐标，这个的数据来源将会是棋盘识别器
            # 随便打印个状态日志
            gVar.logger.PrintString(f"Info: 鼠标左键拖动中 ({gVar.CvPlane_ChangeReference[0]},{gVar.CvPlane_ChangeReference[1]})")
          else:
            gVar.logger.PrintString(f"Info: 鼠标左键拖动中，但未引用任何点")
        else: pass
        # 绘制棋盘表格，包括棋盘内部和外部范围
        draw_color = [255, 0, 0]
        DrawTable_Perspective(frame_roi, gVar.ChessBoard_InnerCorners_CvPlane, gVar.ChessBoard_Rows, gVar.ChessBoard_Cols, draw_color, 2)
        DrawIrregularQuad(frame_roi, gVar.ChessBoard_OuterCorners_CvPlane, draw_color, 2) # 绘制棋盘外部范围四边形
        cv2.circle(frame_roi, gVar.ChessBoard_InnerCorner_TopLeft_CvPlane, 10, draw_color, 2) # 绘制棋盘内部左上角圆
        cv2.circle(frame_roi, gVar.ChessBoard_InnerCorner_TopRight_CvPlane, 10, draw_color, 2) # 绘制棋盘内部右上角圆
        cv2.circle(frame_roi, gVar.ChessBoard_InnerCorner_BotRight_CvPlane, 10, draw_color, 2) # 绘制棋盘内部右下角圆
        cv2.circle(frame_roi, gVar.ChessBoard_InnerCorner_BotLeft_CvPlane, 10, draw_color, 2) # 绘制棋盘内部左下角圆
        cv2.circle(frame_roi, gVar.ChessBoard_OuterCorner_TopLeft_CvPlane, 10, draw_color, 2) # 绘制棋盘外部左上角圆
        cv2.circle(frame_roi, gVar.ChessBoard_OuterCorner_TopRight_CvPlane, 10, draw_color, 2) # 绘制棋盘外部右上角圆
        cv2.circle(frame_roi, gVar.ChessBoard_OuterCorner_BotRight_CvPlane, 10, draw_color, 2) # 绘制棋盘外部右下角圆
        cv2.circle(frame_roi, gVar.ChessBoard_OuterCorner_BotLeft_CvPlane, 10, draw_color, 2) # 绘制棋盘外部左下角圆

      # 在画面中拖拽两条线段，使其与两条连杆平行，实现机械臂的标定操作
      elif gVar.IsCalibrateRobotArm: # 如果正在标定机械臂模式
        # 在画面中手动拖拽两条线段，使其与两条连杆平行，然后系统就能够与其锚定，进行后续步骤
        if gVar.LButtonDownFlag: # 如果左键按下标志位触发
          gVar.LButtonDownFlag = False # 清除左键按下标志位
          gVar.is_pressed = True # 设置按下状态
          mx = gVar.mouse_x # 存定鼠标x坐标
          my = gVar.mouse_y # 存定鼠标y坐标
          # 在鼠标按下时，判断鼠标离哪一个点最近，然后将其引用为CvPlane_ChangeReference，之后这个点会跟随鼠标移动
          DisRefToLine1Start = math.dist((mx,my), gVar.CvPlane_AnchorLine1_Start) # 计算鼠标到标定线1的起始点的距离
          DisRefToLine1End = math.dist((mx,my), gVar.CvPlane_AnchorLine1_End) # 计算鼠标到标定线1的结束点的距离
          DisRefToLine2Start = math.dist((mx,my), gVar.CvPlane_AnchorLine2_Start) # 计算鼠标到标定线2的起始点的距离
          DisRefToLine2End = math.dist((mx,my), gVar.CvPlane_AnchorLine2_End) # 计算鼠标到标定线2的结束点的距离
          gVar.logger.PrintString(f"Info: -------------------------------------")
          gVar.logger.PrintString(f"Info:   DisRefToLine1Start | {DisRefToLine1Start:.2f} px")
          gVar.logger.PrintString(f"Info:   DisRefToLine1End   | {DisRefToLine1End:.2f} px")
          gVar.logger.PrintString(f"Info:   DisRefToLine2Start | {DisRefToLine2Start:.2f} px")
          gVar.logger.PrintString(f"Info:   DisRefToLine2End   | {DisRefToLine2End:.2f} px")
          gVar.logger.PrintString(f"Info: -------------------------------------")
          EffectiveRadius = 20.0 # 有效半径
          # 如果鼠标和这个点的距离在有效半径内，就引用为这个点
          if DisRefToLine1Start < EffectiveRadius: gVar.CvPlane_ChangeReference = gVar.CvPlane_AnchorLine1_Start
          if DisRefToLine1End <= DisRefToLine1Start and DisRefToLine1End < EffectiveRadius: gVar.CvPlane_ChangeReference = gVar.CvPlane_AnchorLine1_End
          if DisRefToLine2Start <= DisRefToLine1End and DisRefToLine2Start < EffectiveRadius: gVar.CvPlane_ChangeReference = gVar.CvPlane_AnchorLine2_Start
          if DisRefToLine2End <= DisRefToLine2Start and DisRefToLine2End < EffectiveRadius: gVar.CvPlane_ChangeReference = gVar.CvPlane_AnchorLine2_End
          gVar.logger.PrintString(f"Info: 鼠标左键按下事件触发")
        elif gVar.LButtonUpFlag: # 如果左键释放标志位触发
          gVar.LButtonUpFlag = False # 清除左键释放标志位
          gVar.is_pressed = False # 清除按下状态
          gVar.CvPlane_ChangeReference = None # 清除引用
          gVar.logger.PrintString(f"Info: 鼠标左键释放事件触发")
        else: pass
        if gVar.is_pressed and gVar.MouseMoveFlag: # 如果在按下状态，且鼠标移动标志位触发
          if gVar.CvPlane_ChangeReference is not None: # 如果有成功引用到一个坐标点
            gVar.CvPlane_ChangeReference[0] = gVar.mouse_x # 引用点的坐标跟随鼠标移动
            gVar.CvPlane_ChangeReference[1] = gVar.mouse_y # 引用点的坐标跟随鼠标移动
            # 根据标定线的坐标，计算出肩关节角度和肘关节角度，绘制实际的连杆线段
            ArmPlane_AnchorLine1_Start = gVar.PlaneMapper_Cv2Arm.transform(gVar.CvPlane_AnchorLine1_Start) # 实际机械臂坐标系的坐标
            ArmPlane_AnchorLine1_End = gVar.PlaneMapper_Cv2Arm.transform(gVar.CvPlane_AnchorLine1_End) # 实际机械臂坐标系的坐标
            ArmPlane_AnchorLine2_Start = gVar.PlaneMapper_Cv2Arm.transform(gVar.CvPlane_AnchorLine2_Start) # 实际机械臂坐标系的坐标
            ArmPlane_AnchorLine2_End = gVar.PlaneMapper_Cv2Arm.transform(gVar.CvPlane_AnchorLine2_End) # 实际机械臂坐标系的坐标
            gVar.DegAngle_Runtime_Shoulder = round( math.atan2(
              ArmPlane_AnchorLine1_End[1]-ArmPlane_AnchorLine1_Start[1],
              ArmPlane_AnchorLine1_End[0]-ArmPlane_AnchorLine1_Start[0]
            ) * 180 / math.pi, 2 ) # 计算肩关节的角度，保留2位小数
            gVar.DegAngle_Runtime_Elbow = round( math.atan2(
              ArmPlane_AnchorLine2_End[1]-ArmPlane_AnchorLine2_Start[1],
              ArmPlane_AnchorLine2_End[0]-ArmPlane_AnchorLine2_Start[0]
            ) * 180 / math.pi, 2 ) # 计算肘关节的角度，保留2位小数
            gVar.logger.PrintString(f"Info: 鼠标左键拖动中 ({gVar.CvPlane_ChangeReference[0]},{gVar.CvPlane_ChangeReference[1]})")
          else:
            gVar.logger.PrintString(f"Info: 鼠标左键拖动中，但未引用任何点")
        else: pass
        MyDrawDoubleConnectingRod( # 绘制双连杆线段
          frame_roi, # 输入的图像帧
          gVar.LengthOfShoulder, # 肩关节长度
          gVar.DegAngle_Runtime_Shoulder, # 肩关节角度
          gVar.LengthOfElbow, # 肘关节长度
          gVar.DegAngle_Runtime_Elbow, # 肘关节实时角度
        )
        # 绘制两条标定线，分别是肩关节角度线1，肘关节角度线2（标定线最后绘制，防止标定线被连杆遮挡）
        draw_color = [255, 0, 0]
        cv2.arrowedLine(frame_roi, gVar.CvPlane_AnchorLine1_Start, gVar.CvPlane_AnchorLine1_End, draw_color, 2)
        cv2.arrowedLine(frame_roi, gVar.CvPlane_AnchorLine2_Start, gVar.CvPlane_AnchorLine2_End, draw_color, 2)
        cv2.circle(frame_roi, gVar.CvPlane_AnchorLine1_Start, 10, draw_color, 2)
        cv2.circle(frame_roi, gVar.CvPlane_AnchorLine1_End, 10, draw_color, 2)
        cv2.circle(frame_roi, gVar.CvPlane_AnchorLine2_Start, 10, draw_color, 2)
        cv2.circle(frame_roi, gVar.CvPlane_AnchorLine2_End, 10, draw_color, 2)



    elif gVar.CurrMode == gVar.MODE_ARRANGE: # 如果是整理模式（整理模式的操作完成后，检验棋盘已全部归位，会自动进入对弈模式）
      cv2.putText(frame_roi, f"IsArranged: {gVar.IsArranged}", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2) # 在图片上显示是否整理完成
      gVar.ChessBoard_IntersectionPointsGrid_CvPlane = GetAllIntersectionPointOfTable_Perspective(gVar.ChessBoard_InnerCorners_CvPlane, gVar.ChessBoard_Rows, gVar.ChessBoard_Cols) # 获取棋盘的所有交点坐标
      gVar.ChessBoard_ChessSituation_ForChessEngine = [list(row) for row in INIT_CHESSBOARD] # 初始化棋盘状态为初始状态，这个的数据是和棋盘引擎绑定的
      if not gVar.IsArranged: # 如果未整理完成，继续识别图像，整理棋盘
        ChessObjects = gVar.ChessModel_Recognizer.Recognize(frame_roi_cp) # 调用棋子识别模型，将图片的复制品传进去
        if ChessObjects is not None: # 如果检测到了棋子，则更新ChessBoard_ChessSituation_FromRecognizer
          gVar.ChessBoard_ChessPiecePointsGrid_CvPlane = GetAllIntersectionPointOfTable_Perspective(gVar.ChessBoard_InnerCorners_CvPlane, gVar.ChessBoard_Rows, gVar.ChessBoard_Cols) # 初始化为棋盘表格交点坐标，接下来会从棋盘识别器中对其进行更新
          gVar.ChessBoard_ChessSituation_FromRecognizer = [ [NOCHESS for _ in range (gVar.ChessBoard_Cols+1)] for _ in range(gVar.ChessBoard_Rows+1) ] # 初始化棋盘状态为无棋子，接下来会从棋盘识别器中对其进行更新
          for chessobj in ChessObjects: # 遍历所有棋子
            cx, cy, r, cls_idx, conf, is_red = chessobj # 提取棋子的圆心X坐标、圆心Y坐标、半径、类别索引、置信度、是否红色棋子
            if is_point_in_quad((cx,cy), gVar.ChessBoard_OuterCorners_CvPlane): # 如果棋子的圆心在棋盘外部角点的四边形范围内，才算是局中棋子，才可以进行后续处理
              _, _, nearest_row, nearest_col = find_nearest_intersection((cx,cy), gVar.ChessBoard_IntersectionPointsGrid_CvPlane) # 找到最近的交点，即棋盘上的位置
              chess_piece = None # 初始化棋子类型为None
              match cls_idx: # 根据棋子类别索引，判断是哪个棋子，按照ChessInterface的格式更新棋盘状态
                case 0: chess_piece =     R_KING if is_red else B_KING     # 索引0 对应 帥/將
                case 1: chess_piece =   R_BISHOP if is_red else B_BISHOP   # 索引1 对应 仕/士
                case 2: chess_piece =      R_CAR if is_red else B_CAR      # 索引2 对应 車
                case 3: chess_piece =    R_HORSE if is_red else B_HORSE    # 索引3 对应 馬
                case 4: chess_piece =   R_CANNON if is_red else B_CANNON   # 索引4 对应 炮/砲
                case 5: chess_piece = R_ELEPHANT if is_red else B_ELEPHANT # 索引5 对应 象/相
                case 6: chess_piece =     R_PAWN if is_red else B_PAWN     # 索引6 对应 兵/卒
                case _: gVar.logger.PrintString(f"Error: 出现未知的棋子类别索引 {cls_idx}")
              if chess_piece is not None: # 如果棋子有被更新
                gVar.ChessBoard_ChessPiecePointsGrid_CvPlane[nearest_row][nearest_col] = [cx,cy] # 更新棋子坐标
                gVar.ChessBoard_ChessSituation_FromRecognizer[nearest_row][nearest_col] = chess_piece # 更新棋盘状态
              else: # 如果棋子是未知类型
                gVar.logger.PrintString(f"Error: 出现未知的棋子类别索引 {cls_idx}")
          # 遍历所有棋子完成后，打印一下棋盘状态，看看还有什么地方没有对齐
          gVar.logger.PrintString(f"Info: ChessSituation_ForChessEngine: {gVar.ChessBoard_ChessSituation_ForChessEngine}")
          gVar.logger.PrintString(f"Info: ChessSituation_FromRecognizer: {gVar.ChessBoard_ChessSituation_FromRecognizer}")
          if gVar.ChessBoard_ChessSituation_FromRecognizer == gVar.ChessBoard_ChessSituation_ForChessEngine: # 如果棋盘初始状态与棋盘引擎状态一致（已全部归位）
            gVar.IsArranged = True # 标记为整理完成
          else: # 棋盘状态与棋盘引擎状态不一致，棋盘未全部归位
            gVar.logger.PrintString(f"Info: 棋子未归位，整理棋盘中，请等候......")
        else: # ChessObjects为None，画面中没有检测到任何棋子
          gVar.logger.PrintString(f"Info: 画面中没有检测到任何哪怕一个棋子")
      else: # 如果已整理完成，则进入对弈模式，开始运行游戏
        gVar.IsArranged = False # 游戏开始了，棋盘又要乱了，标记为未整理完成
        gVar.IsGameRunning = True # 标记为游戏运行
        gVar.IsGameOver = False # 标记为游戏未结束
        gVar.IsUserTurn = True # 标记为用户回合（用户先落子）
        gVar.CurrMode = gVar.MODE_PLAYING # 切换到对弈模式
        ElephantFishChessInit(gVar.ChessBoard_ChessSituation_ForChessEngine) # 初始化象棋引擎
        gVar.logger.PrintString(f"Info: 整理完成，即将退出【整理模式】，进入【对弈模式】")
        gVar.logger.PrintString(f"Info: 象棋引擎初始化完成，游戏开始运行，请用户先落子")
        gVar.UserMove = None # 清空用户落子路径，准备下一次对弈
        gVar.PcMoveAgainstUser = None # 清空电脑走棋路径，准备下一次对弈
        gVar.IsUserWin = False # 清空用户是否赢了，准备下一次对弈
        gVar.IsPcWin = False # 清空电脑是否赢了，准备下一次对弈



    elif gVar.CurrMode == gVar.MODE_PLAYING: # 如果对弈模式
      # 画面中显示一些对弈状态变量信息
      cv2.putText(frame_roi, f"IsGameRunning: {gVar.IsGameRunning}", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
      cv2.putText(frame_roi, f"IsGameOver: {gVar.IsGameOver}", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
      cv2.putText(frame_roi, f"IsUserTurn: {gVar.IsUserTurn}", (10,130), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
      cv2.putText(frame_roi, f"IsEngineRunning: {gVar.ChessEngine_IsRunning}", (10,560), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
      cv2.putText(frame_roi, f"IsEngineFinished: {gVar.ChessEngine_ResultFinished}", (10,590), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
      if gVar.IsGameRunning and not gVar.IsUserTurn: # 如果游戏运行中，且是电脑回合
        cv2.putText(frame_roi, "Now it's turn of PC", (10,160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)
        if not gVar.ChessEngine_IsRunning and not gVar.ChessEngine_ResultFinished: # 如果象棋引擎没在运行，且没有获得结果，则进行棋盘识别并调用象棋引擎
          ChessObjects = gVar.ChessModel_Recognizer.Recognize(frame_roi_cp) # 调用棋子识别模型，将图片的复制品传进去
          if ChessObjects is not None: # 如果检测到了棋子，则更新ChessBoard_ChessSituation_FromRecognizer
            gVar.ChessBoard_ChessPiecePointsGrid_CvPlane = GetAllIntersectionPointOfTable_Perspective(gVar.ChessBoard_InnerCorners_CvPlane, gVar.ChessBoard_Rows, gVar.ChessBoard_Cols) # 初始化为棋盘表格交点坐标，接下来会从棋盘识别器中对其进行更新
            gVar.ChessBoard_ChessSituation_FromRecognizer = [ [NOCHESS for _ in range (gVar.ChessBoard_Cols+1)] for _ in range(gVar.ChessBoard_Rows+1) ] # 初始化棋盘状态为无棋子，接下来会从棋盘识别器中对其进行更新
            for chessobj in ChessObjects: # 遍历所有棋子
              cx, cy, r, cls_idx, conf, is_red = chessobj # 提取棋子的圆心X坐标、圆心Y坐标、半径、类别索引、置信度、是否红色棋子
              if is_point_in_quad((cx,cy), gVar.ChessBoard_OuterCorners_CvPlane): # 如果棋子的圆心在棋盘外部角点的四边形范围内，才算是局中棋子，才能进行后续处理
                _, _, nearest_row, nearest_col = find_nearest_intersection((cx,cy), gVar.ChessBoard_IntersectionPointsGrid_CvPlane) # 找到最近的交点，即棋盘上的位置
                chess_piece = None # 初始化棋子类型为None
                match cls_idx: # 根据棋子类别索引，判断是哪个棋子，按照ChessInterface的格式更新棋盘状态
                  case 0: chess_piece =     R_KING if is_red else B_KING     # 索引0 对应 帥/將
                  case 1: chess_piece =   R_BISHOP if is_red else B_BISHOP   # 索引1 对应 仕/士
                  case 2: chess_piece =      R_CAR if is_red else B_CAR      # 索引2 对应 車
                  case 3: chess_piece =    R_HORSE if is_red else B_HORSE    # 索引3 对应 馬
                  case 4: chess_piece =   R_CANNON if is_red else B_CANNON   # 索引4 对应 炮/砲
                  case 5: chess_piece = R_ELEPHANT if is_red else B_ELEPHANT # 索引5 对应 象/相
                  case 6: chess_piece =     R_PAWN if is_red else B_PAWN     # 索引6 对应 兵/卒
                  case _: gVar.logger.PrintString(f"Error: 出现未知的棋子类别索引 {cls_idx}")
                if chess_piece is not None: # 如果棋子有被更新
                  gVar.ChessBoard_ChessPiecePointsGrid_CvPlane[nearest_row][nearest_col] = [cx,cy] # 更新棋子坐标
                  gVar.ChessBoard_ChessSituation_FromRecognizer[nearest_row][nearest_col] = chess_piece # 更新棋盘状态
                else: # 如果棋子是未知类型
                  gVar.logger.PrintString(f"Error: 出现未知的棋子类别索引 {cls_idx}")
            # 遍历所有棋子完成后，打印一下棋盘状态，看看还有什么地方没有对齐
            gVar.logger.PrintString(f"Info: ChessSituation_ForChessEngine: {gVar.ChessBoard_ChessSituation_ForChessEngine}")
            gVar.logger.PrintString(f"Info: ChessSituation_FromRecognizer: {gVar.ChessBoard_ChessSituation_FromRecognizer}")
            if gVar.ChessBoard_ChessSituation_FromRecognizer == gVar.ChessBoard_ChessSituation_ForChessEngine: # 如果棋盘状态与棋盘引擎状态一致（用户根本没落子）
              gVar.IsUserTurn = True # 回标为用户回合（用户落子）
              gVar.logger.PrintString(f"Info: 棋盘状态与棋盘引擎状态一致，用户根本没落子，请用户赶紧落子")
            else: # 棋盘状态与棋盘引擎状态不一致，用户落子了，但还不确定这改变是否合法
              diff_pos = find_diff_position_in_two_chessboard( # 获取棋盘的不同
                gVar.ChessBoard_ChessSituation_FromRecognizer,
                gVar.ChessBoard_ChessSituation_ForChessEngine
              ) # 将会返回一个列表，里面每个元素是一个行列索引值[row_idx, col_idx]，表示两个棋盘在这个位置上不一样
              gVar.UserMove = None # 初始化用户落子字符串为None
              user_turn_origin_pos_str = None # 初始化用户落子起始点输入字符串为None
              user_turn_target_pos_str = None # 初始化用户落子目标点输入字符串为None
              if diff_pos is not None: # 棋子确实有被移动，然后进一步检验
                if len(diff_pos) == 2: # 如果只有两个位置被移动（这才是合法的走法，无论怎么落子吃子，最终改变的只有两个位置）
                  for row,col in diff_pos: # 遍历这两个位置不同点
                    if gVar.ChessBoard_ChessSituation_FromRecognizer[row][col] is NOCHESS: # 如果是空位置，这就是用户落子起始点
                      user_turn_origin_pos_str = chr( row+ord('a')) + chr(col+ord('0') ) # 构建象棋引擎的起始点输入字符串格式
                    else: # 如果不是空位置，这就是用户落子目标点
                      user_turn_target_pos_str = chr( row+ord('a')) + chr(col+ord('0') ) # 构建象棋引擎的目标点输入字符串格式
                  if user_turn_origin_pos_str is not None and user_turn_target_pos_str is not None: # 如果有起始点和目标点
                    gVar.UserMove = user_turn_origin_pos_str + user_turn_target_pos_str # 合并起始点和目标点，这就是最终输入象棋引擎的字符串格式
                    gVar.logger.PrintString(f"Info: 用户落子字符串为 {gVar.UserMove}") # 记录用户落子字符串
                else: # 如果发生改变的位置不是两处
                  gVar.logger.PrintString(f"Error: 每一次落子，发生改变的位置应是两处，非法走法，请重新按空格键确认落子") # 记录错误日志
                  gVar.logger.PrintString(f"Error: 发生改变的位置为 {diff_pos}") # 记录发生改变的位置
                  gVar.logger.PrintString(
                    f"Error: Recognizer的 {len(diff_pos)} 个位置分别为"
                    + " ".join([f"{gVar.ChessBoard_ChessSituation_FromRecognizer[diff_pos[i][0]][diff_pos[i][1]]}" for i in range(len(diff_pos))]) )
                  gVar.logger.PrintString(
                    f"Error: ChessEngine的 {len(diff_pos)} 个位置分别为"
                    + " ".join([f"{gVar.ChessBoard_ChessSituation_ForChessEngine[diff_pos[i][0]][diff_pos[i][1]]}" for i in range(len(diff_pos))]) )
                  gVar.IsUserTurn = True # 用户落子异常，回标为用户回合（用户落子）
              else: # 如果没有发生改变的位置
                gVar.logger.PrintString(f"Info: 没有找到改变的位置，用户可能没有落子，请重新按空格键确认落子")
                gVar.IsUserTurn = True # 用户落子异常，回标为用户回合（用户落子）
              if gVar.UserMove is not None: # 如果有用户落子字符串
                gVar.ChessEngine_Result = None # 初始化调用象棋引擎的结果为None
                gVar.ChessEngine_IsRunning = True # 初始化调用象棋引擎是否正在运行为True
                gVar.ChessEngine_ResultFinished = False # 初始化调用象棋引擎的结果是否完成为False
                gVar.ChessEngine_CallThread = threading.Thread(target=ChessEngine_CallFunc) # 创建线程，调用象棋引擎决策
                gVar.ChessEngine_CallThread.start() # 启动象棋引擎线程
                gVar.logger.PrintString(f"Info: 用户 {gVar.UserMove} 落子，传入象棋引擎决策，请等待一会……")
              else: # 如果没有用户落子字符串
                gVar.logger.PrintString(f"Info: 没有成功组合用户落子字符串，用户落子异常，请重新按空格键确认落子")
                gVar.IsUserTurn = True # 用户落子异常，回标为用户回合（用户落子）
          else: # ChessObjects为None，画面中没有检测到任何棋子
            gVar.logger.PrintString(f"Info: 画面中没有检测到任何哪怕一个棋子")
        elif not gVar.ChessEngine_IsRunning and gVar.ChessEngine_ResultFinished: # 如果象棋引擎没在运行，且获得结果了
          gVar.ChessEngine_ResultFinished = False # 在获得结果后，就应该立马把这个标志位置False了，防止下次循环再进来
          if gVar.ChessEngine_Result is None: # 如果没有象棋引擎的结果，则说明象棋引擎决策失败
            gVar.logger.PrintString(f"Error: 调用象棋引擎决策失败") # 记录错误日志
          else: # 如果有象棋引擎的结果，则说明象棋引擎决策成功
            if gVar.ChessEngine_Result == 'invalid': # 如果象棋引擎判断用户走棋无效
              gVar.logger.PrintString(f"Error: 用户 {gVar.UserMove} 落子无效，请重新落子") # 记录错误日志
              gVar.IsUserTurn = True # 用户落子异常，回标为用户回合（用户落子）
            elif gVar.ChessEngine_Result == -1: # 如果象棋引擎判断用户走棋有效，且用户赢了
              gVar.logger.PrintString(f"Info: 用户 {gVar.UserMove} 落子有效，且赢得了游戏") # 记录用户赢了游戏
              MakeMove(gVar.ChessBoard_ChessSituation_ForChessEngine, gVar.UserMove) # 更新棋盘引擎状态
              gVar.IsGameRunning = False # 游戏结束标志位
              gVar.IsGameOver = True # 游戏结束标志位
              gVar.IsUserWin = True # 游戏结束标志位
              gVar.IsPcWin = False # 游戏结束标志位
            else: # 如果象棋引擎判断用户走棋有效，且棋局还能继续
              pc_move, pc_check, pc_capture, depth, time_used, HasPCWon = gVar.ChessEngine_Result # 获取引擎计算出的电脑走法
              HasUserAte = IsBlack(gVar.ChessBoard_ChessSituation_ForChessEngine[ord(gVar.UserMove[2])-ord('a')][ord(gVar.UserMove[3])-ord('0')]) # 检查用户目标落点是否有黑棋（用户是否吃子）
              if HasUserAte: gVar.logger.PrintString(f"Info: 用户 {gVar.UserMove} 落子有效，且吃一子") # 记录用户落子字符串，是否吃子
              MakeMove(gVar.ChessBoard_ChessSituation_ForChessEngine, gVar.UserMove) # 更新用户走棋后的棋盘状态
              gVar.logger.PrintString(f"Info: 电脑 {pc_move} 走法应对用户 {gVar.UserMove}")
              HasPCAte = IsRed(gVar.ChessBoard_ChessSituation_ForChessEngine[ord(pc_move[2])-ord('a')][ord(pc_move[3])-ord('0')]) # 检查电脑目标落点是否有红棋（电脑是否吃子）
              if HasPCAte: # 如果电脑吃子
                gVar.logger.PrintString(f"Info: 电脑 {pc_move} 走法肯定有效，且吃一子") # 记录电脑落子字符串，是否吃子
                cap_cmd = CreateCommandList_DriveMotor_CapOppoPiece( # 生成执行机械臂吃子操作的指令列表
                  StartPosIndex  = [ ord(pc_move[0])-ord('a'), ord(pc_move[1])-ord('0') ],
                  TargetPosIndex = [ ord(pc_move[2])-ord('a'), ord(pc_move[3])-ord('0') ]
                )
                for i, cc in enumerate(cap_cmd): # 遍历吃子操作指令列表，依次发送指令，打印发送日志
                  gVar.MainStream.WriteFrame(UartStream_FrameHead.FrameHead2_Req, cc) # 发送指令
                  gVar.logger.PrintHexBytes(msg=cc, prefix=f"CapOppoPiece[{i:02d}]: ") # 打印日志
              else: # 如果电脑是普通落子不吃子
                drop_cmd = CreateCommandList_DriveMotor_DropSelfPiece( # 生成执行机械臂落子操作的指令列表
                  StartPosIndex  = [ ord(pc_move[0])-ord('a'), ord(pc_move[1])-ord('0') ],
                  TargetPosIndex = [ ord(pc_move[2])-ord('a'), ord(pc_move[3])-ord('0') ]
                )
                for i, dc in enumerate(drop_cmd): # 遍历落子操作指令列表，依次发送指令，打印发送日志
                  gVar.MainStream.WriteFrame(UartStream_FrameHead.FrameHead2_Req, dc) # 发送指令
                  gVar.logger.PrintHexBytes(msg=dc, prefix=f"DropSelfPiece[{i:02d}]: ") # 打印日志
              MakeMove(gVar.ChessBoard_ChessSituation_ForChessEngine, pc_move) # 更新电脑走棋后的棋盘状态
              if HasPCWon: # 如果电脑赢了
                gVar.logger.PrintString(f"Info: 电脑 {pc_move} 走法肯定有效，且赢得了游戏") # 记录电脑赢了游戏
                gVar.IsGameRunning = False # 游戏结束标志位
                gVar.IsGameOver = True # 游戏结束标志位
                gVar.IsUserWin = False # 游戏结束标志位
                gVar.IsPcWin = True # 游戏结束标志位
              if pc_check: # 如果电脑查杀了用户军
                gVar.logger.PrintString(f"Info: 电脑 {pc_move} 走法肯定有效，且正在将用户军")
              gVar.PcMoveAgainstUser = pc_move # 记录电脑走棋字符串
              gVar.IsUserTurn = True # 电脑成功应对用户落子，回标为用户回合（用户落子）
        elif gVar.ChessEngine_IsRunning: # 如果象棋引擎在运行中
          if gVar.UserMove is not None and len(gVar.UserMove) == 4: # 如果有用户落子字符串
            cv2.arrowedLine( frame_roi, # 显示用户落子路径的箭头线
              gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ ord(gVar.UserMove[0])-ord('a') ] [ ord(gVar.UserMove[1])-ord('0') ],
              gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ ord(gVar.UserMove[2])-ord('a') ] [ ord(gVar.UserMove[3])-ord('0') ],
              gVar.UserMoveArrowColor, 5
            ) # 绘制用户落子的路径
      elif gVar.IsGameRunning and gVar.IsUserTurn: # 如果游戏运行中，且是用户回合，对棋盘局势不作识别，提示用户落子，等待用户按空格键确认
        cv2.putText(frame_roi, "Move piece and Press SPACE to confirm", (10,160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2) # 图像标注落子提示
        if gVar.PcMoveAgainstUser is not None and len(gVar.PcMoveAgainstUser) == 4:
          cv2.arrowedLine( frame_roi, # 在图像帧中绘制电脑落子路径的箭头线
            gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ ord(gVar.PcMoveAgainstUser[0])-ord('a') ] [ ord(gVar.PcMoveAgainstUser[1])-ord('0') ],
            gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ ord(gVar.PcMoveAgainstUser[2])-ord('a') ] [ ord(gVar.PcMoveAgainstUser[3])-ord('0') ],
            gVar.PcMoveArrowColor, 5
          )
      elif not gVar.IsGameRunning and gVar.IsGameOver: # 如果游戏不在运行中，且游戏结束了，提示用户按空格键返回并重新开始
        cv2.putText(frame_roi, "Game Over, press SPACE to Return and Restart", (10,160), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2) # 图像标注游戏游戏结束了提示
        if gVar.IsUserWin: # 如果用户赢了
          cv2.arrowedLine( frame_roi,
            gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ ord(gVar.UserMove[0])-ord('a') ] [ ord(gVar.UserMove[1])-ord('0') ],
            gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ ord(gVar.UserMove[2])-ord('a') ] [ ord(gVar.UserMove[3])-ord('0') ],
            gVar.UserMoveArrowColor, 5
          ) # 绘制用户落子的路径
        elif gVar.IsPcWin: # 如果电脑赢了
          cv2.arrowedLine( frame_roi,
            gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ ord(gVar.PcMoveAgainstUser[0])-ord('a') ] [ ord(gVar.PcMoveAgainstUser[1])-ord('0') ],
            gVar.ChessBoard_IntersectionPointsGrid_CvPlane [ ord(gVar.PcMoveAgainstUser[2])-ord('a') ] [ ord(gVar.PcMoveAgainstUser[3])-ord('0') ],
            gVar.PcMoveArrowColor, 5
          ) # 绘制电脑走棋路径
        else: # 输赢状态异常
          gVar.logger.PrintString(f"Error: 未知游戏结束标志位，IsUserWin={gVar.IsUserWin}, IsPcWin={gVar.IsPcWin}")



    cv2.imshow("frame_roi", frame_roi) # 在窗口中显示图像



    # 初始为待机模式
    # 按'Enter'键，确认标定数据，将机械臂实时角度同步到变量中，并执行机械臂复位操作
    # 按'1'键，进入/退出 标定模式
    #          先标定棋盘，再标定机械臂，需要严格按照此顺序标定，然后按下Enter键确认，
    #          因为标定棋盘后，有了正确的平面映射单应矩阵，标定机械臂的角度才能计算正确
    # 按'2'键，进入/退出 整理模式（机械臂自动整理棋盘，直至所有棋子归位）
    # 按'3'键，进入/退出 对弈模式（开始下棋）
    # 按'Space'键，用户落子后确认落子
    # 按'q'键，显示/隐藏 双连杆线段
    # 按'w'键，显示/隐藏 棋盘表格
    PressKey = cv2.waitKey(10) & 0xFF

    if PressKey == 27: # 如果按下ESC键
      if gVar.CurrMode is gVar.MODE_STANDBY: # 如果是待机模式，才能退出
        gVar.logger.PrintString(f"Info: 已按下 Esc 键，即将退出程序")
        break # 退出循环
      elif gVar.CurrMode is gVar.MODE_CALIBRATION: # 如果是标定模式
        gVar.IsCalibrateRobotArm = False # 退出标定机械臂模式
        gVar.IsCalibrateChessBoard = False # 退出标定棋盘模式
        gVar.CurrMode = gVar.MODE_STANDBY # 切换到待机模式
        gVar.logger.PrintString(f"Info: 退出【标定模式】，未执行任何标定操作")
      elif gVar.CurrMode is gVar.MODE_ARRANGE or gVar.CurrMode is gVar.MODE_PLAYING: # 如果是整理/对弈模式
        gVar.logger.PrintString(f"Info: 需要先退出【整理/对弈模式】，才能退出程序")
      else: # 其他模式
        gVar.logger.PrintString(f"Info: 未知模式，模式编号 {gVar.CurrMode}")

    elif PressKey == ord('\r'): # 如果按下'Enter'键
      if gVar.CurrMode is gVar.MODE_CALIBRATION and gVar.IsCalibrateChessBoard: # 如果是标定模式，且正在标定棋盘模式
        # 在标定的时候就已经更新完所有所需更新的参数了，这里随便设置设置状态就行
        gVar.IsCalibrateRobotArm = False # 退出标定机械臂模式
        gVar.IsCalibrateChessBoard = False # 退出标定棋盘模式
        gVar.CurrMode = gVar.MODE_STANDBY # 切换到待机模式
        gVar.logger.PrintString(f"Info: 退出【标定模式】，并已执行标定操作")
      elif gVar.CurrMode is gVar.MODE_CALIBRATION and gVar.IsCalibrateRobotArm: # 如果是标定模式，且正在标定机械臂模式
        # 在标定模式下拖拽两条线段，已经确定了两条线段的位置，将两条线段的坐标计算出来的角度直接施加给机械臂
        gVar.logger.PrintString(f"Info: ---------------------------------")
        gVar.logger.PrintString(f"Info:  肩关节当前标定角度 | {gVar.DegAngle_Runtime_Shoulder:.2f} degrees")
        gVar.logger.PrintString(f"Info:  肘关节当前标定角度 | {gVar.DegAngle_Runtime_Elbow:.2f} degrees")
        gVar.logger.PrintString(f"Info: ---------------------------------")
        gVar.logger.PrintString(f"Info:  肩关节复位目标角度 | {gVar.DegAngle_StandByPos_Shoulder:.2f} degrees")
        gVar.logger.PrintString(f"Info:  肘关节复位目标角度 | {gVar.DegAngle_StandByPos_Ebow:.2f} degrees")
        gVar.logger.PrintString(f"Info: ---------------------------------")
        # 通过两条线段计算出来的角度，来对步进电机对象的位置信息进行更新，并计算出驱动其回到待机位置的步数
        gVar.tsm.DRIVE_MOTOR(gVar.DegAngle_Runtime_Shoulder, gVar.DegAngle_Runtime_Elbow, 0) # 不取返回值，仅更新位置信息
        dStepShoulder, dStepElbow, dStepLift = gVar.tsm.DRIVE_MOTOR( # 这一步就需要取返回值，来驱动步进电机执行复位操作
          gVar.DegAngle_StandByPos_Shoulder, # 目标肩关节角度：待机位置
          gVar.DegAngle_StandByPos_Ebow, # 目标肘关节角度：待机位置
          gVar.DegAngle_StandByPos_Lift, # 目标竖轴关节角度：待机位置
        )
        gVar.logger.PrintString(f"Info: --------------------------------------")
        gVar.logger.PrintString(f"Info:  肩关节复位需要旋转步数 | {dStepShoulder} steps")
        gVar.logger.PrintString(f"Info:  肘关节复位需要旋转步数 | {dStepElbow} steps")
        gVar.logger.PrintString(f"Info:  竖关节复位需要旋转步数 | {dStepLift} steps")
        gVar.logger.PrintString(f"Info: --------------------------------------")
        # 计算出驱动其回到待机位置的步数后，以通信协议发送指令，执行实际硬件操作
        send_cmd = CreateCommand_VerticalAxisRst() # 创建复位竖轴命令，先复位竖轴，再移动肩关节和肘关节
        gVar.MainStream.WriteFrame(UartStream_FrameHead.FrameHead2_Req, send_cmd) # 发送复位竖轴命令
        send_cmd = CreateCommand_BasicMove(gVar.StepperMotorShoulder_Index, 0x01, dStepShoulder, Speed=200)
        gVar.MainStream.WriteFrame(UartStream_FrameHead.FrameHead2_Req, send_cmd)
        send_cmd = CreateCommand_BasicMove(gVar.StepperMotorElbow_Index, 0x01, dStepElbow, Speed=200)
        gVar.MainStream.WriteFrame(UartStream_FrameHead.FrameHead2_Req, send_cmd)
        send_cmd = CreateCommand_BasicMove(gVar.StepperMotorLift_Index, 0x01, dStepLift, Speed=200)
        gVar.MainStream.WriteFrame(UartStream_FrameHead.FrameHead2_Req, send_cmd)
        # 从步进电机对象中获取位置信息，更新程序中全局变量的角度、以及标定线的角度 
        gVar.DegAngle_Runtime_Shoulder = gVar.tsm.PositionShoulder
        gVar.DegAngle_Runtime_Elbow = gVar.tsm.PositionElbow
        # 更新状态变量
        gVar.IsCalibrateRobotArm = False # 退出标定机械臂模式
        gVar.IsCalibrateChessBoard = False # 退出标定棋盘模式
        gVar.CurrMode = gVar.MODE_STANDBY # 切换到待机模式
        gVar.logger.PrintString(f"Info: 退出【标定模式】，并已执行标定操作")

    elif PressKey == ord('1'): # 如果按下'1'键
      if gVar.CurrMode is gVar.MODE_STANDBY: # 如果是待机模式，才能进入标定模式
        gVar.CurrMode = gVar.MODE_CALIBRATION # 切换到机械臂标定模式
        gVar.IsCalibrateChessBoard = True # 进入标定棋盘模式
        gVar.IsCalibrateRobotArm = False # 不在标定机械臂模式
        gVar.logger.PrintString(f"Info: 进入【标定模式：机械臂标定】")
      elif gVar.CurrMode is gVar.MODE_CALIBRATION and not gVar.IsCalibrateRobotArm and gVar.IsCalibrateChessBoard: # 如果是标定模式，且不在标定机械臂，且正在标定棋盘模式
        gVar.IsCalibrateRobotArm = True # 进入标定机械臂模式
        gVar.IsCalibrateChessBoard = False # 不在标定棋盘模式
        gVar.logger.PrintString(f"Info: 进入【标定模式：机械臂标定】")
      elif gVar.CurrMode is gVar.MODE_CALIBRATION and gVar.IsCalibrateRobotArm and not gVar.IsCalibrateChessBoard: # 如果是标定模式，且正在标定机械臂，且不在标定棋盘模式
        gVar.IsCalibrateRobotArm = False # 不在标定机械臂模式
        gVar.IsCalibrateChessBoard = True # 进入标定棋盘模式
        gVar.logger.PrintString(f"Info: 进入【标定模式：棋盘标定】")

    elif PressKey == ord('2'): # 如果按下'2'键，从待机模式切换到整理模式
      if gVar.CurrMode is gVar.MODE_STANDBY: # 如果是待机模式，才能进入整理模式
        gVar.CurrMode = gVar.MODE_ARRANGE # 切换到整理模式
        gVar.logger.PrintString(f"Info: 进入【整理模式】")
      elif gVar.CurrMode is gVar.MODE_ARRANGE: # 如果是整理模式，才能退出
        gVar.CurrMode = gVar.MODE_STANDBY # 切换到待机模式
        gVar.logger.PrintString(f"Info: 退出【整理模式】")

    elif PressKey == ord('3'): # 如果按下'3'键，从待机模式切换到对弈模式
      if gVar.CurrMode is gVar.MODE_STANDBY: # 如果是待机模式，才能进入对弈模式
        gVar.CurrMode = gVar.MODE_PLAYING # 切换到对弈模式
        gVar.logger.PrintString(f"Info: 进入【对弈模式】")
      elif gVar.CurrMode is gVar.MODE_PLAYING: # 如果是对弈模式，才能退出
        gVar.CurrMode = gVar.MODE_STANDBY # 切换到待机模式
        gVar.logger.PrintString(f"Info: 退出【对弈模式】")

    elif PressKey == ord(' '): # 如果按下空格键，确认落子
      if gVar.CurrMode is gVar.MODE_PLAYING and gVar.IsGameOver: # 如果是对弈模式，且游戏结束了，按空格键可从整理模式重新开始
        gVar.CurrMode = gVar.MODE_ARRANGE # 切换到整理模式
        gVar.logger.PrintString(f"Info: 从【整理模式】重新开始游戏")
      elif gVar.CurrMode is gVar.MODE_PLAYING: # 如果是对弈模式，才能确认落子
        gVar.IsUserTurn = False # 用户按空格键确认落子，所以按下空格后，是为电脑的回合，才会开始调用视觉算法检测棋盘

    elif PressKey == ord('q'): # 如果按下'q'键，切换双连杆线段显示状态
      gVar.IsDrawTwoLine = not gVar.IsDrawTwoLine # 切换双连杆线段显示状态
      gVar.logger.PrintString(f"Info: 切换双连杆线段显示状态为: {gVar.IsDrawTwoLine}")

    elif PressKey == ord('w'): # 如果按下'w'键，切换棋盘表格显示状态
      if gVar.CurrMode is gVar.MODE_STANDBY: # 如果是待机模式，才能显示这个棋盘表格（很占性能）
        gVar.IsAnchorVisible = not gVar.IsAnchorVisible # 切换表格显示状态
        gVar.logger.PrintString(f"Info: 切换棋盘表格显示状态为: {gVar.IsAnchorVisible}")
      else:
        gVar.IsAnchorVisible = False # 如果不是待机模式，不显示棋盘表格
        gVar.logger.PrintString(f"Info: 非待机模式，不显示棋盘表格")

    else: pass # 如果按下了未定义的按键





  # gVar.exit_flag = True # 通知其他多线程退出
  # recv_thread.join() # 等待接收线程退出





  gVar.logger.PrintString("Info: 程序退出") # 打印已退出信息
  time.sleep(0.5) # 延时是为了能把最后一点点数据也打印出来











































# if __name__ == "__main__":
#   import cv2
#   import numpy as np
  
#   # ====================== 颜色阈值（和你原来完全一样） ======================
#   RED_LOW = (0, 80, 80)
#   RED_HIGH = (10, 255, 255)
  
#   # ====================== 打开摄像头 ======================
#   cap = cv2.VideoCapture(1)
  
#   while True:
#     # 读取一帧图像
#     ret, frame = cap.read()
#     if not ret:
#       continue
  
#     # 1. 转 HSV
#     hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
  
#     # 2. 红色二值化（和你逻辑完全一样）
#     red_mask = cv2.inRange(hsv, RED_LOW, RED_HIGH)
  
#     # 3. 显示两个窗口
#     cv2.imshow("Original Camera", frame)          # 原图窗口
#     cv2.imshow("Red Binary Mask", red_mask)        # 红色二值图窗口
  
#     # 按 ESC 退出
#     key = cv2.waitKey(1) & 0xFF
#     if key == 27:
#       break
  
#   # 释放资源
#   cap.release()
#   cv2.destroyAllWindows()