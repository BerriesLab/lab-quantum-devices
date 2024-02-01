import SimpleITK as sitk


def register_mri(img1: sitk.Image, msk1: sitk.Image, img2: sitk.Image, msk2: sitk.Image):
    """
    This function register img2 and img3 to img1, where:
    - img1: 0T1
    - img2: 1/2T1
    - img3: 1T1
    Note: [dose][experiment][contrast][generation]. Each img is a tuple, where the 1st element is the actual MR image
    and the 2nd element is the mask that defines the location of the brain.
    """

    # Cast images and masks in the right format
    img1 = sitk.Cast(img1, sitk.sitkFloat64)
    msk1 = sitk.Cast(msk1, sitk.sitkUInt8)
    img2 = sitk.Cast(img2, sitk.sitkFloat64)
    msk2 = sitk.Cast(msk2, sitk.sitkUInt8)

    # Resample img2 and mask in the physical space of img1
    img2 = sitk.Resample(image1=img2,
                         referenceImage=img1,
                         transform=sitk.AffineTransform(3),
                         interpolator=sitk.sitkLinear,
                         defaultPixelValue=0)

    msk2 = sitk.Resample(image1=msk2,
                         referenceImage=img1,
                         transform=sitk.AffineTransform(3),
                         interpolator=sitk.sitkLinear,
                         defaultPixelValue=0)

    # register img2
    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetFixedImage(img1)
    elastixImageFilter.SetMovingImage(img2)
    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
    elastixImageFilter.SetFixedMask(msk1)
    elastixImageFilter.SetMovingMask(msk2)
    elastixImageFilter.Execute()

    return img1, img2
