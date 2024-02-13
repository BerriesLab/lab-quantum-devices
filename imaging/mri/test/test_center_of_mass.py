from imaging.mri.utilities import *

msk0 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/dataset/2413454 T1wRC0.0.msk.nii")
msk1 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/dataset/2413454 T1wRC0.5.msk.nii")
msk2 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/dataset/2413454 T1wRC1.0.msk.nii")

#mri0 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/dataset/2413454 T1wRC0.0.nii")
#mri1 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/dataset/2413454 T1wRC0.5.nii")
#mri2 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/dataset/2413454 T1wRC1.0.nii")

get_center_of_mass(msk0)

