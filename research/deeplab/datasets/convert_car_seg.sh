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
#     - build_voc2012_data.py
#     - download_and_convert_voc2012.sh
#     - convert_voc2012_aug.sh
#     - add_voc2012_aug_dataset.py
#     - remove_gt_colormap.py
#     + car_seg
#       + VOCdevkit
#         + VOC2012
#           + JPEGImages
#           + SegmentationClass
#

# Exit immediately if a command exits with a non-zero status.
set -e

CURRENT_DIR=$(pwd)
WORK_DIR="./car_seg"
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

# Root path for car dataset.
PASCAL_ROOT="${WORK_DIR}/VOCdevkit/VOC2012"

# Copies JPEG background images, creates color map annotations
# and Remove the colormap in the ground truth annotations.
JPEG_BACKGROUND_FOLDER="${PASCAL_ROOT}/JPEGImages"
SEG_FOLDER="${PASCAL_ROOT}/SegmentationClass"
SEMANTIC_SEG_FOLDER="${PASCAL_ROOT}/SegmentationClassRaw"

if [ ! -d "${JPEG_BACKGROUND_FOLDER}" ]; then
  mkdir -p "${JPEG_BACKGROUND_FOLDER}"
fi

if [ ! -d "${SEG_FOLDER}" ]; then
  mkdir -p "${SEG_FOLDER}"
fi

if [ ! -d "${SEMANTIC_SEG_FOLDER}" ]; then
  mkdir -p "${SEMANTIC_SEG_FOLDER}"
fi

echo "Copies JPEG images and create color map annotations"
python ./preprocess_car_seg.py \
  --seg_list_path="${CURRENT_DIR}/${WORK_DIR}/segmentations.txt" \
  --jpeg_list_path="${CURRENT_DIR}/${WORK_DIR}/backgrounds.txt" \
  --jpeg_folder="${JPEG_BACKGROUND_FOLDER}" \
  --seg_folder="${SEG_FOLDER}"

echo "Removing the color map in ground truth annotations..."
python ./remove_gt_colormap.py \
  --original_gt_folder="${SEG_FOLDER}" \
  --output_dir="${SEMANTIC_SEG_FOLDER}"
