import json
import os
from pathlib import Path
from typing import Optional

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "provider": "lmstudio",
    "lmstudio_url": "http://127.0.0.1:12345/v1",
    "ollama_url": "http://localhost:11434",
    "selected_model": "",
    "output_dir": "",
    "auto_export_md": True,
    "auto_export_excel": True,
    "increment_update": True,
    "prompt_template": "请仔细分析这张图片，提取所有文字内容，并给出简短的内容摘要和关键词。\n格式要求：\n1. 文字内容：\n2. 内容摘要：\n3. 关键词：",
}


class Config:
    _instance: Optional["Config"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._config = DEFAULT_CONFIG.copy()
        self._load()

    def _get_config_path(self) -> Path:
        exe_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        return exe_dir.parent / CONFIG_FILE

    def _load(self):
        config_path = self._get_config_path()
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self._config.update(loaded)
            except Exception:
                pass

    def save(self):
        config_path = self._get_config_path()
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def set(self, key: str, value):
        self._config[key] = value
        self.save()

    @property
    def provider(self) -> str:
        return self._config.get("provider", "lmstudio")

    @property
    def lmstudio_url(self) -> str:
        return self._config.get("lmstudio_url", "http://localhost:1234/v1")

    @property
    def ollama_url(self) -> str:
        return self._config.get("ollama_url", "http://localhost:11434")

    @property
    def selected_model(self) -> str:
        return self._config.get("selected_model", "")

    @property
    def output_dir(self) -> str:
        return self._config.get("output_dir", "")

    @property
    def prompt_template(self) -> str:
        return self._config.get("prompt_template", DEFAULT_CONFIG["prompt_template"])


config = Config()
