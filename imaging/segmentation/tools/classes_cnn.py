import os
import glob
import random
import numpy as np
import torch
import nibabel as nib
import tqdm
import datetime
from monai.networks.nets import UNet
from monai.transforms import Compose, LoadImaged, EnsureChannelFirstd, Spacingd, OrientationD, ScaleIntensityRanged, AsDiscreted
from monai.data import CacheDataset, DataLoader
from monai.losses import DiceLoss
from monai.metrics import DiceMetric
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from skimage.color import label2rgb
from skimage.measure import label, regionprops
from skimage.exposure import rescale_intensity

class NNMealworms:
    def __init__(self):
        self.params = {"dir_data_trn": 'C:\\Users\\dabe\\Desktop\\ct\\dataset_trn', # It includes images and labels
                       "dir_data_val": 'C:\\Users\\dabe\\Desktop\\ct\\dataset_val', # It includes images and labels
                       "experiment": datetime.datetime.now(), # datetime of the experiment
                       "data_percentage": 0.1, # percentage of data to use
                       "dataset_trn_ratio": 0.5, # percentage of data used for training
                       "dataset_val_ratio": 0.5, # percentage of data used for validating
                       "dataset_tst_ratio": 0.0, # percentage of data used for testing
                       'batch_trn_size': 1, # number of data per batch
                       'batch_val_size': 1, # number of data per batch
                       'batch_tst_size': 1, # number of data per batch
                       'dataset_trn': {}, # list of dictionary for training the model (compiled by script)
                       'dataset_val': {}, # list of dictionary for validating the model (compiled by script)
                       'dataset_tst': {}, # list of dictionary for testing the model (compiled by script)
                       'dx': 0.3,
                       'dy': 0.3,
                       'dz': 0.4,
                       # MODEL
                       "model": 0, # 0: UNet, 1: ResNet
                       'n_classes': 2, # for this study, the feature is either a mealworm or background, i.e. 2 classes
                       'kernel_size': 3, # size of the convolutional kernel (in pixels)
                       "up_kernel_size": 3, # size of the upsaling kernel
                       "activation_function": torch.nn.ReLU(),
                       "dropout_ratio": 0,
                       'learning_rate': 1e-3, # learning rate of the Adam optimizer
                       'weight_decay': 1e-4, # weight decay of the Adam optimizer
                       "optimizer": 0, # 0: Adam, 1...
                       # TRAINING - VALIDATION
                       'max_iteration_trn': 100, # max iteration for training
                       'delta_iteration_trn': 1, # number of iterations in-between validation
                       'intensity_min': -1000, # min voxel intensity value of CT scan
                       'intensity_max': +1000, # max voxel intensity value of Ct scan
                       'loss_function': DiceLoss(sigmoid=True), # loss function
                       "dice_metric": DiceMetric(include_background=False, reduction="mean", get_not_nans=False), # define loss metric for the validation
                       # PLOTTING
                       "n_crops": 1, # if n_crops = 1 then plot xy, yz, zx planes passing through the center of the validation sample
                       }
        self.transforms_trn = None
        self.transforms_val = None
        self.transforms_tst = None
        self.loader_trn = None
        self.loader_val = None
        self.loader_tst = None
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.check_gpu()

    # extract dx, dy, and dz from a representative sample
    def get_dxdydz(self):
        if not self.params["dataset_trn"]:
            print("Error: dataset_trn is empty. Build datasets first.")
            return
        if not self.params["dataset_val"]:
            print("Error: dataset_val is empty. Build datasets first.")
            return
        if not self.params["dataset_tst"]:
            print("Error: dataset_tst is empty. Build datasets first.")
            return
        self.params["dx"], self.params["dy"], self.params["dz"] = nib.load(self.params["dataset_trn"][0]["img"]).header.get_zooms()

    # define the transformation for the training dataset
    def compose_transforms_trn(self):
        self.transforms_trn = Compose([
            LoadImaged(keys=["img", "lbl"]),
            EnsureChannelFirstd(keys=["img", "lbl"]),
            AsDiscreted(keys=["lbl"], to_onehot=self.params['n_classes']),
            Spacingd(keys=["img", "lbl"], pixdim=(self.params["dx"], self.params["dy"], self.params["dz"]), mode=("bilinear", "nearest")),
            OrientationD(keys=["img", "lbl"], axcodes="RAS"),
            ScaleIntensityRanged(keys=["img"], a_min=self.params['intensity_min'], a_max=self.params['intensity_max'], b_min=0.0, b_max=1.0, clip=True),
        ])

    # define the transformation for the validation dataset
    def compose_transforms_val(self):
        self.transforms_val = Compose([
            LoadImaged(keys=["img", "lbl"]),
            EnsureChannelFirstd(keys=["img", "lbl"]),
            AsDiscreted(keys=["lbl"], to_onehot=self.params['n_classes']),
            Spacingd(keys=["img", "lbl"], pixdim=(self.params["dx"], self.params["dy"], self.params["dz"]), mode=("bilinear", "nearest")),
            OrientationD(keys=["img", "lbl"], axcodes="RAS"),
            ScaleIntensityRanged(keys=["img"], a_min=self.params['intensity_min'], a_max=self.params['intensity_max'], b_min=0.0, b_max=1.0, clip=True),
        ])

    # define the transformation for the testing dataset
    def compose_transforms_tst(self):
        self.transforms_tst = Compose([
            LoadImaged(keys=["img", "lbl"]),
            EnsureChannelFirstd(keys=["img", "lbl"]),
            AsDiscreted(keys=["lbl"], to_onehot=self.params['n_classes']),
            Spacingd(keys=["img", "lbl"], pixdim=(self.params["dx"], self.params["dy"], self.params["dz"]), mode=("bilinear", "nearest")),
            OrientationD(keys=["img", "lbl"], axcodes="RAS"),
            ScaleIntensityRanged(keys=["img"], a_min=self.params['intensity_min'], a_max=self.params['intensity_max'], b_min=0.0, b_max=1.0, clip=True),
        ])

    # build datasets. This function will not cache the data, just build a list of dictionaries for trn, val, and tst
    def buil_dataset(self):
        # Each sample is a dictionary with (image path, labels path), and no actual data
        # define training and validation dataset
        path_images = sorted(glob.glob(os.path.join(self.params["dir_data_trn"], "img*.nii.gz")))
        path_labels = sorted(glob.glob(os.path.join(self.params["dir_data_trn"], "sgm*.nii.gz")))
        path_dicts = [{"img": image_name, "lbl": label_name} for image_name, label_name in zip(path_images, path_labels)]
        # select subset of data
        if self.params["data_percentage"] < 1:
            path_dicts = path_dicts[:int(len(path_dicts) * self.params["data_percentage"])]
        # Calculate the number of samples for each split
        n = len(path_dicts)
        n_tra = int(self.params["dataset_trn_ratio"] * n)
        n_val = int(self.params["dataset_val_ratio"] * n)
        # Shuffle the data list to randomize the order
        random.shuffle(path_dicts)
        # Split the data into training, validation, and testing sets
        self.params["dataset_trn"] = path_dicts[:n_tra]
        self.params["dataset_val"] = path_dicts[n_tra:n_tra + n_val]
        self.params["dataset_tst"] = path_dicts[n_tra + n_val:]

    # cache datasets and generate dataset loaders
    def cache_data(self):
        dataset_trn = CacheDataset(data=self.params["dataset_trn"], transform=self.transforms_trn)
        self.loader_trn = DataLoader(dataset_trn, batch_size=self.params["batch_trn_size"])
        dataset_val = CacheDataset(data=self.params["dataset_val"], transform=self.transforms_val)
        self.loader_val = DataLoader(dataset_val, batch_size=self.params["batch_val_size"])
        dataset_tst = CacheDataset(data=self.params["dataset_tst"], transform=self.transforms_tst)
        self.loader_tst = DataLoader(dataset_tst, batch_size=self.params["batch_tst_size"])

    # build a UNet model
    def build_unet_model(self):
        model = UNet(
            spatial_dims=3,
            in_channels=1,
            out_channels=self.params["n_classes"],
            channels=(64, 128, 256, 512), #sequence of channels. Top block first. The length of channels should be no less than 2
            strides=(2, 2, 2), # sequence of convolution strides. The length of stride should equal to len(channels) - 1.
            kernel_size=self.params["kernel_size"], #convolution kernel size, the value(s) should be odd. If sequence, its length should equal to dimensions. Defaults to 3
            up_kernel_size=self.params["up_kernel_size"], #upsampling convolution kernel size, the value(s) should be odd. If sequence, its length should equal to dimensions. Defaults to 3
            num_res_units=1,#– number of residual units. Defaults to 0.
            #act=params["activation_function"],
            dropout=self.params["dropout_ratio"]
        ).to(self.device)
        self.model = model

    # check gpu availability and print to screen
    def check_gpu(self):
        print(f"Model running on {self.device}")

    # train model
    def train(self):
        # define optimizer
        if self.params["optimizer"] == 0:
            optimizer = torch.optim.AdamW(self.model.parameters(), lr=self.params['learning_rate'], weight_decay=self.params['weight_decay'])
        dice_score_ = -1 # initialize best_metric so that the 1st validation will result the best
        self.model.train() # set the model to training. This has effect only on some transforms
        #xs = np.array([random.randint(0, 200) for _ in range(self.params["n_crops"])])
        #ys = np.array([random.randint(0, 200) for _ in range(self.params["n_crops"])])
        #zs = np.array([random.randint(0, 200) for _ in range(self.params["n_crops"])])
        for epoch in range(self.params["max_iteration_trn"]):
            epoch_loss = 0
            epoch_trn_iterator= tqdm.tqdm(self.loader_trn, desc="Training (X / X Steps) (loss=X.X)", dynamic_ncols=True, miniters=1)
            for step_trn, batch_trn in enumerate(epoch_trn_iterator):
                # send the training data to device (GPU)
                inputs, targets = batch_trn['img'].to(self.device), batch_trn['lbl'].to(self.device)
                # reset the optimizer (which stores the values from the previous iteration
                optimizer.zero_grad()
                # forward pass
                outputs = self.model(inputs)
                loss = self.params["loss_function"](outputs, targets)
                epoch_loss += loss.item()
                # backpropagation
                loss.backward()
                # update metrics
                optimizer.step()
                # Update the progress bar description with loss and metrics
                epoch_trn_iterator.set_description(f"Training ({epoch+1} / {self.params['max_iteration_trn']} Steps) (loss={epoch_loss:2.5f})")
            if (epoch + 1) % self.params["delta_iteration_trn"] == 0 or (epoch + 1) == self.params["max_iteration_trn"]:
                dice_score = self.validate(epoch)
                # Check if this is the best model so far
                if dice_score > dice_score_:
                    dice_score_ = dice_score
                    print(f"Model at iteration n. {epoch+1} outperforms all previous models. Saving...")
                    torch.save(self.model.state_dict(), f"{self.params['dir_data_val']}\\exp_{self.params['experiment'].strftime('%Y.%m.%d_%H.%M.%S')}_iteration_{epoch+1:03d}_mdl.pth")
                    self.visualize_results(epoch)

    # validate model
    def validate(self, epoch):
        self.model.eval() # set the model to validation. This affects some transforms
        with torch.no_grad(): # disable gradient computation (which is useless for validation)
            epoch_val_iterator = tqdm.tqdm(self.loader_val, desc="Validate (X / X Steps) (dice=X.X)", dynamic_ncols=True, miniters=1)
            self.params["dice_metric"].reset()
            for step_val, batch_val in enumerate(epoch_val_iterator):
                # send the validation data to device (GPU)
                img_val, lbl_val = batch_val["img"].to(self.device), batch_val["lbl"].to(self.device)
                # run inference by forward passing the input data through the model
                prd_val = self.model(img_val)
                # update dice score
                self.params["dice_metric"](y_pred=prd_val, y=lbl_val)
                # Update the progress bar description with loss and metrics
                dice_score = self.params["dice_metric"].aggregate().item()
                epoch_val_iterator.set_description(f"Validate ({epoch+1} / {self.params['max_iteration_trn']} Steps) (dice={dice_score:2.5f})")
            return dice_score

    # plot segmentation
    def visualize_results(self, epoch):
        for step_val, batch_val in enumerate(self.loader_val):
            img_val, lbl_val = batch_val["img"].to(self.device), batch_val["lbl"].to(self.device)
            prd_val = self.model(img_val)
            # convert tensors from one hot encoding to single channel
            img_array = batch_val["img"].numpy()[0, 0, :, :, :]
            lbl_array_val = torch.argmax(batch_val["lbl"], dim=1).numpy()[0, :, :, :]
            lbl_array_prd = torch.argmax(prd_val, dim=1).numpy()[0, :, :, :]
            print(f"Plotting sample {step_val}...")
            # Find the (x,y,z) coordinates of the sample center
            x = int(np.floor(batch_val["img"].shape[2] / 2))
            y = int(np.floor(batch_val["img"].shape[3] / 2))
            z = int(np.floor(batch_val["img"].shape[4] / 2))
            lbl_array_val = label(lbl_array_val, connectivity=1)
            lbl_array_prd = label(lbl_array_prd, connectivity=1)
            # Generate overlay images
            img_array_x = img_array[x, :, :]
            img_array_y = img_array[:, y, :]
            img_array_z = img_array[:, :, z]
            lbl_array_x_val = lbl_array_val[x, :, :]
            lbl_array_y_val = lbl_array_val[:, y, :]
            lbl_array_z_val = lbl_array_val[:, :, z]
            lbl_array_x_prd = lbl_array_prd[x, :, :]
            lbl_array_y_prd = lbl_array_prd[:, y, :]
            lbl_array_z_prd = lbl_array_prd[:, :, z]
            img_label_overlay_x_val = label2rgb(label=lbl_array_x_val, image=rescale_intensity(img_array_x, out_range=(0, 1)), alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
            img_label_overlay_y_val = label2rgb(label=lbl_array_y_val, image=rescale_intensity(img_array_y, out_range=(0, 1)), alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
            img_label_overlay_z_val = label2rgb(label=lbl_array_z_val, image=rescale_intensity(img_array_z, out_range=(0, 1)), alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
            img_label_overlay_x_prd = label2rgb(label=lbl_array_x_prd, image=rescale_intensity(img_array_x, out_range=(0, 1)), alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
            img_label_overlay_y_prd = label2rgb(label=lbl_array_y_prd, image=rescale_intensity(img_array_y, out_range=(0, 1)), alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
            img_label_overlay_z_prd = label2rgb(label=lbl_array_z_prd, image=rescale_intensity(img_array_z, out_range=(0, 1)), alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
            #blend = blend_images(image=batch_trn["image"], label=batch_trn["label"], alpha=0.3, cmap="gray", transparent_background=True)
            fig, axs = plt.subplots(2, ncols=3)
            axs[0, 0].set_title(f"YZ plane at X = {x} px")
            axs[0, 0].imshow(img_label_overlay_x_val)
            axs[1, 0].imshow(img_label_overlay_x_prd)
            axs[0, 1].set_title(f"XZ plane at Y = {y} px")
            axs[0, 1].imshow(img_label_overlay_y_val)
            axs[1, 1].imshow(img_label_overlay_y_prd)
            axs[0, 2].set_title(f"XY plane at Z = {z} px")
            axs[0, 2].imshow(img_label_overlay_z_val)
            axs[1, 2].imshow(img_label_overlay_z_prd)
            #Add rectangles around regions
            regions = regionprops(lbl_array_x_prd)
            for region in regions:
                minr, minc, maxr, maxc = region.bbox
                rect = Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=0.3)
                axs[1, 0].add_patch(rect)
            regions = regionprops(lbl_array_y_prd)
            for region in regions:
                minr, minc, maxr, maxc = region.bbox
                rect = Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=0.3)
                axs[1, 1].add_patch(rect)
            regions = regionprops(lbl_array_z_prd)
            for region in regions:
                minr, minc, maxr, maxc = region.bbox
                rect = Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=0.3)
                axs[1, 2].add_patch(rect)
            # Remove x-axis and y-axis ticks, labels, and tick marks for all subplots
            for ax in axs.flat:
                ax.set_xticks([])
                ax.set_yticks([])
                ax.set_xticklabels([])
                ax.set_yticklabels([])
            # Adjust layout for better spacing
            plt.tight_layout()
            # Save the figure to a file
            plt.savefig(os.path.join(self.params["dir_data_val"], f"plt_img_{step_val:02d}_iteration_{epoch+1:03d}_xyz_{x,y,z}.png"), dpi=1200)
            plt.close()