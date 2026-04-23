"""
中国象棋棋子数据采集工具
基于 PyQt5 + OpenCV，霍夫圆检测定位棋子 → 鼠标点击 → 选择类别 → 保存训练图片。

用法: python data_collector.py
操作:
  - 鼠标左键点击棋子圆形 → 弹出类别选择框
  - 弹窗中数字键 1-7 快速选择类别，Enter 确认，Esc 取消
  - 主窗口中 Space 暂停/继续采集，Esc 退出
"""

# 导入系统模块
import sys
# 导入操作系统模块
import os
# 导入 OpenCV 库
import cv2
# 导入 NumPy 库
import numpy as np

# 从 PyQt5 导入必要的 GUI 组件
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QDialog,
    QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup,
    QMessageBox, QSizePolicy, QWidget, QPushButton
)
# 从 PyQt5 导入核心组件
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
# 从 PyQt5 导入 GUI 相关组件
from PyQt5.QtGui import QFont, QPixmap, QImage

# ==================== 配置参数（与 cam_hough_circle.py 保持一致） ====================

# 摄像头索引（0 为默认摄像头，1 为外部摄像头）
CAM_INDEX = 1
# 摄像头采集宽度
CAP_WIDTH = 1920
# 摄像头采集高度
CAP_HEIGHT = 1080
# 感兴趣区域大小（与采集高度相同）
ROI_SIZE = CAP_HEIGHT  # 1080

# 霍夫圆检测参数 (与 cam_hough_circle.py 一致)
HOUGH_PARAM1 = 80 # 霍夫圆检测参数1（边缘检测阈值）
HOUGH_PARAM2 = 25 # 霍夫圆检测参数2（圆心检测阈值）
HOUGH_MIN_RADIUS = 26 # 最小圆半径
HOUGH_MAX_RADIUS = 37 # 最大圆半径
HOUGH_MIN_DIST = HOUGH_MIN_RADIUS*2.2 # 圆之间的最小距离

# 7 个文字类别（红黑方通过颜色阈值区分，不纳入分类）
CLASSES = ['JIANG', 'SHI', 'CHE', 'MA', 'PAO', 'XIANG', 'BING']
# 类别对应的数字快捷键
CLASS_SHORTCUTS = '1234567'

# 保存图片尺寸（MobileNetV3 训练用）
SAVE_SIZE = 128

# 数据集保存目录（与本脚本同级的 dataset 文件夹）
DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dataset')


# ==================== 自定义控件：可点击的图像标签 ====================

