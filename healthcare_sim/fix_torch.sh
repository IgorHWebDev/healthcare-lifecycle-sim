#!/bin/bash

# Uninstall current versions
pip uninstall -y torch torchvision torchaudio transformers

# Install CUDA-enabled PyTorch
pip install torch==2.1.2 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install transformers with dependencies
pip install transformers==4.36.2 accelerate==0.25.0 safetensors==0.4.1

# Install additional dependencies
pip install sentencepiece protobuf 