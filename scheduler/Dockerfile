FROM python:3.12-slim

WORKDIR /app
ENV SCRAPY_SETTINGS_MODULE=crawler.settings
ENV PYTHONPATH=/app
RUN pip install --no-cache-dir apscheduler psycopg2-binary scrapy httpx lxml simhash openai transformers torch
CMD ["python", "tasks.py"]
