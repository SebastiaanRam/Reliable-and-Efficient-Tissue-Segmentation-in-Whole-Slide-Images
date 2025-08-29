#!/bin/bash

#SBATCH --qos=low
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --gpus-per-task=1
#SBATCH --mem-per-cpu=4G
#SBATCH --time=8:00:00
#SBATCH --job-name=interactive
#SBATCH --no-container-entrypoint
#SBATCH --output=/home/%u/logs/slurm-%j.out
#SBATCH --container-mounts=/data/temporary:/data/temporary
#SBATCH --container-workdir=/nnUNet
#SBATCH --container-image="dockerdex.umcn.nl:5005#sebastiaanram/reliable-and-efficient-tissue-segmentation-in-whole-slide-images:latest"

# export SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL=True

nnUNetv2_predict_tissue \
    -i /data/temporary/sebastiaan/github/Reliable-and-Efficient-Tissue-Segmentation-in-Whole-Slide-Images/scan_list.txt \
    -o /data/temporary/sebastiaan/github/Reliable-and-Efficient-Tissue-Segmentation-in-Whole-Slide-Images/images/masks \
    --b01 \
    -pp strict \
    --resenc
