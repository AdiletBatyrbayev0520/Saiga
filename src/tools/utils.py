import torch
from ultralytics import YOLO
import os
import time

def copyfile(source_path, destination_path):
    with open(source_path, 'rb') as src, open(destination_path, 'wb') as dst:
        dst.write(src.read())

def get_destination_folder(list_of_prefixes):
    destination_folder = "-".join(map(str, list_of_prefixes))
    return destination_folder

def create_destination_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

def get_slice_coordinates(filename):
    x_min = int(filename.split('/')[-1].split('_')[-2].split('.')[0])
    y_min = int(filename.split('/')[-1].split('_')[-1].split('.')[0])
    return x_min, y_min


    