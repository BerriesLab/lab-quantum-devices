import os
import glob
import random
import numpy as np
import torch
import nibabel
import tqdm
import datetime
from monai.networks.nets import UNet
from monai.transforms import Compose, LoadImaged, EnsureChannelFirstd, Spacingd, OrientationD, ScaleIntensityRanged, AsDiscrete
from monai.data import CacheDataset, DataLoader, decollate_batch
from monai.losses import DiceLoss
from monai.metrics import DiceMetric

class NNMealworms:
    def __init__(self):
        self.params = {"dir_data": 'C:\\Users\\dabe\\Desktop\\training data', # It includes images and labels                        "experiment": datetime.datetime, # datetime of the experiment
                       "experiment": datetime.datetime, # datetime of the experiment
                       "trn_ratio": 0.7, # percentage of data used for training
                       "val_ratio": 0.15, # percentage of data used for validating
                       "tst_ratio": 0.15, # percentage of data used for testing
                       "data_percentage": 0.3, # percentage of data to use
                       'batch_train_size': 2, # number of data per batch
                       'set_trn': {}, # list of dictionary for training the model (compiled by script)
                       'set_val': {}, # list of dictionary for validating the model (compiled by script)
                       'set_tst': {}, # list of dictionary for testing the model (compiled by script)
                       # MODEL
                       'n_classes': 1, # for this study, the feature is either a mealworm or not
                       'kernel_size': 3, # size of the convolutional kernel (in pixels)
                       "up_kernel_size": 3,
                       "activation_function": torch.nn.ReLU(),
                       "dropout_ratio": 0,
                       'learning_rate': 1e-3, # learning rate of the Adam optimizer
                       'weight_decay': 1e-4, # weight decay of the Adam optimizer
                       "optimizer": 0, # 0: Adam, 1...
                       # TRAINING - VALIDATION
                       'n_epochs_trn': 100, # max iteration for training
                       'val_interval': 5, # number of iterations in-between validation
                       'intensity_min': -1000, # min voxel intensity value of CT scan
                       'intensity_max': +1000, # max voxel intensity value of Ct scan
                       'loss_function': DiceLoss(sigmoid=True), # loss function
                       "dice_metric": DiceMetric(include_background=True), # define loss metric for the validation
                     }
        # Transforms_training could include operation aimed at incrasing the sample size, such as noising, flipping, rotating etc.
        self.transforms_trn = Compose([
            LoadImaged(keys=["image", "label"]),
            EnsureChannelFirstd(keys=["image", "label"]),
            Spacingd(keys=["image", "label"], pixdim=(dx, dy, dz), mode=("bilinear", "nearest")),
            OrientationD(keys=["image", "label"], axcodes="RAS"),
            ScaleIntensityRanged(keys=["image"], a_min=params['intensity_min'], a_max=params['intensity_max'], b_min=0.0, b_max=1.0, clip=True),
        ])
        self.transforms_val = Compose([
            LoadImaged(keys=["image", "label"]),
            EnsureChannelFirstd(keys=["image", "label"]),
            Spacingd(keys=["image", "label"], pixdim=(dx, dy, dz), mode=("bilinear", "nearest")),
            OrientationD(keys=["image", "label"], axcodes="RAS"),
            ScaleIntensityRanged(keys=["image"], a_min=params['intensity_min'], a_max=params['intensity_max'], b_min=0.0, b_max=1.0, clip=True),
        ])

transforms_tst = transforms_val

    def buil_dataset(self):
        # Each sample is a dictionary with (image path, labels path), and no actual data
        # define training and validation dataset
        path_images = sorted(glob.glob(os.path.join(self.params["dir_data"], "*img.nii.gz")))
        path_labels = sorted(glob.glob(os.path.join(self.params["dir_data"], "*lbl.nii.gz")))
        path_dicts = [{"image": image_name, "label": label_name} for image_name, label_name in zip(path_images, path_labels)]
        # select subset of data
        if self.params["data_percentage"] < 1:
            path_dicts = path_dicts[:int(len(path_dicts) * self.params["data_percentage"])]
        # define training, validation and test sets.
        sets = ["training", "validation", "test"]
        # Calculate the number of samples for each split
        n = len(path_dicts)
        n_tra = int(self.params["trn_ratio"] * n)
        n_val = int(self.params["val_ratio"] * n)
        n_tes = n - n_tra - n_val
        # Shuffle the data list to randomize the order
        random.shuffle(path_dicts)
        # Split the data into training, validation, and testing sets
        self.params["set_trn"] = path_dicts[:n_tra]
        self.params["set_val"] = path_dicts[n_tra:n_tra + n_val]
        self.params["set_tst"] = path_dicts[n_tra + n_val:]
        # get voxel size, assuming that all nifti files have the same specs
        dx, dy, dz = nibabel.load(self.params["set_trn"][0]["image"]).header.get_zooms()


