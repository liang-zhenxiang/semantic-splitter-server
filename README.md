# Semantic Splitter Server - 语义文本分割服务

一个基于 FastAPI 和 ModelScope 的高性能语义文本分割服务，支持中文和英文的智能文本分段。

## 🚀 功能特点

- **智能语义分割**：基于 ModelScope 的 BERT 文档分割模型
- **多语言支持**：支持中文和英文文本分割
- **设备灵活配置**：支持 CPU 和 GPU 设备
- **智能降级机制**：AI 模型不可用时自动切换到规则分割
- **高性能异步**：基于 FastAPI 的异步 Web 框架
- **完整的 API 文档**：自动生成 Swagger/OpenAPI 文档
- **Docker 支持**：提供完整的容器化部署方案
- **健康检查**：内置服务健康状态监控
- **开发友好**：支持热重载和开发模式

## 📁 项目结构

```text
semantic-splitter-server/
├── semantic_splitter/          # 主应用模块
│   ├── application.py          # FastAPI 应用配置
│   ├── run.py                  # 服务启动模块
│   ├── controllers/            # 控制器层
│   │   └── service_api/        # 服务 API
│   │       └── v1/             # API v1 版本
│   │           └── splitter.py # 文本分割接口
│   ├── services/               # 服务层
│   │   └── text_splitter.py    # 文本分割服务
│   └── schemas/                # 数据模型
│       └── splitter.py         # 分割请求模型
├── models/                     # AI 模型权重文件
│   ├── nlp_bert_document-segmentation_chinese-base/
│   └── nlp_bert_document-segmentation_english-base/
├── static/                     # 静态资源
├── scripts/                    # 开发脚本
├── tests/                      # 测试模块
├── manage.py                   # 管理命令入口
├── pyproject.toml              # 项目配置
├── uv.lock                     # 依赖锁定文件
├── Dockerfile                  # Docker 构建文件
└── README.md                   # 项目文档
```

## 🛠️ 环境要求

- **Python**: 3.10 - 3.12
- **系统**: Windows/Linux/macOS
- **内存**: 建议 4GB+ (加载 AI 模型需要)
- **存储**: 2GB+ (模型文件约 800MB)

## ⚡ 快速开始

### 1. 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或使用 pip
pip install uv
```

### 2. 克隆项目

```bash
git clone <项目地址>
cd semantic-splitter-server
```

### 3. 一键设置开发环境

```bash
# 安装依赖并配置开发环境
uv run setup-dev
```

### 4. 启动服务

```bash
# 基本启动 (CPU)
uv run python manage.py runserver

# 指定设备启动
uv run python manage.py runserver --device cpu
uv run python manage.py runserver --device cuda:0

# 开发模式 (热重载)
uv run python manage.py runserver --reload

# 自定义配置
uv run python manage.py runserver --host 0.0.0.0 --port 8080 --device cpu
```

### 5. 访问服务

- **服务地址**: <http://localhost:8000>
- **API 文档**: <http://localhost:8000/docs>
- **健康检查**: <http://localhost:8000/actuator/health>

## 📚 API 接口

### 文本分割

```bash
POST /api/v1/service/splitter/
Content-Type: application/json

{
  "text": "这是一个智能客服应用，可以帮助用户解决各种问题。我们使用先进的AI技术来提供更好的服务体验。",
  "language": "zh",
  "pdf": false
}
```

**响应示例:**

```json
{
  "success": true,
  "message": "分割成功",
  "data": {
    "segments": [
      "这是一个智能客服应用，可以帮助用户解决各种问题",
      "我们使用先进的AI技术来提供更好的服务体验"
    ],
    "segment_count": 2,
    "original_length": 54,
    "language": "zh",
    "is_pdf": false,
    "model_info": {
      "device": "cpu",
      "loaded_models": ["chinese", "english"],
      "model_type": "deep_learning"
    }
  }
}
```

### 模型信息

```bash
GET /api/v1/service/splitter/models
```

### 健康检查

```bash
GET /actuator/health
```

## 🔧 命令行参数

### runserver 命令

```bash
uv run python manage.py runserver [OPTIONS]

选项:
  --host TEXT        监听的主机地址 (默认: 0.0.0.0)
  --port INTEGER     监听的端口 (默认: 8000)
  --workers INTEGER  工作进程数 (默认: 1)
  --log-level TEXT   日志级别 (默认: info)
  --reload           启用热重载 (开发模式)
  --device TEXT      模型运行设备 (cpu/cuda:0/cuda:1/...)
  --help             显示帮助信息
```

### 使用示例

```bash
# 生产环境启动
uv run python manage.py runserver --host 0.0.0.0 --port 8080 --workers 4 --device cpu

# 开发环境启动
uv run python manage.py runserver --reload --device cpu

# GPU 加速启动
uv run python manage.py runserver --device cuda:0
```

## 🐳 Docker 部署

### 构建镜像

```bash
docker build -t semantic-splitter-server .
```

### 基础部署

```bash
# 默认配置（CPU 模式，端口 8000）
docker run -p 8000:8000 semantic-splitter-server
# 等价于：uv run /app/manage.py runserver --host 0.0.0.0 --port 8000 --device cpu
```

### 自定义参数部署

```bash
# 修改端口和设备
docker run -p 8080:8080 semantic-splitter-server \
  runserver --host 0.0.0.0 --port 8080 --device cuda:0

