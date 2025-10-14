FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN sed -i 's|http://deb.debian.org|https://mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libglx-mesa0 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 配置pip使用腾讯云镜像源
RUN pip config set global.index-url https://mirrors.cloud.tencent.com/pypi/simple && \
    pip config set install.trusted-host mirrors.cloud.tencent.com

WORKDIR /app

COPY requirements.txt requirements-app.txt ./

RUN pip install --no-cache-dir -r requirements.txt -r requirements-app.txt

COPY . .

EXPOSE 7860
EXPOSE 8080

CMD ["python3", "-u", "app.py", "--host", "0.0.0.0", "--port", "7860"]