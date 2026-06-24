# -*- coding: utf-8 -*-
import subprocess
import os
import sys
import time
import shutil

print("=" * 60)
print("智能文档识别系统 - 打包工具")
print("=" * 60)

base_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_dir)

python = r"C:\Users\ASUS\AppData\Local\Programs\Python\Python313\python.exe"
if not os.path.exists(python):
    python = sys.executable

print(f"\n使用Python: {python}")

# 检查PyQt6是否安装
print("\n[检查依赖]...")
try:
    subprocess.run([python, "-c", "import PyQt6; print('PyQt6 OK')"], capture_output=True)
except:
    print("安装PyQt6...")
    subprocess.run([python, "-m", "pip", "install", "PyQt6", "-q"])

print("\n[1/3] 打包中...")

# 使用--collect-all确保所有依赖都被收集
result = subprocess.run(
    [python, "-m", "PyInstaller",
     "main.py",
     "--name", "IntelliKnowGraphText",
     "--onefile",
     "--console",
     "--noconfirm",
     "--collect-all", "PyQt6",
     "--collect-all", "sqlmodel",
     "--collect-all", "PIL",
     "--log-level", "ERROR"],
    capture_output=True,
    text=True
)

print(result.stdout[-1000:] if result.stdout else "")
if result.stderr:
    print("警告:", result.stderr[-500:])

# 查找
print("\n[2/3] 查找文件...")
new_exe = None

for root, dirs, files in os.walk(base_dir):
    for f in files:
        if f == "IntelliKnowGraphText.exe" and "dist" in root:
            new_exe = os.path.join(root, f)
            break

if new_exe and os.path.exists(new_exe):
    size = os.path.getsize(new_exe) / 1024 / 1024
    print(f"\n成功! 文件: {new_exe}")
    print(f"大小: {size:.1f} MB")

    ts = int(time.time())
    dst = os.path.join(base_dir, f"IntelliKnowGraphText_v{ts}.exe")
    try:
        shutil.copy2(new_exe, dst)
        print(f"已复制到: {dst}")
    except Exception as e:
        print(f"复制失败: {e}")
else:
    print("\n查找备用位置...")
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if "IntelliKnow" in f and f.endswith(".exe"):
                full = os.path.join(root, f)
                print(f"  找到: {full}")

print("\n[3/3] 完成")