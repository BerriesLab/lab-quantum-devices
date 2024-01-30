import SimpleITK as sitk
from utilities import *


def register_mri(img1: sitk.Image, img2: sitk.Image, img3: sitk.Image):
    """
    This function register img2 and img3 to img1, where:
    - img1: 0T1
    - img2: 1/2T1
    - img3: 1T1
    Note: [dose][experiment][contrast][generation]
    """

    return img1, img2, img3