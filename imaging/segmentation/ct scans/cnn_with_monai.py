import monai
import os
import glob

params = {'experiment_name': {},
          'patch_size': (128, 128, 128),
          'bz_size': 1,
          'n_classes': 2,
          'class_ratios': [1, 10],
          'learning_rate': 1e-3,
          'weight_decay': 1e-4,
          'epoch_num': 1000,
          'val_interval': 5,
          'intensity_min': -1000, # min voxel intensity value of CT scan
          'intensity_max': +1000, # max voxel intensity value of Ct scan
          'seed': 0,
          'train_set': {}, # list of files for training the model
          'val_set': {}, # list of files for validating the model
          'test_set': {}, # list of files for testing the model
          'train_transforms': {},
          'val_transforms': {},
          'loss_function': monai.losses.DiceCELoss(to_onehot_y=True, sigmoid=True) # loss function
}

# STEP1: load dataset
dir_data = 'T:/tutorials/Task09_Spleen'
dir_imagesTr = os.path.join(dir_data, 'ImagesTr')
dir_labelsTr = os.path.join(dir_data, 'LabelsTr')
# define training and validation dataset
train_images = sorted(glob.glob(os.path.join(dir_imagesTr, "*.nii.gz")))
train_labels = sorted(glob.glob(os.path.join(dir_labelsTr, "*.nii.gz")))
data_dicts = [{"image": image_name, "label": label_name} for image_name, label_name in zip(train_images, train_labels)]
# all but the last 9 data are for training, the last nine data are for validation
train_files, val_files = data_dicts[:-9], data_dicts[-9:]
