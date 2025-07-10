from http import HTTPStatus

from fastapi import APIRouter, Body
from fastapi.responses import ORJSONResponse
from loguru import logger

from semantic_splitter.schemas.splitter import SplitterRequest
from semantic_splitter.services.splitter import en_text_splitter, zh_text_splitter


_logger = logger.bind(name=__name__)


router = APIRouter(
    prefix="/splitter",
    tags=["服务API-分段"],
)


@router.post(
    path="/",
    summary="语义分段",
    dependencies=[],
    response_class=ORJSONResponse,
)
async def split_text(
    request: SplitterRequest = Body(..., description="语义分段请求"),
) -> ORJSONResponse:
    """
    语义分段接口

    支持中文和英文的语义分段，基于 ModelScope 的 BERT 模型。
    """
    try:
        _logger.info(f"📝 收到分段请求: 语言={request.language}, PDF={request.pdf}, 文本长度={len(request.text)}")
        if request.language == "zh":
            segments = await zh_text_splitter.split_text(text=request.text, pdf=request.pdf)
        elif request.language == "en":
            segments = await en_text_splitter.split_text(text=request.text, pdf=request.pdf)
        else:
            segments = []

        # 构建响应
        response_data = {
            "success": True,
            "message": "分割成功",
            "data": {
                "segments": segments,
                "segment_count": len(segments),
                "original_length": len(request.text),
                "language": request.language,
            },
        }

        _logger.info(f"✅ 分割成功，生成 {len(segments)} 个片段")

        return ORJSONResponse(
            status_code=HTTPStatus.OK.value,
            content=response_data,
        )

    except Exception as e:
        _logger.error(f"❌ 分割失败: {str(e)}")

        error_response = {
            "success": False,
            "message": f"分割失败: {str(e)}",
            "data": None,
        }

        return ORJSONResponse(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            content=error_response,
        )
