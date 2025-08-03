# NARUTO 印結びプログラミングシステム 🥷

深層学習に基づくリアルタイム手勢認識プログラミングシステム。NARUTOの印を認識してコードプログラミングとキーボード入力を行います。

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Windows](https://img.shields.io/badge/Platform-Windows-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.0+-green.svg)
![ONNX](https://img.shields.io/badge/ONNX-Runtime-orange.svg)

## ✨ 特徴

- 🎯 **リアルタイム手勢認識**: YOLOX-Nanoモデルに基づく効率的なリアルタイム検出
- 💻 **印結びプログラミング**: 印の組み合わせによるコード記述とキーボード入力
- 🖥️ **グラフィカルインターフェース**: 直感的なGUIでリアルタイム映像表示とコードエディター
- ⌨️ **キーボードシミュレーション**: 検出された手勢を自動的にキーボード入力に変換
- 📊 **履歴記録**: 印の履歴とプログラミング結果のリアルタイム表示
- 🎨 **可視化**: 検出ボックス、信頼度スコア、FPSのリアルタイム表示

## 🎮 対応する印

システムは12の十二支の印を認識します：子、丑、寅、卯、辰、巳、午、未、申、酉、戌、亥

## 🚀 クイックスタート

### システム要件

- Windows OS
- Python 3.7+
- カメラデバイス

### インストールと実行

1. **プロジェクトのクローン**
```bash
git clone https://github.com/Wangxs404/naruto-coding
cd naruto-coding
```

2. **依存関係のインストール**
```bash
pip install -r requirements.txt
```

3. **プログラムの実行**
```bash
python app.py
```

## 🎯 使用方法

1. プログラム起動後「開始」ボタンをクリック
2. カメラの前で印のジェスチャーを行う
3. システムが自動的に印を認識してコード入力に変換
4. 特定の印の組み合わせでショートカットとプログラミング操作をトリガー
5. コードエディターでコードを記述・実行

## 📁 プロジェクト構造