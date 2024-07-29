FROM python:3.11-slim-buster

ENV PYTHONUNBUFFERED True

WORKDIR /app

# Required for OpenCV.
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

# Install packages.
RUN pip install --no-cache-dir --upgrade pip
RUN python -m pip install pymongo==4.8.0

# Install packages from requirements.txt.
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt