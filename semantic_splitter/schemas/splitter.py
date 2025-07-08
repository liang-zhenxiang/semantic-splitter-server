from pydantic import BaseModel, Field


class SplitterRequest(BaseModel):
    """语义分段请求Schema"""

    text: str = Field(
        min_length=1,
        description="待分割的文本内容",
        examples=["这是一个智能客服应用，可以帮助用户解决各种问题。我们使用先进的AI技术来提供更好的服务体验。"],
    )
    pdf: bool = Field(
        default=False,
        description="是否是PDF文件文本（影响预处理方式）",
        examples=[False],
    )
    language: str = Field(
        default="zh",
        description="文本语言类型",
        examples=["zh", "en"],
    )
