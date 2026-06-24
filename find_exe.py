# 查找exe文件
import os

base = r"E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files\IntelliKnowGraphText 利用本地大模型处理pdf和图片\IntelliKnowGraphText"

print("查找EXE文件...")

for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith(".exe") and "Intelli" in f:
            full = os.path.join(root, f)
            size = os.path.getsize(full) / 1024 / 1024
            print(f"  {full} ({size:.1f}MB)")