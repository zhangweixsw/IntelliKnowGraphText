import requests
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ModelInfo:
    name: str
    provider: str
    is_vision: bool = False


class ModelDetector:
    VISION_KEYWORDS = [
        "vision", "vl", "llava", "qwen2", "qwen", "glm-4v",
        "llama3.2", "llama3_2", "qwen3", "qwen3.5", "qwen3.5",
        # 所有可能支持视觉的关键词
        "vision", "vl", "Voir", "QVQ"
    ]

    @staticmethod
    def is_vision_model(model_name: str) -> bool:
        """通过模型名称判断是否可能是视觉模型"""
        if not model_name:
            return False
        name_lower = model_name.lower()
        return any(kw in name_lower for kw in ModelDetector.VISION_KEYWORDS)

    @staticmethod
    def detect_lmstudio_models(base_url: str = "http://127.0.0.1:12345") -> List[ModelInfo]:
        """检测LM Studio模型 - 只获取列表，不实际调用"""
        models = []
        try:
            # API v1 获取模型列表
            resp = requests.get(f"{base_url}/v1/models", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get("data", []):
                    model_id = m.get("id", "")
                    if model_id:
                        is_vision = ModelDetector.is_vision_model(model_id)
                        models.append(ModelInfo(
                            name=model_id,
                            provider="lmstudio",
                            is_vision=is_vision
                        ))
        except Exception as e:
            pass

        # 如果v1失败，尝试原始API
        if not models:
            try:
                resp = requests.get(f"{base_url}/models", timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    for m in data.get("data", []):
                        model_id = m.get("id", "")
                        if model_id:
                            is_vision = ModelDetector.is_vision_model(model_id)
                            models.append(ModelInfo(
                                name=model_id,
                                provider="lmstudio",
                                is_vision=is_vision
                            ))
            except Exception as e:
                pass

        return models

    @staticmethod
    def detect_ollama_models(base_url: str = "http://localhost:11434") -> List[ModelInfo]:
        """检测Ollama模型"""
        models = []
        try:
            resp = requests.get(f"{base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for m in data.get("models", []):
                    model_name = m.get("name", "")
                    if model_name:
                        is_vision = ModelDetector.is_vision_model(model_name)
                        models.append(ModelInfo(
                            name=model_name,
                            provider="ollama",
                            is_vision=is_vision
                        ))
        except Exception:
            pass
        return models

    @staticmethod
    def detect_all_models() -> Dict[str, List[ModelInfo]]:
        """检测所有可用模型"""
        lmstudio_models = ModelDetector.detect_lmstudio_models()
        ollama_models = ModelDetector.detect_ollama_models()

        return {
            "lmstudio": lmstudio_models,
            "ollama": ollama_models,
        }

    @staticmethod
    def get_vision_models(models: List[ModelInfo] = None) -> List[ModelInfo]:
        """获取视觉模型列表"""
        if models is None:
            all_models = ModelDetector.detect_all_models()
            vision_models = []
            for provider, model_list in all_models.items():
                vision_models.extend([m for m in model_list if m.is_vision])
            return vision_models
        return [m for m in models if m.is_vision]

    @staticmethod
    def test_connection(provider: str, base_url: str) -> bool:
        """测试连接 - 只发简单请求"""
        try:
            if provider == "lmstudio":
                # 测试基本API可用性
                url = base_url.replace("/v1", "") + "/v1/models"
                resp = requests.get(url, timeout=5)
                return resp.status_code == 200
            else:
                resp = requests.get(f"{base_url}/api/tags", timeout=5)
                return resp.status_code == 200
        except Exception:
            return False