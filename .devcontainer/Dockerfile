FROM mcr.microsoft.com/devcontainers/python:3.11

# Opcional: evitar errores PEP 668
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Instalar dependencias
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt