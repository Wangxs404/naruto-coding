# NARUTO Hand Sign Programming System 🥷

<!-- Language Switch -->
**🌐 Language / 言語**
- [🇨🇳 中文](README.md) | [🇺🇸 English](README_EN.md) | [🇯🇵 日本語](README_JP.md)

---

A real-time gesture recognition programming system based on deep learning that recognizes Naruto hand signs for code programming and keyboard input.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-green.svg)
![ONNX](https://img.shields.io/badge/ONNX-Runtime-orange.svg)

## ✨ Features

- 🎯 **Real-time Gesture Recognition**: Efficient real-time detection based on YOLOX-Nano model
- 💻 **Hand Sign Programming**: Code writing and keyboard input through hand sign combinations
- 🖥️ **Graphical Interface**: Intuitive GUI with real-time video display and code editor
- ⌨️ **Keyboard Simulation**: Detected gestures automatically converted to keyboard input
- 📊 **History Records**: Real-time display of hand sign history and programming results
- 🎨 **Visualization**: Real-time display of detection boxes, confidence scores, and FPS

## 🎮 Supported Hand Signs

The system recognizes 12 zodiac hand signs: Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, Pig

## 🚀 Quick Start

### System Requirements

- Windows OS
- Python 3.7+
- Camera device

### Installation and Running

1. **Clone the project**
```bash
git clone https://github.com/Wangxs404/naruto-coding
cd naruto-coding
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the program**
```bash
python app.py
```

## 🎯 Usage

1. Click the "Start" button after launching the program
2. Make hand sign gestures in front of the camera
3. The system will automatically recognize hand signs and convert them to code input
4. Use specific hand sign combinations to trigger shortcuts and programming operations
5. Write and run code in the code editor

## 📁 Project Structure