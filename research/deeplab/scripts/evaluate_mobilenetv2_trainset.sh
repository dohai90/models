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
#   sh ./scripts/evaluate_mobilenetv2_valset.sh
#
#

# Exit immediately if a command exits with a non-zero status.
set -e

# Move one-level up to tensorflow/models/research directory.
cd ..

# Update PYTHONPATH.
export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim

# Set up the working environment.
export CUDA_VISIBLE_DEVICES=""

CURRENT_DIR=$(pwd)
WORK_DIR="${CURRENT_DIR}/deeplab"

# Run model_test first to make sure the PYTHONPATH is correctly set.
python3 "${WORK_DIR}"/model_test.py -v

# Set up the working directories.
DATASET_DIR="datasets"
CAR_FOLDER="car_seg_resized_denoised"
CAR_DATASET="${WORK_DIR}/${DATASET_DIR}/${CAR_FOLDER}/tfrecord"
EXP_FOLDER="exp/train_car_seg_mobilenetv2"
TRAIN_LOGDIR="${WORK_DIR}/${DATASET_DIR}/${CAR_FOLDER}/${EXP_FOLDER}/train"
EVAL_LOGDIR="${WORK_DIR}/${DATASET_DIR}/${CAR_FOLDER}/${EXP_FOLDER}/eval"

# Run evaluation. This performs eval over the full val split and will take a while.
python3 "${WORK_DIR}"/eval.py \
  --logtostderr \
  --dataset="car_seg" \
  --eval_split="train" \
  --model_variant="mobilenet_v2" \
  --eval_crop_size=769 \
  --eval_crop_size=769 \
  --checkpoint_dir="${TRAIN_LOGDIR}" \
  --eval_logdir="${EVAL_LOGDIR}" \
  --dataset_dir="${CAR_DATASET}" \
  --eval_interval_secs=5400 \
  --max_number_of_evaluations=-1 \
  2>&1 | tee "${EVAL_LOGDIR}/eval_trainset.log"
