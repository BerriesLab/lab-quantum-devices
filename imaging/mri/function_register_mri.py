import SimpleITK as sitk
from utilities import *


def register_mri(img1: list[sitk.Image, sitk.Image], img2: list[sitk.Image, sitk.Image]):
    """
    This function register img2 and img3 to img1, where:
    - img1: 0T1
    - img2: 1/2T1
    - img3: 1T1
    Note: [dose][experiment][contrast][generation]. Each img is a tuple, where the 1st element is the actual MR image
    and the 2nd element is the mask that defines the location of the brain.
    """

    # Cast images and masks in the right format
    sitk.Cast(img1[0], sitk.sitkFloat64)
    sitk.Cast(img1[1], sitk.sitkUInt8)
    sitk.Cast(img2[0], sitk.sitkFloat64)
    sitk.Cast(img2[1], sitk.sitkUInt8)

    # Resample img2 and mask in the physical space of img1
    img2[0] = sitk.Resample(image1=img2[0],
                            referenceImage=img1[0],
                            transform=sitk.AffineTransform(3),
                            interpolator=sitk.sitkLinear,
                            defaultPixelValue=0)

    img2[1] = sitk.Resample(image1=img2[1],
                            referenceImage=img1[0],
                            transform=sitk.AffineTransform(3),
                            interpolator=sitk.sitkLinear,
                            defaultPixelValue=0)

    # register img2
    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetFixedImage(img1[0])
    elastixImageFilter.SetMovingImage(img2[0])
    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
    elastixImageFilter.SetFixedMask(img1[1])
    elastixImageFilter.SetMovingMask(img2[1])
    elastixImageFilter.Execute()

    return img2[0]


mri1 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_0t1w.nii.gz")
msk1 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_0t1w_mask.nii.gz")
mri2 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_05t1w.nii.gz")
msk2 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_05t1w_mask.nii.gz")
mri3 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_1t1w.nii.gz")
msk3 = sitk.ReadImage("E:/2021_local_data/2023_Gd_synthesis/tests/2225172_1t1w_mask.nii.gz")

# Image intensity harmonization - with Z-Score?

mri3_reg = register_mri([mri1, msk1], [mri3, msk3])
check_registration(mri1, mri3_reg, None, [int(x // 2) for x in mri1.GetSize()], [10, 10, 5], 3)
check_contrast(mri1, mri3_reg, [int(x // 2) for x in mri1.GetSize()])
