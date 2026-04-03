# coding=utf-8

# 棋子编号定义
NOCHESS = 0 # 没有棋子

B_KING = 1 # 黑将
B_CAR = 2 # 黑車
B_HORSE = 3 # 黑馬
B_CANNON = 4 # 黑炮
B_BISHOP = 5 # 黑士
B_ELEPHANT = 6 # 黑象
B_PAWN = 7 # 黑卒
B_BEGIN = B_KING
B_END = B_PAWN

R_KING = 8 # 红帅
R_CAR = 9 # 红車
R_HORSE = 10 # 红馬
R_CANNON = 11 # 红炮
R_BISHOP = 12 # 红仕
R_ELEPHANT = 13 # 红相
R_PAWN = 14 # 红兵
R_BEGIN = R_KING
R_END = R_PAWN

UNKNOW = 15 # 未知棋子

chessTextChi = ('+-','将','車','馬','炮','士','象','卒','帅','車','馬','炮','仕','相','兵') # 棋子文本元组

INIT_CHESSBOARD = ( # 棋局初始状态元组
    (   B_CAR,  B_HORSE, B_ELEPHANT, B_BISHOP,  B_KING, B_BISHOP, B_ELEPHANT,  B_HORSE,   B_CAR ),
    ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
    ( NOCHESS, B_CANNON,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS, B_CANNON, NOCHESS ),
    (  B_PAWN,  NOCHESS,     B_PAWN,  NOCHESS,  B_PAWN,  NOCHESS,     B_PAWN,  NOCHESS,  B_PAWN ),
    ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
    ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
    (  R_PAWN,  NOCHESS,     R_PAWN,  NOCHESS,  R_PAWN,  NOCHESS,     R_PAWN,  NOCHESS,  R_PAWN ),
    ( NOCHESS, R_CANNON,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS, R_CANNON, NOCHESS ),
    ( NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS,  NOCHESS,    NOCHESS,  NOCHESS, NOCHESS ),
    (   R_CAR,  R_HORSE, R_ELEPHANT, R_BISHOP,  R_KING, R_BISHOP, R_ELEPHANT,  R_HORSE,   R_CAR ))


def IsRed(chessID) -> bool: # 判断棋子是不是红色棋子
    return R_BEGIN <= chessID <= R_END


def IsBlack(chessID) -> bool: # 判断棋子是不是黑色棋子
    return B_BEGIN <= chessID <= B_END


def GetOneChessString(chessID): # 获取一个棋子的字符串表达形式
    if IsBlack(chessID):
        return '\033[0;37;44m' + chessTextChi[chessID] + '\033[0m' # 黑色棋子：字体白色，背景为蓝色
    elif IsRed(chessID):
        return '\033[0;37;41m' + chessTextChi[chessID] + '\033[0m' # 红色棋子：字体白色，背景为红色
    return chessTextChi[chessID] # 没有棋子，显示一个'+'


def GetLineChessString(line, n): # 获取一行棋子的字符串表达形式
    chessString = chr(n + ord('A'))+ '    ' # 棋盘左边界
    for i in range(8): # 处理一行的前8个棋子
        chessString += GetOneChessString(line[i]) + '---'
    if line[8] == NOCHESS:
        print( chessString + '+' +                       '    ' + chr(n + ord('A')) )
    else:
        print( chessString + GetOneChessString(line[8]) + '   ' + chr(n + ord('A')) )


def PrintChessBoard(chessBoard): # 打印整个棋局
    for i in range(23):
        if i>=2 and i<= 20 and (i-2)%2==0:
            GetLineChessString( chessBoard[int((i-2)/2)], int((i-2)/2) )
        elif i==7 or i==9 or i==13 or i==15:
            print('|    |    |    |    |    |    |    |    |    |    |') # 棋盘竖线
        elif i==0 or i==22:
            print('+----0----1----2----3----4----5----6----7----8----+') # 棋盘上下边界
        elif i==1 or i==21:
            print('|                                                 |') # 棋盘边缘
        elif i==3 or i==17:
            print(r'|    |    |    |    |  \ | /  |    |    |    |    |') # 九宫竖线，原样输出，不转义
        elif i==5 or i==19:
            print(r'|    |    |    |    |  / | \  |    |    |    |    |') # 九宫竖线，原样输出，不转义
        elif i==11:
            print('|    |        楚河               汉界        |    |') # 楚河汉界


def MakeMove(chessBoard, movePath): # 根据某一走法产生走之后的棋盘，参数:(当前棋盘,走棋路线)
    # 注意chessBoard为列表，函数内部是更改列表的单个元素值，这样对形参的更改会影响到实参，正好能实现功能
    # 保存起点的棋子值
    piece = chessBoard[ord(movePath[0])-ord('a')][ord(movePath[1])-ord('0')]
    # 将保存的棋子值放到终点
    chessBoard[ord(movePath[2])-ord('a')][ord(movePath[3])-ord('0')] = piece
    # 将起点设为无棋子
    chessBoard[ord(movePath[0])-ord('a')][ord(movePath[1])-ord('0')] = NOCHESS