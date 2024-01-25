import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from class_BrainAligner import BrainAligner
from utilities import custom_colormap


def register_brain(fix_img: sitk.Image, mov_img: sitk.Image):
    """ This function registers a brain atlas (moving image) to an MR image (fixed image).
    To facilitate the registration, the function consists in the following steps:
    1. Resample the moving image to the fixed image by 3D affine transformation. This allows to match the spacings,
    the origins and to align the direction cosines of the moving image to the fixed image.
    2. Match the intensity histogram of the moving image to the intensity histogram of the fixed image. This is
    necessary to make the image intensities consistent.
    3. Initialize the registration by preliminary placing the brain atlas (moving image) in the center of the
    MR image's brain (fixed image). To this purpose, first the MR image is segmented with the Felzenszwalb algorithm.
    To this purpose, we assume that the MR image is centered, such that the brain is approximately in the center
    of the image. Therefore, we segment a 2D axial slice of the MR in the center. We select the region corresponding
    to the brain as the one whose centroid is closest to a reference point, assigned to each anatomical plane
    (sagittal, dorsal and transverse), and representing the average brain’s position.
    ??? This reference point is selected by the user by left-click on the sagittal, dorsal and transverse section of the MR image.???
    4. Registration - Rigid. To reduce computational time and help the registration procedure to focus on the brain region, we
    applied a mask to the fixed target image. The mask is chosen to correspond to the atlas brain mask,
    dilated with a 3D ball structuring element of radius 10 pixels.
    5 Registration - Elastic."""

    # 1. PROJECT ATLAS ON MR IMAGE SPACE
    # Cast the pixel data type of the moving image to the pixel data type of the fixed image
    mov_img = sitk.Cast(mov_img, fix_img.GetPixelID())
    # Rescale the intensity of both images in the default range [0, 255].
    fix_img = sitk.RescaleIntensity(fix_img)
    mov_img = sitk.RescaleIntensity(mov_img)
    # Create a 3D affine transformation (this should take into account for left- and right-handed systems through plane reflexions or inversions)
    transform = sitk.AffineTransform(3)
    # Set the rotation matrix
    fix_img_direction_cosines = np.array(fix_img.GetDirection()).reshape((3, 3))
    mov_img_direction_cosines = np.array(mov_img.GetDirection()).reshape((3, 3))
    rotation_matrix = np.dot(mov_img_direction_cosines, np.linalg.inv(fix_img_direction_cosines))
    transform.SetMatrix(rotation_matrix.flatten())
    # resample the moving image (the brain atlas) to fit the fixed image (MR image) space
    mov_img = sitk.Resample(image1=mov_img,
                            referenceImage=fix_img,
                            transform=transform,
                            interpolator=sitk.sitkLinear,
                            defaultPixelValue=0,
                            outputPixelType=mov_img.GetPixelIDValue()
                            )
    # sitk.WriteImage(mov_img, "E:/2021_local_data/2023_Gd_synthesis/atlas/canine transformed.nii.gz")

    # 2. MATCH INTENSITY HISTOGRAMS
    mov_img = sitk.HistogramMatching(image=mov_img, referenceImage=fix_img)
    check_registration(fix_img, mov_img)
    plt.show()

    # 3. ALIGN ATLAS TO MR IMAGE
    brain_aligner = BrainAligner(fix_img, mov_img)
    brain_aligner.execute()
    check_registration(fix_img, sitk.Resample(mov_img, brain_aligner.transform))
    plt.show()

    # 4. REGISTRATION
    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetFixedImage(fix_img)
    elastixImageFilter.SetMovingImage(mov_img)
    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
    elastixImageFilter.Execute()
    mov_img = elastixImageFilter.GetResultImage()
    check_registration(fix_img, mov_img)
    plt.show()

    # fix_img_slice_xy = sitk.Extract(fix_img, [fix_img.GetSize()[0], fix_img.GetSize()[1], 0], [0, 0, 50])
    # reg_img_slice_xy = sitk.Extract(reg_img, [reg_img.GetSize()[0], reg_img.GetSize()[1], 0], [0, 0, 50])
    # plt.imshow(sitk.GetArrayViewFromImage(fix_img_slice_xy), cmap="grey")
    # plt.imshow(sitk.GetArrayViewFromImage(reg_img_slice_xy), cmap="jet", alpha=0.3)
    # plt.show()

    return


