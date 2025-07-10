import contextlib
import os
import time
from datetime import datetime
from pathlib import Path

import pytz
from loguru import logger


ROOT_DIR = Path(__file__).parent.parent
ChinaTimeZone = pytz.timezone(os.environ.get("TZ", "Asia/Shanghai"))


# 记录应用启动开始时间
start_time = time.time()


_logger = logger.bind(name=__name__)


_logger.info(
    f"\n🚀 Semantic Splitter Server 开始启动... ({datetime.now(tz=ChinaTimeZone).strftime('%Y-%m-%d %H:%M:%S')})"
)


from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, List, Union

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from starlette.routing import BaseRoute


APP_NAME = "Semantic Splitter Server"


def __remove_route(url: str, routes: List[Union[APIRoute, BaseRoute]]) -> None:
    """
    移除路由
    """
    idx = None
    for i, r in enumerate(routes):
        if isinstance(r, APIRoute) and r.path.lower() == url.lower():
            idx = i
            break
    if isinstance(idx, int):
        routes.pop(idx)


def make_fastapi_offline(
    fast_app: FastAPI,
    static_dir: Path,
    static_url: str,
    doc_endpoints: List[Dict[str, Any]],
) -> None:
    """配置FastAPI应用使用离线文档，支持多个文档端点

    该函数允许FastAPI应用使用本地静态文件提供Swagger和ReDoc文档，
    而不依赖CDN资源。同时支持为不同API路径配置独立的文档页面。

    Args:
        fast_app (FastAPI): FastAPI应用实例
        static_dir (Path, optional): 静态文件目录路径. 默认为ROOT_DIR/"static".
        static_url (str, optional): 静态文件URL前缀. 默认为"/static-offline-docs".
        doc_endpoints (list, optional): 文档端点配置列表. 每个配置项包含:
            - pattern: 路由匹配的正则表达式
            - title: 文档标题
            - docs_url: Swagger UI的URL路径
            - redoc_url: ReDoc的URL路径
            - enabled: 是否启用该文档端点
    """

    # 如果全局禁用了OpenAPI，则直接返回，不创建任何文档端点
    if fast_app.openapi_url is None:
        return

    import re

    from fastapi.openapi.docs import (
        get_redoc_html,
        get_swagger_ui_html,
    )
    from fastapi.openapi.utils import get_openapi
    from fastapi.staticfiles import StaticFiles

    # 挂载静态文件
    fast_app.mount(
        static_url,
        StaticFiles(directory=Path(static_dir / "swagger").as_posix()),
        name="static-offline-docs",
    )

    for endpoint in doc_endpoints:
        # 检查该文档端点是否启用
        if not endpoint.get("enabled", True):
            continue

        pattern_str = endpoint.get("pattern", None)  # 默认匹配所有路由
        title_suffix = endpoint.get("title", "API文档")
        docs_url = endpoint.get("docs_url", None)
        redoc_url = endpoint.get("redoc_url", None)

        # 生成 OpenAPI URL
        openapi_url = f"/openapi-{title_suffix.replace(' ', '-').lower()}.json"

        # 自定义 OpenAPI 生成
        @fast_app.get(openapi_url, include_in_schema=False)
        async def get_custom_openapi(
            pattern_str=pattern_str,
            title_suffix=title_suffix,
        ):
            # 编译正则表达式
            pattern = re.compile(pattern_str)

            # 创建空文档作为默认情况
            empty_openapi = get_openapi(
                title=f"{APP_NAME} - {title_suffix}",
                version="1.0.0",
                routes=[],
            )

            # 其他文档，使用正则匹配
            routes = [
                route
                for route in fast_app.routes
                if hasattr(route, "path") and pattern.match(str(route.path))  # type: ignore
            ]

            # 如果没有匹配的路由，返回空文档
            if not routes:
                return empty_openapi

            return get_openapi(
                title=f"{APP_NAME} - {title_suffix}",
                version="1.0.0",
                routes=routes,
            )

        # 添加 Swagger UI
        if docs_url:
            __remove_route(docs_url, fast_app.routes)

            @fast_app.get(docs_url, include_in_schema=False)
            async def custom_swagger_ui_html(
                request: Request,
                openapi_url=openapi_url,
                title_suffix=title_suffix,
            ):
                root = request.scope.get("root_path")
                favicon = f"{root}{static_url}/favicon.ico"
                return get_swagger_ui_html(
                    openapi_url=f"{root}{openapi_url}",
                    title=f"{APP_NAME} - {title_suffix} - Swagger UI",
                    swagger_js_url=f"{root}{static_url}/swagger-ui-bundle.js",
                    swagger_css_url=f"{root}{static_url}/swagger-ui.css",
                    swagger_favicon_url=favicon,
                )

        # 添加 ReDoc
        if redoc_url:
            __remove_route(redoc_url, fast_app.routes)

            @fast_app.get(redoc_url, include_in_schema=False)
            async def custom_redoc_html(
                request: Request,
                openapi_url=openapi_url,
                title_suffix=title_suffix,
            ):
                root = request.scope.get("root_path")
                favicon = f"{root}{static_url}/favicon.ico"
                return get_redoc_html(
                    openapi_url=f"{root}{openapi_url}",
                    title=f"{APP_NAME} - {title_suffix} - ReDoc",
                    redoc_js_url=f"{root}{static_url}/redoc.standalone.js",
                    with_google_fonts=False,
                    redoc_favicon_url=favicon,
                )


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI):
    # 启动事件
    _logger.info("🔧 正在初始化应用组件...")

    # 初始化文本分割器
    try:
        device = os.environ.get("SEMANTIC_SPLITTER_DEVICE", "cpu")
        _logger.info(f"🤖 正在初始化文本分割器，设备: {device}")

        from semantic_splitter.services.splitter import initialize_text_splitter

        text_splitters = initialize_text_splitter(device=device)

        _logger.info(f"✅ 文本分割器初始化成功，加载的模型: {list(text_splitters.keys())}")

    except Exception as e:
        _logger.error(f"❌ 文本分割器初始化失败: {e}")
        # 注意：这里不抛出异常，让应用继续启动，但分割功能会不可用
        _logger.warning("⚠️ 应用将在没有文本分割功能的情况下继续运行")

    # 计算并打印启动耗时
    completion_time = datetime.now(tz=ChinaTimeZone)
    end_time = completion_time.timestamp()
    startup_duration = end_time - start_time

    _logger.info(
        "\n"
        + "=" * 70
        + "\n"
        + "🎉 Semantic Splitter Server 启动完成！"
        + "\n"
        + f"📊 启动耗时: {startup_duration:.3f} 秒"
        + "\n"
        + f"⏰ 完成时间: {completion_time.strftime('%Y-%m-%d %H:%M:%S')}"
        + "\n"
        + "🔗 访问地址: http://127.0.0.1:8000"
        + "\n"
        + "=" * 70
        + "\n",
    )

    yield
    # 关闭事件
    _logger.info("🛑 Semantic Splitter Server 正在关闭...")


app = FastAPI(
    title=APP_NAME,
    description="一个强大的语义文本分割服务器",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=ROOT_DIR / "static"), name="static")


@app.get(
    path="/actuator/health",
    summary="健康检测",
    tags=["监控"],
)
async def health() -> ORJSONResponse:
    """
    健康检测 - 返回服务健康状态
    """
    return ORJSONResponse(
        status_code=HTTPStatus.OK.value,
        content={
            "status": "UP",
            "timestamp": datetime.now(tz=ChinaTimeZone).isoformat(),
            "service": APP_NAME,
            "version": "1.0.0",
        },
    )


_logger.info("🚀 正在加载路由...")


# 加载路由
# 注意：路由注册顺序非常重要！FastAPI 会按照注册顺序进行路由匹配
# 更具体的路由应该注册在前面，更通用的路由应该注册在后面
# 这是因为 FastAPI 使用第一个匹配的路由，而不是最匹配的路由

# API 路由 - 最具体的路由，应该最先注册
# 所有 /api 开头的请求都会先尝试匹配这个路由
from semantic_splitter.controllers import api_router


_logger.info("✅ 路由加载完成")


app.include_router(api_router, prefix="/api")
