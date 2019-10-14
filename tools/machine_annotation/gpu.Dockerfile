FROM    tensorflow/tensorflow:1.14.0-gpu-py3

# Install dependencies
WORKDIR /opt
RUN     apt update && \
        apt install -y git libsm6 libxrandr2 libxext6 && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*
# libsm6 libxrandr2 libxext6 are for cv2
RUN     pip install opencv-python distribute-config tqdm coloredlogs

WORKDIR /opt/workspace
