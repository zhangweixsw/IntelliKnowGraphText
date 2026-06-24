from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QTextEdit, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette

from utils.config import config
from utils.model_detector import ModelDetector


class WelcomeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("欢迎使用")
        self.setMinimumSize(550, 450)
        self.init_ui()
        # 不在初始化时调用API - 等待用户点击刷新按钮
        # 用户点击"刷新模型"按钮时才检测

    def init_ui(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#1e1e1e"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#d4d4d4"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#252526"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#3c3c3c"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#d4d4d4"))
        self.setPalette(palette)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("欢迎使用 猫头羊zhangweixsw - 智能文档识别系统")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #4ec9b0; padding: 10px;")
        layout.addWidget(title)

        intro_group = self._create_intro_group()
        layout.addWidget(intro_group)

        model_group = self._create_model_group()
        layout.addWidget(model_group)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_skip = QPushButton("跳过")
        self.btn_skip.clicked.connect(self.reject)
        self.btn_skip.setMinimumHeight(36)

        self.btn_next = QPushButton("继续设置 →")
        self.btn_next.clicked.connect(self.accept)
        self.btn_next.setMinimumHeight(36)

        for btn in [self.btn_skip, self.btn_next]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3c3c3c;
                    border: 1px solid #555;
                    border-radius: 4px;
                    padding: 5px 15px;
                    color: #d4d4d4;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                    border: 1px solid #007acc;
                }
            """)

        btn_layout.addWidget(self.btn_skip)
        btn_layout.addWidget(self.btn_next)
        layout.addLayout(btn_layout)

    def _create_intro_group(self) -> QWidget:
        group = QGroupBox("快速开始")
        layout = QVBoxLayout(group)

        intro_text = QTextEdit()
        intro_text.setReadOnly(True)
        intro_text.setPlainText("""
使用步骤：

1. 启动LM Studio或Ollama
2. 在LM Studio中加载一个视觉模型(VLM)
   - 推荐: llava, qwen2-vl, llama3.2-vision
3. 回到本程序，点击"设置"
4. 检查API地址是否正确
5. 点击"刷新模型"检测可用模型
6. 选择视觉模型
7. 点击"测试连接"验证
8. 保存设置

然后就可以开始处理PDF和图片了！
        """.strip())
        intro_text.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: none;
                padding: 10px;
                font-family: 'Microsoft YaHei', sans-serif;
            }
        """)
        layout.addWidget(intro_text)

        return group

    def _create_model_group(self) -> QWidget:
        group = QGroupBox("检测模型")
        layout = QVBoxLayout(group)

        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 刷新模型")
        self.btn_refresh.clicked.connect(self.detect_models)
        self.btn_refresh.setMinimumHeight(36)
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px 15px;
                color: #d4d4d4;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        self.model_status = QLabel("点击刷新模型按钮检测可用模型...")
        self.model_status.setStyleSheet("color: #888;")
        layout.addWidget(self.model_status)

        self.model_list = QTextEdit()
        self.model_list.setReadOnly(True)
        self.model_list.setMaximumHeight(150)
        self.model_list.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
            }
        """)
        layout.addWidget(self.model_list)

        return group

    def detect_models(self):
        from PyQt6.QtWidgets import QMessageBox

        provider = config.provider
        base_url = config.lmstudio_url if provider == "lmstudio" else config.ollama_url
        base_url = base_url.replace("/v1", "").replace("/api", "")

        # 检测连接
        if not ModelDetector.test_connection(provider, base_url):
            self.model_status.setText("无法连接！请检查LM Studio/Ollama是否启动")
            self.model_status.setStyleSheet("color: #f14c4c;")
            self.model_list.setPlainText("""
错误：无法连接到本地大模型服务

请确保：
1. LM Studio 或 OllAMA 已启动
2. API 服务已开启
3. 已加载模型
            """.strip())
            return

        # 检测模型
        if provider == "lmstudio":
            models = ModelDetector.detect_lmstudio_models(base_url)
        else:
            models = ModelDetector.detect_ollama_models(base_url)

        if not models:
            self.model_status.setText("未检测到模型！请在LM Studio中加载模型")
            self.model_status.setStyleSheet("color: #f14c4c;")
            self.model_list.setPlainText("请在LM Studio中加载一个模型后点击刷新")
            return

        # 显示模型
        self.model_status.setText(f"检测到 {len(models)} 个模型")
        self.model_status.setStyleSheet("color: #4ec9b0;")

        vision_models = [m for m in models if m.is_vision]
        text = f"总模型数: {len(models)}\n"
        text += f"视觉模型: {len(vision_models)}\n\n"

        if vision_models:
            text += "✓ 可用的视觉模型:\n"
            for m in vision_models:
                text += f"  - {m.name}\n"
            text += "\n"

        text += "所有模型:\n"
        for m in models:
            vision_tag = " (视觉)" if m.is_vision else ""
            text += f"  - {m.name}{vision_tag}\n"

        self.model_list.setPlainText(text)