FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED True

WORKDIR /app

# Install packages.
RUN pip install --no-cache-dir --upgrade pip
RUN python -m pip install pymongo==4.8.0

# Install packages from requirements.txt.
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt