import torch.nn as nn
import torch
import os
from torch.utils.data import Dataset
import nibabel as nib
from torchvision import transforms

class MealwormsCTDataset(Dataset):
    # data is a list of dictionary tuples ("image path", "labels path")
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        sample = self.data[idx]
        path_image = sample['image']
        path_label = sample['label']
        image = nib.load(path_image).get_fdata()
        label = nib.load(path_label).get_fdata()
        if self.transform:
            image = self.transform(image)
            label = self.transform(label)
        return image, label


# Define your CNN architecture by creating a class that inherits from nn.Module.
# This class should include the layers and operations you want in your CNN.
class FeatureCountingCNN(nn.Module):
    def __init__(self):
        super(FeatureCountingCNN, self).__init__()

        self.features = nn.Sequential(
            # 1st layer
            # For grayscale images such as CT, input channel is 1.
            nn.AvgPool3d(kernel_size=10, stride=10),
            nn.Conv3d(in_channels=1, out_channels=16, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            # 2nd layer
            nn.AvgPool3d(kernel_size=10, stride=10),
            nn.Conv3d(in_channels=16, out_channels=32, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            # 3rd layer
            nn.AvgPool3d(kernel_size=10, stride=10),
            nn.Conv3d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            # 4th layer
            nn.AvgPool3d(kernel_size=10, stride=10),
            nn.Conv3d(in_channels=64, out_channels=128, kernel_size=3, stride=1, padding=1),
            nn.ReLU(),
            # 5th layer
            nn.AvgPool3d(kernel_size=10, stride=10),
            nn.Conv3d(in_channels=128, out_channels=256, kernel_size=3, stride=1, padding=1),
            nn.ReLU()
        )

        self.classifier = nn.Sequential(
            # Fully connected layers for counting
            nn.Linear(128, 1)  # Output is a single count value
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x
