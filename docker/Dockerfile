# 使用支持多架构的基础镜像
# 注意：如果私有镜像不支持多架构，请使用公共镜像或构建多架构基础镜像
FROM harbor-prod.flydiysz.cn/flydiy-base/nts-foundation-flygpt:python312-uv

ENV FLY_SERVER__PORT=20001

WORKDIR /app


# 创建目录
RUN mkdir -p ./configs
RUN mkdir -p ./logs
RUN mkdir -p ./models


# 项目代码
COPY semantic_splitter /app/semantic_splitter
COPY static /app/static
COPY manage.py /app/manage.py
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock
COPY README.md /app/README.md
COPY scripts /app/scripts


# pip install会报错：Python in docker – RuntimeError: can't start new thread
# 解决方案：pip config --user set global.progress_bar off
# 参考：https://stackoverflow.com/questions/70087344/python-in-docker-runtimeerror-cant-start-new-thread
RUN \
    pip config --user set global.progress_bar off && \
    pip install -e .[standard] && \
    rm -rf /app/uv.lock && \
    rm -rf /app/pyproject.toml && \
    rm -rf /root/.cache && \
    apt-get purge -y $(apt-cache search '~c' | awk '{ print $2 }') && \
    apt-get -y autoremove && \
    apt-get -y autoclean && \
    apt-get -y clean all && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apt && \
    rm -rf /tmp/*

# 挂载目录
VOLUME /app/configs
VOLUME /app/logs
VOLUME /app/models

# 设置启动脚本权限
RUN chmod +x /app/scripts/start.sh

# 启动命令
CMD ["/app/scripts/start.sh"]
