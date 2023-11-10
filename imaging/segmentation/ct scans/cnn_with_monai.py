import matplotlib.pyplot as plt
import matplotlib.animation as animation
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
from monai.visualize import plot_2d_or_3d_image, blend_images, matshow3d
from monai.inferers import sliding_window_inference

# define parameters
params = {# DATA
          "dir_data_trn": 'C:\\Users\\dabe\\Desktop\\ct\\training_data', # It includes images and labels
          "dir_data_val": 'C:\\Users\\dabe\\Desktop\\ct\\validation_data', # It includes images and labels
          "experiment": datetime.datetime.now(), # datetime of the experiment
          "trn_ratio": 0.7, # percentage of data used for training
          "val_ratio": 0.15, # percentage of data used for validating
          "tst_ratio": 0.15, # percentage of data used for testing
          "data_percentage": 0.3, # percentage of data to use
          'batch_trn_size': 2, # number of data per batch
          'batch_val_size': 1, # number of data per batch
          'batch_tst_size': 1, # number of data per batch
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
          'val_interval': 1, # number of iterations in-between validation
          'intensity_min': -1000, # min voxel intensity value of CT scan
          'intensity_max': +1000, # max voxel intensity value of Ct scan
          'loss_function': DiceLoss(sigmoid=True), # loss function
          "dice_metric": DiceMetric(include_background=True), # define loss metric for the validation
          # PLOTTING
          "n_crops": 5,
}

#region STEP1: build dataset.
# Each sample is a dictionary with (image path, labels path), and no actual data
# define training and validation dataset
path_images = sorted(glob.glob(os.path.join(params["dir_data_trn"], "*img.nii.gz")))
path_labels = sorted(glob.glob(os.path.join(params["dir_data_trn"], "*lbl.nii.gz")))
path_dicts = [{"image": image_name, "label": label_name} for image_name, label_name in zip(path_images, path_labels)]
# select subset of data
if params["data_percentage"] < 1:
    path_dicts = path_dicts[:int(len(path_dicts) * params["data_percentage"])]
# define training, validation and test sets.
sets = ["training", "validation", "test"]
# Calculate the number of samples for each split
n = len(path_dicts)
n_tra = int(params["trn_ratio"] * n)
n_val = int(params["val_ratio"] * n)
n_tes = n - n_tra - n_val
# Shuffle the data list to randomize the order
random.shuffle(path_dicts)
# Split the data into training, validation, and testing sets
params["set_trn"] = path_dicts[:n_tra]
params["set_val"] = path_dicts[n_tra:n_tra + n_val]
params["set_tst"] = path_dicts[n_tra + n_val:]
# get voxel size, assuming that all nifti files have the same specs
dx, dy, dz = nibabel.load(params["set_trn"][0]["image"]).header.get_zooms()
#endregion

#region STEP2: define transforms for training, validation and testing.
# Transforms_training could include operation aimed at incrasing the sample size, such as noising, flipping, rotating etc.
transforms_trn = Compose([
    LoadImaged(keys=["image", "label"]),
    EnsureChannelFirstd(keys=["image", "label"]),
    Spacingd(keys=["image", "label"], pixdim=(dx, dy, dz), mode=("bilinear", "nearest")),
    OrientationD(keys=["image", "label"], axcodes="RAS"),
    ScaleIntensityRanged(keys=["image"], a_min=params['intensity_min'], a_max=params['intensity_max'], b_min=0.0, b_max=1.0, clip=True),
])

transforms_val = Compose([
    LoadImaged(keys=["image", "label"]),
    EnsureChannelFirstd(keys=["image", "label"]),
    Spacingd(keys=["image", "label"], pixdim=(dx, dy, dz), mode=("bilinear", "nearest")),
    OrientationD(keys=["image", "label"], axcodes="RAS"),
    ScaleIntensityRanged(keys=["image"], a_min=params['intensity_min'], a_max=params['intensity_max'], b_min=0.0, b_max=1.0, clip=True),
])

transforms_tst = transforms_val
# endregion

#region STEP3: Load datasets
dataset_trn = CacheDataset(data=params["set_trn"], transform=transforms_trn)
loader_trn = DataLoader(dataset_trn, batch_size=params["batch_trn_size"])
dataset_val = CacheDataset(data=params["set_val"], transform=transforms_val)
loader_val = DataLoader(dataset_val, batch_size=params["batch_val_size"])
dataset_tst = CacheDataset(data=params["set_tst"], transform=transforms_tst)
loader_tst = DataLoader(dataset_tst, batch_size=params["batch_tst_size"])
# endregion

#region STEP4: Create e U-Net model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Model running on {device}")
model = UNet(
    spatial_dims=3,
    in_channels=1,
    out_channels=params["n_classes"],
    channels=(64, 128, 256), #sequence of channels. Top block first. The length of channels should be no less than 2
    strides=(2, 2,), # sequence of convolution strides. The length of stride should equal to len(channels) - 1.
    kernel_size=params["kernel_size"], #convolution kernel size, the value(s) should be odd. If sequence, its length should equal to dimensions. Defaults to 3
    up_kernel_size=params["up_kernel_size"], #upsampling convolution kernel size, the value(s) should be odd. If sequence, its length should equal to dimensions. Defaults to 3
    num_res_units=1,#– number of residual units. Defaults to 0.
    #act=params["activation_function"],
    dropout=params["dropout_ratio"]
).to(device)
#endregion

#region STEP5: Model training
# define optimizer
if params["optimizer"] == 0:
    optimizer = torch.optim.AdamW(model.parameters(), lr=params['learning_rate'], weight_decay=params['weight_decay'])
