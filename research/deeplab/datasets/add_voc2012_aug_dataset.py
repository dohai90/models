# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""
Add augmented dataset to PASCAL VOC 2012 Segmentation
"""

import os
import scipy.io
import numpy as np
import tensorflow as tf
import shutil

from PIL import Image

FLAGS = tf.app.flags.FLAGS

tf.app.flags.DEFINE_string('aug_data_folder',
                           './pascal_voc_seg/benchmark_RELEASE/dataset',
                           'Augmented data foler')

tf.app.flags.DEFINE_string('original_folder',
                           './pascal_voc_seg/VOCdevkit/VOC2012',
                           'VOCdevkit dataset folder')


aug_train_non_dup = []
aug_val_non_dup = []


def _remove_duplicated_train_val_set(aug_train_filename, aug_val_filename, original_trainval_filename):
    """Remove duplicated filename with trainval from augmented dataset

    :param aug_train_filename:  augmented train file name
    :param aug_val_filename: augmented val file name
    :param original_trainval_filename: original trainval filename
    :return: None
    """
    trainval = [x.strip('\n') for x in open(original_trainval_filename, 'r')]
    aug_train = [x.strip('\n') for x in open(aug_train_filename, 'r')]
    aug_val = [x.strip('\n') for x in open(aug_val_filename, 'r')]

    for x in aug_train:
        if x in trainval:
            continue
        else:
            aug_train_non_dup.append(x)

    for x in aug_val:
        if x in trainval:
            continue
        else:
            aug_val_non_dup.append(x)


def _save_annotation(annotation_np, filename):
    """Save non duplicate annotation into VOC dataset

    :param annotation_np: Segmentation annotation
    :param filename: Output filename
    :return: None
    """
    pil_image = Image.fromarray(annotation_np.astype(dtype=np.uint8))
    pil_image.save(filename)


def _copy_jpeg_to_VOC(image_filename, dest):
    """Copy non duplicated augmented train and val images to VOC dataset

    :param image_filename: jpeg images
    :param dest: destination file
    :return: None
    """
    shutil.copy2(image_filename, dest)


def _create_train_aug(original_train_filename):
    """ Concatenate non duplicated augmented train to original train
        Reorder all list

    :param original_train_filename: original train file name to be concatenated
    :return: None
    """
    if os.path.exists(original_train_filename):
        train = [x.strip('\n') for x in open(original_train_filename, 'r')]
        train += aug_train_non_dup + aug_val_non_dup
        train.sort()

        with open(os.path.join(FLAGS.original_folder, 'ImageSets/Segmentation', 'train_aug.txt'), 'w') as f:
            for x in train:
                f.write(x+'\n')


def main(unused_argv):
    _remove_duplicated_train_val_set(os.path.join(FLAGS.aug_data_folder, 'train.txt'),
                                     os.path.join(FLAGS.aug_data_folder, 'val.txt'),
                                     os.path.join(FLAGS.original_folder, 'ImageSets/Segmentation/trainval.txt'))

    aug_train_val_non_dup = aug_train_non_dup + aug_val_non_dup
    for annotation in aug_train_val_non_dup:
        annotation_dict = scipy.io.loadmat(os.path.join(FLAGS.aug_data_folder, 'cls', annotation + '.mat'),
                                         mat_dtype=True,
                                         squeeze_me=True,
                                         struct_as_record=False)
        annotation_np = annotation_dict['GTcls'].Segmentation
        _save_annotation(annotation_np, os.path.join(FLAGS.original_folder,
                                                     'SegmentationClassRaw',
                                                     annotation + '.png'))
        _copy_jpeg_to_VOC(os.path.join(FLAGS.aug_data_folder,
                                       'img',
                                       annotation + '.jpg'),
                          os.path.join(FLAGS.aug_data_folder, 'JPEGImages'))

    _create_train_aug(os.path.join(FLAGS.original_folder, 'ImageSets/Segmentation', 'train.txt'))


if __name__ == '__main__':
    tf.app.run()

