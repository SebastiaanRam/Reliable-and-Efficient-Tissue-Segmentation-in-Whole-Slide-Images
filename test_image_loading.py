import sys
import os
import openslide

def inspect_wsi(path):
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        return

    try:
        slide = openslide.OpenSlide(path)
    except Exception as e:
        print(f"❌ Could not open slide: {e}")
        return

    print(f"\n--- Inspecting: {os.path.basename(path)} ---")
    print(f"Vendor: {slide.properties.get('openslide.vendor', 'Unknown')}")
    print(f"Level count: {slide.level_count}")
    print(f"Base dimensions (level 0): {slide.dimensions}")

    # Print dimensions for each pyramid level
    for i, dim in enumerate(slide.level_dimensions):
        print(f" Level {i}: {dim} (downsample: {slide.level_downsamples[i]:.2f}x)")

    # Try reading a tiny patch to confirm access
    try:
        patch = slide.read_region((0, 0), slide.level_count - 1, (256, 256))
        print(f"✅ Successfully read a small patch from level {slide.level_count - 1}")
    except Exception as e:
        print(f"❌ Failed to read patch: {e}")

    # Check microns per pixel (MPP)
    mpp_x = slide.properties.get("openslide.mpp-x", None)
    mpp_y = slide.properties.get("openslide.mpp-y", None)
    if mpp_x and mpp_y:
        print(f"MPP: {mpp_x} x {mpp_y}")
    else:
        print("⚠️ MPP metadata not found!")

    slide.close()

def test_wsd(path):
    from wholeslidedata.image.wholeslideimage import WholeSlideImage

    with WholeSlideImage(path) as wsi:
        print("Corrected spacings (MPP) for each level:", wsi.spacings)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_wsi_pipeline.py /path/to/slide.tif")
        sys.exit(1)

    wsi_path = sys.argv[1]
    # inspect_wsi(wsi_path)
    test_wsd(wsi_path)