import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from class_BrainAligner import BrainAligner
from utilities import custom_colormap


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

    # 2.
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

    # 3.
    mov_img = sitk.HistogramMatching(image=mov_img, referenceImage=fix_img)
    #check_registration(fix_img, mov_img)
    #plt.show()
    sitk.WriteImage(fix_img, "E:/2021_local_data/2023_Gd_synthesis/tests/fix img.nii.gz")
    sitk.WriteImage(mov_img, "E:/2021_local_data/2023_Gd_synthesis/tests/mov img.nii.gz")

    # 4.
    brain_aligner = BrainAligner(fix_img, mov_img)
    brain_aligner.execute()
    mov_img = sitk.Resample(mov_img, brain_aligner.transform)
    check_registration(fix_img=fix_img,
                       mov_img=mov_img,
                       slice=[brain_aligner.i, brain_aligner.j, brain_aligner.k],
                       delta_slice=[10, 10, 10],
                       n_slice=3)
    plt.show()
    sitk.WriteImage(fix_img, "E:/2021_local_data/2023_Gd_synthesis/tests/fix img.nii.gz")
    sitk.WriteImage(mov_img, "E:/2021_local_data/2023_Gd_synthesis/tests/mov img.nii.gz")

    # 4. REGISTRATION
    # Run first a rigid registration - This step may be unnecessary, depending on the goodness of the user-input alignment.
    mask = sitk.BinaryThreshold(mov_img, lowerThreshold=0.001, insideValue=1)
    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetFixedImage(fix_img)
    elastixImageFilter.SetMovingImage(mov_img)
    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
    elastixImageFilter.SetFixedMask(mask)
    elastixImageFilter.Execute()
    mov_img = elastixImageFilter.GetResultImage()
    check_registration(fix_img=fix_img,
                       mov_img=mov_img,
                       slice=[brain_aligner.i, brain_aligner.j, brain_aligner.k],
                       delta_slice=[10, 10, 10],
                       n_slice=3)
    plt.show()

    # Run an elastic registration, limiting the volume to a certain percentage of the initial brain atlas volume.
    # Find the bounding box of the brain atlas segmentation, and use an upscaled version of it to define the volume of the fix image
    # available for registration.
    binary_mask = sitk.BinaryThreshold(mov_img, lowerThreshold=0.001, insideValue=1)
    stats_filter = sitk.LabelStatisticsImageFilter()
    stats_filter.Execute(binary_mask, binary_mask)
    bounding_boxes = stats_filter.GetBoundingBox(label=1)


    #bounding_box = sitk.RegionOfInterest(binary_mask, binary_mask.GetBoundingBox(label=0))

    elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("bspline"))
    # Add custom constraint to limit volume change
    #parameter_map["MaximumNumberOfIterations"] = ["200"]
    #parameter_map["GridSpacingSchedule"] = ["8", "6", "4"]
    elastixImageFilter.Execute()
    mov_img = elastixImageFilter.GetResultImage()
    check_registration(fix_img=fix_img,
                       mov_img=mov_img,
                       slice=[brain_aligner.i, brain_aligner.j, brain_aligner.k],
                       delta_slice=[10, 10, 10],
                       n_slice=3)
    plt.show()

    # fix_img_slice_xy = sitk.Extract(fix_img, [fix_img.GetSize()[0], fix_img.GetSize()[1], 0], [0, 0, 50])
    # reg_img_slice_xy = sitk.Extract(reg_img, [reg_img.GetSize()[0], reg_img.GetSize()[1], 0], [0, 0, 50])
    # plt.imshow(sitk.GetArrayViewFromImage(fix_img_slice_xy), cmap="grey")
    # plt.imshow(sitk.GetArrayViewFromImage(reg_img_slice_xy), cmap="jet", alpha=0.3)
    # plt.show()

    return


def check_registration(fix_img: sitk.Image, mov_img: sitk.Image, slice, delta_slice, n_slice):
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
        print(i, j, k)

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