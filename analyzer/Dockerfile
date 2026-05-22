FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir openai transformers torch
CMD ["python", "-c", "from analyzer.summarizer import Summarizer; Summarizer().run()"]
