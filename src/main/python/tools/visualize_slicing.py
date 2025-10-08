#!/usr/bin/env python3
"""
Image Slicing Visualization Tool
Visualizes the process of dividing images into overlapping tiles.

Usage:
    python visualize_slicing.py <image_path> <overlap_percentage> [tile_size]
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import math
from matplotlib.colors import to_rgba


def visualize_image_slicing(image_path, overlap_percentage, tile_size=512, show_tiles_count=6):
    """
    Visualize the image slicing process with overlapping tiles.
    
    Args:
        image_path (str): Path to the input image
        overlap_percentage (float): Percentage of overlap (0-99)
        tile_size (int): Size of each tile in pixels
        show_tiles_count (int): Number of sample tiles to display
    """
    
    # Validate inputs
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    if not 0 <= overlap_percentage < 100:
        raise ValueError("Overlap percentage must be between 0 and 99")
    
    # Load image
    try:
        image = Image.open(image_path)
        img_array = np.array(image)
        print(f"Loaded image: {image_path}")
        print(f"Image size: {image.size[0]} x {image.size[1]} pixels")
    except Exception as e:
        raise ValueError(f"Could not open image: {e}")
    
    # Calculate parameters
    overlap_pixels = int(tile_size * overlap_percentage / 100)
    step_size = tile_size - overlap_pixels
    img_width, img_height = image.size
    
    # Calculate number of tiles
    tiles_x = math.ceil((img_width - overlap_pixels) / step_size)
    tiles_y = math.ceil((img_height - overlap_pixels) / step_size)
    
    print(f"Tile size: {tile_size}x{tile_size} pixels")
    print(f"Overlap: {overlap_percentage}% ({overlap_pixels} pixels)")
    print(f"Step size: {step_size} pixels")
    print(f"Grid: {tiles_x} x {tiles_y} = {tiles_x * tiles_y} tiles")
    
    # Create visualization
    fig = plt.figure(figsize=(20, 12))
    
    # 1. Original image with grid overlay
    ax1 = plt.subplot(2, 3, 1)
    ax1.imshow(img_array)
    ax1.set_title(f'Original Image\n{img_width} x {img_height} pixels', fontsize=12)
    
    # Draw grid lines
    for col in range(tiles_x + 1):
        x = col * step_size
        if x <= img_width:
            ax1.axvline(x=x, color='red', linestyle='-', alpha=0.7, linewidth=1)
    
    for row in range(tiles_y + 1):
        y = row * step_size
        if y <= img_height:
            ax1.axhline(y=y, color='red', linestyle='-', alpha=0.7, linewidth=1)
    
    ax1.set_xlim(0, img_width)
    ax1.set_ylim(img_height, 0)
    
    # 2. Overlap visualization
    ax2 = plt.subplot(2, 3, 2)
    ax2.imshow(img_array, alpha=0.3)
    ax2.set_title(f'Overlap Visualization\n{overlap_percentage}% overlap ({overlap_pixels}px)', fontsize=12)
    
    # Color different overlapping regions
    colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
    
    for row in range(min(tiles_y, 4)):  # Show first few rows
        for col in range(min(tiles_x, 6)):  # Show first few columns
            left = col * step_size
            top = row * step_size
            right = min(left + tile_size, img_width)
            bottom = min(top + tile_size, img_height)
            
            color = colors[(row + col) % len(colors)]
            alpha = 0.3 if (row + col) % 2 == 0 else 0.2
            
            rect = patches.Rectangle(
                (left, top), right - left, bottom - top,
                linewidth=2, edgecolor=color, facecolor=color, alpha=alpha
            )
            ax2.add_patch(rect)
    
    ax2.set_xlim(0, img_width)
    ax2.set_ylim(img_height, 0)
    
    # 3. Step size visualization
    ax3 = plt.subplot(2, 3, 3)
    
    # Create a simplified diagram
    demo_width = 8
    demo_height = 6
    demo_step = 1.5
    demo_tile = 2
    
    ax3.set_xlim(0, demo_width)
    ax3.set_ylim(0, demo_height)
    ax3.set_aspect('equal')
    
    # Draw tiles
    for i in range(4):
        for j in range(3):
            x = i * demo_step
            y = j * demo_step
            if x + demo_tile <= demo_width and y + demo_tile <= demo_height:
                rect = patches.Rectangle(
                    (x, y), demo_tile, demo_tile,
                    linewidth=2, edgecolor='blue', facecolor='lightblue', alpha=0.5
                )
                ax3.add_patch(rect)
                
                # Add tile number
                ax3.text(x + demo_tile/2, y + demo_tile/2, f'{j*4+i}', 
                        ha='center', va='center', fontweight='bold')
    
    # Add dimensions
    ax3.annotate('', xy=(0, -0.3), xytext=(demo_tile, -0.3),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax3.text(demo_tile/2, -0.5, f'Tile size\n({tile_size}px)', ha='center', color='red')
    
    ax3.annotate('', xy=(0, -0.8), xytext=(demo_step, -0.8),
                arrowprops=dict(arrowstyle='<->', color='green', lw=2))
    ax3.text(demo_step/2, -1.0, f'Step size\n({step_size}px)', ha='center', color='green')
    
    overlap_demo = demo_tile - demo_step
    ax3.annotate('', xy=(demo_step, demo_tile + 0.1), xytext=(demo_tile, demo_tile + 0.1),
                arrowprops=dict(arrowstyle='<->', color='purple', lw=2))
    ax3.text((demo_step + demo_tile)/2, demo_tile + 0.3, f'Overlap\n({overlap_pixels}px)', 
             ha='center', color='purple')
    
    ax3.set_title('Tiling Schema', fontsize=12)
    ax3.axis('off')
    
    # 4-6. Sample tiles
    sample_positions = []
    
    # Select interesting tile positions
    positions_to_show = [
        (0, 0),  # Top-left corner
        (min(1, tiles_y-1), min(2, tiles_x-1)),  # Somewhere in middle
        (min(2, tiles_y-1), 0),  # Left edge
        (0, min(3, tiles_x-1)),  # Top edge
        (min(tiles_y-1, 3), min(tiles_x-1, 4)),  # Towards bottom-right
        (min(1, tiles_y-1), min(1, tiles_x-1)),  # Early middle
    ]
    
    for idx, (row, col) in enumerate(positions_to_show[:3]):
        ax = plt.subplot(2, 3, 4 + idx)
        
        # Calculate tile boundaries
        left = col * step_size
        top = row * step_size
        right = min(left + tile_size, img_width)
        bottom = min(top + tile_size, img_height)
        
        # Extract and display tile
        if right > left and bottom > top:
            tile_img = img_array[top:bottom, left:right]
            ax.imshow(tile_img)
            ax.set_title(f'Tile [{row}, {col}]\nPosition: ({left}, {top})\nSize: {right-left}x{bottom-top}', 
                        fontsize=10)
            sample_positions.append((row, col, left, top, right, bottom))
        
        ax.axis('off')
    
    plt.tight_layout()
    
    # Show statistics
    total_pixels = img_width * img_height
    tile_pixels = tile_size * tile_size
    overlap_ratio = overlap_percentage / 100
    
    stats_text = f"""
