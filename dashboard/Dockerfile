FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir streamlit altair pandas psycopg2-binary
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
