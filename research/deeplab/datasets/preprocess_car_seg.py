# ==============================================================================
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
#
# Written by Do Trung Hai (dohai90) and Juhyung Park (jhpark)
# ==============================================================================

"""Copies JPEG files and creates the segmentation color map.

Copies JPEG files and creates the segmentation color map save
the results to output_dir.
"""

import os
import sys
import cv2
import glob
import math
import numpy as np
from PIL import Image
import argparse
from shutil import copyfile

MASK_RGB_DICT = {
    'BG': [255, 255, 255],
    'back_door': [50, 50, 150],
    'front_bumper': [250, 50, 250],
    'front_door_left': [250, 250, 50],
    'front_door_right': [150, 150, 250],
    'front_fender_left': [250, 50, 150],
    'front_fender_right': [250, 150, 250],
    'front_fog_left': [150, 50, 150],
    'front_fog_right': [150, 150, 150],
    'front_lamp_left': [50, 50, 250],
    'front_lamp_right': [250, 150, 150],
    'grille_up': [250, 250, 150],
    'hood': [250, 250, 250],
    'rear_bumper': [250, 50, 50],
    'rear_door_left': [150, 150, 50],
    'rear_door_right': [50, 250, 250],
    'rear_fender_left': [150, 50, 50],
    'rear_fender_right': [150, 250, 150],
    'rear_lamp_left': [50, 50, 50],
    'rear_lamp_right': [50, 150, 50],
    'rear_stop_center': [50, 150, 150],
    'rear_stop_left': [50, 250, 50],
    'rear_stop_right': [250, 150, 50],
    'side_mirror_left': [150, 50, 250],
    'side_mirror_right': [150, 250, 50],
    'side_step_left': [50, 150, 250],
    'side_step_right': [150, 250, 250],
    'trunk': [50, 250, 150]
}

MASK_CLS_DICT = {
    'BG': 0,
    'back_door': 1,
    'front_bumper': 2,
    'front_door_left': 3,
    'front_door_right': 4,
    'front_fender_left': 5,
    'front_fender_right': 6,
    'front_fog_left': 7,
    'front_fog_right': 8,
    'front_lamp_left': 9,
    'front_lamp_right': 10,
    'grille_up': 11,
    'hood': 12,
    'rear_bumper': 13,
    'rear_door_left': 14,
    'rear_door_right': 15,
    'rear_fender_left': 16,
    'rear_fender_right': 17,
    'rear_lamp_left': 18,
    'rear_lamp_right': 19,
    'rear_stop_center': 20,
    'rear_stop_left': 21,
    'rear_stop_right': 22,
    'side_mirror_left': 23,
    'side_mirror_right': 24,
    'side_step_left': 25,
    'side_step_right': 26,
    'trunk': 27
}

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("--seg_list_path", required=True, help="path to file including list of segmentation file name")
ap.add_argument("--jpeg_list_path", required=True, help="path to file including list of jpeg file name")
ap.add_argument("--jpeg_folder", required=True, help="path to jpeg folder")
ap.add_argument("--seg_folder", required=True, help="path to segmentation with color map folder")
ap.add_argument("--separate_folder", required=True,
                help="path to output folder including separate train/val/trainval sets.")
ap.add_argument("--remove_salt_and_pepper_noise", required=True, type=bool, default=True,
                help="remove salt and pepper noise in the annotation images")
args = vars(ap.parse_args())


# Copy jpeg background images to jpeg_folder
def copy_background_jpeg(jpeg_list_path, output_dir):
    print("Copy images process starts ...")
    jpeg_list = [x.strip('\n') for x in open(jpeg_list_path, 'r')]
    for idx, jpeg in enumerate(jpeg_list):
        sys.stdout.write('\r>> Copying image %d/%d' % (
            idx + 1, len(jpeg_list)))
        sys.stdout.flush()
        jpeg_tokens = jpeg.split('/')[4:]
        jpeg_name = "_".join(jpeg_tokens)
        copyfile(jpeg, os.path.join(output_dir, jpeg_name))
    sys.stdout.write('\n')
    sys.stdout.flush()


def create_annotation_with_color_map(seg_list_path, output_dir):
    # Creating palette
    palette = []
    MASK_RGB_DICT_keys = list(MASK_RGB_DICT.keys())
    MASK_RGB_DICT_keys.sort()
    for key in MASK_RGB_DICT_keys:
        palette += MASK_RGB_DICT[key]

    palette += [int(np.random.randint(0, 256, 1)) for x in range(768 - len(palette))]
    palette_2d = np.reshape(palette, [-1, 3])

    color_map = {}
    for idx, rgb in enumerate(palette_2d):
        color_map[str(list(rgb))] = idx

    # Read images and preprocess images
    seg_list = [x.strip("\n") for x in open(seg_list_path, 'r')]

    print("Creates annotation process starts ...")
    for idx, seg in enumerate(seg_list):
        sys.stdout.write('\r>> Converting annotation %d/%d' % (
            idx + 1, len(seg_list)))
        sys.stdout.flush()
        img_np = np.array(Image.open(seg), dtype=np.int32)
        height, width = img_np.shape[0], img_np.shape[1]
        # Remove anti-aliasing artifact
        img_np += 5
        img_np = (img_np // 10) * 10
        img_np = np.clip(img_np, 0, 255)
        img_reshaped = np.reshape(img_np, [-1, 3])

        annotation = []
        for rgb in img_reshaped:
            try:
                annotation.append(color_map[str(list(rgb))])
            except:
                annotation.append(0)

        annotation_2d = np.reshape(annotation, [height, width]).astype(np.uint8)

        if args["remove_salt_and_pepper_noise"]:
            annotation_2d = cv2.medianBlur(annotation_2d, 3)

        pil_img = Image.fromarray(np.array(annotation_2d))
        pil_img.putpalette(palette)
        seg_tokens = seg.split('/')[4:]
        seg_name = '_'.join(seg_tokens)
        pil_img.save(os.path.join(output_dir, seg_name[:-4] + ".png"), 'PNG')
    sys.stdout.write('\n')
    sys.stdout.flush()


def separate_train_val_set(jpeg_folder, separate_folder):
    base_names = []
    _NUM_FOLDS = 5  # 4 folds for training and 1 fold for validation
    trainval_output_filename = os.path.join(separate_folder, 'trainval.txt')
    train_output_filename = os.path.join(separate_folder, 'train.txt')
    val_output_filename = os.path.join(separate_folder, 'val.txt')
    with open(trainval_output_filename, 'w') as f:
        for background_path in glob.glob(os.path.join(jpeg_folder, '*')):
            base_name = os.path.basename(background_path).replace('_0001_Background.jpg', '')
            base_names.append(base_name)
            f.write(base_name+'\n')

    num_images = len(base_names)
    num_per_fold = int(math.ceil(num_images / float(_NUM_FOLDS)))

    with open(train_output_filename, 'w') as f:
        for base_name in base_names[:(num_images-num_per_fold)]:
            f.write(base_name+'\n')

    with open(val_output_filename, 'w') as f:
        for base_name in base_names[(num_images-num_per_fold):]:
            f.write(base_name+'\n')


if __name__ == "__main__":
    copy_background_jpeg(args["jpeg_list_path"], args["jpeg_folder"])
    separate_train_val_set(args["jpeg_folder"], args["separate_folder"])
    create_annotation_with_color_map(args["seg_list_path"], args["seg_folder"])
