#!/usr/bin/env python3
"""
Утилиты для визуализации изображений с боксами
"""

import os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from typing import List, Tuple, Optional


def draw_bounding_boxes_on_image(
    image_path: str, 
    boxes: List[List[float]], 
    output_path: str,
    box_color: str = "red",
    box_width: int = 3,
    label: str = "saiga",
    font_size: int = 20
) -> None:
    """
    Рисует боксы на изображении и сохраняет результат
    
    Args:
        image_path (str): Путь к исходному изображению
        boxes (List[List[float]]): Список боксов в формате [x1, y1, x2, y2]
        output_path (str): Путь для сохранения результата
        box_color (str): Цвет боксов
        box_width (int): Толщина линий боксов
        label (str): Подпись для боксов
        font_size (int): Размер шрифта для подписей
    """
    # Открываем изображение
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Пытаемся загрузить шрифт, если не получается - используем стандартный
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Рисуем каждый бокс
    for i, box in enumerate(boxes):
        x1, y1, x2, y2 = box
        
        # Рисуем прямоугольник
        draw.rectangle([x1, y1, x2, y2], outline=box_color, width=box_width)
        
        # Добавляем подпись
        text = f"{label} {i+1}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Рисуем фон для текста
        text_x = x1
        text_y = y1 - text_height - 5
        if text_y < 0:
            text_y = y1 + 5
            
        draw.rectangle([text_x, text_y, text_x + text_width, text_y + text_height], 
                      fill=box_color)
        draw.text((text_x, text_y), text, fill="white", font=font)
    
    # Сохраняем результат
    image.save(output_path)
    print(f"Изображение с боксами сохранено: {output_path}")


def create_visualization_from_filtered_boxes(
    original_images_folder: str,
    filtered_boxes_list: List[dict],
    output_folder: str,
    box_color: str = "red",
    box_width: int = 3,
    label: str = "saiga"
) -> None:
    """
    Создает визуализацию для всех изображений с отфильтрованными боксами
    
    Args:
        original_images_folder (str): Папка с оригинальными изображениями
        filtered_boxes_list (List[dict]): Список отфильтрованных боксов
        output_folder (str): Папка для сохранения результатов
        box_color (str): Цвет боксов
        box_width (int): Толщина линий боксов
        label (str): Подпись для боксов
    """
    # Создаем папку для результатов
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Обрабатываем каждое изображение
    for image_name in os.listdir(original_images_folder):
        if image_name.endswith((".JPG", ".jpg", ".JPEG", ".jpeg", ".PNG", ".png")):
            source_image_path = os.path.join(original_images_folder, image_name)
            output_image_path = os.path.join(output_folder, f"visualized_{image_name}")
            
            # Находим соответствующие боксы для этого изображения
            image_basename = os.path.splitext(image_name)[0]
            matching_boxes = []
            
            for box_group in filtered_boxes_list:
                if image_basename in box_group['source_image_path']:
                    matching_boxes.extend(box_group['coordinates'])
            
            if matching_boxes:
                print(f"Обрабатываем {image_name}: найдено {len(matching_boxes)} боксов")
                draw_bounding_boxes_on_image(
                    image_path=source_image_path,
                    boxes=matching_boxes,
                    output_path=output_image_path,
                    box_color=box_color,
                    box_width=box_width,
                    label=label
                )
            else:
                print(f"Для {image_name} не найдено боксов")


def create_single_image_visualization(
    image_path: str,
    filtered_boxes_list: List[dict],
    output_path: str,
    box_color: str = "red",
    box_width: int = 3,
    label: str = "saiga"
) -> None:
    """
    Создает визуализацию для одного изображения
    
    Args:
        image_path (str): Путь к изображению
        filtered_boxes_list (List[dict]): Список отфильтрованных боксов
        output_path (str): Путь для сохранения результата
        box_color (str): Цвет боксов
        box_width (int): Толщина линий боксов
        label (str): Подпись для боксов
    """
    image_basename = os.path.splitext(os.path.basename(image_path))[0]
    matching_boxes = []
    
    # Находим соответствующие боксы
    for box_group in filtered_boxes_list:
        if image_basename in box_group['source_image_path']:
            matching_boxes.extend(box_group['coordinates'])
    
    if matching_boxes:
        print(f"Найдено {len(matching_boxes)} боксов для {image_basename}")
        draw_bounding_boxes_on_image(
            image_path=image_path,
            boxes=matching_boxes,
            output_path=output_path,
            box_color=box_color,
            box_width=box_width,
            label=label
        )
    else:
        print(f"Для {image_basename} не найдено боксов")


def create_comparison_visualization(
    image_path: str,
    original_boxes: List[List[float]],
    filtered_boxes: List[List[float]],
    output_path: str,
    original_color: str = "blue",
    filtered_color: str = "red",
    box_width: int = 3
) -> None:
    """
    Создает сравнительную визуализацию оригинальных и отфильтрованных боксов
    
    Args:
        image_path (str): Путь к изображению
        original_boxes (List[List[float]]): Оригинальные боксы
        filtered_boxes (List[List[float]]): Отфильтрованные боксы
        output_path (str): Путь для сохранения результата
        original_color (str): Цвет для оригинальных боксов
        filtered_color (str): Цвет для отфильтрованных боксов
        box_width (int): Толщина линий боксов
    """
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Рисуем оригинальные боксы
    for box in original_boxes:
        x1, y1, x2, y2 = box
        draw.rectangle([x1, y1, x2, y2], outline=original_color, width=box_width)
    
    # Рисуем отфильтрованные боксы
    for box in filtered_boxes:
        x1, y1, x2, y2 = box
        draw.rectangle([x1, y1, x2, y2], outline=filtered_color, width=box_width)
    
    # Добавляем легенду
    legend_y = 10
    draw.rectangle([10, legend_y, 30, legend_y + 20], outline=original_color, width=box_width)
    draw.text((35, legend_y), f"Original ({len(original_boxes)})", fill=original_color)
    
    legend_y += 30
    draw.rectangle([10, legend_y, 30, legend_y + 20], outline=filtered_color, width=box_width)
    draw.text((35, legend_y), f"Filtered ({len(filtered_boxes)})", fill=filtered_color)
    
    image.save(output_path)
    print(f"Сравнительная визуализация сохранена: {output_path}")
