import pandas as pd
from imaging.mri.utilities import *
from class_BrainRegisterer import BrainRegisterer

patient_id = 2225172
patient_id = 2228467
patient_id = 2246881  # cannot identify MRIs
patient_id = 2312203  # no MRI brain
patient_id = 2370557
patient_id = 2387681
patient_id = 2413454  # Registration problem
patient_id = 2415056  # cannot identify MRIs
patient_id = 2415148
patient_id = 2415654
patient_id = 2415781
patient_id = 2416015
patient_id = 2416660

# Load data (brain atlas, database...)
atlas = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/atlas/Johnson et al 2019 Canine Atlas v2/Canine_population_template.nii.gz")
df = pd.read_csv("E:/2021_local_data/2023_Gd_synthesis/DICOM/database filtered.csv", sep=";", index_col=False)

# Register pre-contrast image
path = df[(df["patient id"] == patient_id) & (df["contrast dose"] == 0)]["series directory"].values[0]
mri_0t1w = read_dicom_series(path)
path = df[(df["patient id"] == patient_id) & (df["contrast dose"] == 1 / 2)]["series directory"].values[0]
mri_05t1w = read_dicom_series(path)
path = df[(df["patient id"] == patient_id) & (df["contrast dose"] == 1)]["series directory"].values[0]
mri_1t1w = read_dicom_series(path)

brain_registerer = BrainRegisterer(mri_0t1w, mri_05t1w, mri_1t1w, atlas, patient_id)
brain_registerer.execute()





