#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import cv2 as cv
from PIL import Image, ImageTk
import threading
import time
import csv
import copy
from collections import deque
import numpy as np
import pyautogui
import os
import subprocess
import pygame
from utils.code_editor import CodeEditor
from pygments.styles import get_style_by_name

# 导入键盘映射和手势映射关系
from setting.mappings import HAND_SIGN_NAMES, WORD_MAPPINGS, SPECIAL_KEY_MAPPINGS, SHORTCUT_MAPPINGS

# 导入原有模块
from utils import CvFpsCalc, CvDrawText
from model.yolox.yolox_onnx import YoloxONNX

class NarutoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NARUTO CODING")
        self.root.geometry("1400x800")  # 调整窗口大小
        
        # 初始化pygame音频模块
        pygame.mixer.init()
        self.background_music = "./asset/music.mp3"
        self.music_playing = False
        
        # 状态变量
        self.is_running = False
        self.video_thread = None
        self.cap = None
        self.yolox = None
        
        # 检测相关变量 - 使用与原app.py相同的参数
        self.labels = []
        self.jutsu = []
        self.sign_max_display = 18  # 与原代码一致
        self.sign_max_history = 44  # 与原代码一致
        self.sign_display_queue = deque(maxlen=self.sign_max_display)
        self.sign_history_queue = deque(maxlen=self.sign_max_history)
        self.chattering_check = 1
        self.chattering_check_queue = deque(maxlen=self.chattering_check)
        self.cvFpsCalc = CvFpsCalc()
        
        # 配置变量 (硬编码)
        self.confidence_threshold = 0.7  # 硬编码置信度阈值
        self.language = "中文"  # 硬编码语言设置
        
        # 时间相关
        self.sign_interval = 2.0  # 与原代码一致
        self.jutsu_display_time = 5  # 与原代码一致
        self.sign_interval_start = 0
        self.jutsu_index = 0
        self.jutsu_start_time = 0
        
        # 键盘映射 - 从配置文件导入
        
        self.words = WORD_MAPPINGS
        self.special_keys = SPECIAL_KEY_MAPPINGS
        self.shortcuts = SHORTCUT_MAPPINGS
        
        # 手印序列记录 - 用于检测组合
        self.sign_sequence = []
        
        # 图片展示相关
        self.yin_image = None
        
        self.load_data()
        self.setup_ui()
        self.setup_styles()
        
    def load_data(self):
        """加载标签和忍术数据 - 与原代码相同的方法"""
        try:
            # 加载手印标签
            with open('setting/labels.csv', encoding='utf8') as f:
                labels = csv.reader(f)
                self.labels = [row for row in labels]
            
            # 加载忍术数据
            with open('setting/jutsu.csv', encoding='utf8') as f:
                jutsu = csv.reader(f)
                self.jutsu = [row for row in jutsu]
                
        except Exception as e:
            messagebox.showerror("错误", f"加载数据文件失败: {e}")
            
    def load_images(self):
        """加载图片资源"""
        try:
            # 左侧图片路径列表
            left_image_paths = [
                './asset/子.png',
                './asset/丑.png',
                './asset/寅.png',
                './asset/卯.png',
                './asset/辰.png',
                './asset/巳.png'
            ]
            
            # 加载左侧图片
            self.left_images = []
            for i, image_path in enumerate(left_image_paths):
                if os.path.exists(image_path) and i < len(self.left_image_labels):
                    image = Image.open(image_path)
                    # 调整图片大小
                    image = image.resize((200, 130), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self.left_images.append(photo)
                    self.left_image_labels[i].config(image=photo)
                else:
                    print(f"左侧图片文件不存在: {image_path}")
            
            # 右侧图片路径列表
            right_image_paths = [
                './asset/午.png',
                './asset/未.png',
                './asset/申.png',
                './asset/酉.png',
                './asset/戌.png',
                './asset/亥.png'
            ]
            
            # 加载右侧图片
            self.right_images = []
            for i, image_path in enumerate(right_image_paths):
                if os.path.exists(image_path) and i < len(self.right_image_labels):
                    image = Image.open(image_path)
                    # 调整图片大小
                    image = image.resize((200, 130), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self.right_images.append(photo)
                    self.right_image_labels[i].config(image=photo)
                else:
                    print(f"右侧图片文件不存在: {image_path}")
                
        except Exception as e:
            print(f"加载图片失败: {e}")
        
    def setup_ui(self):
        # 创建主要布局
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 控制按钮区域 - 放在顶部
        control_frame = ttk.LabelFrame(main_frame, text="控制面板")
        control_frame.pack(fill='x', pady=(0, 10))
        
        # 创建一个内容框架，用于放置按钮和图片
        control_content = ttk.Frame(control_frame)
        control_content.pack(fill='x', padx=10, pady=10)
        
        # 按钮框架放在左侧
        btn_frame = ttk.Frame(control_content)
        btn_frame.pack(side='left', fill='y')
        
        self.start_btn = ttk.Button(btn_frame, text="开始", command=self.start_detection)
        self.start_btn.pack(side='left', padx=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_detection, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        # self.clear_btn = ttk.Button(btn_frame, text="清除历史", command=self.clear_history)
        # self.clear_btn.pack(side='left', padx=5)
        
        # 品牌图片框架放在中间
        # 设置品牌框架的固定宽度和高度
        brand_frame = ttk.Frame(control_content, width=200, height=60)
        brand_frame.pack(side='left', fill='both', expand=True, padx=10)
        brand_frame.pack_propagate(False)  # 防止子组件改变frame大小
        
        # 右侧空白区域，用于平衡布局
        right_space = ttk.Frame(control_content)
        right_space.pack(side='left', fill='y')
        
        # 加载并显示品牌图片
        try:
            brand_image_path = './asset/brand.png'
            if os.path.exists(brand_image_path):
                brand_image = Image.open(brand_image_path)
                # 调整图片大小
                brand_image = brand_image.resize((320, 55), Image.Resampling.LANCZOS)
                brand_photo = ImageTk.PhotoImage(brand_image)
                brand_label = ttk.Label(brand_frame, image=brand_photo)
                brand_label.image = brand_photo  # 保持引用以防止垃圾回收
                brand_label.pack(side='top', pady=5)
            else:
                print(f"品牌图片文件不存在: {brand_image_path}")
                brand_label = ttk.Label(brand_frame, text="NARUTO手势识别系统", font=("Arial", 12, "bold"))
                brand_label.pack(side='top', pady=5)
        except Exception as e:
            print(f"加载品牌图片失败: {e}")
            brand_label = ttk.Label(brand_frame, text="NARUTO手势识别系统", font=("Arial", 12, "bold"))
            brand_label.pack(side='top', pady=5)
        
        # 置信度和语言设置已硬编码，UI元素已移除
        
        # 主布局框架 - 分为左右图片区和中间内容区
        main_frame = ttk.Frame(main_frame)
        main_frame.pack(fill='both', expand=True)

        # 左侧图片展示区 - 100%高度
        left_image_frame = ttk.Frame(main_frame)
        left_image_frame.pack(side='left', fill='y', padx=(0, 5))

        # 创建左侧6行图片展示
        self.left_image_labels = []
        for i in range(7):
            label = ttk.Label(left_image_frame)
            label.pack(pady=5)
            self.left_image_labels.append(label)

        # 中间内容区域 - 垂直布局
        center_area = ttk.Frame(main_frame)
        center_area.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # 中间上部区域 - 视频和代码编辑并排
        content_upper = ttk.Frame(center_area)
        content_upper.pack(fill='both', expand=True)

        # 视频和手印历史区域
        video_history_frame = ttk.Frame(content_upper)
        video_history_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

        # 实时视频区
        video_frame = ttk.LabelFrame(video_history_frame, text="忍术施放区")
        video_frame.pack(fill='both', expand=True)

        # 创建Canvas来显示视频，设置合适的尺寸
        self.video_canvas = tk.Canvas(video_frame, bg='black', width=640, height=480)
        self.video_canvas.pack(fill='both', expand=True, padx=10, pady=10)

        # 手印历史显示
        history_frame = ttk.LabelFrame(video_history_frame, text="结印历史")
        history_frame.pack(fill='x', pady=(5, 0))

        self.history_text = tk.Text(history_frame, height=4, font=('Arial', 10))
        self.history_text.pack(fill='x', padx=10, pady=10)

        # 代码执行区
        code_execution_frame = ttk.Frame(content_upper)
        code_execution_frame.pack(side='left', fill='both', expand=True)
        code_execution_frame.grid_rowconfigure(0, weight=1)
        code_execution_frame.grid_columnconfigure(0, weight=1)
        
        # 添加代码编辑器和工具栏
        code_editor_frame = ttk.Frame(code_execution_frame)
        code_editor_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=(5, 2))
        
        # 工具栏
        toolbar = ttk.Frame(code_editor_frame)
        toolbar.pack(side='top', fill='x')
        
        # 添加刷新图标按钮
        refresh_btn = ttk.Button(toolbar, text="🔄", width=3, command=self.insert_print_statement)
        refresh_btn.pack(side='left', padx=2, pady=2)
        
        # 代码编辑器
        self.code_input = CodeEditor(code_editor_frame, height=15, width=80)
        self.code_input.pack(side='top', fill='both', expand=True)
        self.code_input.bind("<Control-Return>", self.write_and_run_code)
        self.code_input.bind("<Control-o>", self.handle_ctrl_o)

        self.code_output = scrolledtext.ScrolledText(code_execution_frame, width=80, height=15, font=('Courier New', 9), bg="white", fg="black", insertbackground="black")
        self.code_output.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(2, 10)) 
        self.code_output.config(state='disabled')

        # 右侧图片展示区 - 100%高度
        right_image_frame = ttk.Frame(main_frame)
        right_image_frame.pack(side='left', fill='y')

        # 创建右侧6行图片展示
        self.right_image_labels = []
        for i in range(7):
            label = ttk.Label(right_image_frame)
            label.pack(pady=5)
            self.right_image_labels.append(label)

        # 教程区 - 只在中间区域下方，不延伸到两侧图片区域
        tutorial_frame = ttk.LabelFrame(center_area, text="-")
        tutorial_frame.pack(fill='x', pady=(5, 0))
        
        # 添加模式选择下拉框
        mode_frame = ttk.Frame(tutorial_frame)
        mode_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(mode_frame, text="教程模式：").pack(side='left', padx=(0, 5))
        self.tutorial_mode = tk.StringVar(value="困难-ASCII")
        mode_combo = ttk.Combobox(mode_frame, textvariable=self.tutorial_mode, 
                                  values=["简单-快捷组合", "困难-ASCII"], 
                                  state="readonly", width=15)
        mode_combo.pack(side='left')
        mode_combo.bind("<<ComboboxSelected>>", self.update_tutorial_mode)
        
        # 教程区的文字内容
        self.tutorial_text = tk.Text(tutorial_frame, height=15, width=100, font=('Courier New', 12))
        self.tutorial_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 初始加载教程内容
        self.load_tutorial_content()
        
        self.tutorial_text.config(state='disabled')  # 设置为只读

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken')
        status_bar.pack(side='bottom', fill='x')

        # 加载并显示图片
        self.load_images()

    # 置信度标签更新功能已移除，因为设置已硬编码
        
    def start_detection(self):
        """开始检测 - 使用与原代码相同的初始化方法"""
        try:
            # 播放背景音乐
            if os.path.exists(self.background_music):
                pygame.mixer.music.load(self.background_music)
                pygame.mixer.music.play(-1)  # -1表示循环播放
                self.music_playing = True
            else:
                print(f"背景音乐文件不存在: {self.background_music}")
            
            # 初始化摄像头 - 与原代码完全一致
            self.cap = cv.VideoCapture(0)  # 默认设备0
            self.cap.set(cv.CAP_PROP_FRAME_WIDTH, 960)   # 与原代码一致
            self.cap.set(cv.CAP_PROP_FRAME_HEIGHT, 540)  # 与原代码一致
            
            if not self.cap.isOpened():
                messagebox.showerror("错误", "无法打开摄像头")
                return
            
            # 初始化模型 - 使用与原代码相同的参数
            self.yolox = YoloxONNX(
                model_path='model/yolox/yolox_nano.onnx',  # 与原代码一致
                input_shape=(416, 416),                   # 与原代码一致
                class_score_th=self.confidence_threshold,  # 使用硬编码的置信度阈值
                nms_th=0.45,                              # 与原代码一致
                nms_score_th=0.1,                         # 与原代码一致
                with_p6=False,                            # 与原代码一致
            )
            
            # 重置检测状态 - 与原代码相同的初始化
            self.sign_display_queue.clear()
            self.sign_history_queue.clear()
            self.chattering_check_queue.clear()
            # 与原代码一致的初始化
            for index in range(-1, -1 - self.chattering_check, -1):
                self.chattering_check_queue.append(index)
            
            self.sign_interval_start = 0
            self.jutsu_index = 0
            self.jutsu_start_time = 0
            
            self.is_running = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            
            # 启动检测线程
            self.video_thread = threading.Thread(target=self.run_detection)
            self.video_thread.daemon = True
            self.video_thread.start()
            
            self.status_var.set("检测中...")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动检测失败: {e}")
            self.stop_detection()
        
    def stop_detection(self):
        """停止检测"""
        self.is_running = False
        
        # 停止背景音乐
        if self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
            
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
        # 清空视频显示
        self.video_canvas.delete("all")
        
        self.status_var.set("已停止")
        
    def clear_history(self):
        """清除历史记录"""
        self.sign_display_queue.clear()
        self.sign_history_queue.clear()
        self.history_text.delete(1.0, tk.END)
        self.code_input.delete(1.0, tk.END)
        self.code_output.config(state='normal')
        self.code_output.delete(1.0, tk.END)
        self.code_output.config(state='disabled')
        
    def update_tutorial_mode(self, event=None):
        """更新教程模式"""
        self.load_tutorial_content()
        
    def load_tutorial_content(self):
        """根据选择的模式加载教程内容"""
        self.tutorial_text.config(state='normal')
        self.tutorial_text.delete(1.0, tk.END)
        
        if self.tutorial_mode.get() == "困难-ASCII":
            # 读取ASCII.md文件内容并显示在教程区（六列展示）
            try:
                with open('ascii.md', 'r', encoding='utf-8') as f:
                    ascii_lines = f.readlines()
                    # 处理ASCII映射表为六列显示
                    formatted_content = ""
                    total_lines = len(ascii_lines)
                    lines_per_column = (total_lines + 5) // 6  # 向上取整，确保能容纳所有行
                    
                    # 创建六列格式
                    for i in range(lines_per_column):
                        row = ""
                        for col in range(6):
                            idx = col * lines_per_column + i
                            if idx < total_lines:
                                # 提取每行的主要内容，去除多余空格
                                line = ascii_lines[idx].strip()
                                # 确保每列宽度一致
                                row += f"{line:<18}"  # 每列固定18个字符宽度
                        formatted_content += row + "\n"
                    
                    self.tutorial_text.insert(1.0, formatted_content)
            except Exception as e:
                self.tutorial_text.insert(1.0, f"无法加载ASCII.md文件: {e}\n基础手印：子丑寅卯辰巳午未申酉戌亥")
        else:
            # 简单模式 - 显示快捷组合
            # simple_content = "巳>戌>未>辰 -> Hello World\n\n"
            simple_content = "丑>寅>子>子>未>戌>午>未>辰>子>巳 -> Hello World\n\n"
            # simple_content += "巳>戌>寅>辰 -> Hello NARUTO\n\n"
            # simple_content += "巳>戌>子>辰 -> Hello AdventureX\n\n"
            simple_content += "常用编程组合:\n\n"
            simple_content += "辰 -> Ctrl+Enter   丑丑 -> Ctrl+V     丑寅 -> Ctrl+X     丑卯 -> Ctrl+Z\n"
            simple_content += "丑辰 -> Ctrl+S     丑巳 -> Ctrl+A     丑午 -> Ctrl+F     丑未 -> Alt+Tab\n"
            
            self.tutorial_text.insert(1.0, simple_content)
        
        self.tutorial_text.config(state='disabled')

    def write_and_run_code(self, event=None):
        code_content = self.code_input.get("1.0", tk.END)
        if not code_content.strip():
            return

        try:
            with open("./utils/naruto.py", "w", encoding="utf-8") as f:
                f.write(code_content)
        except Exception as e:
            self.update_code_output(f"Error writing to ./utils/naruto.py: {e}\n")
            return
        
        # Clear previous output
        self.code_output.config(state='normal')
        self.code_output.delete(1.0, tk.END)
        self.code_output.insert(tk.END, f"PS {os.getcwd()}> python ./utils/naruto.py\n")
        self.code_output.config(state='disabled')

        # Run command in a separate thread to avoid blocking the GUI
        thread = threading.Thread(target=self._execute_command, args=(f"python ./utils/naruto.py",))
        thread.daemon = True
        thread.start()
        return "break" # Prevents the default Enter key behavior in the Text widget

    def _execute_command(self, command):
        try:
            # Execute the command
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                encoding='gbk',
                errors='replace',
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Read output line by line and update the GUI
            for line in iter(process.stdout.readline, ''):
                self.root.after(0, self.update_code_output, line)

            process.stdout.close()
            process.wait()

        except Exception as e:
            self.root.after(0, self.update_code_output, f"Error: {e}\n")

    def update_code_output(self, text):
        self.code_output.config(state='normal')
        self.code_output.insert(tk.END, text)
        self.code_output.see(tk.END)
        self.code_output.config(state='disabled')
        
    def handle_ctrl_o(self, event):
        """处理Ctrl+O快捷键事件"""
        self.insert_print_statement()
        # 阻止事件继续传播，避免默认行为
        return "break"
        
    def insert_print_statement(self):
        """清空编辑区并插入print("")，将光标移动到双引号中间"""
        # 清空编辑区
        self.code_input.text.delete("1.0", tk.END)
        
        # 插入print("")语句
        self.code_input.text.insert("1.0", 'print("")')
        
        # 计算双引号中间的位置
        middle_pos = "1.7"
        
        # 将光标移动到双引号中间
        self.code_input.text.mark_set(tk.INSERT, middle_pos)
        
        # 聚焦到代码编辑器
        self.code_input.text.focus()
        
        # 触发语法高亮
        self.code_input.highlight()

    def setup_styles(self):
        style = get_style_by_name('vs')
        for token, s in style:
            fg = s['color']
            bg = s['bgcolor']
            if fg:
                self.code_input.text.tag_configure(str(token), foreground=f'#{fg}')
            if bg:
                self.code_input.text.tag_configure(str(token), background=f'#{bg}')
        
    def run_detection(self):
        """运行检测循环 - 使用与原代码相同的逻辑"""
        font_path = './utils/font/衡山毛筆フォント.ttf'  # 与原代码一致
        frame_count = 0  # 与原代码一致
        
        while self.is_running:
            try:
                start_time = time.time()
                
                # 读取帧 - 与原代码完全一致
                ret, frame = self.cap.read()
                if not ret:
                    continue
                frame_count += 1
                debug_image = copy.deepcopy(frame)  # 与原代码一致
                
                # FPS计算 - 与原代码一致
                fps_result = self.cvFpsCalc.get()
                
                # 手势检测 - 与原代码一致
                bboxes, scores, class_ids = self.yolox.inference(frame)
                
                # 处理检测结果 - 使用与原代码相同的逻辑
                self.process_detections(bboxes, scores, class_ids)
                
                # 检查忍术匹配 - 与原代码相同的逻辑
                self.check_jutsu()
                
                # 绘制调试图像 - 使用与原代码完全相同的方法
                debug_image = self.draw_debug_image(
                    debug_image, font_path, fps_result, bboxes, scores, class_ids
                )
                
                # 更新GUI显示
                self.root.after(0, self.update_gui, debug_image)
                
                # 控制帧率 - 与原代码一致
                elapsed_time = time.time() - start_time
                sleep_time = max(0, (1.0 / 30) - elapsed_time)  # 30 FPS
                time.sleep(sleep_time)
                
            except Exception as e:
                print(f"检测错误: {e}")
                break
                
    def process_detections(self, bboxes, scores, class_ids):
        """处理检测结果 - 增强版，支持多种键盘映射"""
        score_th = self.confidence_threshold  # 使用硬编码的置信度阈值
        
        for _, score, class_id in zip(bboxes, scores, class_ids):
            class_id = int(class_id) + 1  # 与原代码一致
            
            # 检测阈值未满的结果丢弃 - 与原代码一致
            if score < score_th:
                continue
                
            # 指定回数以上，同じ印が続いた場合に、印检出とみなす - 与原代码完全一致
            self.chattering_check_queue.append(class_id)
            if len(set(self.chattering_check_queue)) != 1:
                continue
                
            # 前回と異なる印の場合のみキューに登録 - 与原代码完全一致
            if (len(self.sign_display_queue) == 0 or 
                self.sign_display_queue[-1] != class_id):
                self.sign_display_queue.append(class_id)
                self.sign_history_queue.append(class_id)
                self.sign_sequence.append(class_id)  # 添加到序列中用于检测组合
                self.sign_interval_start = time.time()  # 印の最終検出時間
                
                # 1. 单个按键映射已移除，直接检查其他映射
                
                # 2. 检查是否匹配单词映射
                self.check_word_mappings()
                
                # 3. 检查是否匹配特殊按键
                self.check_special_key_mappings()
                
                # 4. 检查是否匹配快捷键组合
                self.check_shortcut_mappings()
        
        # 前回の印検出から指定時間が経过した场合、履歴を消去 - 与原代码完全一致
        if (time.time() - self.sign_interval_start) > self.sign_interval:
            self.sign_display_queue.clear()
            self.sign_history_queue.clear()
            self.sign_sequence.clear()  # 清空序列
            
    def check_word_mappings(self):
        """检查是否匹配单词映射"""
        # 首先检查最近的一个手印是否匹配单词映射
        if len(self.sign_sequence) >= 1:
            last_one = tuple(self.sign_sequence[-1:])
            if last_one in self.words:
                word = self.words[last_one]
                # 使用pyautogui模拟键盘输入单词
                pyautogui.write(word)
                # 清空序列，避免重复触发
                self.sign_sequence = []
                return
                
        # 检查最近的两个手印是否匹配单词映射
        if len(self.sign_sequence) >= 2:
            last_two = tuple(self.sign_sequence[-2:])
            if last_two in self.words:
                word = self.words[last_two]
                # 使用pyautogui模拟键盘输入单词
                pyautogui.write(word)
                # 清空序列，避免重复触发
                self.sign_sequence = []
                
    def check_special_key_mappings(self):
        """检查是否匹配特殊按键"""
        # 首先检查最近的1个手印是否匹配特殊按键
        if len(self.sign_sequence) >= 1:
            # 检查1个手印
            last_one = tuple(self.sign_sequence[-1:])
            if last_one in self.special_keys:
                key = self.special_keys[last_one]
                if key is not None:  # 如果不是None，则按下按键
                    pyautogui.press(key)
                # 清空序列，避免重复触发
                self.sign_sequence = []
                return
                
        # 检查最近的2个手印是否匹配特殊按键
        if len(self.sign_sequence) >= 2:
            # 检查2个手印组合
            last_two = tuple(self.sign_sequence[-2:])
            if last_two in self.special_keys:
                key = self.special_keys[last_two]
                if key is not None:  # 如果不是None，则按下按键
                    pyautogui.press(key)
                # 清空序列，避免重复触发
                self.sign_sequence = []
        
        # 检查3个手印组合（用于按键释放）
        if len(self.sign_sequence) >= 3:
            last_three = tuple(self.sign_sequence[-3:])
            if last_three in self.special_keys:
                # None表示释放按键，不需要操作，pyautogui会自动释放
                # 清空序列，避免重复触发
                self.sign_sequence = []
                
    def check_shortcut_mappings(self):
        """检查是否匹配快捷键组合"""
        # 首先检查最近的1个手印是否匹配快捷键组合
        if len(self.sign_sequence) >= 1:
            last_one = tuple(self.sign_sequence[-1:])
            if last_one in self.shortcuts:
                keys = self.shortcuts[last_one]
                # 使用pyautogui模拟组合键
                pyautogui.hotkey(*keys)
                # 清空序列，避免重复触发
                self.sign_sequence = []
                return
                
        # 检查最近的3个手印是否匹配快捷键组合
        if len(self.sign_sequence) >= 3:
            last_three = tuple(self.sign_sequence[-3:])
            if last_three in self.shortcuts:
                keys = self.shortcuts[last_three]
                # 使用pyautogui模拟组合键
                pyautogui.hotkey(*keys)
                # 清空序列，避免重复触发
                self.sign_sequence = []
            
    def check_jutsu(self):
        """检查忍术匹配 - 与原代码完全相同的逻辑"""
        # 从手印历史中匹配忍术名称 - 与原代码一致
        sign_history = ''
        if len(self.sign_history_queue) > 0:
            for sign_id in self.sign_history_queue:
                sign_history = sign_history + self.labels[sign_id][1]
            for index, signs in enumerate(self.jutsu):
                if sign_history == ''.join(signs[4:]):
                    self.jutsu_index = index
                    self.jutsu_start_time = time.time()  # 忍术的最后检测时间
                    break
                
    def draw_debug_image(self, debug_image, font_path, fps_result, bboxes, scores, class_ids):
        """绘制调试图像 - 使用与原代码完全相同的方法"""
        frame_height, frame_width = debug_image.shape[:2]
        score_th = self.confidence_threshold  # 使用硬编码的置信度阈值
        
        # 手印边界框的叠加显示 - 与原代码完全一致
        for bbox, score, class_id in zip(bboxes, scores, class_ids):
            class_id = int(class_id) + 1
            
            # 检测阈值未满的边界框丢弃 - 与原代码一致
            if score < score_th:
                continue
                
            x1, y1 = int(bbox[0]), int(bbox[1])
            x2, y2 = int(bbox[2]), int(bbox[3])
            
            # 边界框(根据长边显示正方形) - 与原代码完全一致
            x_len = x2 - x1
            y_len = y2 - y1
            square_len = x_len if x_len >= y_len else y_len
            square_x1 = int(((x1 + x2) / 2) - (square_len / 2))
            square_y1 = int(((y1 + y2) / 2) - (square_len / 2))
            square_x2 = square_x1 + square_len
            square_y2 = square_y1 + square_len
            
            cv.rectangle(debug_image, (square_x1, square_y1), (square_x2, square_y2), (255, 255, 255), 4)
            cv.rectangle(debug_image, (square_x1, square_y1), (square_x2, square_y2), (0, 0, 0), 2)
            
            # 手印类型 - 与原代码完全一致
            font_size = int(square_len / 2)
            try:
                debug_image = CvDrawText.puttext(
                    debug_image, self.labels[class_id][1],
                    (square_x2 - font_size, square_y2 - font_size), 
                    font_path, font_size, (185, 0, 0)
                )
            except:
                pass
                
        # 创建头部：FPS - 与原代码完全一致
        header_image = np.zeros((int(frame_height / 18), frame_width, 3), np.uint8)
        try:
            header_image = CvDrawText.puttext(
                header_image, "FPS:" + str(fps_result), (5, 0), 
                font_path, int(frame_height / 20), (255, 255, 255)
            )
        except:
            cv.putText(header_image, f"FPS: {fps_result}", (5, 20), 
                      cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
        # 创建底部：手印历史和忍术名称显示 - 与原代码完全一致
        footer_image = np.zeros((int(frame_height / 10), frame_width, 3), np.uint8)
        
        # 生成手印历史字符串 - 与原代码一致
        sign_display = ''
        if len(self.sign_display_queue) > 0:
            for sign_id in self.sign_display_queue:
                sign_display = sign_display + self.labels[sign_id][1]
        
        # 术名表示(指定时间描画) - 与原代码完全一致
        lang_offset = 1 if self.language == "English" else 0
        if lang_offset == 0:
            separate_string = '・'
        else:
            separate_string = '：'
            
        if (time.time() - self.jutsu_start_time) < self.jutsu_display_time:
            if self.jutsu[self.jutsu_index][0] == '':  # 没有属性(火遁等)定义的情况
                jutsu_string = self.jutsu[self.jutsu_index][2 + lang_offset]
            else:  # 有属性(火遁等)定义的情况
                jutsu_string = (self.jutsu[self.jutsu_index][0 + lang_offset] + 
                              separate_string + self.jutsu[self.jutsu_index][2 + lang_offset])
            try:
                footer_image = CvDrawText.puttext(
                    footer_image, jutsu_string, (5, 0), font_path,
                    int(frame_width / self.sign_max_display), (255, 255, 255)
                )
            except:
                cv.putText(footer_image, jutsu_string, (5, 30), 
                          cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        # 手印显示
        else:
            try:
                footer_image = CvDrawText.puttext(
                    footer_image, sign_display, (5, 0), font_path,
                    int(frame_width / self.sign_max_display), (255, 255, 255)
                )
            except:
                cv.putText(footer_image, sign_display, (5, 30), 
                          cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
                
        # 将头部和底部合并到调试图像 - 与原代码完全一致
        debug_image = cv.vconcat([header_image, debug_image])
        debug_image = cv.vconcat([debug_image, footer_image])
        
        return debug_image
        
    def update_gui(self, frame):
        """更新GUI显示 - 修正视频显示方法"""
        try:
            # 更新视频显示 - 使用Canvas确保正确的尺寸显示
            frame_rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            
            # 获取Canvas的实际尺寸
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()
            
            # 如果Canvas还没有初始化完成，使用默认尺寸
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 960
                canvas_height = 600
            
            # 计算缩放比例，保持宽高比
            img_width, img_height = image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y)
            
            # 计算新的尺寸
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # 调整图像大小
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # 清除Canvas并显示新图像
            self.video_canvas.delete("all")
            # 居中显示
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.video_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            
            # 保持引用防止垃圾回收
            self.video_canvas.image = photo
            
            # 更新手印历史显示
            history_text = ""
            if len(self.sign_display_queue) > 0:
                signs = []
                for sign_id in self.sign_display_queue:
                    if sign_id < len(self.labels):
                        signs.append(self.labels[sign_id][1])
                history_text = " → ".join(signs)
                
            self.history_text.delete(1.0, tk.END)
            self.history_text.insert(1.0, history_text)
            
        except Exception as e:
            print(f"GUI更新错误: {e}")
            

    def on_closing(self):
        """关闭程序时的清理"""
        self.stop_detection()
        
        # 确保pygame资源被正确释放
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        pygame.quit()
        
        self.root.destroy()
        
    def run(self):
        """运行应用"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == '__main__':
    app = NarutoGUI()
    app.run()