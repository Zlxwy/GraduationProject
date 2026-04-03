# coding=utf-8

import sys
import os
import copy

# 添加当前目录到Python路径，确保能导入ElephantFish和ChessInterface
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ElephantFish import ElephantFishChessInit, ElephantFishChessSE
from ChessInterface import PrintChessBoard, MakeMove, INIT_CHESSBOARD, IsBlack, IsRed

def create_initial_board():
    # 使用ChessInterface.py中定义的初始棋盘
    return [list(row) for row in INIT_CHESSBOARD]

def main():
    chess_board = create_initial_board() # 以列表形式创建一个初始棋盘
    ElephantFishChessInit(chess_board) # 初始化象棋引擎
    PrintChessBoard(chess_board) # 将当前棋盘打印出来

    print("输入格式：例如 'h7h4' 表示从 h7 移动到 h4")
    print("输入 'quit' 退出程序")
    
    while True:
        user_move = input("\n请输入你的走棋：") # 用户输入指令走棋
        
        if user_move.lower() == 'quit': # 如果输入指令为quit
            print("程序退出！") # 打印程序退出信息
            break # 打印程序退出信息，并退出程序
        
        if len(user_move) != 4: # 如果输入指令长度不为4
            print("输入格式错误，请重新输入！") # 打印输入格式错误信息
            continue # 继续循环，等待用户输入正确指令

        try:
            result = ElephantFishChessSE(user_move) # 将用户走棋指令传入象棋引擎
            if result == 'invalid': # 引擎判断用户走棋无效
                print("走棋无效，请重新输入！") # 打印走棋无效信息
            elif result == -1: # 引擎判断用户赢了
                print(f"\n你走了[{user_move}]后的棋盘：") # 打印用户走棋后的棋盘
                MakeMove(chess_board, user_move) # 更新用户走棋后的棋盘
                PrintChessBoard(chess_board) # 打印用户走棋后的棋盘
                print("恭喜你赢了！") # 打印恭喜用户赢了的信息
                break # 用户胜利，跳出循环
            else: # 引擎判断用户走棋正常
                pc_move, pc_check, pc_capture, depth, time_used, HasPCWon = result # 获取引擎计算出的电脑走法

                # 检查用户是否吃子，并画出用户走棋后的棋盘
                HasUserAte = IsBlack(chess_board[ord(user_move[2])-ord('a')][ord(user_move[3])-ord('0')]) # 检查用户走棋后是否吃子
                print(f"\n你走了[{user_move}]后的棋盘：") # 打印用户走棋后的棋盘
                MakeMove(chess_board, user_move) # 更新用户走棋后的棋盘
                PrintChessBoard(chess_board) # 打印用户走棋后的棋盘
                if HasUserAte: print("用户吃子！！！") # 如果用户吃子，打印提示

                # 检查电脑是否吃子、将军，并画出电脑走棋后的棋盘
                HasPCAte = IsRed(chess_board[ord(pc_move[2])-ord('a')][ord(pc_move[3])-ord('0')]) # 检查电脑走棋后是否吃子
                print(f"\n电脑走了[{pc_move}]后的棋盘：") # 打印电脑走棋后的棋盘
                MakeMove(chess_board, pc_move) # 更新电脑走棋后的棋盘
                PrintChessBoard(chess_board) # 打印电脑走棋后的棋盘
                if HasPCWon: # 如果电脑胜利
                    print("电脑胜利！！！") # 打印提示
                    break # 电脑胜利，跳出循环
                # if pc_capture: print("电脑吃子！！！") # 如果电脑吃子，打印提示
                if HasPCAte: print("电脑吃子！！！") # 如果电脑吃子，打印提示
                if pc_check: print("电脑将军！！！") # 如果电脑将军，打印提示

                print(f"\n")
                print(f"==========================")
                print(f"搜索深度：{depth}")
                print(f"思考时间：{time_used:.2f}秒")
                print(f"==========================")
                    
        except Exception as e:
            print(f"发生错误：{e}")
            print("请重新输入！")

if __name__ == "__main__":
    main()