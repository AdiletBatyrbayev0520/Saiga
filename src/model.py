import torch
from ultralytics import YOLO
import os
import time
from src.tools.utils import copyfile 
import sys
if 'src.config' in sys.modules:
    del sys.modules['src.config']
from src.config import CONFIDENCE_THRESHOLD, SLICE_SIZE, SLICES_FOLDER

def get_devices():
    devices = []
    print(f"CUDA доступна: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Название GPU: {torch.cuda.get_device_name(0)}")
        print(f"Количество GPU: {torch.cuda.device_count()}")
        print(f"Текущий GPU device: {torch.cuda.current_device()}")
        for i in range(torch.cuda.device_count()):
            devices.append(f'cuda:{i}')
        print(f"Доступные устройства: {devices}")
    else:
        print("CUDA недоступна, используется CPU")
        devices.append('cpu')
    return devices

def get_models(model_name, devices):
    models = []
    for device in devices:
        models.append(YOLO(f'{model_name}.pt'))
        models[-1].to(device)
        print(f"Модель загружена на: {device}")
    return models

def create_classes_file(output_folder):
    with open(f"{output_folder}/classes.txt", "w") as f:
        f.write("saiga\n")

def create_annotation_file(image_path, boxes, output_folder, image_size):
    if not os.path.exists(f"{output_folder}/classes.txt"):
        create_classes_file(output_folder)
    filename = image_path.split('/')[-1].split('.')[0]
    with open(f"{output_folder}/{filename}.txt", "w") as f:  # "w" вместо "a"
        for box in boxes:
            x_center = (box[0] + box[2]) / 2 / image_size
            y_center = (box[1] + box[3]) / 2 / image_size
            width = (box[2] - box[0]) / image_size
            height = (box[3] - box[1]) / image_size
            f.write(f"0 {x_center} {y_center} {width} {height}\n")
    # print(f"Аннотации сохранены в {output_folder}/{filename}.txt")

def read_annotation_file(annotation_path, image_size):
    boxes = []
    if os.path.exists(annotation_path):
        with open(annotation_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    x_center = float(parts[1]) * image_size
                    y_center = float(parts[2]) * image_size
                    width = float(parts[3]) * image_size
                    height = float(parts[4]) * image_size
                    left = x_center - width / 2
                    top = y_center - height / 2
                    right = x_center + width / 2
                    bottom = y_center + height / 2
                    boxes.append((left, top, right, bottom))
    return boxes

def process_images(model, output_folder, device):
    print(f"Обработка изображений на устройстве: {device}\nпПапка вывода: {output_folder}")
    start_time = time.time()
    processed_count = 0
    total_detections = 0
    boxes_list = []
    for folder in os.listdir(SLICES_FOLDER):
        folder_path = f"{SLICES_FOLDER}/{folder}"
        if os.path.isdir(folder_path):
            for image_path in os.listdir(folder_path):
                full_image_path = f"{folder_path}/{image_path}"
                predictions = model.predict(full_image_path, conf=CONFIDENCE_THRESHOLD, device=device, verbose=False)
                
                if len(predictions[0].boxes.conf) > 0:
                    boxes_data = {'source_image_path': full_image_path, 'coordinates': predictions[0].boxes.xyxy.tolist()}
                    boxes_list.append(boxes_data)
                    if not os.path.exists(f"{output_folder}/{folder}"):
                        os.makedirs(f"{output_folder}/{folder}")
                    final_image_path = f"{output_folder}/{folder}/{image_path}"
                    copyfile(full_image_path, final_image_path)
                    predictions[0].save(final_image_path)
                    create_annotation_file(
                        image_path=full_image_path, 
                        boxes=predictions[0].boxes.xyxy.tolist(), 
                        output_folder=f"{output_folder}/{folder}", 
                        image_size=SLICE_SIZE
                    )
                    processed_count += 1
                    total_detections += len(predictions[0].boxes.conf)
                    if processed_count % 10 == 0:  
                        print(f"Обработано: {processed_count} изображений с детекциями")

    end_time = time.time()
    print(f"\nГотово! Обработано {processed_count} изображений с детекциями")
    print(f"Общее количество детекций: {total_detections}")
    print(f"Время обработки: {end_time - start_time:.2f} секунд")
    print(f"Устройство: {device}")
    return boxes_list