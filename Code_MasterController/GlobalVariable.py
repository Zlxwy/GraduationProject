# GlobalVariable.py
import numpy as np


MyDevice = "Windows"
# MyDevice = "Linux"























# 每一条对应协议中的命令类型
COMMAND_TYPE_MOTOR_BASIC_MOVE = 0x0000
COMMAND_TYPE_MOTOR_MOVE_ON_PLANE = 0x0001
COMMAND_TYPE_MOTOR_VERTICAL_AXIS_RST = 0x0003
COMMAND_TYPE_MOTOR_VERTICAL_AXIS_MOVE = 0x0002
COMMAND_TYPE_SET_MAGNET_STATUS = 0x0004
COMMAND_TYPE_KEY_CLICK = 0x0005





logger = None # 日志对象
MainStream = None # 主线程的流对象
tsm = None # 三轴步进电机对象


mouse_x = 0
mouse_y = 0
LButtonDownFlag = False
MouseMoveFlag = False
LButtonUpFlag = False
is_pressed = False
mark_point = [0,0]




Cap = None # 摄像头对象

CapWidth = 1920
CapHeight = 1080

RoiWidth = CapHeight
RoiHeight = CapHeight

RoiStartX = (CapWidth-RoiWidth) // 2
RoiStartY = (CapHeight-RoiHeight) // 2

# 系统当前模式
CurrMode = None

# 模式常量（推荐大写，Python 标准命名风格）
MODE_STANDBY     = "MODE_STANDBY" # 待机模式
MODE_CALIBRATION = "MODE_CALIBRATION" # 机械臂标定模式
IsCalibrateRobotArm = False # 是否正在标定机械臂
IsCalibrateChessBoard = False # 是否正在标定棋盘
MODE_ARRANGE     = "MODE_ARRANGE" # 整理模式
MODE_PLAYING     = "MODE_PLAYING" # 对弈模式





IsDrawTwoLine = False # 是否显示双连杆线段
IsAnchorVisible = False # 是否显示棋盘表格


IsArranged = False # 棋子是否整理完成
IsGameRunning = False # 是否正在对弈中
IsGameOver = False # 当前对局是否结束
IsUserTurn = False  # True用户回合，False电脑回合
IsUserWin = False # 用户是否赢了
IsPcWin = False # 电脑是否赢了







ChessBoard_InnerCorner_TopLeft_CvPlane  = [ 204, 199 ] # 棋盘内部左上角坐标，摄像头画面的CV坐标系
ChessBoard_InnerCorner_TopRight_CvPlane = [ 871, 202 ] # 棋盘内部右上角坐标，摄像头画面的CV坐标系
ChessBoard_InnerCorner_BotRight_CvPlane = [ 873, 924 ] # 棋盘内部右下角坐标，摄像头画面的CV坐标系
ChessBoard_InnerCorner_BotLeft_CvPlane  = [ 204, 929 ] # 棋盘内部左下角坐标，摄像头画面的CV坐标系
ChessBoard_InnerCorners_CvPlane = [
  ChessBoard_InnerCorner_TopLeft_CvPlane,
  ChessBoard_InnerCorner_TopRight_CvPlane,
  ChessBoard_InnerCorner_BotRight_CvPlane,
  ChessBoard_InnerCorner_BotLeft_CvPlane ]
ChessBoard_OuterCorner_TopLeft_CvPlane  = [ None, None ] # 棋盘外部左上角坐标，摄像头画面的CV坐标系
ChessBoard_OuterCorner_TopRight_CvPlane = [ None, None ] # 棋盘外部右上角坐标，摄像头画面的CV坐标系
ChessBoard_OuterCorner_BotRight_CvPlane = [ None, None ] # 棋盘外部右下角坐标，摄像头画面的CV坐标系
ChessBoard_OuterCorner_BotLeft_CvPlane  = [ None, None ] # 棋盘外部左下角坐标，摄像头画面的CV坐标系
ChessBoard_OuterCorners_CvPlane = [ # 棋盘外部4个角点的CV坐标系列表
  ChessBoard_OuterCorner_TopLeft_CvPlane,
  ChessBoard_OuterCorner_TopRight_CvPlane,
  ChessBoard_OuterCorner_BotRight_CvPlane,
  ChessBoard_OuterCorner_BotLeft_CvPlane ]

# 以下这部分坐标是以现实世界测量而来，不可改动
ChessBoard_InnerCorner_TopLeft_ArmPlane  = [ +117.00,  +86.00 ] # 棋盘内部左上角坐标，机械臂现实世界的笛卡尔坐标系
ChessBoard_InnerCorner_TopRight_ArmPlane = [ -117.00,  +86.00 ] # 棋盘内部右上角坐标，机械臂现实世界的笛卡尔坐标系
ChessBoard_InnerCorner_BotRight_ArmPlane = [ -117.00, +340.00 ] # 棋盘内部右下角坐标，机械臂现实世界的笛卡尔坐标系
ChessBoard_InnerCorner_BotLeft_ArmPlane  = [ +117.00, +340.00 ] # 棋盘内部左下角坐标，机械臂现实世界的笛卡尔坐标系
ChessBoard_InnerCorners_ArmPlane = [
  ChessBoard_InnerCorner_TopLeft_ArmPlane,
  ChessBoard_InnerCorner_TopRight_ArmPlane,
  ChessBoard_InnerCorner_BotRight_ArmPlane,
  ChessBoard_InnerCorner_BotLeft_ArmPlane ]
