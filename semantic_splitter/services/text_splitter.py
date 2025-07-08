"""
文本分割服务
支持基于 ModelScope 的语义分割模型和简单的规则分割
"""

import os
import re
from typing import Any, Dict, List, Optional

from loguru import logger


_logger = logger.bind(name=__name__)


class SimpleTextSplitter:
    """简单的文本分割器（不依赖深度学习模型）"""

    def __init__(self, device: str = "cpu"):
        self.device = device
        _logger.info(f"🔧 初始化简单文本分割器，设备: {device}")

    def _preprocess_text(self, text: str, is_pdf: bool = False) -> str:
        """文本预处理"""
        if is_pdf:
            # PDF 文本特殊处理
            text = re.sub(r"\n{3,}", r"\n", text)
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\n\n", "", text)
        return text.strip()

    def _split_by_sentences(self, text: str, language: str = "zh") -> List[str]:
        """按句子分割文本"""
        if language in ["zh", "chinese"]:
            # 中文句子分割
            sentences = re.split(r"[。！？\?；;]\s*", text)
        else:
            # 英文句子分割
            sentences = re.split(r"[.!?;]\s+", text)

        return [s.strip() for s in sentences if s.strip()]

    def _split_by_length(self, text: str, max_length: int = 500) -> List[str]:
        """按长度分割文本"""
        if len(text) <= max_length:
            return [text]

        segments = []
        current_pos = 0

        while current_pos < len(text):
            # 尝试在句号、感叹号、问号处分割
            end_pos = min(current_pos + max_length, len(text))
            segment = text[current_pos:end_pos]

            # 如果不是最后一段，尝试在标点符号处截断
            if end_pos < len(text):
                # 查找最后一个标点符号
                last_punct = max(
                    segment.rfind("。"),
                    segment.rfind("！"),
                    segment.rfind("？"),
                    segment.rfind("."),
                    segment.rfind("!"),
                    segment.rfind("?"),
                )

                if last_punct > max_length * 0.3:  # 如果标点符号位置合理
                    segment = segment[: last_punct + 1]
                    current_pos += last_punct + 1
                else:
                    current_pos = end_pos
            else:
                current_pos = end_pos

            if segment.strip():
                segments.append(segment.strip())

        return segments

    async def split_text(self, text: str, language: str = "zh", is_pdf: bool = False) -> List[str]:
        """
        分割文本

        Args:
            text: 输入文本
            language: 语言类型 (zh/en)
            is_pdf: 是否为PDF文本

        Returns:
            分割后的文本片段列表
        """
        if not text.strip():
            return []

        # 文本预处理
        processed_text = self._preprocess_text(text, is_pdf)

        _logger.info(f"🔄 使用简单分割器进行文本分割，语言: {language}, 文本长度: {len(processed_text)}")

        # 首先尝试按句子分割
        sentences = self._split_by_sentences(processed_text, language)

        # 如果句子太长，进一步按长度分割
        final_segments = []
        for sentence in sentences:
            if len(sentence) > 500:
                segments = self._split_by_length(sentence, max_length=500)
                final_segments.extend(segments)
            else:
                final_segments.append(sentence)

        # 过滤空段落
        final_segments = [seg for seg in final_segments if seg.strip()]

        _logger.info(f"✅ 简单分割完成，生成 {len(final_segments)} 个片段")
        return final_segments

    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return ["simple_splitter"]

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "device": self.device,
            "loaded_models": ["simple_splitter"],
            "model_type": "rule_based",
            "model_paths": {},
        }


