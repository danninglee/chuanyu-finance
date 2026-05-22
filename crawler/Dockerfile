FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir scrapy httpx lxml simhash psycopg2-binary
CMD ["scrapy", "runspider", "spiders/eastmoney.py"]