# 启用热重载（开发环境）
docker run -p 8000:8000 semantic-splitter-server \
  runserver --host 0.0.0.0 --port 8000 --reload --device cpu

# 生产环境多进程
docker run -p 8000:8000 semantic-splitter-server \
  runserver --host 0.0.0.0 --port 8000 --workers 4 --device cpu
```

### 使用环境变量

```bash
# GPU 部署
docker run --gpus all -e SEMANTIC_SPLITTER_DEVICE=cuda:0 \
  -p 8000:8000 semantic-splitter-server

# 组合使用环境变量和参数
docker run --gpus all -e SEMANTIC_SPLITTER_DEVICE=cuda:0 \
  -p 8080:8000 semantic-splitter-server \
  runserver --host 0.0.0.0 --port 8000 --workers 2
```

### 运维部署建议

#### 1. 生产环境部署

```bash
docker run -d \
  --name semantic-splitter \
  --restart unless-stopped \
  -p 8000:8000 \
  -e SEMANTIC_SPLITTER_DEVICE=cpu \
  semantic-splitter-server \
  runserver --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

#### 2. GPU 加速部署

```bash
docker run -d \
  --name semantic-splitter-gpu \
  --restart unless-stopped \
  --gpus all \
  -p 8000:8000 \
  -e SEMANTIC_SPLITTER_DEVICE=cuda:0 \
  semantic-splitter-server \
  runserver --host 0.0.0.0 --port 8000 --workers 2 --log-level info
```

#### 3. 负载均衡部署

```bash
# 节点1
docker run -d --name semantic-splitter-1 -p 8001:8000 semantic-splitter-server

# 节点2  
docker run -d --name semantic-splitter-2 -p 8002:8000 semantic-splitter-server

# 节点3
docker run -d --name semantic-splitter-3 -p 8003:8000 semantic-splitter-server
```

#### 4. 健康检查部署

```bash
docker run -d \
  --name semantic-splitter \
  --restart unless-stopped \
  --health-cmd="curl -f http://localhost:8000/actuator/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  -p 8000:8000 \
  semantic-splitter-server
```

### 其他管理命令

```bash
# 查看帮助
docker run semantic-splitter-server --help

# 查看版本信息
docker run semantic-splitter-server --version
```

## 🔄 智能降级机制

服务具备完善的降级机制，确保高可用性：

1. **优先使用**: ModelScope 深度学习模型 (高质量语义分割)
2. **自动降级**: 规则基础分割器 (确保服务可用性)
3. **无缝切换**: 模型加载失败时自动切换，用户无感知

## 🛠️ 开发指南

### 开发环境管理

```bash
# 设置开发环境
uv run setup-dev

# 检查开发环境
uv run check-dev

# 代码格式化
uv run format-code

# 运行测试
uv run pytest
```

### 添加依赖

```bash
# 添加生产依赖
uv add <package-name>

# 添加开发依赖
uv add --dev <package-name>

# 安装特定依赖组
uv sync --extra standard
```

### 代码质量

项目使用 pre-commit hooks 确保代码质量：

```bash
# 安装 pre-commit hooks
uv run pre-commit install

# 手动运行检查
uv run pre-commit run --all-files
```

## 📝 支持的模型

### 中文模型

- **模型**: nlp_bert_document-segmentation_chinese-base
- **路径**: `models/nlp_bert_document-segmentation_chinese-base/`
- **功能**: 中文文本语义分割

### 英文模型

- **模型**: nlp_bert_document-segmentation_english-base
- **路径**: `models/nlp_bert_document-segmentation_english-base/`
- **功能**: 英文文本语义分割

## 🔍 监控和日志

### 健康检查

```bash
curl http://localhost:8000/actuator/health
```

### 日志查看

```bash
# 启动时会显示详细的初始化日志
# 包括模型加载状态、设备信息等
```

### 性能监控

- 服务启动时间统计
- 模型加载状态监控
- 分割请求处理时间记录

## 🚨 故障排除

### 常见问题

1. **模型加载失败**
   - 检查 `models/` 目录是否存在模型文件
   - 确认设备配置是否正确 (GPU 需要 CUDA 支持)
   - 查看启动日志中的错误信息

2. **端口被占用**

   ```bash
   # 查看端口占用
   lsof -i :8000  # macOS/Linux
   netstat -ano | findstr 8000  # Windows
   
   # 杀死进程
   kill -9 <PID>  # macOS/Linux
   taskkill /F /PID <PID>  # Windows
   ```

3. **依赖安装失败**

   ```bash
   # 清理缓存重新安装
   uv cache clean
   rm -rf .venv uv.lock
   uv sync
   ```

### 调试模式

```bash
# 启用详细日志
uv run python manage.py runserver --log-level debug

# 使用简单分割器 (跳过 AI 模型)
# 修改代码强制使用 SimpleTextSplitter
```

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构代码
- `test`: 添加测试
- `chore`: 构建过程或辅助工具变动

## 📄 许可证

Copyright © 2025 Flydiy. All Rights Reserved.

## 🔗 相关链接

- [ModelScope](https://modelscope.cn/) - AI 模型平台
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [uv](https://github.com/astral-sh/uv) - 依赖管理工具

---

如有问题或建议，请提交 Issue 或联系开发团队。
