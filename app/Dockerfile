FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED True

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

# Install packages from requirements.txt.
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt