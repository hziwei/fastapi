FROM python:3.7.9
# 复制到镜像内
COPY . /fastapi
# 工作目录
WORKDIR /fastapi
# 启动安装脚本和依赖
RUN sh scripts/install.sh && sh scripts/system_dependency.sh
# 启动脚本
CMD sh scripts/start.sh
# 健康检查
HEALTHCHECK --interval=20m --timeout=5s --retries=6 \
CMD  sh scripts/healthcheck.sh