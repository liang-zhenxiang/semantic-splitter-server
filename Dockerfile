FROM 192.168.0.25:8888/flydiy-base/nts-foundation-flygpt:python312-uv

WORKDIR /app

ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive
ENV SEMANTIC_SPLITTER_DEVICE=cpu

# 本不该存在的一段代码
RUN pip install uv

# 拷贝项目-模型
COPY models /app/models

# 拷贝项目-代码
COPY semantic_splitter /app/semantic_splitter
COPY static /app/static
COPY scripts /app/scripts
COPY manage.py /app/
COPY pyproject.toml /app/
COPY uv.lock /app/
COPY README.md /app/


RUN \
    # 使用 uv 安装依赖
    uv sync --extra standard && \
    # 清理Python缓存和构建文件
    rm -rf /app/pyproject.toml && \
    rm -rf /root/.cache && \
    # 删除构建脚本（不再需要）
    rm -rf /app/scripts && \
    # 清理编译工具和apt缓存以减小镜像大小
    apt-get purge -y build-essential cmake && \
    apt-get purge -y $(apt-cache search '~c' | awk '{ print $2 }') && \
    apt-get -y autoremove && \
    apt-get -y autoclean && \
    apt-get -y clean all && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apt && \
    rm -rf /tmp/*

# 使用 ENTRYPOINT 和 CMD 组合，支持传递参数
ENTRYPOINT ["uv", "run", "/app/manage.py"]
CMD ["runserver", "--host", "0.0.0.0", "--port", "8000", "--device", "cpu"]
