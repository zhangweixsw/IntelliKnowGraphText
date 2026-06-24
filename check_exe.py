import os

exe_path = r"E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files\IntelliKnowGraphText 利用本地大模型处理pdf和图片\IntelliKnowGraphText\IntelliKnowGraphText.exe"

if os.path.exists(exe_path):
    size = os.path.getsize(exe_path) / 1024 / 1024
    print(f"EXE存在: {exe_path}")
    print(f"大小: {size:.1f} MB")
else:
    print("EXE不存在")

dist_path = r"E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files\IntelliKnowGraphText 利用本地大模型处理pdf和图片\IntelliKnowGraphText\dist"
if os.path.exists(dist_path):
    print(f"\ndist目录存在")
    for root, dirs, files in os.walk(dist_path):
        for f in files:
            if f.endswith('.exe'):
                full = os.path.join(root, f)
                print(f"  {full} - {os.path.getsize(full)/1024/1024:.1f}MB")