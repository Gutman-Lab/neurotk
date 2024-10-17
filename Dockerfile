FROM python:3.12-slim

ENV PYTHONUNBUFFERED=TRUE

# Make non-interactive.
ARG DEBIAN_FRONTEND=noninteractive

USER root

# Update package list.
RUN apt-get update

# Install dependencies for using OpenCV.
RUN apt-get install ffmpeg libsm6 libxext6 -y

# This tells girder_worker to enable gpu if possible.
LABEL com.nvidia.volumes.needed=nvidia_driver

# Install required minimum Python packages required for all CLI.
RUN python -m pip install histomicstk --find-links https://girder.github.io/large_image_wheels
RUN python -m pip install girder-client girder-slicer-cli-web h5py

# Copy the requirements file and install the required packages.
RUN mkdir /opt/scw
WORKDIR /opt/scw
COPY requirements.txt /opt/scw/requirements.txt
RUN pip install -r requirements.txt

# Create a directory to work from, and copy the local files into it.
COPY ./cli /opt/scw/cli
WORKDIR /opt/scw/cli

ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]