#!/usr/bin/env python
"""
Semantic Splitter Server 管理脚本

# 启动服务器
python manage.py runserver

# 启动服务器（自定义主机和端口）
python manage.py runserver --host 0.0.0.0 --port 8080

# 启动服务器（开发模式，支持热重载）
python manage.py runserver --reload

# 启动服务器（指定GPU设备）
python manage.py runserver --device cuda:0

# 启动服务器（指定CPU设备）
python manage.py runserver --device cpu

"""

import os

import click


# 设置时区
os.environ["TZ"] = "Asia/Shanghai"


@click.group()
def cli():
    """Semantic Splitter Server 管理命令行工具"""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="监听的主机地址")
@click.option("--port", type=int, default=8000, help="监听的端口")
@click.option("--workers", type=int, default=1, help="工作进程数")
@click.option("--log-level", default="info", help="日志级别")
@click.option("--reload", is_flag=True, help="启用热重载（开发模式）")
@click.option("--device", default="cpu", help="模型运行设备 (cpu/cuda:0/cuda:1/...)")
def runserver(host, port, workers, log_level, reload, device):
    """启动开发服务器"""
    click.echo("🚀 正在启动 Semantic Splitter Server...")
    click.echo(f"📡 监听地址: {host}:{port}")
    click.echo(f"🔧 工作进程: {workers}")
    click.echo(f"📝 日志级别: {log_level}")
    click.echo(f"🔄 热重载: {'启用' if reload else '禁用'}")
    click.echo(f"🖥️ 运行设备: {device}")
    click.echo("-" * 50)

    # 设置设备环境变量，供应用启动时使用
    os.environ["SEMANTIC_SPLITTER_DEVICE"] = device

    # 导入启动模块
    from semantic_splitter import run

    # 创建命令行参数字典
    server_args = {
        "host": host,
        "port": port,
        "workers": workers,
        "log_level": log_level,
        "reload": reload,
        "device": device,
    }

    # 使用命令行参数启动服务器
    run.main(cli_args=server_args)


if __name__ == "__main__":
    cli()
