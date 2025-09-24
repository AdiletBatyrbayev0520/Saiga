import os
import sys
import argparse
from PIL import Image
import math


def create_image_slices(image_path, overlap_percentage, destination_folder, tile_size=512):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    if not 0 <= overlap_percentage < 100:
        raise ValueError("Overlap percentage must be between 0 and 99")
    
    os.makedirs(destination_folder, exist_ok=True)
    
    try:
        image = Image.open(image_path)
        print(f"Loaded image: {image_path}")
        print(f"Image size: {image.size[0]} x {image.size[1]} pixels")
    except Exception as e:
        raise ValueError(f"Could not open image: {e}")
    
    overlap_pixels = int(tile_size * overlap_percentage / 100)
    step_size = tile_size - overlap_pixels
    
    print(f"Tile size: {tile_size}x{tile_size} pixels")
    print(f"Overlap: {overlap_percentage}% ({overlap_pixels} pixels)")
    print(f"Step size: {step_size} pixels")
    
    img_width, img_height = image.size
    
    tiles_x = math.ceil((img_width - overlap_pixels) / step_size)
    tiles_y = math.ceil((img_height - overlap_pixels) / step_size)
    
    print(f"Will create {tiles_x} x {tiles_y} = {tiles_x * tiles_y} tiles")
    
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    tile_count = 0

    for row in range(tiles_y):
        for col in range(tiles_x):
            left = col * step_size
            top = row * step_size
            right = min(left + tile_size, img_width)
            bottom = min(top + tile_size, img_height)
            
            if (right - left) < tile_size // 2 or (bottom - top) < tile_size // 2:
                continue
            
            tile = image.crop((left, top, right, bottom))
            
            tile_filename = f"{base_name}_tile_{row:03d}_{col:03d}.png"
            tile_path = os.path.join(destination_folder, tile_filename)
            
            tile.save(tile_path)
            tile_count += 1
            
            if tile_count % 50 == 0:
                print(f"Processed {tile_count} tiles...")
    
    print(f"Successfully created {tile_count} tiles in '{destination_folder}'")
    return tile_count


def main():
    parser = argparse.ArgumentParser(
        description="Slice high-resolution images into overlapping tiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python image_slicer.py image.jpg 20 ./tiles/
    python image_slicer.py satellite.tif 15 ./output/ 1024
        """
    )
    
    parser.add_argument("--image_path", help="Path to the input image")
    parser.add_argument("--overlap_percentage", type=float, 
                       help="Overlap percentage between tiles (0-99)")
    parser.add_argument("--destination_folder", 
                       help="Directory to save the sliced images")
    parser.add_argument("--tile-size", type=int, default=512,
                       help="Size of each tile in pixels (default: 512)")
    
    args = parser.parse_args()
    
    try:
        create_image_slices(
            args.image_path, 
            args.overlap_percentage, 
            args.destination_folder,
            args.tile_size
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()