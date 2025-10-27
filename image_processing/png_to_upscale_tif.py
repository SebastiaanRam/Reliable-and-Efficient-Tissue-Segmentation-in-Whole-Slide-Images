from wholeslidedata import WholeSlideImage
from wholeslidedata.interoperability.asap.imagewriter import WholeSlideMaskWriter, WholeSlideImageWriter
from PIL import Image
import numpy as np
from pathlib import Path
from wholeslidedata.iterators import create_patch_iterator

Image.MAX_IMAGE_PIXELS = None

def get_closest_value(value):
    possible_values = [0.25, 0.5, 1, 2, 4, 8, 16, 32, 64]
    closest = min(possible_values, key=lambda x:abs(x-value))
    return closest

def take_closest_number(l, number):
    return min(l, key=lambda x: abs(x - number))

def take_closest_number_index(l, number):
    closest = take_closest_number(l, number)
    for ind, val in enumerate(l):
        if val==closest: return ind

def save_normal_image_as_mask(path, slide_path, out_path):
    """ saves an image-mask (png, jpeg) as pyramidal tif for a given slide """
    reader = WholeSlideImage(str(slide_path), backend='asap')
    print(zip(reader.spacings, reader.shapes))
    spacings = reader.spacings
    shapes = reader.shapes
    reader.close()

    mask = Image.open(str(path))
    mask_arr = np.array(mask)
    mask.close()

    desired_spacing = spacings[0]
    print(f"Saving mask array as TIF at spacing {desired_spacing}")
    return save_array_as_image(mask_arr, spacing=desired_spacing, path=out_path)

def save_array_as_image(arr, path, spacing, tile_size=512):
    """ saves an array as pyramidal tif """
    if len(arr.shape)==2:
        arr = arr[:,:,None]
        writer = WholeSlideMaskWriter()
    else:
        writer = WholeSlideImageWriter()
    shape = arr.shape
    writer.write(
        path=str(path), spacing=spacing, dimensions=(shape[1], shape[0]),
        tile_shape=(tile_size, tile_size, 1),
    )

    for col in range(0, shape[1]+tile_size, tile_size): #+tile_size if array not divisible by tile_size
        for row in range(0, shape[0]+tile_size, tile_size):
            tile = arr[row:row+tile_size, col:col+tile_size]
            if len(tile)==0: continue #for the edge-case
            if tile.shape[0]!=tile_size or tile.shape[1]!=tile_size:
                pad = ((0, tile_size-tile.shape[0]),(0, tile_size-tile.shape[1]),(0,0))
                tile = np.pad(tile, pad, mode='constant')
            writer.write_tile(tile=tile, coordinates=(col,row))  #col,row (x,y)
    writer.save()

def upscale_mask(image_path, mask_path, out_path):
    img = Image.open(mask_path)
    
    print("Upscaling mask...")
    with WholeSlideImage(image_path, backend='asap') as wsi:
        target_size = wsi.shapes[0]
        spacings = wsi.spacings
        print(f"Highest shape of the WSI: {target_size} at spacing {spacings[0]}")

    print(f"Original mask size: {img.size}, target size: {target_size}")
    upscaled = img.resize(target_size, Image.NEAREST)
    upscaled.save(out_path)


if __name__ == "__main__":    
    import argparse
    
    parser = argparse.ArgumentParser(description="Run inference pipeline on a single file")
    parser.add_argument("--path", required=True)
    parser.add_argument("--slide_path", required=True)
    parser.add_argument("--out_path", required=True)
    parser.add_argument("--out_png", required=True)
    args = parser.parse_args()

    path = args.path
    slide_path = args.slide_path
    out_path = args.out_path
    out_png = args.out_png

    upscale_mask(slide_path, path, out_png)
    save_normal_image_as_mask(out_png, slide_path, out_path)
