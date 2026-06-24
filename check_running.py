import os
import sys

# 检查进程
try:
    import psutil
    for proc in psutil.process_iter(['name']):
        if 'IntelliKnow' in proc.info['name']:
            print("程序正在运行，请关闭后再更新")
            sys.exit(1)
except:
    pass

print("程序未运行，开始更新...")

import shutil

base = r"E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files\IntelliKnowGraphText 利用本地大模型处理pdf和图片\IntelliKnowGraphText"
src = os.path.join(base, "dist", "IntelliKnowGraphText", "IntelliKnowGraphText.exe")
dst = os.path.join(base, "IntelliKnowGraphText.exe")

if os.path.exists(src):
    # 尝试删除旧文件
    if os.path.exists(dst):
        try:
            os.remove(dst)
            print("已删除旧文件")
        except:
            print("无法删除旧文件，请手动删除后重试")
            sys.exit(1)

    shutil.copy2(src, dst)
    print(f"已更新: {dst}")
    print(f"大小: {os.path.getsize(dst)/1024/1024:.1f} MB")
else:
    print("未找到源文件，需要重新打包")