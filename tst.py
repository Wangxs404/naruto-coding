import keyboard
import pyautogui

def on_key_1():
    pyautogui.write('apple')

def on_key_2():
    pyautogui.press('enter')

def on_key_3():
    pyautogui.hotkey('ctrl', 'b')

print("快捷键说明：")
print("1 → 输入 'apple'")
print("2 → 模拟回车")
print("3 → 模拟 Ctrl + B")
print("ESC → 退出程序")

keyboard.add_hotkey('1', on_key_1)
keyboard.add_hotkey('2', on_key_2)
keyboard.add_hotkey('3', on_key_3)
keyboard.wait('esc')
