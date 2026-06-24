# IntelliKnowGraphText

利用本地大模型（LLM）智能处理 PDF 和图片，支持图文识别（OCR）和文本分析。

## 功能
- PDF 文档智能解析和内容提取
- 图片内容识别和 OCR 文字提取
- 集成本地大模型进行语义分析
- 支持图文混合处理

## 技术栈
- Python
- 本地大模型（LLM）集成
- PyInstaller 打包

## 项目结构
- `core/` - 核心模块（文档处理、LLM 客户端、处理器）
- `data/` - 数据层（数据库）
- `config.json` - 配置文件
- `main.py` - 入口

## 使用
1. 安装依赖
2. 配置 `config.json`
3. `python main.py`
