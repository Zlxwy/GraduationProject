import tkinter as tk

def draw_flowchart():
    root = tk.Tk()
    root.title("机械臂标定与下棋流程图")
    root.geometry("1200x900")
    
    canvas = tk.Canvas(root, bg="white", scrollregion=(0, 0, 1100, 850))
    canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # 节点定义 - 重新布局，避免交叉
    nodes = {
        'A': {'text': '机器开机', 'x': 500, 'y': 50, 'type': 'process'},
        'B': {'text': '按下Key1', 'x': 500, 'y': 120, 'type': 'process'},
        'C': {'text': '进入机械臂\n标定模式', 'x': 500, 'y': 190, 'type': 'process'},
        'D': {'text': '机器三轴停在\n标定点处', 'x': 500, 'y': 260, 'type': 'process'},
        'E': {'text': '按下Key2', 'x': 500, 'y': 330, 'type': 'process'},
        'F': {'text': '棋子是否\n归位?', 'x': 500, 'y': 420, 'type': 'decision'},
        'G': {'text': '机械手整理棋盘', 'x': 800, 'y': 420, 'type': 'process'},
        'H': {'text': '用户落子', 'x': 500, 'y': 510, 'type': 'process'},
        'I': {'text': '按下Key3', 'x': 500, 'y': 580, 'type': 'process'},
        'J': {'text': '对局是否\n结束?', 'x': 500, 'y': 670, 'type': 'decision'},
        'K': {'text': '电脑决策', 'x': 200, 'y': 670, 'type': 'process'},
        'L': {'text': '电脑下发\n落子命令', 'x': 200, 'y': 580, 'type': 'process'},
        'M': {'text': 'STM32控制\n机械臂落子', 'x': 200, 'y': 490, 'type': 'process'},
        'N': {'text': '对局是否\n结束?', 'x': 200, 'y': 400, 'type': 'decision'},
        'O': {'text': '屏幕显示\n结束信息', 'x': 500, 'y': 770, 'type': 'process'},
    }
    
    def draw_process_box(canvas, x, y, text):
        w, h = 120, 50
        canvas.create_rectangle(x - w/2, y - h/2, x + w/2, y + h/2,
                                 fill="#E3F2FD", outline="#1976D2", width=2)
        canvas.create_text(x, y, text=text, font=("微软雅黑", 11), anchor="center")
    
    def draw_decision_diamond(canvas, x, y, text):
        w, h = 100, 70
        points = [x, y-h/2, x+w/2, y, x, y+h/2, x-w/2, y]
        canvas.create_polygon(points, fill="#FFF3E0", outline="#F57C00", width=2)
        canvas.create_text(x, y, text=text, font=("微软雅黑", 10), anchor="center")
    
    def draw_arrow(canvas, x1, y1, x2, y2, label=""):
        canvas.create_line(x1, y1, x2, y2, fill="#333", width=1.5)
        # 箭头
        dx, dy = x2 - x1, y2 - y1
        length = (dx**2 + dy**2)**0.5
        if length > 0:
            dx, dy = dx/length * 8, dy/length * 8
            px, py = -dy, dx
            canvas.create_polygon([x2, y2, x2-dx+px*0.5, y2-dy+py*0.5, x2-dx-px*0.5, y2-dy-py*0.5],
                                   fill="#333")
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            offset = 15
            canvas.create_text(mx+offset, my, text=label, font=("微软雅黑", 9, "bold"),
                             fill="#D32F2F", anchor="center")
    
    # 绘制节点
    for key, node in nodes.items():
        if node['type'] == 'process':
            draw_process_box(canvas, node['x'], node['y'], node['text'])
        else:
            draw_decision_diamond(canvas, node['x'], node['y'], node['text'])
    
    # 主流程竖线 (A -> B -> C -> D -> E -> F)
    draw_arrow(canvas, 500, 75, 500, 95)
    draw_arrow(canvas, 500, 145, 500, 165)
    draw_arrow(canvas, 500, 215, 500, 235)
    draw_arrow(canvas, 500, 285, 500, 305)
    draw_arrow(canvas, 500, 355, 500, 385)
    
    # F 判断 - 否 -> G (向右)
    draw_arrow(canvas, 550, 420, 740, 420, "否")
    
    # G -> F (向左返回，走下方)
    canvas.create_line(800, 445, 800, 460, fill="#333", width=1.5)
    canvas.create_line(800, 460, 500, 460, fill="#333", width=1.5)
    draw_arrow(canvas, 500, 460, 500, 455)
    
    # F 判断 - 是 -> H
    draw_arrow(canvas, 500, 455, 500, 485)
    
    # H -> I
    draw_arrow(canvas, 500, 535, 500, 555)
    
    # I -> J
    draw_arrow(canvas, 500, 605, 500, 635)
    
    # J 判断 - 是 -> O
    draw_arrow(canvas, 500, 705, 500, 745)
    
    # J 判断 - 否 -> K (向左)
    draw_arrow(canvas, 450, 670, 260, 670, "否")
    
    # K -> L
    draw_arrow(canvas, 200, 645, 200, 605)
    
    # L -> M
    draw_arrow(canvas, 200, 555, 200, 515)
    
    # M -> N
    draw_arrow(canvas, 200, 465, 200, 435)
    
    # N 判断 - 否 -> H (向左再向上到H)
    canvas.create_line(150, 400, 100, 400, fill="#333", width=1.5)
    canvas.create_line(100, 400, 100, 510, fill="#333", width=1.5)
    canvas.create_line(100, 510, 440, 510, fill="#333", width=1.5)
    draw_arrow(canvas, 440, 510, 440, 510)
    canvas.create_polygon([440, 510, 445, 515, 435, 515], fill="#333")
    canvas.create_text(120, 455, text="否", font=("微软雅黑", 9, "bold"), fill="#D32F2F")
    
    # N 判断 - 是 -> O (向右再向下)
    canvas.create_line(250, 400, 350, 400, fill="#333", width=1.5)
    canvas.create_line(350, 400, 350, 770, fill="#333", width=1.5)
    canvas.create_line(350, 770, 440, 770, fill="#333", width=1.5)
    draw_arrow(canvas, 440, 770, 440, 770)
    canvas.create_polygon([440, 770, 445, 775, 435, 775], fill="#333")
    canvas.create_text(300, 385, text="是", font=("微软雅黑", 9, "bold"), fill="#2E7D32")
    
    # O -> E (最外层循环：向右再向上)
    canvas.create_line(560, 770, 620, 770, fill="#333", width=1.5)
    canvas.create_line(620, 770, 620, 330, fill="#333", width=1.5)
    canvas.create_line(620, 330, 560, 330, fill="#333", width=1.5)
    draw_arrow(canvas, 560, 330, 560, 330)
    canvas.create_polygon([560, 330, 555, 335, 565, 335], fill="#333")
    canvas.create_text(640, 550, text="回到\n外层循环", font=("微软雅黑", 9), fill="#666")
    
    # 添加图例
    canvas.create_rectangle(50, 30, 170, 80, fill="#E3F2FD", outline="#1976D2", width=2)
    canvas.create_text(110, 55, text="处理步骤", font=("微软雅黑", 10), anchor="center")
    
    x0, y0 = 50, 95
    points = [110, y0-15, 145, y0+10, 110, y0+35, 75, y0+10]
    canvas.create_polygon(points, fill="#FFF3E0", outline="#F57C00", width=2)
    canvas.create_text(110, y0+10, text="判断", font=("微软雅黑", 10), anchor="center")
    
    root.mainloop()

if __name__ == "__main__":
    draw_flowchart()
