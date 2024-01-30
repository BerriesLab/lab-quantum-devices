import SimpleITK as sitk
from utilities import *


def register_mri(img1: tuple[sitk.Image, sitk.Image], img2: tuple[sitk.Image, sitk.Image], img3: tuple[sitk.Image, sitk.Image]):
    """
    This function register img2 and img3 to img1, where:
    - img1: 0T1
    - img2: 1/2T1
    - img3: 1T1
    Note: [dose][experiment][contrast][generation]. Each img is a tuple, where the 1st element is the actual MR image
    and the 2nd element is the mask that defines the location of the brain.
    """

    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetFixedImage(img1[0])
    elastixImageFilter.SetMovingImage(img2[0])
    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
    elastixImageFilter.SetFixedMask(img1[1])
    elastixImageFilter.SetMovingMask(img2[1])
    elastixImageFilter.Execute()
    mov_img = elastixImageFilter.GetResultImage()

    return img1, img2, img3