# def training(model, params, loader_trn, device):
#     best_metric = -1 # initialize best_metric so that the 1st validation will result the best
#     model.train() # set the model to training. This has effect only on some transforms
#     for epoch in range(params["n_epochs_trn"]):
#         epoch_loss = 0
#         epoch_trn_iterator= tqdm.tqdm(loader_trn, desc="Training (X / X Steps) (loss=X.X)", dynamic_ncols=True)
#         epoch_trn_iterator.set_description(f"Training ({epoch+1} / {params['n_epochs_trn']} Steps) (loss={0:2.5f})")
#         for step_trn, batch_trn in enumerate(epoch_trn_iterator):
#             # send the training data to device (GPU)
#             inputs, targets = batch_trn['image'].to(device), batch_trn['label'].to(device)
#             # reset the optimizer (which stores the values from the previous iteration
#             optimizer.zero_grad()
#             # forward pass
#             outputs = model(inputs)
#             loss = criterion(outputs, targets)
#             epoch_loss += loss.item()
#             # backpropagation
#             loss.backward()
#             # update metrics
#             optimizer.step()
#             # Update the progress bar description with loss and metrics
#             epoch_trn_iterator.set_description(f"Training ({epoch+1} / {params['n_epochs_trn']} Steps) (loss={epoch_loss:2.5f})")
#
# def validate(model, params, loader_val):
#     model.eval() # set the model to validation. This affects some transforms
#     with torch.no_grad(): # disable gradient computation (which is useless for validation)
#         dice_scores = np.zeros(len(loader_val))# = 0.0
#         epoch_val_iterator = tqdm.tqdm(loader_val, desc="Validate (X / X Steps) (dice=X.X)", dynamic_ncols=True)
#         epoch_val_iterator.set_description(f"Validate ({epoch+1} / {params['n_epochs_trn']} Steps) (dice={0:2.5f})")
#         for step_val, batch_val in enumerate(epoch_val_iterator):
#             # send the validation data to device (GPU)
#             images_val, labels_val = batch_val["image"].to(device), batch_val["label"].to(device)
#             # run inference by forward passing the input data through the model
#             prediction_val = model(images_val)
#             # define and apply transforms
#             y_lbl = torch.where(labels_val < 0.5, torch.tensor(0), torch.tensor(1))
#             y_prd = torch.where(prediction_val < 0.5, torch.tensor(0), torch.tensor(1))
#             # calculate Dice scores and retrieve Dice Score
#             dice_scores[step_val] = params["dice_metric"](y_pred=y_prd, y=y_lbl)
#             dice_scores_mean = dice_scores.mean()
#             #dice_score += params["dice_metric"](y_pred=y_prd, y=y_lbl).item()
#             #params["dice_metric"].reset() # prepare metric for next batch
#             # Update the progress bar description with loss and metrics
#             epoch_val_iterator.set_description(f"Validate ({epoch+1} / {params['n_epochs_trn']} Steps) (dice={dice_scores_mean:2.5f})")
#     # close the iterator
#     epoch_val_iterator.close()
#
#     # Check if this is the best model so far
#     if dice_scores_mean > dice_score_best:
#         print(f"Model at iteration n. {epoch+1} outperforms all previous models. Saving...")
#         # update metric
#         dice_score_best = dice_scores_mean
#         # save model
#         torch.save(model.state_dict(), "best_model.pth")

def visualize_results(inputs, labels, outputs):
    # Convert inputs, labels, and outputs to NumPy arrays
    inputs = inputs.cpu().numpy()
    labels = labels.cpu().numpy()
    outputs = outputs[0].cpu().numpy()  # Assuming a single output, adjust if necessary

    # Visualize the results using MONAI's plot_2d_or_3d_image
    plot_2d_or_3d_image(inputs, cmap="gray", title="Input")
    plot_2d_or_3d_image(labels, cmap="coolwarm", title="Ground Truth")
    plot_2d_or_3d_image(outputs, cmap="coolwarm", title="Predicted")