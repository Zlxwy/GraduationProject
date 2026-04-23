# ThreeStepperMotor.py
# 这个类用来维护步进电机行走过的步数、以及当前的角度位置，维护的角度是在极坐标平面上的角度
import time
import math

# from Log import Log

class ThreeStepperMotor:
  def __init__(self):
    self.StepStepperMotorShoulder = int(0) # 标定后步数为0
    self.StepStepperMotorElbow = int(0) # 标定后步数为0
    self.StepStepperMotorLift = int(0) # 标定后步数为0

    self.PositionShoulder = float(0) # 标定后位置为90度
    self.PositionElbow = float(0) # 标定后位置为90度
    self.PositionLift = float(0) # 标定后位置为0%

  """
  更新三轴步进电机的步进步数
  :param StepperMotorType: 步进电机类型，"Shoulder"、"Elbow"、"Lift"
  :param step: 整数，表示步进电机的步进步数
  :return: None
  """
  def UpdateStepperMotorStep(self, StepperMotorType, step):
    if StepperMotorType == "Shoulder":
      self.StepStepperMotorShoulder += step
    elif StepperMotorType == "Elbow":
      self.StepStepperMotorElbow += step
    elif StepperMotorType == "Lift":
      self.StepStepperMotorLift += step

  """
  设置三轴步进电机的位置
  :param StepperMotorType: 步进电机类型，"Shoulder"、"Elbow"、"Lift"
  :param Position: 浮点数，表示步进电机的位置
  :return: None
  """
  def UpdateStepperMotorPosition(self, StepperMotorType, Position):
    if StepperMotorType == "Shoulder":
      self.PositionShoulder += Position
    elif StepperMotorType == "Elbow":
      self.PositionElbow += Position
    elif StepperMotorType == "Lift":
      self.PositionLift += Position

  """
  标定完成
  :return: None
  """
  def AllStepperMotorCalibrateOkay(self):
    # 标定点清零所有步数
    self.UpdateStepperMotorStep("Shoulder", 0)
    self.UpdateStepperMotorStep("Elbow", 0)
    self.UpdateStepperMotorStep("Lift", 0)

    # 标定点此时分别为90度，90度，0%（维护的角度是在极坐标平面上的角度）
    self.UpdateStepperMotorPosition("Shoulder", 90.0)
    self.UpdateStepperMotorPosition("Elbow", 90.0)
    self.UpdateStepperMotorPosition("Lift", 0.0)

  """
  步进电机步数转换为位置
  :param StepperMotorType: 步进电机类型，"Shoulder"、"Elbow"、"Lift"
  :param step: 整数，表示步进电机的步进步数
  :return: 浮点数，表示步进电机的位置，单位为度/%
  """
  def StepToPosition(self, StepperMotorType, step) -> float:
    dPos = 0.0
    if StepperMotorType == "Shoulder":
      # 肩关节电机为800步每圈，所以1步等于360/800=0.45度，齿轮比为20:130，因此乘以20/130
      dPos = step * (360/800) * (20/130)
      # dPos = step * 0.06923076923076923076923076923077
      # dPos = step * 0.069230769
    elif StepperMotorType == "Elbow":
      # 肘关节电机为800步每圈，所以1步等于360/800=0.45度，齿轮比为20:36，因此乘以20/36
      dPos = step * (360/800) * (20/36)
      # dPos = step * 0.25
    elif StepperMotorType == "Lift":
      # 竖轴电机下降到最底部触碰到棋子需要1230步，计算出步数所占1230的比例即可
      dPos = step * 100 / 1230
      # dPos = step * 0.08163265306122448979591836734694
      # dPos = step * 0.08163265
    return dPos

  def PositionToStep(self, StepperMotorType, Position) -> int:
    """
    步进电机位置转换为步数
    :param StepperMotorType: 步进电机类型，"Shoulder"、"Elbow"、"Lift"
    :param Position: 浮点数，表示步进电机的位置，单位为度/%
    :return: 整数，表示步进电机的步进步数
    """
    dStep = 0
    if StepperMotorType == "Shoulder":
      dStep = int(Position / (20/130) / (360/800))
      # dStep = int(Position * 14.4444444444444444444444444)
      # dStep = int(Position * 14.4444444)
    elif StepperMotorType == "Elbow":
      dStep = int(Position / (20/36) / (360/800))
      # dStep = int(Position * 4.0)
    elif StepperMotorType == "Lift":
      dStep = int(Position * 1230 / 100)
      # dStep = int(Position * 12.3)
    return dStep

  def cal_angle_diff(self, zero_degree: float, curr_degree: float, area: float) -> float:
    """
    以 a1 为 0 参考角度，将 a2 转换为极坐标轴上的角度
    与原 C 语言 fmodf 逻辑完全等价
    """
    diff = curr_degree - zero_degree
    value = diff + area * 3.0
    mod = math.fmod(value, area * 2.0)  # Python fmod 对应 C fmodf
    return mod - area

  # 传入三个目标位置，给出三个步数
  # 必须在标定完成后才能调用这个函数
  def DRIVE_MOTOR(self, TargetPosShoulder, TargetPosElbow, TargetPosLift) -> tuple[int, int, int]:
    """
    在标定完成后，输入三轴目标位置，输出三轴步进电机的步进步数
    :param TargetPosShoulder: 浮点数，表示肩关节的目标位置，单位为度
    :param TargetPosElbow: 浮点数，表示肘关节的目标位置，单位为度
    :param TargetPosLift: 浮点数，表示竖轴电机的目标位置，单位为%
    :return: 三元素元组，表示肩关节、肘关节、竖轴电机的步进步数
    """

    dStepShoulder, dStepElbow, dStepLift = 0, 0, 0 # 记录三轴转动步数，作为最终输出

    # 1.将传入目标位置参数四舍五入到2位小数，以避免精度差累积问题
    TargetPosShoulder = round(TargetPosShoulder, 2)
    TargetPosElbow = round(TargetPosElbow, 2)
    TargetPosLift = round(TargetPosLift, 2)

    # 2.计算肩关节需要转动的角度和步数
    # DiffPosShoulder = TargetPosShoulder - self.PositionShoulder # 计算出肩关节需要转动的角度
    DiffPosShoulder = self.cal_angle_diff(self.PositionShoulder, TargetPosShoulder, 180.0)
    DiffStepShoulder = self.PositionToStep("Shoulder", DiffPosShoulder) # 计算出肩关节需要转动的步数
    dStepShoulder += DiffStepShoulder # 累加肩关节需要转动的步数
    # 3.更新肩关节位置信息和步数信息
    self.UpdateStepperMotorPosition("Shoulder", DiffPosShoulder) # 更新肩关节位置
    self.UpdateStepperMotorStep("Shoulder", DiffStepShoulder) # 更新肩关节步数
    # 4.确定肘关节抵消转动角度和步数
    DiffPosElbow = -DiffPosShoulder # 肘关节需要反着肩关节转，抵消其在极坐标上的角度变化
    DiffStepElbow = self.PositionToStep("Elbow", DiffPosElbow) # 计算出肘关节需要转动的步数
    dStepElbow += DiffStepElbow # 累加肘关节抵消转动的步数
    # 5.更新肘关节的步数（这是肘关节抵消转动，不需要更新位置）
    self.UpdateStepperMotorStep("Elbow", DiffStepElbow) # 更新肘关节步数

    # 6.计算肘关节需要转动的角度和步数
    # DiffPosElbow = TargetPosElbow - self.PositionElbow # 计算出肘关节需要转动的角度
    DiffPosElbow = self.cal_angle_diff(self.PositionElbow, TargetPosElbow, 180.0)
    DiffStepElbow = self.PositionToStep("Elbow", DiffPosElbow) # 计算出肘关节需要转动的步数
    dStepElbow += DiffStepElbow # 累加肘关节需要转动的步数
    # 7.更新肘关节位置信息和步数信息
    self.UpdateStepperMotorPosition("Elbow", DiffPosElbow) # 更新肘关节位置
    self.UpdateStepperMotorStep("Elbow", DiffStepElbow) # 更新肘关节步数

    # 8.计算竖轴电机需要转动的百分比和步数
    DiffPosLift = TargetPosLift - self.PositionLift # 计算出竖轴电机需要转动的百分比
    DiffStepLift = self.PositionToStep("Lift", DiffPosLift) # 计算出竖轴电机需要转动的步数
    dStepLift += DiffStepLift # 累加竖轴电机需要转动的步数
    # 9.更新竖轴电机位置信息和步数信息
    self.UpdateStepperMotorPosition("Lift", DiffPosLift) # 更新竖轴电机位置
    self.UpdateStepperMotorStep("Lift", DiffStepLift) # 更新竖轴电机步数
    
    return dStepShoulder, dStepElbow, dStepLift # 最终返回三轴转动步数







