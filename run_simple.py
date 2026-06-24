# -*- coding: utf-8 -*-
import sys
import os

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.getcwd())

try:
    print("1. 导入模块...")

    print("  - PyQt6...")
    from PyQt6.QtWidgets import QApplication
    print("  - MainWindow...")
    from ui.main_window import MainWindow
    print("  - config...")
    from utils.config import config

    print("\n2. 创建应用...")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    print("\n3. 创建窗口...")
    window = MainWindow()
    window.show()

    print("\n4. 运行...")
    sys.exit(app.exec())

except Exception as e:
    print(f"\n错误: {e}")
    import traceback
    traceback.print_exc()
    input("\n按回车退出...")
