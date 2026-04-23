# save as: hello_pyqt5.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QLabel, QMessageBox
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hello PyQt5")
        self.resize(300, 150)

        # 创建组件
        self.label = QLabel("欢迎使用 PyQt5！", self)
        self.button = QPushButton("点我一下", self)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        # 绑定事件
        self.button.clicked.connect(self.on_button_click)

    def on_button_click(self):
        QMessageBox.information(self, "提示", "你好！你点击了按钮。")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())