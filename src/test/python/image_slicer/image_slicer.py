import os
import sys
import argparse
from PIL import Image
import math
from resources.config import OVERLAPPING_PERCENTAGE, SLICES_FOLDER, SLICE_SIZE, DATASET_FOLDER
# Разрешаем загрузку поврежденных изображений
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
def create_image_slices(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if not image_path.lower().endswith(".jpg") and not image_path.lower().endswith(".jpeg") and not image_path.lower().endswith(".png"):
        print(f"Skipping invalid image: {image_path}")
        return 0

    if not 0 <= OVERLAPPING_PERCENTAGE < 100:
        raise ValueError("Overlap percentage must be between 0 and 99")
    destination_folder = SLICES_FOLDER
    os.makedirs(destination_folder, exist_ok=True)
    image_name = os.path.basename(image_path)
    destination_folder = os.path.join(destination_folder, f"{image_name}")
    destination_folder = os.path.splitext(destination_folder)[0]
    os.makedirs(destination_folder, exist_ok=True)

    try:
        if os.path.getsize(image_path) == 0:
            raise ValueError(f"File is empty: {image_path}")
        
        image = Image.open(image_path)
        image.verify()
        image = Image.open(image_path)
        image.load()

        print(f"Loaded image: {image_path}")
        print(f"Image size: {image.size[0]} x {image.size[1]} pixels")
    except Exception as e:
        raise ValueError(f"Could not open image: {e}")

    overlap_pixels = int(SLICE_SIZE * OVERLAPPING_PERCENTAGE / 100)
    step_size = SLICE_SIZE - overlap_pixels

    print(f"slice size: {SLICE_SIZE}x{SLICE_SIZE} pixels")
    print(f"Overlap: {OVERLAPPING_PERCENTAGE}% ({overlap_pixels} pixels)")
    print(f"Step size: {step_size} pixels")
    
    img_width, img_height = image.size
    
    slices_x = math.ceil((img_width - overlap_pixels) / step_size)
    slices_y = math.ceil((img_height - overlap_pixels) / step_size)
    
    print(f"Will create {slices_x} x {slices_y} = {slices_x * slices_y} slices")
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    slice_count = 0

    for row in range(slices_y):
        for col in range(slices_x):
            left = col * step_size
            top = row * step_size
            right = left + SLICE_SIZE
            bottom = top + SLICE_SIZE
            if left + SLICE_SIZE > img_width:
                left = img_width - SLICE_SIZE
                right = img_width
            if top + SLICE_SIZE > img_height:
                top = img_height - SLICE_SIZE
                bottom = img_height


            if (right - left) < SLICE_SIZE // 2 or (bottom - top) < SLICE_SIZE // 2:
                print("!!!!!! Error bro: right-left < SLICE_SIZE // 2 or bottom-top < SLICE_SIZE // 2")
                break
            
            slice = image.crop((left, top, right, bottom))
            
            slice_filename = f"{base_name}_slice_{row:03d}_{col:03d}_{left}_{top}.png"
            slice_path = os.path.join(destination_folder, slice_filename)
            
            slice.save(slice_path)
            slice_count += 1
            
            if slice_count % 50 == 0:
                print(f"Processed {slice_count} slices...")
    
    print(f"Successfully created {slice_count} slices in '{destination_folder}'")
    return slice_count

    
def create_images_slices_parallel(workers=1):
    from multiprocessing import Pool, cpu_count
    from tqdm import tqdm 

    image_paths = [f"{DATASET_FOLDER}/{image_path}" for image_path in os.listdir(DATASET_FOLDER) 
                   if image_path.lower().endswith((".jpg", ".jpeg", ".png"))]
    if workers == -1:
        workers = max(1, cpu_count() - 1)
    print(f"Processing {len(image_paths)} images using {workers} processes")

    with Pool(processes=workers) as pool:
        results = list(tqdm(
            pool.imap(create_image_slices, image_paths),
            total=len(image_paths),
            desc="Processing images"
        ))

    total_slices = sum(results)
    successful_images = len(results)  # All completed images
    print(f"\nCompleted: {successful_images} images, {total_slices} total slices")

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
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()