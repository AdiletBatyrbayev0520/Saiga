import os

MODEL_NAME = os.path.join("resources", "models", "best_4_pytorch")
OVERLAPPING_PERCENTAGE = 20
SLICE_SIZE = 640
SLICES_FOLDER = "slices"

PREDICT_FOLDER_PREFIX = "predicted_images_with_annotations"
CONFIDENCE_THRESHOLD = 0.5

OUTLIER_FILTER_FOLDER_PREFIX = "outlier_filtered"
OUTLIER_THRESHOLD_K = 3

IOU_FOLDER_PREFIX = "iou_filtered"
IOU_THRESHOLD = 0.5

EPOCHS = 150

DATASET_FOLDER = os.path.join("resources", "dataset")
# DATASET_FOLDER = "resources/dataset"