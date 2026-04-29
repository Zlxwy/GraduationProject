## 安装Python包

如果有显卡
```bash
pip install torch==2.10.0 torchvision==0.25.0 torchaudio==2.10.0 --index-url https://download.pytorch.org/whl/cuxxx
pip install matplotlib opencv-python pyserial PyQt5
```

如果没有显卡
```bash
pip install torch torchvision matplotlib opencv-python pyserial PyQt5
```

## 运行程序

```bash
# python main.py "串口设备号"
python main.py COM9 # Windows
python3 main.py /dev/ttyACM0 # Linux
```
> 如果在 Ubuntu 运行的时候，确定串口号输入正确，但还是打不开串口，
> 可尝试运行 `sudo chmod 666 "串口设备号"`，给设备加上权限。 