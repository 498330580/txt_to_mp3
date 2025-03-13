FROM python:3.10-slim

WORKDIR /app

# 安装 ffmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 创建必要的目录
RUN mkdir -p /app/data/images /app/data/out_mp4

VOLUME ["/app/data/import", "/app/data/out_text", "/app/data/out_mp3", "/app/data/tmp", "/app/data/images", "/app/data/out_mp4"]

EXPOSE 7860

CMD ["python", "app.py"]