# if __name__ == "__main__":
#   logger = Log()



#   logger.PrintString('-'*10 + 'start' + '-'*10)

#   tsm = ThreeStepperMotor()
#   tsm.AllStepperMotorCalibrateOkay() # 在XY平面标定完成、竖轴复位后，才可调用此函数
#   logger.PrintString(f"肩关节初始位置：{tsm.PositionShoulder}度")
#   logger.PrintString(f"肩关节初始步数：{tsm.StepStepperMotorShoulder}步")
#   logger.PrintString(f"肘关节初始位置：{tsm.PositionElbow}度")
#   logger.PrintString(f"肘关节初始步数：{tsm.StepStepperMotorElbow}步")
#   logger.PrintString(f"竖轴电机初始位置：{tsm.PositionLift}%")
#   logger.PrintString(f"竖轴电机初始步数：{tsm.StepStepperMotorLift}步")

#   # logger.PrintString('-'*10 + '1' + '-'*10)
  
#   # # 去到待机位，仿人类右手弓式姿势
#   # # 在极坐标平面上，即肩关节0度，肘关节90度，竖轴电机0%
#   # TargetPosShoulder = 0.00 # 肩关节电机目标位置(0.0度)
#   # TargetPosElbow = 45.00 # 肘关节电机目标位置(45.0度)
#   # TargetPosLift = 50.00 # 竖轴电机目标位置(50.0%)

