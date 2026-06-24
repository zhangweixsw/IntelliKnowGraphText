import os
import base64
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image
import io

try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


class ImageProcessor:
    @staticmethod
    def load_image(file_path: str) -> Optional[Image.Image]:
        try:
            return Image.open(file_path)
        except Exception:
            return None

    @staticmethod
    def image_to_base64(img: Image.Image, format: str = "PNG") -> str:
        buffered = io.BytesIO()
        img.save(buffered, format=format)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    @staticmethod
    def resize_if_needed(img: Image.Image, max_size: int = 2048) -> Image.Image:
        if img.width > max_size or img.height > max_size:
            ratio = min(max_size / img.width, max_size / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            return img.resize(new_size, Image.Resampling.LANCZOS)
        return img


class PDFProcessor:
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Tuple[str, List[Image.Image]]:
        images = []
        text_content = ""

        if PYPDF_AVAILABLE:
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text_content += page.extract_text() or ""
            except Exception:
                pass

        if PDF2IMAGE_AVAILABLE:
            try:
                images = convert_from_path(file_path, dpi=150)
            except Exception:
                pass

        return text_content, images

    @staticmethod
    def get_pdf_as_images(file_path: str) -> List[Image.Image]:
        if not PDF2IMAGE_AVAILABLE:
            return []
        try:
            return convert_from_path(file_path, dpi=150)
        except Exception:
            return []


class FileScanner:
    SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
    SUPPORTED_PDF_EXTENSIONS = {".pdf"}

    @staticmethod
    def scan_directory(dir_path: str, recursive: bool = True) -> List[str]:
        files = []
        path = Path(dir_path)

        if recursive:
            for ext in FileScanner.SUPPORTED_IMAGE_EXTENSIONS | FileScanner.SUPPORTED_PDF_EXTENSIONS:
                files.extend(path.rglob(f"*{ext}"))
        else:
            for ext in FileScanner.SUPPORTED_IMAGE_EXTENSIONS | FileScanner.SUPPORTED_PDF_EXTENSIONS:
                files.extend(path.glob(f"*{ext}"))

        return [str(f) for f in files]

    @staticmethod
    def is_supported(file_path: str) -> bool:
        ext = Path(file_path).suffix.lower()
        return ext in FileScanner.SUPPORTED_IMAGE_EXTENSIONS or ext in FileScanner.SUPPORTED_PDF_EXTENSIONS

    @staticmethod
    def get_file_type(file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext in FileScanner.SUPPORTED_PDF_EXTENSIONS:
            return "pdf"
        elif ext in FileScanner.SUPPORTED_IMAGE_EXTENSIONS:
            return "image"
        return "unknown"
