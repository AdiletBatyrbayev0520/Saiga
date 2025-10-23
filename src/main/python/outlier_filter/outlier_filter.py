import numpy as np
from src.main.resources.config import OUTLIER_THRESHOLD_K


def filter_outliers(boxes_list):
    """
    Фильтрует выбросы из списка боксов на основе их площади.
    
    Args:
        boxes_list: Список словарей с ключами 'source_image_path' и 'coordinates'
        
    Returns:
        filtered_boxes_from_outliers: Отфильтрованный список боксов
    """
    filtered_boxes_from_outliers = []
    
    for boxes in boxes_list:
        areas = []
        for box in boxes['coordinates']:
            box_area = (box[2] - box[0]) * (box[3] - box[1])
            areas.append(box_area)
        
        if not areas:  # Если нет координат, пропускаем
            continue
            
        mean_of_areas = sum(areas) / len(areas)

        q1 = np.percentile(areas, 25)
        q3 = np.percentile(areas, 75)
        iqr = q3 - q1
        lower_bound = q1 - OUTLIER_THRESHOLD_K * iqr
        upper_bound = q3 + OUTLIER_THRESHOLD_K * iqr
        
        filtered_coordinates_from_outliers = []
        for box in boxes['coordinates']:
            box_area = (box[2] - box[0]) * (box[3] - box[1])
            if box_area > lower_bound and box_area < upper_bound:
                filtered_coordinates_from_outliers.append(box)
        
        print("sum of areas", sum(areas))
        print("mean of areas", mean_of_areas)
        print("lower_bound", lower_bound)
        print("upper_bound", upper_bound)
        print("iqr", iqr)
        print("amount of filtered_coordinates_from_outliers", len(filtered_coordinates_from_outliers))
        
        if len(filtered_coordinates_from_outliers) > 0:
            filtered_boxes_from_outliers.append({
                'source_image_path': boxes['source_image_path'], 
                'coordinates': filtered_coordinates_from_outliers
            })

    print("amount of filtered_boxes_from_outliers", len(filtered_boxes_from_outliers))
    return filtered_boxes_from_outliers