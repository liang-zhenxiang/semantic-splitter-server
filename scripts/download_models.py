#!/usr/bin/env python3
"""
模型下载脚本（魔搭社区 modelscope.cn 版，官方SDK）
使用 modelscope SDK 下载全部模型文件，自动创建本地目录结构。
"""

import os
from pathlib import Path
from modelscope.hub.api import HubApi
from modelscope.hub.snapshot_download import snapshot_download

# 配置：模型列表
MODELS = [
    {
        "name": "nlp_bert_document-segmentation_chinese-base",
        "modelscope_id": "iic/nlp_bert_document-segmentation_chinese-base",
    },
    {
        "name": "nlp_bert_document-segmentation_english-base",
        "modelscope_id": "iic/nlp_bert_document-segmentation_english-base",
    },
]

# 本地模型存放根目录
MODELS_ROOT = Path("/app/models")


def download_model(model):
    model_dir = MODELS_ROOT / model["name"]
    print(f"\n开始下载模型: {model['name']} 到 {model_dir}")
    # 使用 modelscope 官方SDK下载
    snapshot_download(
        model_id=model["modelscope_id"],
        cache_dir=str(model_dir),
        revision="master",
        local_dir=str(model_dir),
    )
    print(f"模型 {model['name']} 下载完成。")


def main():
    print("=== 魔搭社区模型自动下载脚本（官方SDK） ===")
    for model in MODELS:
        download_model(model)
    print("\n所有模型下载任务完成。")


if __name__ == "__main__":
    main()
