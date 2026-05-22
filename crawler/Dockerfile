FROM python:3.12-slim

WORKDIR /app
ENV SCRAPY_SETTINGS_MODULE=crawler.settings
ENV PYTHONPATH=/app
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir scrapy httpx lxml simhash psycopg2-binary
CMD ["scrapy", "runspider", "crawler/spiders/eastmoney.py"]
