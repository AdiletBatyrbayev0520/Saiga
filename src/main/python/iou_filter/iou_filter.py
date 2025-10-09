import os
from src.main.resources.config import IOU_THRESHOLD

def calculate_iou(box1, box2):
    # box = [x1, y1, x2, y2]
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    print("intersection_area", intersection_area)
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - intersection_area
    print("union_area", union_area)

    if union_area == 0:
        return 0.0

    return intersection_area / union_area

def update_coordinates(boxes_list):
    new_boxes_list = boxes_list.copy()
    for boxes in new_boxes_list:
        x_min = int(boxes['source_image_path'].split('/')[-1].split('_')[-2].split('.')[0])
        y_min = int(boxes['source_image_path'].split('/')[-1].split('_')[-1].split('.')[0])

        for box in boxes['coordinates']:
            box[0] = box[0] + x_min
            box[1] = box[1] + y_min
            box[2] = box[2] + x_min
            box[3] = box[3] + y_min

    return new_boxes_list
def verbose(all_boxes, i, j, iou):
    print(f"Боксы с IoU > {IOU_THRESHOLD}:")
    print(f"Бокс 1: {all_boxes[i]['coordinates']} (из {all_boxes[i]['source']})")
    print(f"Бокс 2: {all_boxes[j]['coordinates']} (из {all_boxes[j]['source']})")         
    print(f"IoU: {iou:.4f}")    
    print("---")

def filter_iou(boxes_list):
    new_boxes_list = update_coordinates(boxes_list)
    all_boxes = []
    for box_group in new_boxes_list:
        source_path = box_group['source_image_path']
        for coord in box_group['coordinates']:
            all_boxes.append({
                'coordinates': coord,
                'source': source_path
            })

    with_duplicates = len(all_boxes)
    print(f"Всего боксов для сравнения: {with_duplicates}")
    count = 0
    duplicates_list = []
    for i in range(len(all_boxes)):
        for j in range(i + 1, len(all_boxes)):
            iou = calculate_iou(all_boxes[i]['coordinates'], all_boxes[j]['coordinates'])
            if iou > IOU_THRESHOLD:
                if all_boxes[i]['coordinates'] not in duplicates_list:
                    duplicates_list.append(all_boxes[i]['coordinates'])
                    verbose(all_boxes, i, j, iou)
                    count += 1
                else:
                    if all_boxes[j]['coordinates'] not in duplicates_list:
                        duplicates_list.append(all_boxes[j]['coordinates'])
                        verbose(all_boxes, i, j, iou)
                        count += 1
    filtered_boxes_list = []       
    
    for boxes in new_boxes_list:
        coordinates = []
        for box in boxes['coordinates']:
            if box not in duplicates_list:
                coordinates.append(box)
        if coordinates:
            filtered_boxes_list.append({
                'source_image_path': boxes['source_image_path'],
                'coordinates': coordinates
            })


    print(f"Количество боксов с IoU > {IOU_THRESHOLD}: {count}")
    without_duplicates = len(all_boxes) - count
    print(f"Количество боксов без дубликатов: {without_duplicates}")
    return filtered_boxes_list  