#   # # 计算肩关节需要转动的角度和步数
#   # DiffPosShoulder = TargetPosShoulder - tsm.PositionShoulder # 计算出肩关节需要转动的角度
#   # DiffStepShoulder = tsm.PositionToStep("Shoulder", DiffPosShoulder) # 计算出肩关节需要转动的步数
#   # logger.PrintString(f"肩关节转动的步数为：{DiffStepShoulder}步")
#   # logger.PrintString(f"回算肩关节转动角度：{tsm.StepToPosition("Shoulder", DiffStepShoulder)}")
#   # # 更新肩关节位置信息和步数信息
#   # tsm.UpdateStepperMotorPosition("Shoulder", DiffPosShoulder)
#   # tsm.UpdateStepperMotorStep("Shoulder", DiffStepShoulder)
#   # logger.PrintString(f"肩关节当前位置：{tsm.PositionShoulder}度")
#   # logger.PrintString(f"肩关节当前步数：{tsm.StepStepperMotorShoulder}步")
#   # # 确定肘关节抵消转动角度和步数
#   # DiffPosElbow = -DiffPosShoulder # 肘关节需要反着肩关节转，抵消其在极坐标上的角度变化
#   # DiffStepElbow = tsm.PositionToStep("Elbow", DiffPosElbow) # 计算出肘关节需要转动的步数
#   # logger.PrintString(f"肘关节抵消转动的步数为：{DiffStepElbow}步")
#   # logger.PrintString(f"回算肘关节抵消转动角度：{tsm.StepToPosition("Elbow", DiffStepElbow)}")
#   # # 更新肘关节的步数（这是肘关节抵消转动，不需要更新位置）
#   # tsm.UpdateStepperMotorStep("Elbow", DiffStepElbow)
#   # logger.PrintString(f"肘关节当前位置：{tsm.PositionElbow}度")
#   # logger.PrintString(f"肘关节当前步数：{tsm.StepStepperMotorElbow}步")

#   # logger.PrintString('-'*10 + '2' + '-'*10)

