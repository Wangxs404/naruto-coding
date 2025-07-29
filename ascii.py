characters = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 两两组合
combinations = [a + b for a in characters for b in characters]

# 映射到ASCII码
ascii_map = {}

for i in range(128):
    ascii_map[i] = combinations[i]

# 将结果写入 ascii.txt 文件
with open("ascii.txt", "w", encoding="utf-8") as f:
    for i in range(128):
        ascii_char = chr(i)  # 获取ASCII码对应的字符
        f.write(f"ASCII {i}: {ascii_char} -> {ascii_map[i]}\n")

print("结果已写入 ascii.txt 文件")
