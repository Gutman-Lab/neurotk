FROM python:3.11-slim-buster

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app

# set working directory in container
WORKDIR /app

# Copy and install packages
COPY requirements.txt /app

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt 
RUN pip install --no-cache-dir "uvicorn[standard]" gunicorn 
RUN pip install -U "celery[redis,librabbitmq]"

# Run locally
# CMD gunicorn --bind 0.0.0.0:8050 app:server
