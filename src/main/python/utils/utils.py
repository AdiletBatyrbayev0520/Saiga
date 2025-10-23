import torch
from ultralytics import YOLO
import os
import time

def copyfile(source_path, destination_path):
    with open(source_path, 'rb') as src, open(destination_path, 'wb') as dst:
        dst.write(src.read())
        
def copyfolder(source_folder, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    for item in os.listdir(source_folder):
        src_path = os.path.join(source_folder, item)
        dst_path = os.path.join(destination_folder, item)
        if os.path.isdir(src_path):
            copyfolder(src_path, dst_path)
        else:
            copyfile(src_path, dst_path)

def get_destination_folder(list_of_prefixes):
    destination_folder = "-".join(map(str, list_of_prefixes))
    return destination_folder

def create_destination_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def get_slice_coordinates(filename):
    # Используем os.path.basename для кроссплатформенной работы
    basename = os.path.basename(filename)
    x_min = int(basename.split('_')[-2].split('.')[0])
    y_min = int(basename.split('_')[-1].split('.')[0])
    return x_min, y_min


    