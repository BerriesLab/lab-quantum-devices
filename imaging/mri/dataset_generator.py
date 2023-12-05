# Studies on Gadolinium concentration in veterinary MRI
# Brain tumors, and other disorders that degrade the blood-brain barrier,
# allow these agents to penetrate into the brain and facilitate their detection by contrast-enhanced MRI
# The aim of the project will be to reduce the overall load of gadolinium to (veterinarian) patients.
# To achieve this, we can generate full dose clinical scan, using deep learning, from lower (50% or even 10%)
# dose scan (see attached paper as an example, there are more out there).
# Henning has already organised that both a 50% and 100% dose scan are acquired in many of the clinical
# scans performed at Tierspital.

from monai.transforms import Compose, LoadImaged, EnsureChannelFirstd, OrientationD, SaveImaged, RandCropByLabelClassesd
from monai.data import CacheDataset, DataLoader

# Define paths
path_dataraw = "\\Users\\berri\\mri\\rawdata"
path_dataset = "\\Users\\berri\\mri\\dataset"
path_dict = [{"image": path_dataraw, "label": path_label}]
params = {"n_crops": 100,
          "n_classes": 2, # for a binary classification (feature vs backgorund) you need two classes
          "class_ratio": [1, 10], # it assumes that 0 (the background) is the first class
          }

# Define transforms for loading and preprocessing the NIfTI files
transforms = Compose([
    #CropLabelledVolumed(keys=["image", "label"]),
    LoadImaged(keys=["image", "label"]),
    EnsureChannelFirstd(keys=["image", "label"]),
    #Spacingd(keys=["image", "label"], pixdim=(dx, dy, dz), mode=("bilinear", "nearest")),
    OrientationD(keys=["image", "label"], axcodes="RAS"),
    #ScaleIntensityRanged(keys=["image"], a_min=params['intensity_min'], a_max=params['intensity_max'], b_min=0.0, b_max=1.0, clip=True),
    RandCropByLabelClassesd(
        keys=["image", "label"],
        label_key="label",
        spatial_size=(64, 64, 64),
        ratios=params["class_ratio"],
        num_classes=params["n_classes"],
        num_samples=params["n_crops"],
        image_threshold=0,
    ),
    SaveImaged(keys=["image", "label"],
               output_dir=path_out,
               separate_folder=False,
               output_postfix=""),

    #ToTensor(),  # Convert the cropped image to a PyTorch tensor
])

dataset = CacheDataset(data=path_dict, transform=transforms)
loader = DataLoader(dataset)
data = {"image": path_dataraw, "label": path_label}
dataset.transform(data)


