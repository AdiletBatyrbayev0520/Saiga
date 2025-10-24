FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    ultralytics \
    sagemaker-inference \
    flask

ENV PATH="/opt/ml/code:${PATH}"
ENV SAGEMAKER_PROGRAM=inference.py

COPY model/inference.py /opt/ml/code/
