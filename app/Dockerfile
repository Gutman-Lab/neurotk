FROM python:3.12-slim

# Run Python in unbuffered mode.
ENV PYTHONUNBUFFERED=True

# Ignore warnings of using pip as the root user.
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

# Update package list.
RUN apt-get update

# Required for OpenCV.
RUN apt-get install ffmpeg libsm6 libxext6 -y

# NOTE: Install dependencies that take a while to install (could be removed later).
RUN pip install --no-cache-dir dsa-helpers
RUN pip install --no-cache-dir dash[celery]
RUN pip install --no-cache-dir dash-bootstrap-components
RUN pip install --no-cache-dir watchdog==4.0.1
RUN pip install --no-cache-dir dash_ag_grid
RUN pip install --no-cache-dir dash-paperdragon

# Install Python dependencies from local requirements.txt.
# COPY requirements.txt /app
# RUN pip install --no-cache-dir -r requirements.txt