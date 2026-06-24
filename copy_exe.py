import os
import time

src = r"E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files\IntelliKnowGraphText 利用本地大模型处理pdf和图片\IntelliKnowGraphText\dist\IntelliKnowGraphText\IntelliKnowGraphText.exe"
dst = r"E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files\IntelliKnowGraphText 利用本地大模型处理pdf和图片\IntelliKnowGraphText\IntelliKnowGraphText.exe"

if os.path.exists(dst):
    try:
        os.remove(dst)
        print("已删除旧文件")
        time.sleep(1)
    except:
        print("无法删除旧文件，可能正在运行")
        exit(1)

import shutil
shutil.copy2(src, dst)
print(f"已复制新版本到: {dst}")