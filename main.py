import sys
import os
import traceback


def main():
    print("=" * 60)
    print("智能文档识别系统 - 猫头羊zhangweixsw")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        from PyQt6.QtGui import QPalette, QColor
        from ui.main_window import MainWindow
        from utils.config import config
        from utils.model_detector import ModelDetector

        print("[1/4] 导入模块完成")
        
        # 创建应用
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # 设置主题
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#d4d4d4"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#252526"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#2d2d2d"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#3c3c3c"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#d4d4d4"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#007acc"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        app.setPalette(palette)

        print("[2/4] 应用创建完成")
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        print("[3/4] 主窗口创建完成")
        print(f"    当前模型: {config.selected_model or '未选择'}")
        print(f"    API地址: {config.lmstudio_url}")
        
        # 首次使用提示
        print("[4/4] 检查配置...")
        
        if not config.selected_model:
            print("    提示: 首次使用，需要选择模型")
            QMessageBox.information(
                window,
                "首次使用 - 请先设置",
                "请按以下步骤操作：\n\n"
                "1. 点击【设置】按钮\n"
                "2. 检查API地址: http://127.0.0.1:12345/v1\n"
                "3. 点击【刷新模型】按钮\n"
                "4. 选择一个视觉模型(如llama3.2-vision)\n"
                "5. 点击【测试连接】验证\n"
                "6. 点击【保存】\n\n"
                "提示: 处理PDF和图片需要视觉模型"
            )
        else:
            print(f"    已选择模型: {config.selected_model}")
            # 检查是否是视觉模型
            from utils.model_detector import ModelDetector
            if ModelDetector.is_vision_model(config.selected_model):
                print("    ✓ 识别为视觉模型")
            else:
                print("    ⚠ 可能不是视觉模型，请确认已选择正确的模型")

        print("=" * 60)
        print("程序已启动！窗口应该已显示")
        print("=" * 60)
        
        sys.exit(app.exec())

    except ImportError as e:
        print(f"[错误] 缺少模块: {e}")
        print("请运行: pip install PyQt6 requests pillow pdf2image pypdf python-dotenv sqlmodel openpyxl")
        input("\n按回车退出...")
        
    except Exception as e:
        print(f"[错误] 启动失败: {e}")
        traceback.print_exc()
        input("\n按回车退出...")


if __name__ == "__main__":
    main()