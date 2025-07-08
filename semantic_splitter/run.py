import os
from pathlib import Path

from uvicorn import run

from semantic_splitter.application import app  # noqa: F401


def main(cli_args=None):
    """
    启动 Semantic Splitter Server

    Args:
        cli_args: 命令行参数字典，包含 host, port, workers, log_level 等
    """
    # 默认配置
    default_config = {
        "host": "0.0.0.0",
        "port": 8000,
        "workers": 1,
        "log_level": "info",
        "reload": False,
        "reload_dirs": None,
        "reload_excludes": None,
    }

    # 合并命令行参数
    if cli_args:
        default_config.update(cli_args)

    # 从环境变量获取配置
    host = os.getenv("HOST", default_config["host"])
    port = int(os.getenv("PORT", default_config["port"]))
    workers = int(os.getenv("WORKERS", default_config["workers"]))
    log_level = os.getenv("LOG_LEVEL", default_config["log_level"])
    reload = os.getenv("RELOAD", "false").lower() == "true"

    # 开发模式配置
    if reload:
        reload_dirs = [str(Path(__file__).parent)]
        reload_excludes = ["*.pyc", "__pycache__", "*.log"]
    else:
        reload_dirs = None
        reload_excludes = None

    # 启动服务器
    run(
        app="semantic_splitter.application:app",
        host=host,
        port=port,
        log_level=log_level,
        workers=workers if not reload else 1,  # reload 模式下只能使用单进程
        reload=reload,
        reload_dirs=reload_dirs,
        reload_excludes=reload_excludes,
    )


if __name__ == "__main__":
    main()