class ModelScopeTextSplitter:
    """基于 ModelScope 的文本分割器"""

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.models: Dict[str, Any] = {}
        self.model_paths = {
            "chinese": "models/nlp_bert_document-segmentation_chinese-base",
            "english": "models/nlp_bert_document-segmentation_english-base",
        }
        self._load_models()

    def _load_models(self):
        """加载所有可用的模型"""
        try:
            from modelscope.pipelines import pipeline

            _logger.info(f"🔧 正在加载文本分割模型到设备: {self.device}")

            # 加载中文模型
            if os.path.exists(self.model_paths["chinese"]):
                _logger.info("📚 加载中文语义分割模型...")
                self.models["chinese"] = pipeline(
                    task="document-segmentation", model=self.model_paths["chinese"], device=self.device
                )
                _logger.info("✅ 中文模型加载成功")
            else:
                _logger.warning(f"⚠️ 中文模型路径不存在: {self.model_paths['chinese']}")

            # 加载英文模型
            if os.path.exists(self.model_paths["english"]):
                _logger.info("📚 加载英文语义分割模型...")
                self.models["english"] = pipeline(
                    task="document-segmentation", model=self.model_paths["english"], device=self.device
                )
                _logger.info("✅ 英文模型加载成功")
            else:
                _logger.warning(f"⚠️ 英文模型路径不存在: {self.model_paths['english']}")

            if not self.models:
                raise RuntimeError("没有成功加载任何模型")

        except ImportError as e:
            _logger.error(f"❌ ModelScope 导入失败: {e}")
            raise ImportError("无法导入 ModelScope，请安装: pip install modelscope[nlp]")
        except Exception as e:
            _logger.error(f"❌ 模型加载失败: {e}")
            raise

    def _preprocess_text(self, text: str, is_pdf: bool = False) -> str:
        """文本预处理"""
        if is_pdf:
            # PDF 文本特殊处理
            text = re.sub(r"\n{3,}", r"\n", text)
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\n\n", "", text)
        return text.strip()

    def _cut_sentence_chinese(self, para: str) -> List[str]:
        """中文句子切分（优化版）"""
        para = re.sub(r'([。！!？\?])([^"\'])', r"\1\n\2", para)
        para = re.sub(r'(\.{6})([^"\'])', r"\1\n\2", para)
        para = re.sub(r'(\…{2})([^"\'])', r"\1\n\2", para)
        para = re.sub(r'([。！？\?]["\'])([^，。！？\?])', r"\1\n\2", para)
        para = para.rstrip()
        return [sentence for sentence in para.split("\n") if sentence.strip()]

    async def split_text(self, text: str, language: str = "zh", is_pdf: bool = False) -> List[str]:
        """
        分割文本

        Args:
            text: 输入文本
            language: 语言类型 (zh/en)
            is_pdf: 是否为PDF文本

        Returns:
            分割后的文本片段列表
        """
        if not text.strip():
            return []

        # 确定使用的模型
        model_key = "chinese" if language in ["zh", "chinese"] else "english"

        if model_key not in self.models:
            # 如果指定语言的模型不存在，尝试使用其他模型
            available_models = list(self.models.keys())
            if not available_models:
                raise RuntimeError("没有可用的模型")
            model_key = available_models[0]
            _logger.warning(f"⚠️ 指定语言模型不存在，使用 {model_key} 模型")

        try:
            # 文本预处理
            processed_text = self._preprocess_text(text, is_pdf)

            # 特殊处理中文模型的句子切分
            if model_key == "chinese":
                # 暂时替换 ModelScope 的句子切分方法
                from modelscope.pipelines.nlp.document_segmentation_pipeline import DocumentSegmentationPipeline

                original_cut_sentence = DocumentSegmentationPipeline.cut_sentence
                DocumentSegmentationPipeline.cut_sentence = lambda self, para: self._cut_sentence_chinese(para)

            # 执行语义分割
            _logger.info(f"🔄 使用 {model_key} 模型进行语义分割，文本长度: {len(processed_text)}")
            result = self.models[model_key](documents=processed_text)

            # 恢复原始方法
            if model_key == "chinese":
                DocumentSegmentationPipeline.cut_sentence = original_cut_sentence

            # 处理结果
            if isinstance(result, dict) and "text" in result:
                segments = [
                    segment.replace("\t", "").strip() for segment in result["text"].split("\n\t") if segment.strip()
                ]
            else:
                segments = [processed_text]  # 降级处理

            _logger.info(f"✅ 分割完成，生成 {len(segments)} 个片段")
            return segments

        except Exception as e:
            _logger.error(f"❌ 文本分割失败: {e}")
            # 降级到简单分割器
            _logger.info("🔄 降级使用简单分割器...")
            simple_splitter = SimpleTextSplitter(self.device)
            return await simple_splitter.split_text(text, language, is_pdf)

    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return list(self.models.keys())

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "device": self.device,
            "loaded_models": list(self.models.keys()),
            "model_type": "deep_learning",
            "model_paths": self.model_paths,
        }


# 全局分割器实例
_text_splitter: Optional[Any] = None


def get_text_splitter():
    """获取文本分割器实例"""
    global _text_splitter
    if _text_splitter is None:
        raise RuntimeError("文本分割器未初始化")
    return _text_splitter


def initialize_text_splitter(device: str = "cpu"):
    """初始化文本分割器"""
    global _text_splitter

    try:
        # 首先尝试使用 ModelScope
        _text_splitter = ModelScopeTextSplitter(device=device)
        _logger.info("✅ 已初始化 ModelScope 文本分割器")
    except Exception as e:
        _logger.warning(f"⚠️ ModelScope 分割器初始化失败: {e}")
        _logger.info("🔄 降级使用简单文本分割器...")
        _text_splitter = SimpleTextSplitter(device=device)
        _logger.info("✅ 已初始化简单文本分割器")

    return _text_splitter
