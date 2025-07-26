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

# 导入原有模块
from utils import CvFpsCalc, CvDrawText
from model.yolox.yolox_onnx import YoloxONNX

class NarutoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NARUTO 手势识别系统 v2.0")
        self.root.geometry("1400x800")  # 调整窗口大小
        
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
        
        # 时间相关
        self.sign_interval = 2.0  # 与原代码一致
        self.jutsu_display_time = 5  # 与原代码一致
        self.sign_interval_start = 0
        self.jutsu_index = 0
        self.jutsu_start_time = 0
        
        # 键盘映射 - 与原代码完全一致
        self.letters = {
            1: 'g',
            7: 'i', 
            3: 't',
            11: 'n',
            5: 'enter',
            6: 'space',
        }
        
        # 手势引导数据 - 简化为仅包含手势名称
        self.gesture_guide = {
            '子': '子',
            '丑': '丑',
            '寅': '寅',
            '卯': '卯',
            '辰': '辰',
            '巳': '巳',
            '午': '午',
            '未': '未',
            '申': '申',
            '酉': '酉',
            '戌': '戌',
            '亥': '亥'
        }
        
        # 加载引导图片
        self.guide_image = None
        self.load_guide_image()
        
        self.load_data()
        self.setup_ui()
        
    def load_guide_image(self):
        """加载手势引导图片"""
        try:
            image_path = "./asset/yin.png"
            if os.path.exists(image_path):
                # 加载并调整图片大小
                pil_image = Image.open(image_path)
                # 调整图片大小以适应显示区域
                pil_image = pil_image.resize((280, 200), Image.Resampling.LANCZOS)
                self.guide_image = ImageTk.PhotoImage(pil_image)
            else:
                print(f"引导图片不存在: {image_path}")
        except Exception as e:
            print(f"加载引导图片失败: {e}")
        
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
        
    def setup_ui(self):
        # 创建主要布局
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 左侧区域 - 视频显示（占据更多空间）
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # 视频显示区域 - 修正尺寸设置
        video_frame = ttk.LabelFrame(left_frame, text="实时视频")
        video_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 创建Canvas来显示视频，确保正确的尺寸
        self.video_canvas = tk.Canvas(video_frame, bg='black', width=960, height=600)
        self.video_canvas.pack(padx=10, pady=10)
        
        # 控制按钮区域
        control_frame = ttk.LabelFrame(left_frame, text="控制面板")
        control_frame.pack(fill='x')
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="开始检测", command=self.start_detection)
        self.start_btn.pack(side='left', padx=(0, 5))
        
        self.stop_btn = ttk.Button(btn_frame, text="停止检测", command=self.stop_detection, state='disabled')
        self.stop_btn.pack(side='left', padx=5)
        
        self.clear_btn = ttk.Button(btn_frame, text="清除历史", command=self.clear_history)
        self.clear_btn.pack(side='left', padx=5)
        
        # 右侧区域 - 信息面板（固定宽度）
        right_frame = ttk.Frame(main_frame, width=350)
        right_frame.pack(side='right', fill='y')
        right_frame.pack_propagate(False)  # 防止自动调整大小
        
        # 隐藏参数设置区域 - 注释掉以下代码块
        # settings_frame = ttk.LabelFrame(right_frame, text="参数设置")
        # settings_frame.pack(fill='x', pady=(0, 10), padx=10)
        # 
        # # 置信度阈值 - 默认值与原代码一致
        # ttk.Label(settings_frame, text="置信度阈值:").pack(anchor='w', padx=10, pady=(10, 0))
        # self.confidence_var = tk.DoubleVar(value=0.7)  # 与原代码默认值一致
        # confidence_scale = ttk.Scale(settings_frame, from_=0.1, to=1.0, 
        #                            variable=self.confidence_var, orient='horizontal')
        # confidence_scale.pack(fill='x', padx=10)
        # 
        # # 显示置信度值
        # self.confidence_label = ttk.Label(settings_frame, text="0.70")
        # self.confidence_label.pack(anchor='w', padx=10)
        # confidence_scale.configure(command=self.update_confidence_label)
        # 
        # # 语言选择
        # ttk.Label(settings_frame, text="显示语言:").pack(anchor='w', padx=10, pady=(10, 0))
        # self.lang_var = tk.StringVar(value="中文")
        # lang_combo = ttk.Combobox(settings_frame, textvariable=self.lang_var, 
        #                         values=["中文", "English"], state="readonly")
        # lang_combo.pack(fill='x', padx=10, pady=(0, 10))
        
        # 保留变量初始化但不显示UI
        self.confidence_var = tk.DoubleVar(value=0.7)
        self.lang_var = tk.StringVar(value="中文")
        
        # 手印历史显示
        history_frame = ttk.LabelFrame(right_frame, text="手印历史")
        history_frame.pack(fill='x', pady=(0, 10), padx=10)
        
        self.history_text = tk.Text(history_frame, height=4, width=30, font=('Arial', 10))
        self.history_text.pack(fill='x', padx=10, pady=10)
        
        # 隐藏当前忍术显示区域 - 注释掉以下代码块
        # jutsu_frame = ttk.LabelFrame(right_frame, text="当前忍术")
        # jutsu_frame.pack(fill='x', pady=(0, 10), padx=10)
        # 
        # self.jutsu_label = tk.Label(jutsu_frame, text="无", font=('Arial', 12, 'bold'), 
        #                           fg='red', bg='white', relief='sunken', height=2)
        # self.jutsu_label.pack(fill='x', padx=10, pady=10)
        
        # 保留变量但不显示UI
        self.jutsu_label = tk.Label(self.root)  # 创建隐藏的标签
        
        # 代码编辑区（原输入法测试区，增高并更名）
        input_frame = ttk.LabelFrame(right_frame, text="代码编辑区")
        input_frame.pack(fill='both', expand=True, pady=(0, 10), padx=10)  # 使用expand=True来占据更多空间
        
        ttk.Label(input_frame, text="检测到的手势会自动输入对应字母:").pack(anchor='w', padx=10, pady=(10, 5))
        
        # 增加高度从3改为8，使其占据更多空间
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, width=30, font=('Arial', 9))
        self.input_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))  # 使用expand=True
        
        # 手势引导区 - 修改为显示图片
        guide_frame = ttk.LabelFrame(right_frame, text="手势引导")
        guide_frame.pack(fill='both', expand=True, padx=10)
        
        # 当前引导手势选择
        self.current_guide_var = tk.StringVar(value="子")
        guide_select_frame = ttk.Frame(guide_frame)
        guide_select_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(guide_select_frame, text="选择手势:").pack(side='left')
        guide_combo = ttk.Combobox(guide_select_frame, textvariable=self.current_guide_var,
                                 values=list(self.gesture_guide.keys()), state="readonly", width=8)
        guide_combo.pack(side='left', padx=(5, 0))
        guide_combo.bind('<<ComboboxSelected>>', self.update_gesture_guide)
        
        # 图片显示区域
        self.guide_image_label = tk.Label(guide_frame, bg='white', relief='sunken')
        self.guide_image_label.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken')
        status_bar.pack(side='bottom', fill='x')
        
        # 初始化手势引导
        self.update_gesture_guide()
        
    def update_confidence_label(self, value):
        """更新置信度标签"""
        self.confidence_label.config(text=f"{float(value):.2f}")
        
    def update_gesture_guide(self, event=None):
        """更新手势引导内容 - 显示图片而不是文字"""
        gesture = self.current_guide_var.get()
        
        # 显示引导图片
        if self.guide_image:
            self.guide_image_label.config(image=self.guide_image, text="")
        else:
            # 如果图片加载失败，显示手势名称
            self.guide_image_label.config(image="", text=f"手势: {gesture}", 
                                        font=('Arial', 16, 'bold'), fg='black')
        
    def start_detection(self):
        """开始检测 - 使用与原代码相同的初始化方法"""
        try:
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
                class_score_th=self.confidence_var.get(),
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
        self.jutsu_label.config(text="无")
        self.input_text.delete(1.0, tk.END)
        
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
        """处理检测结果 - 与原代码完全相同的逻辑"""
        score_th = self.confidence_var.get()
        
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
                self.sign_interval_start = time.time()  # 印の最終検出時間
                
                # 模拟键盘输入 - 与原代码一致
                if class_id in self.letters:
                    letter = self.letters[class_id]
                    pyautogui.press(letter)
                    # 更新输入测试区
                    self.root.after(0, self.update_input_text, letter)
        
        # 前回の印検出から指定時間が経過した場合、履歴を消去 - 与原代码完全一致
        if (time.time() - self.sign_interval_start) > self.sign_interval:
            self.sign_display_queue.clear()
            self.sign_history_queue.clear()
            
    def check_jutsu(self):
        """检查忍术匹配 - 与原代码完全相同的逻辑"""
        # 印の履歴から術名をマッチング - 与原代码一致
        sign_history = ''
        if len(self.sign_history_queue) > 0:
            for sign_id in self.sign_history_queue:
                sign_history = sign_history + self.labels[sign_id][1]
            for index, signs in enumerate(self.jutsu):
                if sign_history == ''.join(signs[4:]):
                    self.jutsu_index = index
                    self.jutsu_start_time = time.time()  # 術の最終検出時間
                    break
                
    def draw_debug_image(self, debug_image, font_path, fps_result, bboxes, scores, class_ids):
        """绘制调试图像 - 使用与原代码完全相同的方法"""
        frame_height, frame_width = debug_image.shape[:2]
        score_th = self.confidence_var.get()
        
        # 印のバウンディングボックスの重畳表示 - 与原代码完全一致
        for bbox, score, class_id in zip(bboxes, scores, class_ids):
            class_id = int(class_id) + 1
            
            # 检测阈值未满的边界框丢弃 - 与原代码一致
            if score < score_th:
                continue
                
            x1, y1 = int(bbox[0]), int(bbox[1])
            x2, y2 = int(bbox[2]), int(bbox[3])
            
            # バウンディングボックス(長い辺にあわせて正方形を表示) - 与原代码完全一致
            x_len = x2 - x1
            y_len = y2 - y1
            square_len = x_len if x_len >= y_len else y_len
            square_x1 = int(((x1 + x2) / 2) - (square_len / 2))
            square_y1 = int(((y1 + y2) / 2) - (square_len / 2))
            square_x2 = square_x1 + square_len
            square_y2 = square_y1 + square_len
            
            cv.rectangle(debug_image, (square_x1, square_y1), (square_x2, square_y2), (255, 255, 255), 4)
            cv.rectangle(debug_image, (square_x1, square_y1), (square_x2, square_y2), (0, 0, 0), 2)
            
            # 印の種類 - 与原代码完全一致
            font_size = int(square_len / 2)
            try:
                debug_image = CvDrawText.puttext(
                    debug_image, self.labels[class_id][1],
                    (square_x2 - font_size, square_y2 - font_size), 
                    font_path, font_size, (185, 0, 0)
                )
            except:
                pass
                
        # ヘッダー作成：FPS - 与原代码完全一致
        header_image = np.zeros((int(frame_height / 18), frame_width, 3), np.uint8)
        try:
            header_image = CvDrawText.puttext(
                header_image, "FPS:" + str(fps_result), (5, 0), 
                font_path, int(frame_height / 20), (255, 255, 255)
            )
        except:
            cv.putText(header_image, f"FPS: {fps_result}", (5, 20), 
                      cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
        # フッター作成：印の履歴、および、術名表示 - 与原代码完全一致
        footer_image = np.zeros((int(frame_height / 10), frame_width, 3), np.uint8)
        
        # 印の履歴文字列生成 - 与原代码一致
        sign_display = ''
        if len(self.sign_display_queue) > 0:
            for sign_id in self.sign_display_queue:
                sign_display = sign_display + self.labels[sign_id][1]
        
        # 术名表示(指定时间描画) - 与原代码完全一致
        lang_offset = 1 if self.lang_var.get() == "English" else 0
        if lang_offset == 0:
            separate_string = '・'
        else:
            separate_string = '：'
            
        if (time.time() - self.jutsu_start_time) < self.jutsu_display_time:
            if self.jutsu[self.jutsu_index][0] == '':  # 属性(火遁等)の定義が無い場合
                jutsu_string = self.jutsu[self.jutsu_index][2 + lang_offset]
            else:  # 属性(火遁等)の定義が有る場合
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
        # 印表示
        else:
            try:
                footer_image = CvDrawText.puttext(
                    footer_image, sign_display, (5, 0), font_path,
                    int(frame_width / self.sign_max_display), (255, 255, 255)
                )
            except:
                cv.putText(footer_image, sign_display, (5, 30), 
                          cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
                
        # ヘッダーとフッターをデバッグ画像へ結合 - 与原代码完全一致
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
            
            # 更新忍术显示
            lang_offset = 1 if self.lang_var.get() == "English" else 0
            if (time.time() - self.jutsu_start_time) < self.jutsu_display_time and self.jutsu_index < len(self.jutsu):
                jutsu_row = self.jutsu[self.jutsu_index]
                if len(jutsu_row) > 2 + lang_offset:
                    if jutsu_row[0] == '':
                        jutsu_text = jutsu_row[2 + lang_offset]
                    else:
                        separator = '：' if lang_offset == 1 else '・'
                        jutsu_text = jutsu_row[0 + lang_offset] + separator + jutsu_row[2 + lang_offset]
                    self.jutsu_label.config(text=jutsu_text, fg='red')
                else:
                    self.jutsu_label.config(text="无", fg='black')
            else:
                self.jutsu_label.config(text="无", fg='black')
                
        except Exception as e:
            print(f"GUI更新错误: {e}")
            
    def update_input_text(self, letter):
        """更新输入测试区"""
        try:
            if letter == 'enter':
                self.input_text.insert(tk.END, "\n")
            elif letter == 'space':
                self.input_text.insert(tk.END, " ")
            else:
                self.input_text.insert(tk.END, letter)
            self.input_text.see(tk.END)
        except Exception as e:
            print(f"输入更新错误: {e}")
            
    def on_closing(self):
        """关闭程序时的清理"""
        self.stop_detection()
        self.root.destroy()
        
    def run(self):
        """运行应用"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == '__main__':
    app = NarutoGUI()
    app.run()