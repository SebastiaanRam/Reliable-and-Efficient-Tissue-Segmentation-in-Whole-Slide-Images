import os
import argparse
from pathlib import Path
import torch


def expand_folders_to_files(input_txt_path: str, output_txt_path: str) -> int:
    """
    Read a text file that may contain folders or files, and create a new text file
    with all individual TIFF file paths.
    
    Args:
        input_txt_path (str): Path to input text file (may contain folders)
        output_txt_path (str): Path to output text file (will contain only file paths)
        
    Returns:
        int: Number of files found
    """
    all_files = []
    
    with open(input_txt_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue
            
            path = Path(line)
            
            # If it's a file, add it directly
            if path.is_file():
                if path.suffix.lower() in ['.tif', '.tiff'] and 'mask' not in path.name.lower():
                    all_files.append(str(path))
                else:
                    print(f"Warning: Skipping non-TIFF file (line {line_num}): {line}")
            
            # If it's a directory, find all TIFF files within
            elif path.is_dir():
                print(f"Expanding folder (line {line_num}): {line}")
                tiff_files = []
                for extension in ['*.tif', '*.tiff']:
                    tiff_files.extend(path.rglob(extension))
                
                # Filter out masks
                tiff_files = [str(f) for f in tiff_files if 'mask' not in f.name.lower()]
                
                if tiff_files:
                    print(f"  Found {len(tiff_files)} TIFF files")
                    all_files.extend(tiff_files)
                else:
                    print(f"  Warning: No TIFF files found in {line}")
            
            # Path doesn't exist
            else:
                print(f"Warning: Path not found (line {line_num}): {line}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_files = []
    for f in all_files:
        if f not in seen:
            seen.add(f)
            unique_files.append(f)
    
    # Write expanded list to output file
    with open(output_txt_path, 'w') as f:
        for file_path in unique_files:
            f.write(f"{file_path}\n")
    
    print(f"\nExpanded to {len(unique_files)} unique TIFF files")
    print(f"File list saved to: {output_txt_path}")
    
    return len(unique_files)


def main():
    parser = argparse.ArgumentParser(description="Tissue segmentation pipeline using nnU-Net")
    parser.add_argument("--input", "-i", required=True, 
                       help="Input: single .tif file, folder, or .txt file with file/folder paths")
    parser.add_argument("--output", "-o", required=True, 
                       help="Path to output folder for masks")
    parser.add_argument("--tmp_folder", "-t", required=False, default="/tmp",
                       help="Path to temporary folder (default: /tmp)")
    parser.add_argument("--overwrite", action="store_true",
                       help="Overwrite existing masks if they already exist")
    parser.add_argument("--resenc", action="store_true",
                       help="Use residual encoder (better prediction but slower inference)")
    parser.add_argument("--pp", choices=["lite", "strict", "none"], default="none",
                       help="Postprocessing mode (default: none)")
    parser.add_argument("--lowres", action="store_true",
                       help="Use 20um model for faster inference")
    parser.add_argument("--device", type=str, default="cuda", choices=["cuda", "cpu", "mps"],
                       help="Device to use for inference (default: cuda)")
    parser.add_argument("--npp", type=int, default=8,
                       help="Number of CPU workers for preprocessing (default: 8)")
    args = parser.parse_args()

    # Setup paths
    input_path = Path(args.input)
    tmp_path = Path(args.tmp_folder)
    
    if tmp_path != Path("/tmp") and not tmp_path.exists():
        tmp_path.mkdir(parents=True, exist_ok=True)
        print(f"Created temporary folder: {tmp_path}")
    
    # Parse postprocessing config
    if args.pp == "lite":
        pp_cfg = dict(fill_holes=True, min_area_rel=0.002, keep_largest=False, min_area=None, close_r=0)
    elif args.pp == "strict":
        pp_cfg = dict(keep_largest=True, fill_holes=True, min_area=1000, min_area_rel=None, close_r=0)
    else:
        pp_cfg = None

    # Determine what to pass to predict_tissue
    inference_input = None
    
    if input_path.is_file():
        if input_path.suffix.lower() == '.txt':
            # Text file - might contain folders, so expand it
            print(f"Processing list file: {args.input}")
            expanded_list = tmp_path / "expanded_file_list.txt"
            num_files = expand_folders_to_files(str(input_path), str(expanded_list))
            
            if num_files == 0:
                raise ValueError("No TIFF files found to process")
            
            inference_input = str(expanded_list)
        elif input_path.suffix.lower() in ['.tif', '.tiff']:
            # Single TIFF file
            print(f"Processing single file: {args.input}")
            inference_input = str(input_path)
        else:
            raise ValueError(f"Unsupported file type: {input_path.suffix}")
    elif input_path.is_dir():
        # Directory - predict_tissue can handle this directly
        print(f"Processing folder: {args.input}")
        inference_input = str(input_path)
    else:
        raise ValueError(f"Input path does not exist: {args.input}")

    # Initialize predictor
    print(f"\nInitializing tissue predictor...")
    from nnunetv2.inference.predict_tissue import TissueNNUnetPredictor
    
    device = torch.device(args.device)
    if args.device == 'cuda':
        torch.set_num_threads(1)
        torch.set_num_interop_threads(1)
    elif args.device == 'cpu':
        import multiprocessing
        torch.set_num_threads(multiprocessing.cpu_count())
    
    predictor = TissueNNUnetPredictor(
        tile_step_size=0.5,
        use_gaussian=True,
        use_mirroring=True,
        perform_everything_on_device=True,
        device=device,
        verbose=False,
        verbose_preprocessing=False,
        allow_tqdm=True
    )
    
    # Load model weights
    resolution = '20' if args.lowres else '10'
    model_base = '/data/temporary/sebastiaan/tissue_segmentation/models'
    
    try:
        if args.resenc:
            print(f'Using {resolution}um model with ResEnc architecture')
            model_path = f'{model_base}/trained_on_{resolution}um_ResEnc'
            checkpoint = f'checkpoint_{resolution}um_ResEnc.pth'
        else:
            print(f'Using {resolution}um model')
            model_path = f'{model_base}/trained_on_{resolution}um'
            checkpoint = f'checkpoint_{resolution}um.pth'
        
        predictor.initialize_from_trained_tissue_model_folder(
            model_path,
            use_folds='all',
            checkpoint_name=checkpoint
        )
        
        print("Model loaded successfully\n")
        
        # Run inference using predict_tissue's built-in methods
        print(f"Starting inference pipeline...")
        print(f"Input: {inference_input}")
        print(f"Output: {args.output}")
        print(f"Overwrite: {args.overwrite}")
        print(f"CPU workers: {args.npp}")
        
        # Use the full pipeline mode
        predictor.predict_tissue_from_files(
            list_of_lists_or_source_folder=inference_input,
            output_folder_or_list_of_truncated_output_files=args.output,
            suffix=None,  # Not needed when using .txt or single file
            extension=None,
            exclude=None,
            save_probabilities=False,
            overwrite=args.overwrite,
            num_processes_preprocessing=args.npp,
            num_processes_segmentation_export=3,
            folder_with_segs_from_prev_stage=None,
            num_parts=1,
            part_id=0,
            binary_01=False,
            keep_parent=False,
            lowres=args.lowres,
            pp_cfg=pp_cfg,
            use_full_pipeline=True,  # Use the complete pipeline
            tmp_path=str(tmp_path)
        )
        
        print("\n✓ Inference completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n✗ Inference failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        print("\nCleaning up resources...")
        del predictor
        if args.device == 'cuda':
            torch.cuda.empty_cache()


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)