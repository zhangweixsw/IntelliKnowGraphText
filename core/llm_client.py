import json
import re
import requests
from typing import Optional, Dict, Any, List
from PIL import Image
import io
import base64

from utils.config import config


class ImageProcessor:
    @staticmethod
    def resize_if_needed(img: Image.Image, max_size: int = 2048) -> Image.Image:
        if img.width > max_size or img.height > max_size:
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            return img.resize(new_size, Image.Resampling.LANCZOS)
        return img

    @staticmethod
    def image_to_base64(img: Image.Image, format: str = "PNG") -> str:
        buffered = io.BytesIO()
        img.save(buffered, format=format)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")


def get_api_url() -> str:
    """获取API URL"""
    provider = config.provider
    if provider == "lmstudio":
        url = config.lmstudio_url
    else:
        url = config.ollama_url

    if url.startswith("http"):
        return url.rstrip("/")
    return f"http://127.0.0.1:12345"


class LLMClient:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or config.provider
        self.base_url = get_api_url()
        self.model = config.selected_model
        self.last_error = ""

    def is_vision_model(self) -> bool:
        """检测当前模型是否支持视觉 - 包含qwen3.5-0.8b"""
        if not self.model:
            return False

        model_lower = self.model.lower()
        
        # qwen3.5-0.8b 确实支持视觉！
        if "qwen3.5" in model_lower or "qwen3" in model_lower:
            print(f"[DEBUG] {self.model} 识别为qwen系列模型")
            return True
        
        # 其他视觉模型关键词
        vision_keywords = ["vision", "vl", "llava", "qwen2-vl", "glm-4v", "llama3.2", "llama3_2", "qvq"]
        return any(kw in model_lower for kw in vision_keywords)

    def test_connection(self) -> bool:
        """测试API连接 - 发送简单的文本测试"""
        try:
            import requests
            
            # 获取base URL
            base = self.base_url.replace("/v1", "").rstrip("/")
            if not base.startswith("http"):
                base = "http://127.0.0.1:12345"
            
            # 先测试列表API
            urls = [f"{base}/v1/models", f"{base}/models"]
            for url in urls:
                try:
                    resp = requests.get(url, timeout=10)
                    if resp.status_code == 200:
                        print(f"[DEBUG] 模型列表API正常: {url}")
                        break
                except:
                    pass
            
            # 测试文本生成是否正常
            test_payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "你好"}],
                "max_tokens": 10,
            }
            
            test_urls = [
                f"{base}/v1/chat/completions",
                f"{base}/chat/completions",
            ]
            
            for url in test_urls:
                try:
                    resp = requests.post(url, json=test_payload, timeout=30)
                    if resp.status_code == 200:
                        print(f"[DEBUG] 文本API正常: {url}")
                        return True
                    else:
                        print(f"[DEBUG] 文本API失败: {url} HTTP {resp.status_code}")
                except Exception as e:
                    print(f"[DEBUG] 文本API异常: {str(e)[:50]}")
            
            self.last_error = "无法连接到LM Studio API"
            return False
            
        except Exception as e:
            self.last_error = str(e)
            return False

    def chat(
        self,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Optional[str]:
        if self.provider == "lmstudio":
            return self._chat_lmstudio(messages, temperature, max_tokens)
        else:
            return self._chat_ollama(messages, temperature, max_tokens)

    def _chat_lmstudio(
        self, messages: list, temperature: float, max_tokens: int
    ) -> Optional[str]:
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            resp = requests.post(url, json=payload, timeout=300)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            else:
                self.last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            self.last_error = str(e)
        return None

    def _chat_ollama(
        self, messages: list, temperature: float, max_tokens: int
    ) -> Optional[str]:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        try:
            resp = requests.post(url, json=payload, timeout=300)
            if resp.status_code == 200:
                data = resp.json()
                return data["message"]["content"]
            else:
                self.last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            self.last_error = str(e)
        return None

    def vision_chat(
        self,
        image: Image.Image,
        prompt: str,
        temperature: float = 0.7,
    ) -> Optional[str]:
        if not self.is_vision_model():
            self.last_error = f"模型 {self.model} 不支持视觉输入，请选择VLM模型(如llava, qwen2-vl等)"
            return None

        img = ImageProcessor.resize_if_needed(image, 2048)
        img_b64 = ImageProcessor.image_to_base64(img)

        if self.provider == "lmstudio":
            return self._vision_lmstudio(img, img_b64, prompt, temperature)
        else:
            return self._vision_ollama(img, img_b64, prompt, temperature)

    def _vision_lmstudio(
        self, image: Image.Image, img_b64: str, prompt: str, temperature: float
    ) -> Optional[str]:
        # 减小图片尺寸以避免过大问题
        image = ImageProcessor.resize_if_needed(image, 1024)
        img_b64 = ImageProcessor.image_to_base64(image)
        
        # 尝试多个可能的base URL
        base_urls = [
            "http://127.0.0.1:12345",
            "http://localhost:12345",
            self.base_url.replace("/v1", "").rstrip("/"),
        ]
        base_urls = list(set(base_urls))

        print(f"[DEBUG] 使用模型: {self.model}")
        print(f"[DEBUG] 图片大小: {len(img_b64)} bytes")

        # 尝试多种格式
        for base in base_urls:
            # 格式1-4: 不同的消息格式
            payloads = [
                # 标准OpenAI vision格式 (带文本)
                {
                    "model": self.model,
                    "messages": [{"role": "user", "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    ]}],
                    "temperature": temperature,
                },
                # 简化格式 - 图片URL放text位置 (某些模型)
                {
                    "model": self.model,
                    "messages": [{"role": "user", "content": f"{prompt}\n![img](data:image/png;base64,{img_b64})"}],
                    "temperature": temperature,
                },
                # 纯图片格式
                {
                    "model": self.model,
                    "messages": [{"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    ]}],
                    "temperature": temperature,
                },
                # base64直接发送 (不使用URL格式)
                {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "images": [img_b64],
                    "temperature": temperature,
                },
            ]

            for i, payload in enumerate(payloads):
                for url in [f"{base}/v1/chat/completions", f"{base}/chat/completions"]:
                    try:
                        resp = requests.post(url, json=payload, timeout=120)
                        
                        if resp.status_code == 200:
                            data = resp.json()
                            if "choices" in data and len(data["choices"]) > 0:
                                content = data["choices"][0]["message"].get("content", "")
                                if content:
                                    print(f"[DEBUG] 成功! URL: {url}, 格式: {i+1}")
                                    return content
                        
                        error_text = resp.text
                        if "does not support" in error_text.lower():
                            print(f"[DEBUG] 格式{i+1}不支持图片: {error_text[:100]}")
                        elif resp.status_code != 200:
                            print(f"[DEBUG] 格式{i+1} HTTP {resp.status_code}: {error_text[:100]}")
                        
                    except Exception as e:
                        print(f"[DEBUG] 格式{i+1} 异常: {str(e)[:80]}")

        self.last_error = f"模型 {self.model} 无法处理图片输入"
        print(f"[ERROR] {self.last_error}")
        return None

    def _vision_ollama(
        self, image: Image.Image, img_b64: str, prompt: str, temperature: float
    ) -> Optional[str]:
        url = f"{self.base_url}/api/chat"

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "images": [img_b64],
                }
            ],
            "stream": False,
        }

        try:
            resp = requests.post(url, json=payload, timeout=300)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("message", {}).get("content", "")
            else:
                self.last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
        except Exception as e:
            self.last_error = str(e)

        return None

    @staticmethod
    def parse_response(response: str) -> Dict[str, str]:
        if not response:
            return {"raw_text": "", "summary": "", "keywords": ""}

        raw_text = ""
        summary = ""
        keywords = ""

        lines = response.split("\n")
        current_section = None
        section_content = []
        keywords_found = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "文字内容" in line or "原始文字" in line or "提取的文字" in line or "正文" in line:
                if current_section and section_content:
                    content = "\n".join(section_content).strip()
                    if current_section == "raw_text":
                        raw_text = content
                    elif current_section == "summary":
                        summary = content
                    elif current_section == "keywords":
                        keywords = content
                current_section = "raw_text"
                section_content = []
                if ":" in line:
                    section_content.append(line.split(":", 1)[1].strip())
            elif "内容摘要" in line or "摘要" in line or "总结" in line:
                if current_section and section_content:
                    content = "\n".join(section_content).strip()
                    if current_section == "raw_text":
                        raw_text = content
                    elif current_section == "summary":
                        summary = content
                    elif current_section == "keywords":
                        keywords = content
                current_section = "summary"
                section_content = []
                if ":" in line:
                    section_content.append(line.split(":", 1)[1].strip())
            elif "关键词" in line or "关键" in line or ("标签" in line and not keywords_found):
                if current_section and section_content:
                    content = "\n".join(section_content).strip()
                    if current_section == "raw_text":
                        raw_text = content
                    elif current_section == "summary":
                        summary = content
                    elif current_section == "keywords":
                        keywords = content
                current_section = "keywords"
                section_content = []
                keywords_found = True
                if ":" in line:
                    section_content.append(line.split(":", 1)[1].strip())
            else:
                section_content.append(line)

        if current_section and section_content:
            content = "\n".join(section_content).strip()
            if current_section == "raw_text":
                raw_text = content
            elif current_section == "summary":
                summary = content
            elif current_section == "keywords":
                keywords = content

        if not raw_text and not summary and not keywords:
            raw_text = response

        return {
            "raw_text": raw_text.strip(),
            "summary": summary.strip(),
            "keywords": keywords.strip(),
        }