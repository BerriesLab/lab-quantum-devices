import matplotlib.pyplot as plt
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision.datasets import ImageFolder
from torchvision import transforms
import torch.nn as nn
import os
import nibabel as nib
import glob
from imaging.segmentation.tools.classes_cnn import FeatureCountingCNN, MealwormsCTDataset

params = {'epochs': 1000,}

# STEP1: build dataset. Each sample is a dictionary with (image path, labels path), and no actual data
dir_data = 'T:/data raw/ct/training data'
# dir_imagesTr = os.path.join(dir_data, 'ImagesTr')
# dir_labelsTr = os.path.join(dir_data, 'LabelsTr')
# define training and validation dataset
train_images = sorted(glob.glob(os.path.join(dir_data, "*img.nii.gz")))
train_labels = sorted(glob.glob(os.path.join(dir_data, "*lbl.nii.gz")))
data_dicts = [{"image": image_name, "label": label_name} for image_name, label_name in zip(train_images, train_labels)]
files_train = data_dicts[:-9]
files_valid = data_dicts[-9:]

# *** STEP2 *** DATALOADER
# define the transformer to convert datatype to pytorch tensor and normalize
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean=(0.0,), std=(1.0,))])
# Batch size determines how many samples are loaded into memory and processed together in parallel.
# It affects memory usage, introduces a form of regularization called batch normalization, and time to converge.
batch_size = 1
loader_train = DataLoader(MealwormsCTDataset(files_train, transform=transform), batch_size=batch_size, shuffle=True)
loader_valid = DataLoader(MealwormsCTDataset(files_valid, transform=transform), batch_size=batch_size, shuffle=False)
# test_loader = DataLoader(MealwormsCTDataset(test_data, transform=transform), batch_size=batch_size, shuffle=False)


# check on cuda
device = ("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using {device} device")

# STEP2: create the model, and define the otimizer and loss fuction
# create a model instance of FeatureCountingCNN
model = FeatureCountingCNN()
# define the optimizer and the loss function
optimizer = torch.optim.Adam(model.parameters())
loss_function = nn.L1Loss()

# STEP3: train the CNN
# Set the model to training mode
model.train()
for epoch in range(params['epochs']):
    total_loss = 0.0
    for i, (images, labels) in enumerate(loader_train):
        # the additaional channels are the batch size
        # Zero the parameter gradients. Must be reset manually before startig the calculation for each sample
        optimizer.zero_grad()
        # Forward pass
        outputs = model.forward(images)
        # Calculate the loss
        loss = loss_function(outputs, labels)
        # Backpropagation and optimization
        loss.backward()
        optimizer.step()
        # Print statistics
        total_loss += loss.item()
        if (i + 1) % 100 == 0:
            print(f'Epoch [{epoch + 1}/{params["epochs"]}], Batch [{i + 1}], Loss: {total_loss / 100:.4f}')
            total_loss = 0.0