dice_score_best = -1 # initialize best_metric so that the 1st validation will result the best
model.train() # set the model to training. This has effect only on some transforms
for epoch in range(params["n_epochs_trn"]):
    epoch_loss = 0
    epoch_trn_iterator= tqdm.tqdm(loader_trn, desc="Training (X / X Steps) (loss=X.X)", dynamic_ncols=True)
    epoch_trn_iterator.set_description(f"Training ({epoch+1} / {params['n_epochs_trn']} Steps) (loss={0:2.5f})")
    for step_trn, batch_trn in enumerate(epoch_trn_iterator):
        # send the training data to device (GPU)
        inputs, targets = batch_trn['image'].to(device), batch_trn['label'].to(device)
        # reset the optimizer (which stores the values from the previous iteration
        optimizer.zero_grad()
        # forward pass
        outputs = model(inputs)
        loss = params["loss_function"](outputs, targets)
        epoch_loss += loss.item()
        # backpropagation
        loss.backward()
        # update metrics
        optimizer.step()
        # Update the progress bar description with loss and metrics
        epoch_trn_iterator.set_description(f"Training ({epoch+1} / {params['n_epochs_trn']} Steps) (loss={epoch_loss:2.5f})")
    # close the iterator
    epoch_trn_iterator.close()

    if (epoch + 1) % params["val_interval"] == 0 or (epoch + 1) == params["n_epochs_trn"]:
        model.eval() # set the model to validation. This affects some transforms
        with torch.no_grad(): # disable gradient computation (which is useless for validation)
            dice_scores = np.zeros(len(loader_val))# = 0.0
            epoch_val_iterator = tqdm.tqdm(loader_val, desc="Validate (X / X Steps) (dice=X.X)", dynamic_ncols=True)
            epoch_val_iterator.set_description(f"Validate ({epoch+1} / {params['n_epochs_trn']} Steps) (dice={0:2.5f})")
            for step_val, batch_val in enumerate(epoch_val_iterator):
                # send the validation data to device (GPU)
                images_val, labels_val = batch_val["image"].to(device), batch_val["label"].to(device)
                # run inference by forward passing the input data through the model
                prediction_val = model(images_val)
                # define and apply transforms
                y_lbl = torch.where(labels_val < 0.5, torch.tensor(0), torch.tensor(1))
                y_prd = torch.where(prediction_val < 0.5, torch.tensor(0), torch.tensor(1))
                # calculate Dice scores and retrieve Dice Score
                dice_scores[step_val] = params["dice_metric"](y_pred=y_prd, y=y_lbl)
                dice_scores_mean = dice_scores.mean()
                #dice_score += params["dice_metric"](y_pred=y_prd, y=y_lbl).item()
                #params["dice_metric"].reset() # prepare metric for next batch
                # Update the progress bar description with loss and metrics
                epoch_val_iterator.set_description(f"Validate ({epoch+1} / {params['n_epochs_trn']} Steps) (dice={dice_scores_mean:2.5f})")
        # close the iterator
        epoch_val_iterator.close()

        # Check if this is the best model so far
        if dice_scores_mean > dice_score_best:
            print(f"Model at iteration n. {epoch+1} outperforms all previous models. Saving...")
            # update metric
            dice_score_best = dice_scores_mean
            # save model
            torch.save(model.state_dict(), f"{params['dir_data_val']}\\experiment {params['experiment'].strftime('%Y.%m.%d %H.%M.%S')} - iteration {epoch+1:03d} - model.pth")

            # Plot the input image, ground truth, and predicted output
            ret_lbl = blend_images(image=images_val[0], label=labels_val[0], alpha=0.3, cmap="hsv", rescale_arrays=False)
            ret_prd = blend_images(image=images_val[0], label=prediction_val[0], alpha=0.3, cmap="hsv", rescale_arrays=False)
            xs = np.array([random.randint(0, images_val.shape[2]) for _ in range(params["n_crops"])])
            ys = np.array([random.randint(0, images_val.shape[3]) for _ in range(params["n_crops"])])
            zs = np.array([random.randint(0, images_val.shape[4]) for _ in range(params["n_crops"])])
            for i in range(params["n_crops"]):
                fig, axs = plt.subplots(2, ncols=3)
                # find a random point inside the image
                x = xs[i]
                y = ys[i]
                z = zs[i]
                axs[0, 0].set_title(f"YZ plane at X = {x} px")
                axs[0, 0].imshow(torch.moveaxis(ret_lbl[:, :, :, z], 0, -1))
                axs[1, 0].imshow(torch.moveaxis(ret_prd[:, :, :, z], 0, -1))
                axs[0, 1].set_title(f"XZ plane at Y = {y} px")
                axs[0, 1].imshow(torch.moveaxis(ret_lbl[:, :, y, :], 0, -1))
                axs[1, 1].imshow(torch.moveaxis(ret_prd[:, :, y, :], 0, -1))
                axs[0, 2].set_title(f"XY plane at Z = {z} px")
                axs[0, 2].imshow(torch.moveaxis(ret_lbl[:, x, :, :], 0, -1))
                axs[1, 2].imshow(torch.moveaxis(ret_prd[:, x, :, :], 0, -1))
                # Remove x-axis and y-axis ticks, labels, and tick marks for all subplots
                for ax in axs.flat:
                    ax.set_xticks([])
                    ax.set_yticks([])
                    ax.set_xticklabels([])
                    ax.set_yticklabels([])
                # Adjust layout for better spacing
                plt.tight_layout()
                # Save the figure to a file
                plt.savefig(f"{params['dir_data_val']}\\experiment {params['experiment'].strftime('%Y.%m.%d %H.%M.%S')} - iteration {epoch+1:03d} - xyz {x,y,z}.png", dpi=1200)
#endregion
