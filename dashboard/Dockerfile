FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --no-cache-dir streamlit altair pandas psycopg2-binary pydantic-settings
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py", "--server.address=0.0.0.0"]
