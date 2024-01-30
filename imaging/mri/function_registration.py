import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from class_BrainAligner import BrainAligner
from utilities import *


def register_brain(fix_img: sitk.Image, mov_img: sitk.Image):
    """
    This function registers a brain atlas (moving image) to an MR image (fixed image).It consists in the following steps:

    1. Rescale intensity of fixed and moving image in the range [0, 1], and resample the moving image to the fixed image
    with a 3D affine transformation. The resulting moving image has same spacings, origin and direction cosines as the fixed image,
    i.e. the fixed and moving image now share the same space.

    2. Match the intensity histogram of the moving image to the intensity histogram of the fixed image. This is
    necessary to make the image intensities comparable.

    3. Initialize the registration by (i) aligning the brain atlas center with the MR image brain center, and (ii) rescaling the brain atlas
    to match approximately the brain in the MR image.

    4. Rigid registration. Register the brain atlas with a rigid transformation. A mask is usd to limit the region available for registration.
    The mask is defined as the atlas brain mask dilated with a 3D ball structuring element of radius 10 mm.

    5 Registration - Elastic."""

    # 1.
    mov_img = sitk.Cast(mov_img, fix_img.GetPixelID())
    fix_img = sitk.RescaleIntensity(fix_img, 0, 1)
    mov_img = sitk.RescaleIntensity(mov_img, 0, 1)

    transform = sitk.AffineTransform(3)
    fix_img_direction_cosines = np.array(fix_img.GetDirection()).reshape((3, 3))
    mov_img_direction_cosines = np.array(mov_img.GetDirection()).reshape((3, 3))
    rotation_matrix = np.dot(mov_img_direction_cosines, np.linalg.inv(fix_img_direction_cosines))
    transform.SetMatrix(rotation_matrix.flatten())
    mov_img = sitk.Resample(image1=mov_img,
                            referenceImage=fix_img,
                            transform=transform,
                            interpolator=sitk.sitkLinear,
                            defaultPixelValue=0,
                            outputPixelType=mov_img.GetPixelIDValue()
                            )
    sitk.WriteImage(fix_img, "E:/2021_local_data/2023_Gd_synthesis/tests/fix img.nii.gz")
    sitk.WriteImage(mov_img, "E:/2021_local_data/2023_Gd_synthesis/tests/mov img.nii.gz")

    # 2.
    mov_img = sitk.HistogramMatching(image=mov_img, referenceImage=fix_img)
    sitk.WriteImage(fix_img, "E:/2021_local_data/2023_Gd_synthesis/tests/fix img.nii.gz")
    sitk.WriteImage(mov_img, "E:/2021_local_data/2023_Gd_synthesis/tests/mov img.nii.gz")

    # 3.
    brain_aligner = BrainAligner(fix_img, mov_img)
    brain_aligner.execute()
    mov_img = sitk.Resample(mov_img, brain_aligner.transform)
    check_registration(fix_img=fix_img,
                       mov_img=mov_img,
                       slice=[brain_aligner.i, brain_aligner.j, brain_aligner.k],
                       delta_slice=[10, 10, 10],
                       n_slice=3)
    sitk.WriteImage(fix_img, "E:/2021_local_data/2023_Gd_synthesis/tests/fix img.nii.gz")
    sitk.WriteImage(mov_img, "E:/2021_local_data/2023_Gd_synthesis/tests/mov img.nii.gz")

    # 4.
    # Create a mask to constrain the moving image to a certain volume
    D = 5e-3  # in mm
    mask = sitk.BinaryThreshold(mov_img, lowerThreshold=0.001, insideValue=1)
    r = np.array([D * 1e3 / mask.GetSpacing()[0], D * 1e3 / mask.GetSpacing()[1], D * 1e3 / mask.GetSpacing()[2]], dtype=int)
    mask_dilated = sitk.BinaryDilate(mask, [int(x) for x in r])
    contour = sitk.BinaryDilate(sitk.BinaryContour(mask_dilated), [2, int(2 * r[1] / r[0]), int(2 * r[2] / r[0])])

    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetFixedImage(fix_img)
    elastixImageFilter.SetMovingImage(mov_img)
    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
    elastixImageFilter.SetFixedMask(mask)
    elastixImageFilter.Execute()
    mov_img = elastixImageFilter.GetResultImage()

    elastixImageFilter.SetFixedImage(fix_img)
    elastixImageFilter.SetMovingImage(mov_img)
    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("bspline"))
    elastixImageFilter.SetFixedMask(mask)
    elastixImageFilter.Execute()
    mov_img = elastixImageFilter.GetResultImage()

    check_registration(fix_img=fix_img,
                       mov_img=mov_img,
                       mask=contour,
                       slice=[fix_img.GetSize()[0] // 2, fix_img.GetSize()[1] // 2, fix_img.GetSize()[2] // 2],
                       delta_slice=[10, 10, 5],
                       n_slice=3)

    return


def check_registration(fix_img: sitk.Image, mov_img: sitk.Image, mask: sitk.Image or None, slice, delta_slice, n_slice):
    """
    Plot xy, xz and yz slices of fixed and moving images overlay. The selected slices are determined
    by the list of n tuples [(i, j, k)_1, (i, j, k)_2 ... (i, j, k)_n], where the i, j, and k represent
    the voxel indices in the image coordinate system. Since the same tuples are used to extract slices of
    both images, and the tuples are selected on the basis of the fixed image properties,
    the plot is ideal to display the quality of the registration.
    """

    # Calculate initial slice
    i0 = slice[0] - (delta_slice[0] * n_slice) // 2
    j0 = slice[1] - (delta_slice[1] * n_slice) // 2
    k0 = slice[2] - (delta_slice[2] * n_slice) // 2

    fig, ax = plt.subplots(n_slice, 3)
    ax = ax.flatten()
    for t, idx in enumerate(np.linspace(0, n_slice + 3, 3, dtype=int)):

        i = int(i0 + delta_slice[0] * idx)
        j = int(j0 + delta_slice[0] * idx)
        k = int(k0 + delta_slice[0] * idx)

        ax[idx + 0].set_title("xy - axial") if idx == 0 else None
        extract_axial_section(ax[idx + 0], fix_img, k, "gray")
        extract_axial_section(ax[idx + 0], mov_img, k, custom_colormap())
        extract_axial_section(ax[idx + 0], mask, k, custom_colormap_for_mask()) if isinstance(mask, sitk.Image) else None

        ax[idx + 1].set_title("xz - coronal") if idx == 0 else None
        extract_coronal_section(ax[idx + 1], fix_img, j, "gray")
        extract_coronal_section(ax[idx + 1], mov_img, j, custom_colormap())
        extract_coronal_section(ax[idx + 1], mask, j, custom_colormap_for_mask()) if isinstance(mask, sitk.Image) else None

        ax[idx + 2].set_title("yz - sagittal") if idx == 0 else None
        extract_sagittal_section(ax[idx + 2], fix_img, i, "gray")
        extract_sagittal_section(ax[idx + 2], mov_img, i, custom_colormap())
        extract_sagittal_section(ax[idx + 2], mask, i, custom_colormap_for_mask()) if isinstance(mask, sitk.Image) else None

        t += 1

    plt.tight_layout()
    plt.show()
