import torch
from ultralytics import YOLO
import os
import time
from python.utils.utils import copyfile
import sys
if 'src.config' in sys.modules:
    del sys.modules['src.config']
from resources.config import CONFIDENCE_THRESHOLD, SLICE_SIZE, SLICES_FOLDER
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

def get_models(model_name, devices, model_format=".pt"):
    models = []
    for device in devices:
        models.append(YOLO(f'{model_name}{model_format}'))
        models[-1].to(device)
        print(f"Модель загружена на: {device}")
    return models

def create_classes_file(output_folder):
    with open(f"{output_folder}/classes.txt", "w") as f:
        f.write("saiga\n")

def create_annotation_file(image_path, boxes, classes_folder, image_size=(SLICE_SIZE, SLICE_SIZE)):
    if not os.path.exists(f"{classes_folder}/classes.txt"):
        create_classes_file(classes_folder)
    filename = os.path.splitext(os.path.basename(image_path))[0]
    annotation_path = os.path.join(classes_folder, f"{filename}.txt")
    with open(annotation_path, "w") as f:  # "w" вместо "a"
        for box in boxes:
            x_center = (box[0] + box[2]) / 2 / image_size[0]
            y_center = (box[1] + box[3]) / 2 / image_size[1]
            width = (box[2] - box[0]) / image_size[0]
            height = (box[3] - box[1]) / image_size[1]
            f.write(f"0 {x_center} {y_center} {width} {height}\n")
    # print(f"Аннотации сохранены в {output_folder}/{filename}.txt")
def create_annotation_folder(folder_path, boxes, output_folder, image_size):
    images_list = os.listdir(folder_path)
    for image_path in images_list:
        if image_path.endswith(".png"):
            full_image_path = os.path.join(folder_path, image_path)
            create_annotation_file(full_image_path, boxes, output_folder, image_size)
        
def read_annotation_file(annotation_path, image_size):
    coordinates = []  
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
                    coordinates.append([left, top, right, bottom])
    source_image_path = os.path.splitext(annotation_path)[0] + '.png'
    if not len(coordinates) == 0:
        boxes_data = {'source_image_path': source_image_path, 'coordinates': coordinates}
        return boxes_data
    return None

def read_annotation_folder(folder_path, image_size=SLICE_SIZE):
    boxes_list = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt") and not filename.startswith("classes"):
            annotation_path = os.path.join(folder_path, filename)
            boxes_data = read_annotation_file(annotation_path, image_size)
            if boxes_data:  
                boxes_list.append(boxes_data)
        subfolder_path = os.path.join(folder_path, filename)
        if os.path.isdir(subfolder_path):
            boxes_list.extend(read_annotation_folder(subfolder_path, image_size))
    return boxes_list

def process_folder(folder_path, model, device, output_folder):
    predictions = model.predict(folder_path, conf=CONFIDENCE_THRESHOLD, device=device, verbose=False)
    total_detections = sum(len(prediction.boxes.conf) for prediction in predictions)
    destination_folder_path = os.path.join(output_folder, os.path.basename(folder_path))
    boxes_list = []
    if total_detections > 0:
        for prediction in predictions:
            if len(prediction.boxes.conf) > 0:
                if not os.path.exists(destination_folder_path):
                    os.makedirs(destination_folder_path)
                image_filename = os.path.basename(prediction.path)
                destination_image_path = os.path.join(destination_folder_path, image_filename)
                source_image_path = os.path.join(folder_path, image_filename)
                boxes_data = {'source_image_path': source_image_path, 'coordinates': prediction.boxes.xyxy.tolist()}
                boxes_list.append(boxes_data)
                copyfile(source_image_path, destination_image_path)
                create_annotation_file(
                    image_path=destination_image_path,
                    boxes=prediction.boxes.xyxy.tolist(),
                    classes_folder=destination_folder_path,
                    image_size=(SLICE_SIZE, SLICE_SIZE)
                )
    return total_detections, boxes_list

# def worker_function(args):
#     """Wrapper function for multiprocessing"""
#     folder_path, model, device, output_folder = args
#     return process_folder(folder_path, model, device, output_folder)

# def process_folders_parallel(models, devices, output_folder):
#     start_time = time.time()
#     total_detections = 0
#     folders_list = os.listdir(SLICES_FOLDER)
    
#     tasks = []
#     num_workers = len(models)
    
#     for i, folder in enumerate(folders_list):
#         model_idx = i % len(models)
#         device_idx = (i // len(models)) % len(devices)
#         tasks.append((f"{SLICES_FOLDER}/{folder}", models[model_idx], devices[device_idx], output_folder))
#     print(f"Обработка {len(tasks)} папок с детекциями используя {num_workers} процессов")
#     with Pool(processes=num_workers) as pool:
#         results = list(tqdm(
#             pool.imap(worker_function, tasks),
#             total=len(tasks),
#             desc="Processing folders"
#         ))
    
#     total_detections = sum(results)
#     processed_count = len([r for r in results if r > 0])
    
#     end_time = time.time()
#     print(f"\nГотово! Обработано {processed_count} папок с детекциями")
#     print(f"Общее количество детекций: {total_detections}")
#     print(f"Время обработки: {end_time - start_time:.2f} секунд")
#     return total_detections

def process_folders(model, device, output_folder, slices_folder=SLICES_FOLDER):
    print(f"Обработка изображений на устройстве: {device}\nПапка вывода: {output_folder}")
    start_time = time.time()
    processed_count = 0
    total_detections = 0
    for folder in os.listdir(slices_folder):
        folder_path = os.path.join(slices_folder, folder)
        if os.path.isdir(folder_path):
            detections, boxes_list = process_folder(folder_path, model, device, output_folder)
            if detections > 0:
                processed_count += 1
                total_detections += detections

    end_time = time.time()
    print(f"\nГотово! Обработано {processed_count} изображений с детекциями")
    print(f"Общее количество детекций: {total_detections}")
    print(f"Время обработки: {end_time - start_time:.2f} секунд")
    print(f"Устройство: {device}")
    return total_detections