#   # # 计算肘关节需要转动的角度和步数
#   # DiffPosElbow = TargetPosElbow - tsm.PositionElbow # 计算出肘关节需要转动的角度
#   # DiffStepElbow = tsm.PositionToStep("Elbow", DiffPosElbow) # 计算出肘关节需要转动的步数
#   # logger.PrintString(f"肘关节转动的步数为：{DiffStepElbow}步")
#   # logger.PrintString(f"回算肘关节转动角度：{tsm.StepToPosition("Elbow", DiffStepElbow)}")
#   # # 更新肘关节位置信息和步数信息
#   # tsm.UpdateStepperMotorPosition("Elbow", DiffPosElbow)
#   # tsm.UpdateStepperMotorStep("Elbow", DiffStepElbow)
#   # logger.PrintString(f"肘关节当前位置：{tsm.PositionElbow}度")
#   # logger.PrintString(f"肘关节当前步数：{tsm.StepStepperMotorElbow}步")

#   # logger.PrintString('-'*10 + '3' + '-'*10)

#   # # 计算竖轴电机需要转动的百分比和步数
#   # DiffPosLift = TargetPosLift - tsm.PositionLift # 计算出竖轴电机需要转动的百分比
#   # DiffStepLift = tsm.PositionToStep("Lift", DiffPosLift) # 计算出竖轴电机需要转动的步数
#   # logger.PrintString(f"竖轴电机转动的步数为：{DiffStepLift}步")
#   # logger.PrintString(f"回算竖轴电机转动百分比：{tsm.StepToPosition("Lift", DiffStepLift)}")
#   # # 更新竖轴电机位置信息和步数信息
#   # tsm.UpdateStepperMotorPosition("Lift", DiffPosLift)
#   # tsm.UpdateStepperMotorStep("Lift", DiffStepLift)
#   # logger.PrintString(f"竖轴电机当前位置：{tsm.PositionLift}%")
#   # logger.PrintString(f"竖轴电机当前步数：{tsm.StepStepperMotorLift}步")



#   logger.PrintString('-'*10 + '1' + '-'*10)

#   dStepShoulder, dStepElbow, dStepLift = tsm.DRIVE_MOTOR(0.00, 45.00, 50.00)
#   logger.PrintString(f"肩关节转动的步数为：{dStepShoulder}步")
#   logger.PrintString(f"肘关节转动的步数为：{dStepElbow}步")
#   logger.PrintString(f"竖轴电机转动的步数为：{dStepLift}步")
#   logger.PrintString(f"肩关节当前位置：{tsm.PositionShoulder}度")
#   logger.PrintString(f"肘关节当前位置：{tsm.PositionElbow}度")
#   logger.PrintString(f"竖轴电机当前位置：{tsm.PositionLift}%")
#   logger.PrintString(f"肩关节当前步数：{tsm.StepStepperMotorShoulder}步")
#   logger.PrintString(f"肘关节当前步数：{tsm.StepStepperMotorElbow}步")
#   logger.PrintString(f"竖轴电机当前步数：{tsm.StepStepperMotorLift}步")

#   logger.PrintString('-'*10 + '2' + '-'*10)

#   dStepShoulder, dStepElbow, dStepLift = tsm.DRIVE_MOTOR(45.00, 90.00, 75.00)
#   logger.PrintString(f"肩关节转动的步数为：{dStepShoulder}步")
#   logger.PrintString(f"肘关节转动的步数为：{dStepElbow}步")
#   logger.PrintString(f"竖轴电机转动的步数为：{dStepLift}步")
#   logger.PrintString(f"肩关节当前位置：{tsm.PositionShoulder}度")
#   logger.PrintString(f"肘关节当前位置：{tsm.PositionElbow}度")
#   logger.PrintString(f"竖轴电机当前位置：{tsm.PositionLift}%")
#   logger.PrintString(f"肩关节当前步数：{tsm.StepStepperMotorShoulder}步")
#   logger.PrintString(f"肘关节当前步数：{tsm.StepStepperMotorElbow}步")
#   logger.PrintString(f"竖轴电机当前步数：{tsm.StepStepperMotorLift}步")

#   logger.PrintString('-'*10 + 'end' + '-'*10)



#   time.sleep(0.5)
#   logger.stop()
