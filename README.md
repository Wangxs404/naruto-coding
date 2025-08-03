# NARUTO 结印编程系统 🥷

一个基于深度学习的实时手势识别编程系统，通过识别火影忍者手印来进行代码编程和键盘输入。

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-green.svg)
![ONNX](https://img.shields.io/badge/ONNX-Runtime-orange.svg)

## ✨ 特性

- 🎯 **实时手势识别**: 基于YOLOX-Nano模型的高效实时检测
- 💻 **结印编程**: 通过手印组合进行代码编写和键盘输入
- 🖥️ **图形界面**: 直观的GUI界面，支持实时视频显示和代码编辑
- ⌨️ **键盘模拟**: 检测到的手势自动转换为键盘输入
- 📊 **历史记录**: 实时显示手印历史和编程结果
- 🎨 **可视化**: 实时显示检测框、置信度和FPS信息

## 🎮 支持的手印

系统支持识别12个十二生肖手印：子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥

## 🚀 快速开始

### 系统要求

- Windows 系统
- Python 3.7+
- 摄像头设备

### 安装和运行

1. **克隆项目**

```bash
git clone https://github.com/Wangxs404/naruto-coding
cd naruto-coding
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **运行程序**

```bash
python app.py
```

## 🎯 使用方法

1. 启动程序后点击"开始"按钮
2. 在摄像头前做出手印动作
3. 系统会自动识别手印并转换为代码输入
4. 使用特定手印组合可以触发快捷键和编程操作
5. 在代码编辑器中编写和运行代码

## 📁 项目结构

```
NARUTO-FINAL/
├── app.py                    # 主程序
├── model/yolox/              # YOLOX模型文件
├── setting/                  # 配置文件
├── utils/                    # 工具模块
├── asset/                    # 资源文件
└── requirements.txt          # 依赖列表
```

## ⚙️ 技术特点

- **检测模型**: YOLOX-Nano (~3.5MB)
- **推理速度**: 30+ FPS
- **支持平台**: Windows
- **实时性**: 低延迟手势识别

## 📄 许可证

本项目采用 MIT 许可证。

---

**注意**: 本项目仅供学习和研究使用。

**注意**: 本项目仅供学习和研究使用，请遵守相关法律法规。
