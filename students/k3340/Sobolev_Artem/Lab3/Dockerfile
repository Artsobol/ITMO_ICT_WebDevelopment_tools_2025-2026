FROM python:3.12-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 8111

CMD ["uvicorn", "main:mainapp", "--host", "0.0.0.0", "--port", "8111"]
