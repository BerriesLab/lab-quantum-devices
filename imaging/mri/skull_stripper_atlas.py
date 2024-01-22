import pandas as pd
from imaging.mri.utilities import *

# Skull stripping is performed on T1, 1T1 and 1/2T1 MR images. To the purpose of model training,
# save the pairs (skull, brain segment): the brain segment will be used to weight the registration and model training.

# load canine brain atlas
# atlas = sitk.ReadImage("/Users/berri/Medical Imaging/mri/brain atlas/canine.nii.gz")
atlas = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/atlas/Johnson et al 2019 Canine Atlas v2/Canine_population_template.nii.gz")

# load database
# df = pd.read_csv("/Users/berri/Medical Imaging/mri/database.csv", sep=";", index_col=False)
df = pd.read_csv("E:/2021_local_data/2023_Gd_synthesis/DICOM/database.csv", sep=";", index_col=False)
# filter df: drop all rows where "modality" != MR
df = df[df["modality"].str.lower() == "mr"]
# filter df: drop all rows where "series description" == NaN
df = df.dropna(subset="series description")
# filter df: drop all rows where "series description" does not include "T1" and "tra"
# this condition may be updated with a more refined case selection
df = df[(df["series description"].str.contains("t1", case=False,)) &
        (df["series description"].str.contains("tra", case=False,))]
# force datetime dtype for "series datetime" -> required to measure intervals
df["series datetime"] = pd.to_datetime(df["series datetime"], format="%Y.%m.%d %H:%M:%S")

# group data and find series to load in dataset
grouped = df.groupby(["patient species", "patient id"])
for key, grp in grouped:
    # select dogs and make sure there are three T1 series
    if key[0] != "dog" or grp["series description"].count() != 3:
        continue
    # measure intervals between T1 series
    grp = grp.sort_values("series datetime").reset_index()
    grp["interval"] = grp["series datetime"].diff()
    # if time interval is smaller than 3 minutes, the time would not be enough for dose administration and imaging
    # therefore the group must be discarded.
    if grp['interval'].iloc[1:].lt(pd.Timedelta(minutes=3)).any():
        continue
    # add column with contrast dose
    grp["contrast dose"] = [0, 1 / 2, 1]
    # mark the rows as good for dataset
    grp["dataset"] = True
    print(key)
    print(grp[["series description", "series datetime", "direction", "dataset", "contrast dose"]].sort_values("series datetime"))
    print("\n")

    # get nifti image from pre-contrast series T1
    path = grp[grp["contrast dose"] == 0]["series directory"].values[0]
    mri = read_dicom_series(path)

    # register atlas to mr image
    registered = register_brain(fix_img=mri, mov_img=atlas, registration="rigid")
    slice_to_plot = 50

    # Plot the slice using Matplotlib
    plt.figure(figsize=(15, 5))
    # Plot the first image
    plt.subplot(1, 3, 1)
    plt.imshow(sitk.GetArrayFromImage(mri)[slice_to_plot, :, :], cmap='gray')
    plt.title('MR')
    plt.axis('off')  # Turn off axis labels for better visualization

    # Plot the second image
    plt.subplot(1, 3, 2)
    plt.imshow(sitk.GetArrayFromImage(atlas)[slice_to_plot, :, :], cmap='gray')
    plt.title('Atlas')
    plt.axis('off')

    # Plot the third image
    plt.subplot(1, 3, 3)
    plt.imshow(sitk.GetArrayFromImage(mri)[slice_to_plot, :, :], cmap='gray')
    plt.imshow(sitk.GetArrayFromImage(registered)[slice_to_plot, :, :], cmap='jet', alpha=0.5)
    plt.title('??')
    plt.axis('off')
    plt.show()
