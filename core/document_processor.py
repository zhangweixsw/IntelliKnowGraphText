import os
from pathlib import Path
from typing import List, Optional, Callable, Dict
from PIL import Image

from core.llm_client import LLMClient
from core.processors import PDFProcessor, FileScanner, ImageProcessor
from data.database import db, compute_file_hash
from utils.config import config


class ProcessingResult:
    def __init__(
        self,
        file_path: str,
        success: bool,
        raw_text: str = "",
        summary: str = "",
        keywords: str = "",
        error: str = "",
    ):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.success = success
        self.raw_text = raw_text
        self.summary = summary
        self.keywords = keywords
        self.error = error


class DocumentProcessor:
    def __init__(self):
        self.llm_client = LLMClient()
        self._stop_flag = False

    def stop(self):
        self._stop_flag = True

    def can_process(self) -> tuple:
        """检查是否可以处理文件"""
        if not self.llm_client.model:
            return False, "未选择模型！请在设置中选择模型"

        if not self.llm_client.is_vision_model():
            return False, f"当前模型 '{self.llm_client.model}' 不支持视觉输入！请在设置中选择视觉模型（如llava, qwen2-vl等）"

        # 尝试测试连接
        test_result = self.llm_client.test_connection()
        if not test_result:
            return False, f"无法连接到LM Studio！错误: {self.llm_client.last_error}"

        return True, ""

    def process_file(
        self, file_path: str, progress_callback: Optional[Callable] = None
    ) -> ProcessingResult:
        if self._stop_flag:
            return ProcessingResult(file_path, False, error="已停止")

        file_hash = compute_file_hash(file_path)
        if not file_hash:
            return ProcessingResult(file_path, False, error="无法计算文件哈希")

        existing = db.get_by_hash(file_hash)
        if existing and config.get("increment_update", True):
            return ProcessingResult(
                file_path,
                True,
                raw_text=existing.raw_text,
                summary=existing.summary,
                keywords=existing.keywords,
            )

        file_type = FileScanner.get_file_type(file_path)

        try:
            if file_type == "pdf":
                return self._process_pdf(file_path, file_hash, progress_callback)
            elif file_type == "image":
                return self._process_image(file_path, file_hash, progress_callback)
            else:
                return ProcessingResult(file_path, False, error="不支持的文件类型")
        except Exception as e:
            return ProcessingResult(file_path, False, error=str(e))

    def _process_image(
        self, file_path: str, file_hash: str, progress_callback: Optional[Callable]
    ) -> ProcessingResult:
        img = ImageProcessor.load_image(file_path)
        if not img:
            return ProcessingResult(file_path, False, error="无法加载图片")

        if progress_callback:
            progress_callback(f"正在识别图片: {os.path.basename(file_path)}")

        # 检查模型是否支持视觉
        if not self.llm_client.is_vision_model():
            error_msg = f"当前模型 '{self.llm_client.model}' 不支持视觉输入！\n请在设置中选择视觉模型（如llava, qwen2-vl等）"
            return ProcessingResult(file_path, False, error=error_msg)

        response = self.llm_client.vision_chat(img, config.prompt_template)
        if not response:
            error_detail = self.llm_client.last_error or "大模型调用失败"
            return ProcessingResult(file_path, False, error=error_detail)

        parsed = LLMClient.parse_response(response)
        file_type = FileScanner.get_file_type(file_path)

        db.add_document(
            file_path=file_path,
            file_name=os.path.basename(file_path),
            file_hash=file_hash,
            file_type=file_type,
            raw_text=parsed.get("raw_text", ""),
            summary=parsed.get("summary", ""),
            keywords=parsed.get("keywords", ""),
            model_used=self.llm_client.model,
        )

        return ProcessingResult(
            file_path,
            True,
            raw_text=parsed.get("raw_text", ""),
            summary=parsed.get("summary", ""),
            keywords=parsed.get("keywords", ""),
        )

    def _process_pdf(
        self, file_path: str, file_hash: str, progress_callback: Optional[Callable]
    ) -> ProcessingResult:
        if progress_callback:
            progress_callback(f"正在处理PDF: {os.path.basename(file_path)}")

        # 检查模型是否支持视觉
        if not self.llm_client.is_vision_model():
            error_msg = f"当前模型 '{self.llm_client.model}' 不支持视觉输入！\n请在设置中选择视觉模型（如llava, qwen2-vl等）"
            return ProcessingResult(file_path, False, error=error_msg)

        text_content, images = PDFProcessor.extract_text_from_pdf(file_path)

        if images:
            all_text = []
            all_summary = []
            all_keywords = []

            for i, img in enumerate(images):
                if progress_callback:
                    progress_callback(
                        f"正在识别PDF第{i+1}/{len(images)}页: {os.path.basename(file_path)}"
                    )

                response = self.llm_client.vision_chat(img, config.prompt_template)
                if response:
                    parsed = LLMClient.parse_response(response)
                    if parsed.get("raw_text"):
                        all_text.append(parsed["raw_text"])
                    if parsed.get("summary"):
                        all_summary.append(parsed["summary"])
                    if parsed.get("keywords"):
                        all_keywords.append(parsed["keywords"])

            raw_text = "\n\n---\n\n".join(all_text)
            summary = "\n".join(all_summary)
            keywords = ", ".join(set(", ".join(all_keywords).split(",")))

        else:
            raw_text = text_content
            summary = ""
            keywords = ""

        db.add_document(
            file_path=file_path,
            file_name=os.path.basename(file_path),
            file_hash=file_hash,
            file_type="pdf",
            raw_text=raw_text,
            summary=summary,
            keywords=keywords,
            model_used=self.llm_client.model,
        )

        return ProcessingResult(
            file_path,
            True,
            raw_text=raw_text,
            summary=summary,
            keywords=keywords,
        )

    def process_directory(
        self,
        dir_path: str,
        recursive: bool = True,
        progress_callback: Optional[Callable] = None,
    ) -> List[ProcessingResult]:
        self._stop_flag = False
        files = FileScanner.scan_directory(dir_path, recursive)
        results = []

        for i, file_path in enumerate(files):
            if self._stop_flag:
                break

            if progress_callback:
                progress_callback(f"处理中 ({i+1}/{len(files)}): {os.path.basename(file_path)}")

            result = self.process_file(file_path)
            results.append(result)

        return results