def check_registration(fix_img: sitk.Image, mov_img: sitk.Image, n_slices=3):
    """
    Plot xy, xz and yz slices of fixed and moving images overlay. The selected slices are determined
    by the list of n tuples [(i, j, k)_1, (i, j, k)_2 ... (i, j, k)_n], where the i, j, and k represent
    the voxel indices in the image coordinate system. Since the same tuples are used to extract slices of
    both images, and the tuples are selected on the basis of the fixed image properties,
    the plot is ideal to display the quality of the registration.
    """

    n = np.array(fix_img.GetSize()) // (n_slices + 1)
    fig, ax = plt.subplots(n_slices, 3)
    ax = ax.flatten()
    for t, idx in enumerate(np.linspace(0, n_slices + 3, 3, dtype=int)):

        i = int(n[0] * (t + 1))
        j = int(n[1] * (t + 1))
        k = int(n[2] * (t + 1))

        ax[idx + 0].set_axis_off()
        ax[idx + 0].set_title("xy - axial") if idx == 0 else None
        fix_img_slice = sitk.Extract(fix_img, [fix_img.GetSize()[0], fix_img.GetSize()[1], 0], [0, 0, k])
        mov_img_slice = sitk.Extract(mov_img, [mov_img.GetSize()[0], mov_img.GetSize()[1], 0], [0, 0, k])
        fix_img_extent = [0,
                          (0 + fix_img_slice.GetSize()[0]) * fix_img_slice.GetSpacing()[0],
                          (0 - fix_img_slice.GetSize()[1]) * fix_img_slice.GetSpacing()[1],
                          0]
        mov_img_extent = [0,
                          (0 + mov_img_slice.GetSize()[0]) * mov_img_slice.GetSpacing()[0],
                          (0 - mov_img_slice.GetSize()[1]) * mov_img_slice.GetSpacing()[1],
                          0]
        ax[idx + 0].imshow(sitk.GetArrayFromImage(fix_img_slice), cmap='gray', extent=fix_img_extent)
        ax[idx + 0].imshow(sitk.GetArrayFromImage(mov_img_slice), cmap=custom_colormap(), extent=mov_img_extent)

        ax[idx + 1].set_axis_off()
        ax[idx + 1].set_title("xz - coronal") if idx == 0 else None
        fix_img_slice = sitk.Extract(fix_img, [fix_img.GetSize()[0], 0, fix_img.GetSize()[2]], [0, j, 0])
        mov_img_slice = sitk.Extract(mov_img, [mov_img.GetSize()[0], 0, mov_img.GetSize()[2]], [0, j, 0])
        fix_img_extent = [0,
                          (0 + fix_img_slice.GetSize()[0]) * fix_img_slice.GetSpacing()[0],
                          (0 - fix_img_slice.GetSize()[1]) * fix_img_slice.GetSpacing()[1],
                          0]
        mov_img_extent = [0,
                          (0 + mov_img_slice.GetSize()[0]) * mov_img_slice.GetSpacing()[0],
                          (0 - mov_img_slice.GetSize()[1]) * mov_img_slice.GetSpacing()[1],
                          0]
        ax[idx + 1].imshow(sitk.GetArrayFromImage(fix_img_slice), cmap='gray', extent=fix_img_extent)
        ax[idx + 1].imshow(sitk.GetArrayFromImage(mov_img_slice), cmap=custom_colormap(), extent=mov_img_extent)

        ax[idx + 2].set_axis_off()
        ax[idx + 2].set_title("yz - sagittal") if idx == 0 else None
        fix_img_slice = sitk.Extract(fix_img, [0, fix_img.GetSize()[1], fix_img.GetSize()[2]], [i, 0, 0])
        mov_img_slice = sitk.Extract(mov_img, [0, mov_img.GetSize()[1], mov_img.GetSize()[2]], [i, 0, 0])
        fix_img_extent = [0,
                          (0 + fix_img_slice.GetSize()[0]) * fix_img_slice.GetSpacing()[0],
                          (0 - fix_img_slice.GetSize()[1]) * fix_img_slice.GetSpacing()[1],
                          0]
        mov_img_extent = [0,
                          (0 + mov_img_slice.GetSize()[0]) * mov_img_slice.GetSpacing()[0],
                          (0 - mov_img_slice.GetSize()[1]) * mov_img_slice.GetSpacing()[1],
                          0]
        ax[idx + 2].imshow(sitk.GetArrayFromImage(fix_img_slice), cmap='gray', extent=fix_img_extent)
        ax[idx + 2].imshow(sitk.GetArrayFromImage(mov_img_slice), cmap=custom_colormap(), extent=mov_img_extent)

        t += 1
    plt.tight_layout()