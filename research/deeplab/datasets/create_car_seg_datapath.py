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
# Written by Do Trung Hai (dohai90)
# ==============================================================================

import os
import glob
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("--data_root", required=True,
                help="path to folder including images.")
ap.add_argument("--output_list_dir", required=True,
                help="path to output folder including a list of background and annotations.")

args = vars(ap.parse_args())


def list_backgrounds_and_annotations_path(data_root, output_list_dir):

    background_paths = []
    annotation_paths = []
    valid_background_paths = []
    valid_annotation_paths = []

    for path in glob.glob(os.path.join(data_root, "**"), recursive=True):
        if '_0000_Layer 1.jpg' in str(os.path.basename(path)):
            annotation_paths.append(path)
        if '_0001_Background.jpg' in str(os.path.basename(path)):
            background_paths.append(path)

    for annotation_path in annotation_paths:
        if not os.path.isfile(annotation_path):
            continue

        token = os.path.basename(annotation_path).replace('_0000_Layer 1.jpg', '')
        background_path = str(os.path.dirname(annotation_path)) + '/' + token + '_0001_Background.jpg'

        if background_path in background_paths and os.path.isfile(background_path):
            valid_annotation_paths.append(annotation_path)
            valid_background_paths.append(background_path)
        else:
            print("Invalid annotation: {}".format(annotation_path))

    backgrounds_list_filename = os.path.join(output_list_dir, 'backgrounds.txt')
    if os.path.isfile(backgrounds_list_filename):
        print("Remove old backgrounds list...")
        os.remove(backgrounds_list_filename)
    with open(backgrounds_list_filename, 'w') as f:
        for background_path in valid_background_paths:
            f.write(background_path+'\n')

    annotations_list_filename = os.path.join(output_list_dir, 'segmentations.txt')
    if os.path.isfile(annotations_list_filename):
        print("Remove old annotations list...")
        os.remove(annotations_list_filename)
    with open(annotations_list_filename, 'w') as f:
        for annotation_path in valid_annotation_paths:
            f.write(annotation_path+'\n')


if __name__ == "__main__":
    list_backgrounds_and_annotations_path(args["data_root"], args['output_list_dir'])
