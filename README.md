# NARUTO 手势识别系统 🥷

一个基于深度学习的实时手势识别系统，能够识别火影忍者中的十二生肖手印并检测对应的忍术。

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-green.svg)
![ONNX](https://img.shields.io/badge/ONNX-Runtime-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 特性

- 🎯 **实时手势识别**: 基于YOLOX-Nano模型的高效实时检测
- 🔥 **忍术识别**: 支持14种经典忍术的手印序列识别
- 🖥️ **图形界面**: 直观的GUI界面，支持实时视频显示
- ⌨️ **键盘模拟**: 检测到的手势可自动转换为键盘输入
- 📊 **历史记录**: 实时显示手印历史和忍术匹配结果
- 🎨 **可视化**: 实时显示检测框、置信度和FPS信息

## 🎮 支持的手印

系统支持识别以下12个十二生肖手印：

| 手印 | 生肖 | 英文名 | 键盘映射 |
|------|------|--------|----------|
| 子 | 鼠 | Rat | - |
| 丑 | 牛 | Ox | - |
| 寅 | 虎 | Tiger | t |
| 卯 | 兔 | Hare | - |
| 辰 | 龙 | Dragon | - |
| 巳 | 蛇 | Snake | enter |
| 午 | 马 | Horse | space |
| 未 | 羊 | Ram | i |
| 申 | 猴 | Monkey | - |
| 酉 | 鸡 | Bird | - |
| 戌 | 狗 | Dog | - |
| 亥 | 猪 | Boar | n |

## 🔥 支持的忍术

系统可以识别以下忍术的手印序列：

### 火遁系列
- **豪火球术** (Fireball Jutsu): 巳→寅→申→亥→午→寅
- **凤仙花术** (Phoenix Flower Jutsu): 子→寅→戌→丑→卯→寅
- **龙火术** (Dragon Flame Jutsu): 巳→辰→卯→寅
- **火龙炎弹术** (Dragon Flame Bomb): 未→午→巳→辰→子→丑→寅

### 水遁系列
- **水乱破术** (Water Trumpet): 辰→寅→卯
- **水鲛弹术** (Water Shark Bomb Jutsu): 寅→丑→辰→卯→酉→辰→未
- **水龙弹术** (Water Dragon Jutsu): 44个手印的复杂序列

### 通用忍术
- **分身术** (Clone Jutsu): 未→巳→寅
- **替身术** (Substitution Jutsu): 未→亥→丑→戌→巳
- **通灵术** (Summoning Jutsu): 戌→亥→酉→申→未
- **通灵·土遁追牙术**: 寅→巳→辰→戌
- **通灵·秽土转生术**: 寅→巳→戌→辰→祈
- **尸鬼封尽术** (Reaper Death Seal): 巳→亥→未→卯→戌→子→酉→午→巳→祈

## 🚀 快速开始

### 环境要求

- Python 3.7+
- OpenCV 4.0+
- 摄像头设备

### 安装依赖

```bash
pip install opencv-python
pip install pillow
pip install numpy
pip install onnxruntime
pip install pyautogui
```

### 运行程序

```bash
python gui_app.py
```

## 📁 项目结构

```
NARUTO-DEV/
├── gui_app.py                 # 主程序GUI界面
├── model/
│   └── yolox/
│       ├── yolox_nano.onnx    # YOLOX-Nano模型文件
│       ├── yolox_onnx.py      # 模型推理类
│       └── ...
├── setting/
│   ├── labels.csv             # 手印标签配置
│   └── jutsu.csv             # 忍术配置
├── utils/
│   ├── cvfpscalc.py          # FPS计算工具
│   ├── cvdrawtext.py         # 文本绘制工具
│   └── font/                 # 字体文件
├── asset/
│   └── yin.png               # 手势引导图片
└── post_process_gen_tools/    # 模型后处理工具
```

## 🎯 使用方法

1. **启动程序**: 运行 `python gui_app.py`
2. **开始检测**: 点击"开始检测"按钮
3. **手势识别**: 在摄像头前做出手印动作
4. **查看结果**: 在右侧面板查看识别历史和忍术匹配
5. **键盘输入**: 部分手势会自动转换为键盘输入
6. **停止检测**: 点击"停止检测"按钮

## ⚙️ 技术细节

### 模型架构
- **检测模型**: YOLOX-Nano
- **输入尺寸**: 416×416
- **推理框架**: ONNX Runtime
- **检测阈值**: 0.7 (可调)
- **NMS阈值**: 0.45

### 性能指标
- **模型大小**: ~3.5MB
- **推理速度**: 30+ FPS (CPU)
- **检测精度**: 高精度手印识别
- **延迟**: 低延迟实时检测

## 🔧 配置说明

### 手印配置 (setting/labels.csv)
```csv
None,無
Ne(Rat),子
Ushi(Ox),丑
...
```

### 忍术配置 (setting/jutsu.csv)
```csv
火遁,Fire Style,豪火球术,Fireball Jutsu,巳,寅,申,亥,午,寅
...
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

### 贡献指南
1. Fork 这个仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 原始项目作者: KazuhitoTakahashi
- YOLOX模型: [YOLOX](https://github.com/Megvii-BaseDetection/YOLOX)
- 火影忍者手印参考: 岸本齐史的《火影忍者》

## 📞 联系

如果你有任何问题或建议，请通过以下方式联系：

- 提交 [Issue](../../issues)
- 发送邮件或其他联系方式

---

**注意**: 本项目仅供学习和研究使用，请遵守相关法律法规。