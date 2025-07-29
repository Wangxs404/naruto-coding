#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
键盘映射和手势映射关系配置文件
"""

# 手印ID到键盘按键的映射 - 单个按键
# KEYBOARD_MAPPINGS = {
#     # 1: 'h',    # Ne(Rat)/子
#     7: 'i',    # Uma(Horse)/午
#     3: 't',    # Tora(Tiger)/寅
#     11: 'n',   # Inu(Dog)/戌
#     5: 'enter', # Tatsu(Dragon)/辰
#     3: 'space', # Mi(Snake)/巳
#     # 2: 'o',    # Ushi(Ox)/丑
#     4: 'u',    # U(Hare)/卯
#     8: 'r',    # Hitsuji(Ram)/未
#     9: 's',    # Saru(Monkey)/申
#     10: 'b',   # Tori(Bird)/酉
#     12: 'p',   # I(Boar)/亥
# }

# 手印组合到单词的映射
WORD_MAPPINGS = {
    (6,): 'hello',  # 数字1对应键入单词hello
    (8,): 'world',  # 数字2对应键入单词world
    (3,): 'NARUTO',  # 数字1对应键入单词NARUTO
    (1,): 'AdventureX',  # 数字1对应键入单词AdventureX
}

# 手印组合到特殊按键的映射
SPECIAL_KEY_MAPPINGS = {
    (11,): 'space',  # 数字4对应按下tab键
}

# 手印组合到快捷键的映射
SHORTCUT_MAPPINGS = {
    (13,): ['ctrl', 'enter'],  # 数字3对应按下ctrl+enter
    (10,): ['ctrl', 'o'],  # 数字4对应按下ctrl+o
}

# 手印ID到名称的映射
HAND_SIGN_NAMES = {
    1: '子 (Ne/Rat)',
    2: '丑 (Ushi/Ox)',
    3: '寅 (Tora/Tiger)',
    4: '卯 (U/Hare)',
    5: '辰 (Tatsu/Dragon)',
    6: '巳 (Mi/Snake)',
    7: '午 (Uma/Horse)',
    8: '未 (Hitsuji/Ram)',
    9: '申 (Saru/Monkey)',
    10: '酉 (Tori/Bird)',
    11: '戌 (Inu/Dog)',
    12: '亥 (I/Boar)',
}
