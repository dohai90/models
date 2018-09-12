#!/bin/bash
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
#
# Script to preprocess the car dataset.
#
# Usage:
#   bash ./convert_car_seg.sh
#
# The folder structure is assumed to be:
#  + datasets
#     - build_data.py
#     - build_car_seg_data.py
#     - remove_gt_colormap.py
#     - preprocess_car_seg.py
#     - segmentation_dataset.py
#     - convert_car_seg.sh
#     - train_car_seg_mobilenetv2.sh
#     + car_seg
#       + VOCdevkit
#         + VOC2012
#           + JPEGImages
#           + SegmentationClass
#

# Exit immediately if a command exits with a non-zero status.
set -e

CURRENT_DIR=$(pwd)
WORK_DIR="./car_seg_resized_denoised"
if [ ! -d "${WORK_DIR}" ]; then
  mkdir -p "${WORK_DIR}"
fi
cd "${WORK_DIR}"

# Create VOCdevkit/VOC2012 folder if not exist
VOC_DIR="VOCdevkit/VOC2012"
if [ ! -d "${VOC_DIR}" ]; then
  mkdir -p "${VOC_DIR}"
fi
cd "${CURRENT_DIR}"

# Root path for car dataset before processing.
DATA_ROOT="/content/dohai90/old_car_mask_data"

# Root path for car dataset for processing.
CAR_ROOT="${WORK_DIR}/VOCdevkit/VOC2012"

# Copies JPEG background images, creates color map annotations
# and remove the colormap in the ground truth annotations.
IMAGE_FOLDER="${CAR_ROOT}/JPEGImages"
SEG_FOLDER="${CAR_ROOT}/SegmentationClass"
SEMANTIC_SEG_FOLDER="${CAR_ROOT}/SegmentationClassRaw"
LIST_FOLDER="${CAR_ROOT}/ImageSets/Segmentation"

if [ ! -d "${IMAGE_FOLDER}" ]; then
  mkdir -p "${IMAGE_FOLDER}"
fi

if [ ! -d "${SEG_FOLDER}" ]; then
  mkdir -p "${SEG_FOLDER}"
fi

if [ ! -d "${SEMANTIC_SEG_FOLDER}" ]; then
  mkdir -p "${SEMANTIC_SEG_FOLDER}"
fi

if [ ! -d "${LIST_FOLDER}" ]; then
  mkdir -p "${LIST_FOLDER}"
fi


echo "Create backgrounds and annotations list..."
python ./create_car_seg_datapath.py \
  --data_root="${DATA_ROOT}" \
  --output_list_dir="${WORK_DIR}"

echo "Copies JPEG images and separates into train/val/trainval sets then creates color map annotations..."
python ./preprocess_car_seg.py \
  --seg_list_path="${CURRENT_DIR}/${WORK_DIR}/segmentations.txt" \
  --jpeg_list_path="${CURRENT_DIR}/${WORK_DIR}/backgrounds.txt" \
  --jpeg_folder="${IMAGE_FOLDER}" \
  --seg_folder="${SEG_FOLDER}" \
  --separate_folder="${LIST_FOLDER}" \
  --input_size=769 \
  --remove_salt_and_pepper_noise=true

echo "Removing the color map in ground truth annotations..."
python ./remove_gt_colormap.py \
  --original_gt_folder="${SEG_FOLDER}" \
  --output_dir="${SEMANTIC_SEG_FOLDER}"

# Build TFRecords of the dataset.
# First, create output directory for storing TFRecords.
OUTPUT_DIR="${WORK_DIR}/tfrecord"
if [ ! -d "${OUTPUT_DIR}" ]; then
  mkdir -p "${OUTPUT_DIR}"
fi

echo "Converting CAR SEGMENTATION dataset to TFRecords..."
python ./build_car_seg_data.py \
  --image_folder="${IMAGE_FOLDER}" \
  --semantic_segmentation_folder="${SEMANTIC_SEG_FOLDER}" \
  --list_folder="${LIST_FOLDER}" \
  --image_format="jpg" \
  --output_dir="${OUTPUT_DIR}"
