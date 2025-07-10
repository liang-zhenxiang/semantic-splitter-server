import re
from typing import Dict, List, Literal, Optional

from loguru import logger


_logger = logger.bind(name=__name__)


def cut_sentence(self, para):
    """self 不能省略，用于类内部方法使用"""
    _logger.info("override modelscope.pipelines.nlp.document_segmentation_pipeline.cut_sentence")
    para = re.sub(r"([。！!？\?])([^”’])", r"\1\n\2", para)
    para = re.sub(r"(\.{6})([^”’])", r"\1\n\2", para)
    para = re.sub(r"(\…{2})([^”’])", r"\1\n\2", para)
    para = re.sub(r"([。！？\?][”’])([^，。！？\?])", r"\1\n\2", para)
    para = para.rstrip()
    return [_ for _ in para.split("\n") if _]


chinese_model_name = "nlp_bert_document-segmentation_chinese-base"


class AliTextSplitter:
    p = None
    model_name = None
    model_path = None
    raw_cut_sentence = None

    def __init__(
        self,
        model_name: str,
        model_path: str,
        device: str,
    ):
        super().__init__()

        try:
            from modelscope.pipelines import pipeline
            from modelscope.pipelines.nlp.document_segmentation_pipeline import (
                DocumentSegmentationPipeline as pp,  # noqa: N813
            )

            self.raw_cut_sentence = pp.cut_sentence
        except ImportError as e:
            _logger.error(f"Could not import modelscope python package: {e}")
            raise ImportError(
                "Could not import modelscope python package. Please install modelscope with `pip install modelscope`. "
            )

        model_path = model_name if model_path is None else model_path

        self.model_name = model_name
        self.model_path = model_path

        self.p = pipeline(task="document-segmentation", model=model_path, device=device)
        _logger.info(f"Model {model_path} loaded successfully.")

    async def split_text(self, text: str, pdf: bool = False) -> List[str]:
        # use_document_segmentation参数指定是否用语义切分文档，此处采取的文档语义分割模型为达摩院开源的nlp_bert_document-segmentation_chinese-base，论文见https://arxiv.org/abs/2107.09278
        # 如果使用模型进行文档语义切分，那么需要安装modelscope[nlp]：pip install "modelscope[nlp]" -f https://modelscope.oss-cn-beijing.aliyuncs.com/releases/repo.html
        # 考虑到使用了三个模型，可能对于低配置gpu不太友好，因此这里将模型load进cpu计算，有需要的话可以替换device为自己的显卡id
        if pdf:
            text = re.sub(r"\n{3,}", r"\n", text)
            text = re.sub(r"\s", " ", text)
            text = re.sub("\n\n", "", text)

        from modelscope.pipelines.nlp.document_segmentation_pipeline import (
            DocumentSegmentationPipeline as pp,  # noqa: N813
        )

        if self.model_name == chinese_model_name:
            pp.cut_sentence = cut_sentence
        else:
            pp.cut_sentence = self.raw_cut_sentence

        result = self.p(documents=text)  # type: ignore
        sent_list = [i.replace("\t", "") for i in result["text"].split("\n\t") if i]  # type: ignore
        return sent_list


# 全局分割器缓存
_text_splitters: Dict[str, Optional[AliTextSplitter]] = {
    "zh": None,
    "en": None,
}


def get_text_splitter(language: Literal["zh", "en"] = "zh") -> AliTextSplitter:
    """获取文本分割器实例

    Args:
        language: 语言类型，"zh" 或 "en"

    Returns:
        AliTextSplitter: 文本分割器实例

    Raises:
        RuntimeError: 如果分割器未初始化
        ValueError: 如果语言类型不支持
    """
    if language not in ["zh", "en"]:
        raise ValueError(f"不支持的语言类型: {language}，支持的语言类型: zh, en")

    if _text_splitters[language] is None:
        raise RuntimeError(f"{language} 文本分割器未初始化，请先调用 initialize_text_splitter()")

    return _text_splitters[language]


def initialize_text_splitter(device: str = "cpu") -> Dict[str, AliTextSplitter]:
    """初始化文本分割器

    Args:
        device: 设备类型，默认为 "cpu", 可选值为 "cpu" 或 "cuda:0", "cuda:1" 等

    Returns:
        Dict[str, AliTextSplitter]: 初始化的分割器字典
    """
    global _text_splitters

    try:
        # 初始化中文分割器
        if _text_splitters["zh"] is None:
            _text_splitters["zh"] = AliTextSplitter(
                model_name=chinese_model_name,
                model_path="models/nlp_bert_document-segmentation_chinese-base",
                device=device,
            )
            _logger.info("✅ 已初始化中文文本分割器")

        # 初始化英文分割器
        if _text_splitters["en"] is None:
            _text_splitters["en"] = AliTextSplitter(
                model_name="nlp_bert_document-segmentation_english-base",
                model_path="models/nlp_bert_document-segmentation_english-base",
                device=device,
            )
            _logger.info("✅ 已初始化英文文本分割器")

        _logger.info("🎉 所有文本分割器初始化完成")
        return _text_splitters

    except Exception as e:
        _logger.error(f"❌ 文本分割器初始化失败: {e}")
        raise