class ImageLabel(QLabel):
    """显示摄像头画面，自动缩放填满窗口，支持鼠标点击检测棋子圆形"""

    # 定义信号，用于传递被点击圆的索引
    circle_clicked = pyqtSignal(int)  # 参数: 被点击圆的索引

    def __init__(self, parent=None):
        # 调用父类构造函数
        super().__init__(parent)
        # 存储检测到的圆列表 [(cx, cy, r), ...]  原始图像坐标系
        self._circles = []       
        # 原始图像宽度
        self._img_w = 0          
        # 原始图像高度
        self._img_h = 0          
        # 原始分辨率 QPixmap（独立拷贝，不被 GC）
        self._orig_pixmap = None 
        # 设置最小尺寸
        self.setMinimumSize(400, 400)
        # 设置尺寸策略为可扩展
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 设置对齐方式为居中
        self.setAlignment(Qt.AlignCenter)
        # 设置鼠标指针为十字形
        self.setStyleSheet('cursor: crosshair;')

    def update_image(self, cv_img, circles):
        """接收 OpenCV BGR 图像和圆列表，刷新显示"""
        # 将 BGR 图像转换为 RGB 图像
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        # 获取图像的高度、宽度和通道数
        h, w, ch = rgb.shape
        # 存储原始图像宽度
        self._img_w = w
        # 存储原始图像高度
        self._img_h = h
        # 存储圆列表，如果为空则存储空列表
        self._circles = circles or []
        # .copy() 确保 QPixmap 持有独立数据，不依赖 numpy 数组生命周期
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        # 创建 QPixmap 并复制数据
        self._orig_pixmap = QPixmap.fromImage(qimg).copy()
        # 调用缩放方法
        self._rescale()

    def _rescale(self):
        """将原始 pixmap 按当前 label 尺寸等比缩放并显示"""
        # 如果原始 pixmap 为 None，则返回
        if self._orig_pixmap is None:
            return
        # 获取当前 label 的宽度和高度
        label_w, label_h = self.width(), self.height()
        # 如果尺寸过小，则返回
        if label_w < 2 or label_h < 2:
            return
        # 等比缩放 pixmap
        scaled = self._orig_pixmap.scaled(
            label_w, label_h, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        # 直接调父类 setPixmap，避免子类重写干扰
        super().setPixmap(scaled)

    def resizeEvent(self, event):
        """窗口大小变化时重新缩放，保证画面始终填满"""
        # 调用父类的 resizeEvent 方法
        super().resizeEvent(event)
        # 调用缩放方法
        self._rescale()

    def mousePressEvent(self, event):
        # 如果不是左键点击或没有圆，则返回
        if event.button() != Qt.LeftButton or not self._circles:
            return

        # 获取当前显示的缩放后 pixmap
        pm = super().pixmap()  # 当前显示的缩放后 pixmap
        # 如果 pixmap 为 None，则返回
        if pm is None:
            return

        # 缩放后的 pixmap 在 label 中居中，计算偏移
        sw, sh = pm.width(), pm.height()
        offset_x = (self.width() - sw) / 2.0
        offset_y = (self.height() - sh) / 2.0

        # 鼠标点击坐标 → 缩放 pixmap 坐标
        px = event.x() - offset_x
        py = event.y() - offset_y
        # 如果点击位置不在 pixmap 范围内，则返回
        if px < 0 or py < 0 or px > sw or py > sh:
            return

        # 缩放 pixmap 坐标 → 原始图像坐标
        ix = int(px * self._img_w / sw)
        iy = int(py * self._img_h / sh)

        # 判断点击落在哪个圆内（给予 1.2 倍容差）
        for i, (cx, cy, r) in enumerate(self._circles):
            if (ix - cx) ** 2 + (iy - cy) ** 2 <= (r * 1.2) ** 2:
                # 发送信号，传递圆的索引
                self.circle_clicked.emit(i)
                return


# ==================== 类别选择对话框 ====================

class CategoryDialog(QDialog):
    """选择棋子类别的弹窗，左侧预览裁剪图片，右侧单选按钮"""

    def __init__(self, piece_img_bgr, parent=None):
        # 调用父类构造函数
        super().__init__(parent)
        # 设置窗口标题
        self.setWindowTitle('Select Piece Category')
        # 设置最小尺寸
        self.setMinimumSize(460, 340)
        # 初始化 UI
        self._init_ui(piece_img_bgr)

    def _init_ui(self, img_bgr):
        # 创建水平布局作为根布局
        root = QHBoxLayout(self)

        # ---- 左侧：棋子预览 ----
        # 创建垂直布局
        left = QVBoxLayout()
        # 创建预览标题
        title = QLabel('Piece Preview')
        # 设置字体
        title.setFont(QFont('Microsoft YaHei', 11, QFont.Bold))
        # 设置对齐方式为居中
        title.setAlignment(Qt.AlignCenter)
        # 添加标题到布局
        left.addWidget(title)

        # 创建预览标签
        preview = QLabel()
        # 设置对齐方式为居中
        preview.setAlignment(Qt.AlignCenter)
        # 设置固定尺寸
        preview.setFixedSize(200, 200)
        # 设置样式
        preview.setStyleSheet('border: 2px solid #aaa; border-radius: 10px;')
        # 将 BGR 图像转换为 RGB 图像
        rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        # 获取图像的高度、宽度和通道数
        h, w, ch = rgb.shape
        # 创建 QImage
        qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        # 设置预览图像
        preview.setPixmap(
            QPixmap.fromImage(qimg).scaled(
                190, 190, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        # 添加预览到布局
        left.addWidget(preview)
        # 将左侧布局添加到根布局
        root.addLayout(left)

        # ---- 右侧：类别单选 ----
        # 创建垂直布局
        right = QVBoxLayout()
        # 创建选择标题
        sel_title = QLabel('Select Category:')
        # 设置字体
        sel_title.setFont(QFont('Microsoft YaHei', 11, QFont.Bold))
        # 添加标题到布局
        right.addWidget(sel_title)

        # 创建按钮组
        self._bg = QButtonGroup(self)
        # 遍历类别列表
        for i, cls_name in enumerate(CLASSES):
            # 创建单选按钮
            rb = QRadioButton(f'  {CLASS_SHORTCUTS[i]}.  {cls_name}')
            # 设置字体
            rb.setFont(QFont('Microsoft YaHei', 13))
            # 默认选中第一个
            if i == 0:
                rb.setChecked(True)
            # 添加按钮到按钮组
            self._bg.addButton(rb, i)
            # 添加按钮到布局
            right.addWidget(rb)

        # 创建提示标签
        hint = QLabel('Enter=Confirm  |  Esc=Cancel  |  Number keys to select')
        # 设置对齐方式为居中
        hint.setAlignment(Qt.AlignCenter)
        # 设置样式
        hint.setStyleSheet('color: #888; font-size: 11px;')
        # 添加提示到布局
        right.addWidget(hint)

        # 确认 / 取消按钮
        # 创建水平布局
        btn_layout = QHBoxLayout()
        # 创建确认按钮
        btn_ok = QPushButton('Confirm')
        # 设置字体
        btn_ok.setFont(QFont('Microsoft YaHei', 11))
        # 设置固定高度
        btn_ok.setFixedHeight(36)
        # 连接点击信号到 accept 槽
        btn_ok.clicked.connect(self.accept)
        # 创建取消按钮
        btn_cancel = QPushButton('Cancel')
        # 设置字体
        btn_cancel.setFont(QFont('Microsoft YaHei', 11))
        # 设置固定高度
        btn_cancel.setFixedHeight(36)
        # 连接点击信号到 reject 槽
        btn_cancel.clicked.connect(self.reject)
        # 添加按钮到布局
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        # 添加按钮布局到右侧布局
        right.addLayout(btn_layout)

        # 将右侧布局添加到根布局
        root.addLayout(right)

        # 设置布局
        self.setLayout(root)

    # ---- 键盘事件 ----
    def keyPressEvent(self, event):
        # 如果按下 Enter 键
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # 接受对话框
            self.accept()
        # 如果按下 Esc 键
        elif event.key() == Qt.Key_Escape:
            # 拒绝对话框
            self.reject()
        else:
            # 计算数字键对应的索引
            n = event.key() - Qt.Key_0
            # 如果是数字键 1-7
            if 1 <= n <= 7:
                # 选中对应的单选按钮
                self._bg.button(n - 1).setChecked(True)
            else:
                # 调用父类的 keyPressEvent 方法
                super().keyPressEvent(event)

    def selected_class(self):
        # 返回选中的类别
        return CLASSES[self._bg.checkedId()]


# ==================== 主窗口 ====================

class DataCollector(QMainWindow):
    def __init__(self):
        # 调用父类构造函数
        super().__init__()
        # 设置窗口标题
        self.setWindowTitle('Chinese Chess · Data Collector')
        # 设置最小尺寸
        self.setMinimumSize(900, 960)

        # 当前帧 ROI (BGR)
        self._roi = None          
        # 当前帧检测到的圆 [(cx, cy, r), ...]
        self._circles = []        
        # 当前高亮的圆索引 (-1 表示无)
        self._highlight = -1      
        # 是否暂停采集
        self._paused = False      

        # 初始化 UI
        self._init_ui()
        # 初始化摄像头
        self._init_camera()
        # 创建目录
        self._create_dirs()
        # 更新统计信息
        self._update_stats()

        # 定时器：~30 FPS 采集
        self._timer = QTimer(self)
        # 连接定时器信号到槽函数
        self._timer.timeout.connect(self._on_timer)
        # 启动定时器，每 33 毫秒触发一次
        self._timer.start(33)

    # ---------- 初始化 ----------

    def _init_ui(self):
        # 创建中央部件
        central = QWidget()
        # 设置中央部件
        self.setCentralWidget(central)
        # 创建垂直布局
        layout = QVBoxLayout(central)
        # 设置布局边距
        layout.setContentsMargins(5, 5, 5, 5)

        # 创建图像标签
        self._label = ImageLabel()
        # 连接 circle_clicked 信号到槽函数
        self._label.circle_clicked.connect(self._on_circle_clicked)
        # 添加图像标签到布局
        layout.addWidget(self._label, 1)

    def _init_camera(self):
        # 打开摄像头
        self._cam = cv2.VideoCapture(CAM_INDEX)
        # 如果无法打开摄像头
        if not self._cam.isOpened():
            # 显示错误信息
            QMessageBox.critical(self, 'Error', 'Cannot open camera')
            # 退出程序
            sys.exit(1)
        # 设置摄像头宽度
        self._cam.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_WIDTH)
        # 设置摄像头高度
        self._cam.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_HEIGHT)

    def _create_dirs(self):
        # 遍历类别列表
        for cls_name in CLASSES:
            # 创建目录，如果不存在
            os.makedirs(os.path.join(DATASET_DIR, cls_name), exist_ok=True)

    # ---------- 定时采集 ----------

    def _on_timer(self):
        # 如果暂停，则返回
        if self._paused:
            return

        # 读取摄像头帧
        ret, frame = self._cam.read()
        # 如果读取失败，则返回
        if not ret:
            return

        # 获取帧的高度和宽度
        h, w = frame.shape[:2]
        # 计算 ROI 的坐标
        x, y = (w - ROI_SIZE) // 2, (h - ROI_SIZE) // 2
        # 提取 ROI 区域
        roi = frame[y:y + ROI_SIZE, x:x + ROI_SIZE].copy()
        # 存储 ROI
        self._roi = roi

        # 霍夫圆检测
        # 转换为灰度图
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # 高斯模糊
        blur = cv2.GaussianBlur(gray, (19, 19), 2.5)
        # 霍夫圆检测
        circles = cv2.HoughCircles(
            blur, cv2.HOUGH_GRADIENT, dp=1,
            minDist=HOUGH_MIN_DIST,
            param1=HOUGH_PARAM1, param2=HOUGH_PARAM2,
            minRadius=HOUGH_MIN_RADIUS, maxRadius=HOUGH_MAX_RADIUS
        )

        # 如果检测到圆
        if circles is not None:
            # 转换为整数
            circles = np.uint16(np.around(circles))
            # 存储圆列表
            self._circles = [
                (int(c[0]), int(c[1]), int(c[2])) for c in circles[0]
            ]
        else:
            # 否则存储空列表
            self._circles = []

        # 重绘
        self._redraw()

    # ---------- 绘制 ----------

    def _redraw(self):
        # 如果 ROI 为 None，则返回
        if self._roi is None:
            return
        # 复制 ROI 用于显示
        display = self._roi.copy()

        # 绘制所有圆
        for cx, cy, r in self._circles:
            # 绘制圆心
            cv2.circle(display, (cx, cy), 1, (0, 100, 255), 3)
            # 绘制圆
            cv2.circle(display, (cx, cy), r, (255, 0, 255), 2)

        # 高亮选中的圆
        if 0 <= self._highlight < len(self._circles):
            # 获取选中圆的参数
            cx, cy, r = self._circles[self._highlight]
            # 绘制高亮圆
            cv2.circle(display, (cx, cy), r + 5, (0, 255, 0), 3)
            # 绘制选中文字
            cv2.putText(display, 'SELECTED', (cx - 50, cy - r - 12),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 更新图像标签
        self._label.update_image(display, self._circles)

    # ---------- 点击圆 → 弹窗选择 ----------

    def _on_circle_clicked(self, idx):
        # 如果没有圆或索引超出范围，则返回
        if not self._circles or idx >= len(self._circles):
            return

        # 高亮并暂停采集
        self._highlight = idx
        self._paused = True
        # 重绘
        self._redraw()

        # 获取选中圆的参数
        cx, cy, r = self._circles[idx]
        # 计算裁剪 padding
        pad = int(r * 1.2)
        # 获取 ROI 的高度和宽度
        ih, iw = self._roi.shape[:2]
        # 裁剪棋子区域
        piece = self._roi[max(cy - pad, 0):cy + pad, max(cx - pad, 0):cx + pad]

        # 创建类别选择对话框
        dlg = CategoryDialog(piece, self)
        # 如果用户确认
        if dlg.exec_() == QDialog.Accepted:
            # 获取选中的类别
            cls_name = dlg.selected_class()
            # 保存棋子图片
            self._save_piece(cx, cy, r, cls_name)
            # 显示保存成功信息
            self.statusBar().showMessage(
                f'Saved: {cls_name}  |  Space=Pause  Esc=Exit'
            )
            # 更新统计信息
            self._update_stats()
        else:
            # 显示取消标注信息
            self.statusBar().showMessage('Annotation cancelled')

        # 取消高亮，恢复采集
        self._highlight = -1
        self._paused = False

    # ---------- 保存棋子图片 ----------

    def _save_piece(self, cx, cy, r, cls_name):
        # 计算裁剪 padding
        pad = int(r * 1.2)
        # 获取 ROI 的高度和宽度
        ih, iw = self._roi.shape[:2]
        # 裁剪棋子区域
        piece = self._roi[max(cy - pad, 0):cy + pad, max(cx - pad, 0):cx + pad]

        # 如果裁剪区域为空，则返回
        if piece.size == 0:
            return

        # 缩放到 SAVE_SIZE x SAVE_SIZE
        piece = cv2.resize(piece, (SAVE_SIZE, SAVE_SIZE))

        # 计算保存路径
        dir_path = os.path.join(DATASET_DIR, cls_name)
        # 计算文件数量
        count = len(os.listdir(dir_path))
        # 生成文件名
        filename = f'{cls_name}_{count:04d}.jpg'
        # 计算文件路径
        filepath = os.path.join(dir_path, filename)

        # 直接使用 cv2.imwrite 保存图片
        # cv2.imwrite(filepath, piece)
        cv2.imencode('.jpg', piece)[1].tofile(filepath)

    # ---------- 统计信息 ----------

    def _update_stats(self):
        # 存储统计信息
        parts = []
        # 遍历类别列表
        for cls_name in CLASSES:
            # 计算类别目录路径
            dir_path = os.path.join(DATASET_DIR, cls_name)
            # 计算文件数量
            n = len(os.listdir(dir_path)) if os.path.exists(dir_path) else 0
            # 添加统计信息
            parts.append(f'{cls_name}: {n}')
        # 显示统计信息
        self.statusBar().showMessage(
            ' | '.join(parts) + '  |  Click piece to annotate  Space=Pause  Esc=Exit'
        )

    # ---------- 键盘快捷键 ----------

    def keyPressEvent(self, event):
        # 如果按下空格键
        if event.key() == Qt.Key_Space:
            # 切换暂停状态
            self._paused = not self._paused
            # 如果暂停
            if self._paused:
                # 显示暂停信息
                self.statusBar().showMessage('Paused  |  Space=Resume')
            else:
                # 更新统计信息
                self._update_stats()
        # 如果按下 Esc 键
        elif event.key() == Qt.Key_Escape:
            # 关闭窗口
            self.close()
        else:
            # 调用父类的 keyPressEvent 方法
            super().keyPressEvent(event)

    # ---------- 关闭 ----------

    def closeEvent(self, event):
        # 停止定时器
        self._timer.stop()
        # 释放摄像头
        self._cam.release()
        # 接受关闭事件
        event.accept()


# ==================== 入口 ====================

if __name__ == '__main__':
    # 创建应用程序
    app = QApplication(sys.argv)
    # 创建主窗口
    window = DataCollector()
    # 显示主窗口
    window.show()
    # 运行应用程序
    sys.exit(app.exec_())