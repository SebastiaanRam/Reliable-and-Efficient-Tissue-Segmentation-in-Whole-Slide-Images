from pathlib import Path
from annovert import Annovert, ConverterConfig
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

config = ConverterConfig()
converter = Annovert(config)

converter.convert_file(
    input_path="/data/temporary/sebastiaan/histai/HISTAI-skin-b1/case_0860/processed/output/masks/slide_H&E_0_mask.tif",
    output_path="/data/temporary/sebastiaan/histai/HISTAI-skin-b1/case_0860/processed/slide_H&E_0_mask.geojson",  # optional if config set
    target_format="geojson", # see supported formats
    image_path="/data/temporary/sebastiaan/histai/HISTAI-skin-b1/case_0860/processed/slide_H&E_0.tiff"
)