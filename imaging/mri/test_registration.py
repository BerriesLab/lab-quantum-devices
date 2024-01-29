import numpy as np
import SimpleITK as sitk
from imaging.mri.function_registration import check_registration
import matplotlib.pyplot as plt

D = 5e-3
fix_img = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/fix img.nii.gz")
mov_img = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/mov img.nii.gz")
check_registration(fix_img=fix_img,
                   mov_img=mov_img,
                   slice=[fix_img.GetSize()[0]//2, fix_img.GetSize()[1]//2, fix_img.GetSize()[2]//2],
                   delta_slice=[10, 10, 5],
                   n_slice=3)
plt.show()

mask = sitk.BinaryThreshold(mov_img, lowerThreshold=0.001, insideValue=1)
r = np.array([D * 1e3 / mask.GetSpacing()[0], D * 1e3 / mask.GetSpacing()[1], D * 1e3 / mask.GetSpacing()[2]], dtype=int)
mask_dilated = sitk.BinaryDilate(mask, [int(x) for x in r])

elastixImageFilter = sitk.ElastixImageFilter()
elastixImageFilter.SetFixedImage(fix_img)
elastixImageFilter.SetMovingImage(mov_img)
elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("bspline"))
elastixImageFilter.SetFixedMask(mask)
elastixImageFilter.Execute()
mov_img = elastixImageFilter.GetResultImage()

check_registration(fix_img=fix_img,
                   mov_img=mov_img,
                   slice=[fix_img.GetSize()[0]//2, fix_img.GetSize()[1]//2, fix_img.GetSize()[2]//2],
                   delta_slice=[10, 10, 10],
                   n_slice=3)
plt.show()