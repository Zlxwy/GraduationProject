## 安装Python包

- 如果有 NVIDIA 显卡
```bash
pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cuxxx
pip install matplotlib opencv-python pyserial PyQt5
```

- 如果没有 NVIDIA 显卡
```bash
pip install torch torchvision matplotlib opencv-python pyserial PyQt5
```

## 启动程序

先查看串口设备号，在 Windows 系统中，设备号通常是 COMx ，在 Linux 系统中，设备号通常是 /dev/ttyXxx

- 如果是 Windows 系统，运行 `python main.py COMx`
- 如果是 Linux 系统，运行 `python3 main.py /dev/ttyACMx`

> 如果在 Ubuntu 运行的时候，确定串口号输入正确，但还是打不开串口，
> 可尝试运行 `sudo chmod 666 "串口设备号"`，给设备加上权限。 

## 程序使用

在进入程序后，画面中显示摄像头画面，此时为待机模式，画面左上角显示 **MODE_STANDBY**
![待机模式界面](./.README_assets/待机模式界面.png)

键盘按数字 **1** ，进入校准模式，画面左上角显示 **MODE_CALIBRATION** ，此时为校准棋盘状态，拖拽画面中显示的棋盘表格角点，对准棋盘。
![校准棋盘界面](./.README_assets/校准棋盘界面.png)

对准棋盘后，键盘再次按数字 **1** ，进入校准机械臂状态，拖拽画面中显示的两条箭头线段，与平面上的两条机械臂平行。
![校准机械臂界面](./.README_assets/校准机械臂界面.png)

棋盘表格、机械臂箭头线段都拖拽对准后，键盘按下 **Enter** 键，此时远离机械臂，机械臂准备回归待机位置。
![机械臂复位至待机位](./.README_assets/机械臂复位至待机位.png)

机械臂回归待机位置后，键盘按数字 **2** ，进入整理模式，此时画面左上角显示 **MODE_ARRANGE** ，需要手动将所有棋子回归原位（本来是想让机械臂自动整理的，但没有实现这个功能😔）。
![整理模式界面](./.README_assets/整理模式界面.png)

棋子摆回原位后，程序将会自动切换至对弈模式，画面左上角显示 **MODE_PLAYING** 。
![对弈模式界面](./.README_assets/对弈模式界面.png)

用户执红棋，机械臂执黑棋，默认用户先手，用户在落子后，**按空格键确认落子**，机械臂开始决策思考。

对局结束，一方被将军后，重新摆放好棋子，**按空格键可重新开始对局**。