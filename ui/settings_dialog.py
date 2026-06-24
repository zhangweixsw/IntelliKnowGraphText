from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit,
    QCheckBox,
    QTextEdit,
    QGroupBox,
    QMessageBox,
    QWidget,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from utils.config import config
from utils.model_detector import ModelDetector, ModelInfo


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumSize(600, 500)
        self.init_ui()
        self.load_settings()
        self.detect_models()

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

        title = QLabel("设置")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #4ec9b0; padding: 10px;")
        layout.addWidget(title)

        provider_group = self._create_provider_group()
        layout.addWidget(provider_group)

        model_group = self._create_model_group()
        layout.addWidget(model_group)

        output_group = self._create_output_group()
        layout.addWidget(output_group)

        options_group = self._create_options_group()
        layout.addWidget(options_group)

        prompt_group = self._create_prompt_group()
        layout.addWidget(prompt_group)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_save = QPushButton("保存")
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.clicked.connect(self.reject)

        for btn in [self.btn_save, self.btn_cancel]:
            btn.setMinimumHeight(36)
            btn.setMinimumWidth(100)
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

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def _create_provider_group(self) -> QWidget:
        group = QGroupBox("大模型提供商")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        row.addWidget(QLabel("选择提供商:"))

        self.combo_provider = QComboBox()
        self.combo_provider.addItems(["LM Studio", "Ollama"])
        self.combo_provider.currentTextChanged.connect(self.on_provider_changed)
        row.addWidget(self.combo_provider)

        row.addWidget(QLabel("API地址:"))

        self.edit_url = QLineEdit()
        self.edit_url.setPlaceholderText("http://localhost:1234/v1")
        row.addWidget(self.edit_url)

        self.btn_test = QPushButton("测试连接")
        self.btn_test.clicked.connect(self.test_connection)
        row.addWidget(self.btn_test)

        layout.addLayout(row)

        return group

    def _create_model_group(self) -> QWidget:
        group = QGroupBox("模型选择")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        row.addWidget(QLabel("可用模型:"))

        self.combo_model = QComboBox()
        self.combo_model.setMinimumWidth(300)
        row.addWidget(self.combo_model)

        self.btn_refresh = QPushButton("🔄 刷新模型")
        self.btn_refresh.clicked.connect(self.detect_models)
        row.addWidget(self.btn_refresh)

        layout.addLayout(row)

        self.model_status = QLabel("未检测到模型")
        self.model_status.setStyleSheet("color: #888;")
        layout.addWidget(self.model_status)

        return group

    def _create_output_group(self) -> QWidget:
        group = QGroupBox("导出设置")
        layout = QVBoxLayout(group)

        row = QHBoxLayout()
        row.addWidget(QLabel("导出目录:"))

        self.edit_output = QLineEdit()
        self.edit_output.setPlaceholderText("默认: 当前目录")
        row.addWidget(self.edit_output)

        self.btn_browse = QPushButton("浏览")
        self.btn_browse.clicked.connect(self.browse_output_dir)
        row.addWidget(self.btn_browse)

        layout.addLayout(row)

        return group

    def _create_options_group(self) -> QWidget:
        group = QGroupBox("选项")
        layout = QVBoxLayout(group)

        self.chk_auto_md = QCheckBox("自动导出MD文件")
        self.chk_auto_md.setStyleSheet("color: #d4d4d4;")
        layout.addWidget(self.chk_auto_md)

        self.chk_auto_excel = QCheckBox("自动导出Excel文件")
        self.chk_auto_excel.setStyleSheet("color: #d4d4d4;")
        layout.addWidget(self.chk_auto_excel)

        self.chk_increment = QCheckBox("增量更新 (只处理新文件/修改的文件)")
        self.chk_increment.setStyleSheet("color: #d4d4d4;")
        layout.addWidget(self.chk_increment)

        return group

    def _create_prompt_group(self) -> QWidget:
        group = QGroupBox("提示词模板")
        layout = QVBoxLayout(group)

        self.edit_prompt = QTextEdit()
        self.edit_prompt.setPlaceholderText("输入提示词模板...")
        self.edit_prompt.setMinimumHeight(120)
        self.edit_prompt.setStyleSheet("""
            QTextEdit {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Microsoft YaHei', sans-serif;
            }
        """)
        layout.addWidget(self.edit_prompt)

        hint = QLabel("提示: 使用 {image} 或直接传入图片")
        hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(hint)

        return group

    def load_settings(self):
        provider = config.provider
        self.combo_provider.setCurrentText(
            "LM Studio" if provider == "lmstudio" else "Ollama"
        )

        if provider == "lmstudio":
            # 使用保存的URL或默认值
            saved_url = config.lmstudio_url
            self.edit_url.setText(saved_url if saved_url else "http://127.0.0.1:12345/v1")
        else:
            self.edit_url.setText(config.ollama_url)

        self.edit_output.setText(config.output_dir)
        self.chk_auto_md.setChecked(config.get("auto_export_md", True))
        self.chk_auto_excel.setChecked(config.get("auto_export_excel", True))
        self.chk_increment.setChecked(config.get("increment_update", True))
        self.edit_prompt.setPlainText(config.prompt_template)

        saved_model = config.selected_model
        if saved_model:
            self.combo_model.addItem(saved_model)
            self.combo_model.setCurrentText(saved_model)

    def on_provider_changed(self, text: str):
        if text == "LM Studio":
            self.edit_url.setText("http://127.0.0.1:12345/v1")
        else:
            self.edit_url.setText("http://localhost:11434")
        self.detect_models()

    def detect_models(self):
        provider = (
            "lmstudio" if self.combo_provider.currentText() == "LM Studio" else "ollama"
        )
        base_url = self.edit_url.text().replace("/v1", "").replace("/api", "")

        if provider == "lmstudio":
            models = ModelDetector.detect_lmstudio_models(base_url)
        else:
            models = ModelDetector.detect_ollama_models(base_url)

        self.combo_model.clear()

        if models:
            for m in models:
                display = f"{m.name} {'(视觉模型)' if m.is_vision else ''}"
                self.combo_model.addItem(display, m.name)

            self.model_status.setText(f"检测到 {len(models)} 个模型")
            self.model_status.setStyleSheet("color: #4ec9b0;")
        else:
            self.model_status.setText("未检测到模型，请确保已启动LM Studio或Ollama")
            self.model_status.setStyleSheet("color: #f14c4c;")

    def test_connection(self):
        provider = (
            "lmstudio" if self.combo_provider.currentText() == "LM Studio" else "ollama"
        )
        base_url = self.edit_url.text()

        if ModelDetector.test_connection(provider, base_url):
            QMessageBox.information(self, "连接成功", "成功连接到本地大模型服务!")
            self.detect_models()
        else:
            QMessageBox.warning(
                self, "连接失败", "无法连接到本地大模型服务，请确保LM Studio或Ollama已启动"
            )

    def browse_output_dir(self):
        from PyQt6.QtWidgets import QFileDialog
        dir_path = QFileDialog.getExistingDirectory(self, "选择导出目录")
        if dir_path:
            self.edit_output.setText(dir_path)

    def save_settings(self):
        provider = (
            "lmstudio" if self.combo_provider.currentText() == "LM Studio" else "ollama"
        )
        config.set("provider", provider)
        config.set("selected_model", self.combo_model.currentData() or self.combo_model.currentText())

        if provider == "lmstudio":
            config.set("lmstudio_url", self.edit_url.text())
        else:
            config.set("ollama_url", self.edit_url.text())

        config.set("output_dir", self.edit_output.text())
        config.set("auto_export_md", self.chk_auto_md.isChecked())
        config.set("auto_export_excel", self.chk_auto_excel.isChecked())
        config.set("increment_update", self.chk_increment.isChecked())
        config.set("prompt_template", self.edit_prompt.toPlainText())

        config.save()
        self.accept()
