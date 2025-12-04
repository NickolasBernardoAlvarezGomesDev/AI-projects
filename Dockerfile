FROM python:3.11-slim

# evitar interatividade
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# dependências do sistema (opcional, mas ajuda)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copia requirements
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

# copia o projeto
COPY . /app/

EXPOSE 8000
