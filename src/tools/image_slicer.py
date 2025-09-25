import os
import sys
import argparse
from PIL import Image
import math
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def create_image_slices(image_path, overlap_percentage, destination_folder, slice_size=512):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    if not 0 <= overlap_percentage < 100:
        raise ValueError("Overlap percentage must be between 0 and 99")
    
    os.makedirs(destination_folder, exist_ok=True)
    image_name = os.path.basename(image_path)
    destination_folder = os.path.join(destination_folder, f"{image_name}")
    destination_folder = os.path.splitext(destination_folder)[0]
    os.makedirs(destination_folder, exist_ok=True)

    try:
        image = Image.open(image_path)
        logger.info(f"Loaded image: {image_path}")
        logger.info(f"Image size: {image.size[0]} x {image.size[1]} pixels")
    except Exception as e:
        raise ValueError(f"Could not open image: {e}")
    
    overlap_pixels = int(slice_size * overlap_percentage / 100)
    step_size = slice_size - overlap_pixels
    
    logger.info(f"slice size: {slice_size}x{slice_size} pixels")
    logger.info(f"Overlap: {overlap_percentage}% ({overlap_pixels} pixels)")
    logger.info(f"Step size: {step_size} pixels")
    
    img_width, img_height = image.size
    
    slices_x = math.ceil((img_width - overlap_pixels) / step_size)
    slices_y = math.ceil((img_height - overlap_pixels) / step_size)
    
    logger.info(f"Will create {slices_x} x {slices_y} = {slices_x * slices_y} slices")
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    slice_count = 0

    for row in range(slices_y):
        for col in range(slices_x):
            left = col * step_size
            top = row * step_size
            right = min(left + slice_size, img_width)
            bottom = min(top + slice_size, img_height)
            
            if (right - left) < slice_size // 2 or (bottom - top) < slice_size // 2:
                continue
            
            slice = image.crop((left, top, right, bottom))
            
            slice_filename = f"{base_name}_slice_{row:03d}_{col:03d}_{left}_{top}.png"
            slice_path = os.path.join(destination_folder, slice_filename)
            
            slice.save(slice_path)
            slice_count += 1
            
            if slice_count % 50 == 0:
                logger.info(f"Processed {slice_count} slices...")
    
    logger.info(f"Successfully created {slice_count} slices in '{destination_folder}'")
    return slice_count


def main():
    parser = argparse.ArgumentParser(
        description="Slice high-resolution images into overlapping slices",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python image_slicer.py image.jpg 20 ./slices/
    python image_slicer.py satellite.tif 15 ./output/ 1024
        """
    )
    
    parser.add_argument("--image_path", help="Path to the input image")
    parser.add_argument("--overlap_percentage", type=float, 
                       help="Overlap percentage between slices (0-99)")
    parser.add_argument("--destination_folder", 
                       help="Directory to save the sliced images")
    parser.add_argument("--slice-size", type=int, default=512,
                       help="Size of each slice in pixels (default: 512)")
    
    args = parser.parse_args()
    
    try:
        create_image_slices(
            args.image_path, 
            args.overlap_percentage, 
            args.destination_folder,
            args.slice_size
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()