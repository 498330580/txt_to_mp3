FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

VOLUME ["/app/data/import", "/app/data/out_text", "/app/data/out_mp3", "/app/data/tmp"]

EXPOSE 7860

CMD ["python", "app.py"]