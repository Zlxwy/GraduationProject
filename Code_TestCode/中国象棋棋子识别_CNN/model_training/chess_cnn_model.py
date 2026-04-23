"""
中国象棋棋子分类 CNN 模型定义

供 train_cnn.py（训练）和 recognize.py（推理）共用，避免重复定义。
"""

import torch
import torch.nn as nn


class ChessCNN(nn.Module):
    """用于中国象棋棋子分类的卷积神经网络 (128x128 RGB -> num_classes类)"""

    def __init__(self, num_classes=7):
        super().__init__()
        # 卷积特征提取（3 个 Block，每个 Block 两次卷积 + 池化）
        self.features = nn.Sequential(
            # Block 1: 128x128 -> 64x64, 32 channels
            nn.Conv2d(3, 32, 3, padding=1),   nn.BatchNorm2d(32),  nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, 3, padding=1),   nn.BatchNorm2d(32),  nn.ReLU(inplace=True),
            nn.MaxPool2d(2),                   nn.Dropout2d(0.2),

            # Block 2: 64x64 -> 32x32, 64 channels
            nn.Conv2d(32, 64, 3, padding=1),   nn.BatchNorm2d(64),  nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1),   nn.BatchNorm2d(64),  nn.ReLU(inplace=True),
            nn.MaxPool2d(2),                   nn.Dropout2d(0.3),

            # Block 3: 32x32 -> 16x16, 128 channels
            nn.Conv2d(64, 128, 3, padding=1),  nn.BatchNorm2d(128), nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(inplace=True),
            nn.MaxPool2d(2),                   nn.Dropout2d(0.3),
        )

        # 全局平均池化 -> 固定 128*4*4 = 2048 维
        self.avgpool = nn.AdaptiveAvgPool2d((4, 4))

        # 分类头
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = self.classifier(x)
        return x
