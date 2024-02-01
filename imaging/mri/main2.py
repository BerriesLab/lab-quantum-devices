import pandas as pd
from imaging.mri.utilities import *
from function_register_brain_atlas import register_brain_atlas
from function_register_mri import register_mri
from class_BrainRegisterer import BrainRegisterer

# Skull stripping is performed on T1, 1T1 and 1/2T1 MR images. To the purpose of model training,
# save the pairs (skull, brain segment): the brain segment will be used to weight the registration and model training.

# Load data (brain atlas, database...)
# atlas = sitk.ReadImage("/Users/berri/Medical Imaging/mri/brain atlas/canine.nii.gz")
# df = pd.read_csv("/Users/berri/Medical Imaging/mri/database.csv", sep=";", index_col=False)
atlas = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/atlas/Johnson et al 2019 Canine Atlas v2/Canine_population_template.nii.gz")
df = pd.read_csv("E:/2021_local_data/2023_Gd_synthesis/DICOM/database.csv", sep=";", index_col=False)

# filter DataFrame
df = df[df["modality"].str.lower() == "mr"]
df = df.dropna(subset="series description")
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

    # if time interval is smaller than 3 minutes, the time would not be enough for dose administration and imaging,
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

    # Register pre-contrast image
    path = grp[grp["contrast dose"] == 0]["series directory"].values[0]
    mri_0t1w = read_dicom_series(path)
    path = grp[grp["contrast dose"] == 1 / 2]["series directory"].values[0]
    mri_05t1w = read_dicom_series(path)
    path = grp[grp["contrast dose"] == 1]["series directory"].values[0]
    mri_1t1w = read_dicom_series(path)
    brain_registerer = BrainRegisterer(mri_0t1w, mri_05t1w, mri_1t1w, atlas)
    brain_registerer.execute()
    brain_0t1w = register_brain_atlas(fix_img=mri_0t1w, mov_img=atlas)
    sitk.WriteImage(brain_0t1w, f"E:/2021_local_data/2023_Gd_synthesis/tests/{key[1]}_0t1w_mask.nii.gz")
    sitk.WriteImage(mri_0t1w, f"E:/2021_local_data/2023_Gd_synthesis/tests/{key[1]}_0t1w.nii.gz")

    # Register 1/2-dose image


    brain_05t1w = register_brain_atlas(fix_img=mri_05t1w, mov_img=atlas)
    sitk.WriteImage(brain_05t1w, f"E:/2021_local_data/2023_Gd_synthesis/tests/{key[1]}_05t1w_mask.nii.gz")
    sitk.WriteImage(mri_05t1w, f"E:/2021_local_data/2023_Gd_synthesis/tests/{key[1]}_05t1w.nii.gz")

    # Register Full-dose image

    brain_1t1w = register_brain_atlas(fix_img=mri_1t1w, mov_img=atlas)
    sitk.WriteImage(brain_1t1w, f"E:/2021_local_data/2023_Gd_synthesis/tests/{key[1]}_1t1w_mask.nii.gz")
    sitk.WriteImage(mri_1t1w, f"E:/2021_local_data/2023_Gd_synthesis/tests/{key[1]}_1t1w.nii.gz")

    # Image intensity harmonization with Z-Score
    mri_0t1w, mri_05t1w, mri_1t1w = rescale_intensity_zscore([mri_0t1w, mri_05t1w, mri_1t1w])

    # Image registration
    register_mri([mri_0t1w, mri_05t1w, mri_1t1w])

