import subprocess
import sys
import os

os.chdir(r"E:\Windows 10 System\WeiLi syc\ALL IN ONE\Github Files\IntelliKnowGraphText 利用本地大模型处理pdf和图片\IntelliKnowGraphText")

deps = ["PyQt6", "requests", "pillow", "pdf2image", "pypdf", "python-dotenv", "sqlmodel", "openpyxl"]
for dep in deps:
    subprocess.run([sys.executable, "-m", "pip", "install", dep, "-q"], check=False)

os.environ["QT_QPA_PLATFORM"] = "windows"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, "#1e1e1e")
    palette.setColor(palette.ColorRole.WindowText, "#d4d4d4")
    palette.setColor(palette.ColorRole.Base, "#252526")
    palette.setColor(palette.ColorRole.AlternateBase, "#2d2d2d")
    palette.setColor(palette.ColorRole.ToolTipBase, "#2d2d2d")
    palette.setColor(palette.ColorRole.Text, "#d4d4d4")
    palette.setColor(palette.ColorRole.Button, "#3c3c3c")
    palette.setColor(palette.ColorRole.ButtonText, "#d4d4d4")
    palette.setColor(palette.ColorRole.Highlight, "#007acc")
    palette.setColor(palette.ColorRole.HighlightedText, "#ffffff")
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
