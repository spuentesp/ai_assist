FROM mcr.microsoft.com/devcontainers/python:3.11

# Install Docker CLI and Docker Compose
RUN apt-get update && \
    apt-get install -y docker.io docker-compose && \
    apt-get clean