#!/usr/bin/env python3
"""
模型下载脚本
用于在容器运行时下载必要的模型文件
"""

import os
import sys
import requests
import zipfile
from pathlib import Path
from tqdm import tqdm

# 模型配置
MODELS_CONFIG = {
    "chinese": {
        "name": "nlp_bert_document-segmentation_chinese-base",
        "url": "https://huggingface.co/flydiy/nlp_bert_document-segmentation_chinese-base/resolve/main/",
        "files": [
            "config.json",
            "pytorch_model.bin",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
            "special_tokens_map.json",
            "added_tokens.json",
        ],
    },
    "english": {
        "name": "nlp_bert_document-segmentation_english-base",
        "url": "https://huggingface.co/flydiy/nlp_bert_document-segmentation_english-base/resolve/main/",
        "files": [
            "config.json",
            "pytorch_model.bin",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.txt",
            "special_tokens_map.json",
            "added_tokens.json",
        ],
    },
}


def download_file(url, filepath):
    """下载单个文件"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with open(filepath, "wb") as f:
            with tqdm(total=total_size, unit="B", unit_scale=True, desc=filepath.name) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        pbar.update(len(chunk))
        return True
    except Exception as e:
        print(f"下载失败 {url}: {e}")
        return False


def download_model(model_key, model_config, models_dir):
    """下载指定模型的所有文件"""
    model_dir = models_dir / model_config["name"]
    model_dir.mkdir(parents=True, exist_ok=True)

    print(f"开始下载 {model_key} 模型...")

    success_count = 0
    for filename in model_config["files"]:
        url = model_config["url"] + filename
        filepath = model_dir / filename

        if filepath.exists():
            print(f"文件已存在，跳过: {filename}")
            success_count += 1
            continue

        print(f"下载: {filename}")
        if download_file(url, filepath):
            success_count += 1

    print(f"{model_key} 模型下载完成: {success_count}/{len(model_config['files'])} 文件")
    return success_count == len(model_config["files"])


def main():
    """主函数"""
    models_dir = Path("/app/models")

    if not models_dir.exists():
        print(f"创建模型目录: {models_dir}")
        models_dir.mkdir(parents=True, exist_ok=True)

    print("开始下载模型文件...")

    all_success = True
    for model_key, model_config in MODELS_CONFIG.items():
        if not download_model(model_key, model_config, models_dir):
            all_success = False

    if all_success:
        print("所有模型下载完成！")
        sys.exit(0)
    else:
        print("部分模型下载失败，请检查网络连接或手动下载")
        sys.exit(1)


if __name__ == "__main__":
    main()
