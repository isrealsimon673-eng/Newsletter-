FROM python:3.11-slim
WORKDIR /app
COPY agent/ ./agent/
COPY agent/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || true
ENTRYPOINT ["python", "agent/main.py"]
