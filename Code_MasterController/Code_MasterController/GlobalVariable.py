# GlobalVariable.py

exit_flag = False # 退出标志位

# 每一条对应协议中的命令类型
COMMAND_TYPE_MOTOR_BASIC_MOVE = 0x0000
COMMAND_TYPE_MOTOR_MOVE_ON_PLANE = 0x0001
COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST = 0x0003
COMMAND_TYPE_MOTOR_VERTICAL_AXIS_MOVE = 0x0002
COMMAND_TYPE_SET_MAGNET_STATUS = 0x0004
COMMAND_TYPE_KEY_CLICK = 0x0005

draw_table_flag = False # 绘制表格标志位

logger = None

CamIndex = 1
CapWidth = 1920
CapHeight = 1080
RoiWidth = CapHeight
RoiHeight = CapHeight