Image Slicing Statistics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Original image: {img_width} × {img_height} = {total_pixels:,} pixels
Tile size: {tile_size} × {tile_size} = {tile_pixels:,} pixels
Overlap percentage: {overlap_percentage}% ({overlap_pixels} pixels)
Step size: {step_size} pixels
Grid dimensions: {tiles_x} × {tiles_y} = {tiles_x * tiles_y} tiles

Memory usage (approximate):
- Original image: {total_pixels * 3 / 1024 / 1024:.1f} MB (RGB)
- All tiles: {tiles_x * tiles_y * tile_pixels * 3 / 1024 / 1024:.1f} MB
- Compression ratio: {(tiles_x * tiles_y * tile_pixels) / total_pixels:.1f}x
"""
    
    plt.figtext(0.02, 0.02, stats_text, fontsize=10, family='monospace',
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
    
    plt.show()
    # Let's save figure
    
    return sample_positions


def create_detailed_overlap_visualization(image_path, overlap_percentage, tile_size=512):
    """
    Create a detailed visualization focusing on overlap regions.
    """
    
    # Load image
    image = Image.open(image_path)
    img_array = np.array(image)
    img_width, img_height = image.size
    
    # Calculate parameters
    overlap_pixels = int(tile_size * overlap_percentage / 100)
    step_size = tile_size - overlap_pixels
    
    # Focus on a small region to show overlap clearly
    focus_width = min(tile_size * 3, img_width)
    focus_height = min(tile_size * 3, img_height)
    focus_img = img_array[:focus_height, :focus_width]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Left: Original region
    ax1.imshow(focus_img)
    ax1.set_title(f'Original Image Region\n{focus_width} × {focus_height} pixels')
    
    # Right: With overlap heatmap
    ax2.imshow(focus_img, alpha=0.5)
    
    # Create overlap heatmap
    overlap_map = np.zeros((focus_height, focus_width))
    
    tiles_x = math.ceil((focus_width - overlap_pixels) / step_size)
    tiles_y = math.ceil((focus_height - overlap_pixels) / step_size)
    
    for row in range(tiles_y):
        for col in range(tiles_x):
            left = col * step_size
            top = row * step_size
            right = min(left + tile_size, focus_width)
            bottom = min(top + tile_size, focus_height)
            
            if right > left and bottom > top:
                overlap_map[top:bottom, left:right] += 1
    
    # Show overlap intensity
    im = ax2.imshow(overlap_map, alpha=0.6, cmap='hot', vmin=0, vmax=overlap_map.max())
    plt.colorbar(im, ax=ax2, label='Overlap Count')
    
    # Draw grid
    for col in range(tiles_x + 1):
        x = col * step_size
        if x <= focus_width:
            ax2.axvline(x=x, color='cyan', linestyle='-', alpha=0.8, linewidth=2)
    
    for row in range(tiles_y + 1):
        y = row * step_size
        if y <= focus_height:
            ax2.axhline(y=y, color='cyan', linestyle='-', alpha=0.8, linewidth=2)
    
    ax2.set_title(f'Overlap Heatmap\nRed = More Overlap')
    
    plt.tight_layout()
    plt.show()



def main():
    parser = argparse.ArgumentParser(description="Visualize image slicing process")
    parser.add_argument("image_path", help="Path to the input image")
    parser.add_argument("overlap_percentage", type=float, 
                       help="Overlap percentage between tiles (0-99)")
    parser.add_argument("--tile-size", type=int, default=512,
                       help="Size of each tile in pixels (default: 512)")
    parser.add_argument("--detailed", action="store_true",
                       help="Show detailed overlap visualization")
    
    args = parser.parse_args()
    
    try:
        print("Creating main visualization...")
        visualize_image_slicing(args.image_path, args.overlap_percentage, args.tile_size)
        
        if args.detailed:
            print("Creating detailed overlap visualization...")
            create_detailed_overlap_visualization(
                args.image_path, args.overlap_percentage, args.tile_size
            )
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()