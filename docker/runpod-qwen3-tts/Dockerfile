# Qwen3-TTS RunPod Serverless Worker (models downloaded at startup)
# Generates speech from text with voice cloning and emotion control
#
# Build (from repo root):
#   docker buildx build --platform linux/amd64 -t ghcr.io/rubensfq/video-toolkit-qwen3-tts:latest --push docker/runpod-qwen3-tts/
#
# Image size: ~8GB (model weights downloaded to /runpod-volume on first cold start, ~2min)
# Cold start: ~2min on first start (model download), ~30s on warm starts
#
# Test locally:
#   docker run --gpus all -p 8000:8000 ghcr.io/rubensfq/video-toolkit-qwen3-tts:latest

FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# Install ffmpeg for WAV→MP3 conversion
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

# Install torchaudio (matching PyTorch 2.4.0 from base image)
RUN pip install --no-cache-dir torchaudio==2.4.0

# Install qwen-tts and dependencies
RUN pip install --no-cache-dir \
    qwen-tts \
    soundfile \
    runpod \
    boto3 \
    requests

WORKDIR /app

# Models are downloaded at container startup into /runpod-volume (persisted across
# warm starts on the same worker). Set HF_HOME to that path so huggingface_hub
# and from_pretrained() both use the same cache location.
ENV HF_HOME=/runpod-volume/huggingface
ENV PYTHONUNBUFFERED=1

# Copy handler
COPY handler.py /app/handler.py

# Start handler
CMD ["python", "-u", "/app/handler.py"]
