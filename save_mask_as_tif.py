slide_path = "/data/temporary/sebastiaan/github/Reliable-and-Efficient-Tissue-Segmentation-in-Whole-Slide-Images/images/DI_S03_P000001_C0023_B101_T01_L37_A32_E001.tif"
path = "/data/temporary/sebastiaan/github/Reliable-and-Efficient-Tissue-Segmentation-in-Whole-Slide-Images/images/masks/DI_S03_P000001_C0023_B101_T01_L37_A32_E001.png"
out = "/data/temporary/sebastiaan/github/Reliable-and-Efficient-Tissue-Segmentation-in-Whole-Slide-Images/images/masks/DI_S03_P000001_C0023_B101_T01_L37_A32_E001.tif"

from wholeslidedata import WholeSlideImage
from wholeslidedata.interoperability.asap.imagewriter import WholeSlideMaskWriter, WholeSlideImageWriter
from PIL import Image
import numpy as np

def take_closest_number(l, number):
    return min(l, key=lambda x: abs(x - number))

def take_closest_number_index(l, number):
    closest = take_closest_number(l, number)
    for ind, val in enumerate(l):
        if val==closest: return ind

def save_array_as_image(arr, path, spacing, tile_size=512):
    """ saves an array as pyramidal tif """
    if len(arr.shape)==2:
        arr = arr  # shape (H, W)
        writer = WholeSlideMaskWriter()
    else:
        if arr.shape[2] == 1:
            arr = np.squeeze(arr, axis=2)  # shape (H, W)
        writer = WholeSlideImageWriter()
    shape = arr.shape
    writer.write(
        path=str(path), spacing=spacing, dimensions=(shape[1], shape[0]),
        tile_shape=(tile_size, tile_size),
    )

    for col in range(0, shape[1]+tile_size, tile_size): #+tile_size if array not divisible by tile_size
        for row in range(0, shape[0]+tile_size, tile_size):
            tile = arr[row:row+tile_size, col:col+tile_size]
            if len(tile)==0: continue #for the edge-case
            if tile.shape[0]!=tile_size or tile.shape[1]!=tile_size:
                if tile.ndim == 3:
                    pad = ((0, tile_size-tile.shape[0]), (0, tile_size-tile.shape[1]), (0,0))
                elif tile.ndim == 2:
                    pad = ((0, tile_size-tile.shape[0]), (0, tile_size-tile.shape[1]))
                tile = np.pad(tile, pad, mode='constant')
            if isinstance(writer, WholeSlideMaskWriter) and tile.shape[-1] == 1:
                tile = np.squeeze(tile, axis=2)
            writer.write_tile(tile=tile, coordinates=(col,row))  #col,row (x,y)
    writer.save()

def save_normal_image_as_mask(path, slide_path, out_path):
    """ saves an image-mask (png, jpeg) as pyramidal tif for a given slide """
    reader = WholeSlideImage(str(slide_path), backend='asap')
    print(zip(reader.spacings, reader.shapes))
    spacings = reader.spacings
    shapes = reader.shapes
    reader.close()

    mask = Image.open(str(path))
    mask_arr = np.array(mask)
    h,w = mask.height, mask.width
    mask.close()

    heights = [hw[0] for hw in shapes]
    level = take_closest_number_index(heights, h)
    print('for mask shape(%d,%d) closest level %d with spacing  %.3f, shape %s' % \
          (h, w, level, spacings[level], str(shapes[level])))

    spacing = spacings[level]
    return save_array_as_image(mask_arr, spacing=spacing, path=out_path)

save_normal_image_as_mask(path, slide_path, out)