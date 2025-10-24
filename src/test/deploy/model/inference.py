import json
import torch
import numpy as np
from PIL import Image
import io
import base64
import os
import sys
from ultralytics import YOLO


DEFAULT_CONFIDENCE_THRESHOLD = 0.5

def get_device():
    if torch.cuda.is_available():
        device = f'cuda:0'
        print(f"CUDA доступна: {torch.cuda.get_device_name(0)}")
    else:
        device = 'cpu'
        print(f"CUDA недоступна, используется CPU")
    return device

def model_fn(model_dir):
    model_path = None
    model_format = None
    
    for file in os.listdir(model_dir):
        if file.endswith('best_4_pytorch.pt'):
            model_path = os.path.join(model_dir, file)
            model_format = '.pt'
            break
    
    if model_path is None:
        raise FileNotFoundError(f"Файл модели не найден в {model_dir}")
    
    print(f"Загрузка модели из: {model_path}")
    model = YOLO(model_path)
    
    device = get_device()
    model.to(device)
    print(f"Модель загружена на: {device}")
    
    return model

def input_fn(request_body, request_content_type):
    if request_content_type == 'application/x-image':
        image = Image.open(io.BytesIO(request_body))
        return image
    elif request_content_type == 'application/json':
        data = json.loads(request_body)
        
        if 'image' not in data:
            raise ValueError("JSON должен содержать поле 'image'")
        
        image_bytes = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_bytes))
        
        conf_threshold = data.get('confidence_threshold', None)
        return {'image': image, 'conf_threshold': conf_threshold}
    else:
        raise ValueError(f"Неподдерживаемый тип контента: {request_content_type}")

def predict_fn(input_data, model):
    
    if isinstance(input_data, dict):
        image = input_data['image']
        conf_threshold = input_data.get('conf_threshold', DEFAULT_CONFIDENCE_THRESHOLD)
    else:
        image = input_data
        conf_threshold = DEFAULT_CONFIDENCE_THRESHOLD
    
    predictions = model.predict(image, conf=conf_threshold, device=get_device(), verbose=False)
    
    return {
        'predictions': predictions,
    }

def output_fn(prediction, response_content_type):
    if response_content_type == 'application/json':
        return json.dumps(prediction, ensure_ascii=False, indent=2)
    raise ValueError(f"Неподдерживаемый тип контента: {response_content_type}")