ChessBoard_OuterCorner_TopLeft_ArmPlane  = [ +133.75, +72.75  ] # 棋盘外部左上角坐标，机械臂现实世界的笛卡尔坐标系
ChessBoard_OuterCorner_TopRight_ArmPlane = [ -133.75, +72.75  ] # 棋盘外部右上角坐标，机械臂现实世界的笛卡尔坐标系
ChessBoard_OuterCorner_BotRight_ArmPlane = [ -133.75, +353.25 ] # 棋盘外部右下角坐标，机械臂现实世界的笛卡尔坐标系
ChessBoard_OuterCorner_BotLeft_ArmPlane  = [ +133.75, +353.25 ] # 棋盘外部左下角坐标，机械臂现实世界的笛卡尔坐标系
ChessBoard_OuterCorners_ArmPlane = [
  ChessBoard_OuterCorner_TopLeft_ArmPlane,
  ChessBoard_OuterCorner_TopRight_ArmPlane,
  ChessBoard_OuterCorner_BotRight_ArmPlane,
  ChessBoard_OuterCorner_BotLeft_ArmPlane ]
ChessBoard_CapBox_ArmPlane = [ +203.75, +288.25 ] # 吃子盒的坐标，被吃的棋子都丢在这里

LengthOfShoulder = 185 # 机械臂肩部的毫米长度
LengthOfElbow = 194 # 机械臂肘部的毫米长度

PlaneMapper_Arm2Cv = None # 机械臂arm坐标系到画面cv坐标系的映射器，将会在主程序中初始化
PlaneMapper_Cv2Arm = None # 画面cv坐标系到机械臂arm坐标系的映射器，将会在主程序中初始化

ChessBoard_Rows = 9 # 棋盘行数，这是棋盘表格空格的行数，而不是横线的行数
ChessBoard_Cols = 8 # 棋盘列数，这是棋盘表格空格的列数，而不是竖线的列数

CvPlane_ChangeReference = None # 变更参考点坐标
CvPlane_AnchorLine1_Start = [ +538, +30  ] # 标定线1的起始坐标
CvPlane_AnchorLine1_End   = [ +538, +400 ] # 标定线1的结束坐标
CvPlane_AnchorLine2_Start = [ +538, +440 ] # 标定线2的起始坐标
CvPlane_AnchorLine2_End   = [ +538, +980 ] # 标定线2的结束坐标

DegAngle_Runtime_Shoulder = 90.00 # 肩关节实时角度
DegAngle_Runtime_Elbow = 90.00 # 腕关节实时角度

DegAngle_StandByPos_Shoulder = 0.00 # 肩关节待机位置
DegAngle_StandByPos_Ebow = 90.00 # 腕关节待机位置
DegAngle_StandByPos_Lift = 0.00 # 竖轴关节待机位置

StepperMotorShoulder_Index = 0 # 肩关节步进电机索引
StepperMotorElbow_Index = 1 # 腕关节步进电机索引
StepperMotorLift_Index = 2 # 竖轴关节步进电机索引





ChessModel_Recognizer = None # 棋子识别器对象
ChessModel_InputSize = 128 # 模型输入尺寸
ChessModel_CONFIDENCE_THRESHOLD = 0.5 # 置信度阈值

ChessModel_ClassesLabels = ['JIANG', 'SHI', 'CHE', 'MA', 'PAO', 'XIANG', 'BING'] # 棋子识别器的类别标签
ChessModel_DispLabels = ['J', 'S', 'C', 'M', 'P', 'X', 'B'] # 实际显示的棋子标签，字母少一些

# 霍夫圆检测参数
HOUGH_PARAM1 = 80 # 霍夫圆检测参数1（边缘检测阈值）
HOUGH_PARAM2 = 25 # 霍夫圆检测参数2（圆心检测阈值）
HOUGH_MIN_RADIUS = 26 # 最小圆半径
HOUGH_MAX_RADIUS = 37 # 最大圆半径
HOUGH_MIN_DIST = HOUGH_MIN_RADIUS*2.2 # 圆之间的最小距离



# 以下这两个变量都是标准化的，只在程序中进行匹配，随象棋引擎而更新的
ChessBoard_IntersectionPointsGrid_CvPlane = None # 直线交点的标准点阵信息，CV坐标系的，要在程序中初始化，维度(10,9,2)
ChessBoard_ChessSituation_ForChessEngine = None # 棋盘当前局势状态，用于棋盘引擎的，要在程序中初始化，维度(10,9,1)

# 以下这两个变量都是检测现实世界的棋盘状态获取的，这两个变量会同步更新
ChessBoard_ChessPiecePointsGrid_CvPlane = None # 棋盘棋子点阵信息，CV坐标系的，要在程序中初始化，维度(10,9,2)，这个列表除了有棋子的位置，其他元素都和ChessBoard_IntersectionPointGrid_CV中的元素相同
ChessBoard_ChessSituation_FromRecognizer = None # 棋盘当前局势状态，从识别器中获取的，要在程序中初始化，维度(10,9,1)




ChessEngine_CallThread = None # 调用象棋引擎的线程
ChessEngine_Result = None # 调用象棋引擎的结果
ChessEngine_IsRunning = None # 调用象棋引擎是否正在运行
ChessEngine_ResultFinished = False # 调用象棋引擎的结果是否完成


UserMove = None # 用户落子字符串
PcMoveAgainstUser = None # 电脑落子字符串，对弈中电脑落子
UserMoveArrowColor = ( 0, 0, 255 ) # 用户走棋路径用红色
PcMoveArrowColor = ( 30, 30, 30 ) # 电脑走棋路径用灰色
