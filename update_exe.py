import os
import shutil
import time

base = r"E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files\IntelliKnowGraphText 利用本地大模型处理pdf和图片\IntelliKnowGraphText"
src = os.path.join(base, "dist", "IntelliKnowGraphText", "IntelliKnowGraphText.exe")
dst = os.path.join(base, "IntelliKnowGraphText.exe")

if os.path.exists(src):
    size = os.path.getsize(src) / 1024 / 1024
    print(f"源文件: {size:.1f} MB")

    try:
        if os.path.exists(dst):
            os.remove(dst)
            print("已删除旧EXE")
            time.sleep(0.5)
    except:
        print("无法删除旧文件，程序可能正在运行")
        print("请关闭正在运行的程序后重新运行此脚本")
        input("按回车退出...")
        exit(1)

    shutil.copy2(src, dst)
    print(f"已更新: {dst}")
    print(f"新大小: {os.path.getsize(dst)/1024/1024:.1f} MB")
else:
    print("未找到新EXE文件")