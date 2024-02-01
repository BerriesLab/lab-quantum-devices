import SimpleITK as sitk
from utilities import *
from function_register_mri import *

mri1 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_0t1w.nii.gz")
msk1 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_0t1w_mask.nii.gz")
mri2 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_05t1w.nii.gz")
msk2 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_05t1w_mask.nii.gz")
mri3 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_1t1w.nii.gz")
msk3 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_1t1w_mask.nii.gz")

# Image intensity harmonization - with Z-Score
mri1, mri2, mri3 = rescale_intensity_zscore([mri1, mri2, mri3])
mri1, mri2 = register_mri(mri1, msk1, mri2, msk2)
mri1, mri3 = register_mri(mri1, msk1, mri3, msk3)

check_registration(mri1, mri3, None, [int(x // 2) for x in mri1.GetSize()], [10, 10, 5], 3)
check_contrast(mri1, mri3, [int(x // 2) for x in mri1.GetSize()])
