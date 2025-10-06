import torch
from ultralytics import YOLO
import os
import time
from src.tools.utils import copyfile, copyfolder
import sys
if 'src.config' in sys.modules:
    del sys.modules['src.config']
from src.config import CONFIDENCE_THRESHOLD, SLICE_SIZE, SLICES_FOLDER
from multiprocessing import Pool, cpu_count
from tqdm import tqdm 

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
def create_annotation_folder(folder_path, boxes, output_folder, image_size):
    images_path = os.listdir(folder_path)
    for image_path in images_path:
        full_image_path = f"{folder_path}/{image_path}"
        create_annotation_file(full_image_path, boxes, output_folder, image_size)
        
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

def process_folder(folder_path, model, device, output_folder):
    predictions = model.predict(folder_path, conf=CONFIDENCE_THRESHOLD, device=device, verbose=False)
    total_detections = sum(len(prediction.boxes.conf) for prediction in predictions)
    final_folder_path = f"{output_folder}/{folder_path.split('/')[-1]}"
    if total_detections > 0:
        for prediction in predictions:
            if len(prediction.boxes.conf) > 0:
                if not os.path.exists(final_folder_path):
                    os.makedirs(final_folder_path)
                final_image_path = f"{final_folder_path}/{prediction.path.split('\\')[-1]}"
                source_image_path = f"{folder_path}/{prediction.path.split('\\')[-1]}"
                copyfile(source_image_path, final_image_path)
                create_annotation_file(
                    image_path=final_image_path,
                    boxes=prediction.boxes.xyxy.tolist(),
                    output_folder=final_folder_path,
                    image_size=SLICE_SIZE
                )
    return total_detections

def worker_function(args):
    """Wrapper function for multiprocessing"""
    folder_path, model, device, output_folder = args
    return process_folder(folder_path, model, device, output_folder)

def process_folders_parallel(models, devices, output_folder):
    start_time = time.time()
    total_detections = 0
    folders_list = os.listdir(SLICES_FOLDER)
    
    tasks = []
    num_workers = len(models)
    
    for i, folder in enumerate(folders_list):
        model_idx = i % len(models)
        device_idx = (i // len(models)) % len(devices)
        tasks.append((f"{SLICES_FOLDER}/{folder}", models[model_idx], devices[device_idx], output_folder))
    print(f"Обработка {len(tasks)} папок с детекциями используя {num_workers} процессов")
    with Pool(processes=num_workers) as pool:
        results = list(tqdm(
            pool.imap(worker_function, tasks),
            total=len(tasks),
            desc="Processing folders"
        ))
    
    total_detections = sum(results)
    processed_count = len([r for r in results if r > 0])
    
    end_time = time.time()
    print(f"\nГотово! Обработано {processed_count} папок с детекциями")
    print(f"Общее количество детекций: {total_detections}")
    print(f"Время обработки: {end_time - start_time:.2f} секунд")
    return total_detections

def process_folders(model, device, output_folder):
    print(f"Обработка изображений на устройстве: {device}\nпПапка вывода: {output_folder}")
    start_time = time.time()
    processed_count = 0
    total_detections = 0
    for folder in os.listdir(SLICES_FOLDER):
        folder_path = f"{SLICES_FOLDER}/{folder}"
        if os.path.isdir(folder_path):
            total_detections += process_folder(folder_path, model, device, output_folder)
    end_time = time.time()
    print(f"\nГотово! Обработано {processed_count} изображений с детекциями")
    print(f"Общее количество детекций: {total_detections}")
    print(f"Время обработки: {end_time - start_time:.2f} секунд")
    print(f"Устройство: {device}")
    return total_detections