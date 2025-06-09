# ./chroma_server/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala dependencias de sistema mínimas
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    protobuf-compiler \
    && apt-get clean

# Instala Chroma desde GitHub
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --upgrade git+https://github.com/chroma-core/chroma.git@main

# Directorio de datos persistente
VOLUME /chroma_data

EXPOSE 8000

CMD ["chroma", "run", "--path", "/chroma_data"]
