import re
from typing import List

from loguru import logger


_logger = logger.bind(name=__name__)


def cut_sentence(self, para):
    print("override modelscope.pipelines.nlp.document_segmentation_pipeline.cut_sentence")
    para = re.sub(r"([。！!？\?])([^”’])", r"\1\n\2", para)
    para = re.sub(r"(\.{6})([^”’])", r"\1\n\2", para)
    para = re.sub(r"(\…{2})([^”’])", r"\1\n\2", para)
    para = re.sub(r"([。！？\?][”’])([^，。！？\?])", r"\1\n\2", para)
    para = para.rstrip()
    return [_ for _ in para.split("\n") if _]


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
        print(f"Model {model_path} loaded successfully.")

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

        if self.model_name == "nlp_bert_document-segmentation_chinese-base":
            pp.cut_sentence = cut_sentence
        else:
            pp.cut_sentence = self.raw_cut_sentence

        result = self.p(documents=text)  # type: ignore
        sent_list = [i.replace("\t", "") for i in result["text"].split("\n\t") if i]  # type: ignore
        return sent_list


zh_text_splitter = AliTextSplitter(
    model_name="nlp_bert_document-segmentation_zh-base",
    model_path="models/nlp_bert_document-segmentation_chinese-base",
    device="cpu",
)

en_text_splitter = AliTextSplitter(
    model_name="nlp_bert_document-segmentation_english-base",
    model_path="models/nlp_bert_document-segmentation_english-base",
    device="cpu",
)
