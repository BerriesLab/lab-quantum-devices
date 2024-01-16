import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import SimpleITK as sitk
from utilities import convert_dicom_to_nifti

# Skull stripping is performed on T1, 1T1 and 1/2T1 MR images. To the purpose of model training,
# save the pairs (skull, brain segment): the brain segment will be used to weight the registration and model training.

# load canine brain atlas
atlas = sitk.ReadImage("/Users/berri/Medical Imaging/mri/brain atlas/canine.nii.gz")
img = sitk.GetArrayFromImage(atlas)
# get atlas spacing
atlas_spacing = atlas.GetSpacing()

# load database
df = pd.read_csv("/Users/berri/Medical Imaging/mri/database.csv", sep=";", index_col=False)
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
    path = grp[grp["contrast dose"] == 0]["series directory"]
    mri = sitk.ReadImage(path)


    #convert_dicom_to_nifti(grp["series directory"],



# df = df.dropna(subset="series description")[(df["modality"].str.lower() == "mr") and
#                                             (df["series description"].str.contains("tra t1", case=False)) and
#                                             (df["patient species"].str.lower() == "dog")]