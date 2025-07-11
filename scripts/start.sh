#!/bin/bash

# 启动脚本
# 在容器启动时自动下载模型并启动服务

set -e

echo "=== Semantic Splitter Server 启动脚本 ==="

# 检查模型目录
MODELS_DIR="/app/models"
if [ ! -d "$MODELS_DIR" ]; then
    echo "创建模型目录: $MODELS_DIR"
    mkdir -p "$MODELS_DIR"
fi

# 检查模型文件是否存在
CHINESE_MODEL_DIR="$MODELS_DIR/nlp_bert_document-segmentation_chinese-base"
ENGLISH_MODEL_DIR="$MODELS_DIR/nlp_bert_document-segmentation_english-base"

# 检查是否需要下载模型
NEED_DOWNLOAD=false

if [ ! -d "$CHINESE_MODEL_DIR" ] || [ ! -f "$CHINESE_MODEL_DIR/pytorch_model.bin" ]; then
    echo "中文模型文件缺失，需要下载"
    NEED_DOWNLOAD=true
fi

if [ ! -d "$ENGLISH_MODEL_DIR" ] || [ ! -f "$ENGLISH_MODEL_DIR/pytorch_model.bin" ]; then
    echo "英文模型文件缺失，需要下载"
    NEED_DOWNLOAD=true
fi

# 下载模型
if [ "$NEED_DOWNLOAD" = true ]; then
    echo "开始下载模型文件..."
    cd /app
    python scripts/download_models.py
    
    if [ $? -eq 0 ]; then
        echo "模型下载完成！"
    else
        echo "模型下载失败，但继续启动服务..."
    fi
else
    echo "模型文件已存在，跳过下载"
fi

# 启动服务
echo "启动 Semantic Splitter Server..."
exec python manage.py runserver 