# Base image
FROM dockerdex.umcn.nl:5005/diag/base-images:pathology-pt2.7.1 

# Set working directory
WORKDIR /resources

# Install system dependencies and Python packages
RUN apt-get update && apt-get install --yes \
    gcc \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    python3-dev \
    libopenslide-dev \
    openslide-tools \
    tmux \
    wget \
    vim && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --upgrade git+https://github.com/DIAGNijmegen/pathology-whole-slide-data@main
# Use blosc2<=3.8.0 because from 3.9.0 the package requires numpy>2.0
RUN pip3 install --no-cache-dir "blosc2<=3.8.0"

# Set working directory for nnUNet
WORKDIR /nnUNet

# Copy nnUNet source code into the image
COPY . /nnUNet

# Install nnUNet in editable mode
RUN pip3 install --no-cache-dir -e .

# Replicate docker-compose environment variables
ENV nnUNet_raw=/tmp \
    nnUNet_preprocessed=/tmp \
    nnUNet_results=/tmp

# Expose port 5000
EXPOSE 5000
