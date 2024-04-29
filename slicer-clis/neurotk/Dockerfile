FROM pytorch/pytorch:2.2.2-cuda12.1-cudnn8-runtime

ENV PYTHONUNBUFFERED=TRUE

# Make non-interactive
ARG DEBIAN_FRONTEND=noninteractive

USER root

# This tells girder_worker to enable gpu if possible
LABEL com.nvidia.volumes.needed=nvidia_driver

# Install Python packages.
RUN pip install "scikit-image<0.23"
RUN python -m pip install histomicstk --find-links https://girder.github.io/large_image_wheels
RUN python -m pip install girder-client girder-slicer-cli-web h5py

# Create a directory to work from, and copy the local files into it.
RUN mkdir /opt/scw
COPY . /opt/scw
WORKDIR /opt/scw/cli

ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]