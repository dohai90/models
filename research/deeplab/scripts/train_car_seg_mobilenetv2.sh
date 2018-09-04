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
# This script is used to run train, val and visualize on car_seg dataset using MobileNet-v2.
# Users could also modify from this script for their use case.
#
# Usage:
#   # From the tensorflow/models/research/deeplab directory.
#   sh ./scripts/train_car_seg_mobilenetv2.sh
#
#

# Exit immediately if a command exits with a non-zero status.
set -e

# Move one-level up to tensorflow/models/research directory.
cd ..

# Update PYTHONPATH.
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim

# Set up the working environment.
CURRENT_DIR=$(pwd)
WORK_DIR="${CURRENT_DIR}/deeplab"

# Run model_test first to make sure the PYTHONPATH is correctly set.
python "${WORK_DIR}"/model_test.py -v

# Go to datasets folder and check car_seg is presented or not.
# If not, run convert_car_seg.sh
DATASET_DIR="datasets"
CAR_FOLDER="car_seg"
cd "${WORK_DIR}/${DATASET_DIR}"
if [ ! -d "${CAR_FOLDER}" ]; then
  sh convert_car_seg.sh
fi

# Go back to original directory.
cd "${CURRENT_DIR}"

# Set up the working directories.
EXP_FOLDER="exp/train_car_seg_mobilenetv2"
INIT_FOLDER="${WORK_DIR}/${DATASET_DIR}/${CAR_FOLDER}/init_models"
TRAIN_LOGDIR="${WORK_DIR}/${DATASET_DIR}/${CAR_FOLDER}/${EXP_FOLDER}/train"
EVAL_LOGDIR="${WORK_DIR}/${DATASET_DIR}/${CAR_FOLDER}/${EXP_FOLDER}/eval"
VIS_LOGDIR="${WORK_DIR}/${DATASET_DIR}/${CAR_FOLDER}/${EXP_FOLDER}/vis"
EXPORT_DIR="${WORK_DIR}/${DATASET_DIR}/${CAR_FOLDER}/${EXP_FOLDER}/export"

if [ ! -d "${INIT_FOLDER}" ]; then
  mkdir -p "${INIT_FOLDER}"
fi

if [ ! -d "${TRAIN_LOGDIR}" ]; then
  mkdir -p "${TRAIN_LOGDIR}"
fi

if [ ! -d "${EVAL_LOGDIR}" ]; then
  mkdir -p "${EVAL_LOGDIR}"
fi

if [ ! -d "${VIS_LOGDIR}" ]; then
  mkdir -p "${VIS_LOGDIR}"
fi

if [ ! -d "${EXPORT_DIR}" ]; then
  mkdir -p "${EXPORT_DIR}"
fi

# Copy locally the trained checkpoint as the initial checkpoint.
CKPT_NAME="mobilenet_v2_1.0_224"
cd "${INIT_FOLDER}"
if [ ! -d "${CKPT_NAME}" ]; then
  ln -s "/content/dohai90/pretrained_models/mobilenet_v2_1.0_224"
fi
cd "${CURRENT_DIR}"

CAR_DATASET="${WORK_DIR}/${DATASET_DIR}/${CAR_FOLDER}/tfrecord"

# Train 30000 iterations.
NUM_ITERATIONS=30000
python "${WORK_DIR}"/train.py \
  --logtostderr \
  --dataset="car_seg" \
  --train_split="train" \
  --model_variant="mobilenet_v2" \
  --output_stride=16 \
  --train_crop_size=513 \
  --train_crop_size=513 \
  --train_batch_size=4 \
  --training_number_of_steps="${NUM_ITERATIONS}" \
  --fine_tune_batch_norm=true \
  --tf_initial_checkpoint="${INIT_FOLDER}/${CKPT_NAME}/mobilenet_v2_1.0_224.ckpt" \
  --train_logdir="${TRAIN_LOGDIR}" \
  --dataset_dir="${CAR_DATASET}"
