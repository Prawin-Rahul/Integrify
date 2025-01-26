FROM python:3.9-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libssl-dev \
    build-essential \
    gcc \
    && apt-get clean

RUN pip install --no-cache-dir -r requirements.txt


COPY . /app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
