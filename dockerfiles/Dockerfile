# Base image
FROM dockerdex.umcn.nl:5005/diag/base-images:base-pt2.1

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



# Set working directory for nnUNet
WORKDIR /nnUNet

# Copy nnUNet source code into the image
COPY . /nnUNet
COPY models /models

# Install nnUNet in editable mode
RUN pip install --no-cache-dir -e .

# Replicate docker-compose environment variables
ENV nnUNet_raw=/path/to/raw \
    nnUNet_preprocessed=/path/to/preprocessed \
    nnUNet_results=/path/to/results

# Expose port 5000
EXPOSE 5000