import numpy as np
import SimpleITK as sitk
from skimage.segmentation import felzenszwalb
import matplotlib.pyplot as plt
from aligner import BrainAligner


def cosines_to_patient(direction_cosines):
    # Convert the direction cosines to a 3x2 matrix
    matrix = np.array(direction_cosines).reshape((3, 2))
    # Determine orientation labels
    orientation_labels = []

    # determines the sign of the angle between the image first row and the right-to-left patient direction
    if matrix[0, 0] > 0:
        orientation_labels.append('R')
    elif matrix[0, 0] < 0:
        orientation_labels.append('L')

    # determines the sign of the angle between the image first column and the anterior-to-posterior patient direction
    if matrix[1, 1] > 0:
        orientation_labels.append('A')
    elif matrix[1, 1] < 0:
        orientation_labels.append('P')

    # determines the sign of the angle between the image first row and the head(S)-to-feet(I) patient direction
    if matrix[2, 0] > 0:
        orientation_labels.append('S')
    elif matrix[2, 0] < 0:
        orientation_labels.append('I')

    # Join orientation labels to get the final orientation
    orientation = ''.join(orientation_labels)

    return orientation


def read_dicom_series(path_dicom_series):
    """Read a DICOM series and convert it to 3D nifti image"""
    # Load the DICOM series
    reader = sitk.ImageSeriesReader()
    dicom_series = reader.GetGDCMSeriesFileNames(path_dicom_series)
    reader.SetFileNames(dicom_series)
    image = reader.Execute()
    # Convert the SimpleITK image to NIfTI format in memory
    # nifti_image = sitk.GetImageFromArray(sitk.GetArrayFromImage(image))
    # nifti_image.CopyInformation(image)
    # Convert the SimpleITK image to NIfTI format
    # sitk.WriteImage(image, path_nifti)
    return image


def register_brain(fix_img: sitk.Image, mov_img: sitk.Image, registration="rigid"):
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

    # 1. Resampling
    # Cast the pixel data type of the moving image to the pixel data type of the fixed image
    mov_img = sitk.Cast(mov_img, fix_img.GetPixelID())
    # Rescale the intensity to set min value (or background) equal to 0.
    mov_img = sitk.RescaleIntensity(mov_img, outputMinimum=0, outputMaximum=np.max(sitk.GetArrayViewFromImage(mov_img)))
    # Create a 3D affine transformation (this should take into account for left- and right-handed systems
    # through plane reflexions or inversions)
    transform = sitk.AffineTransform(3)
    # Set the translation, i.e. the difference between origins
    # This translation leads to an error (a black image): comment the line for avoiding translation
    # transform.SetTranslation(np.array(fix_img.GetOrigin()) - np.array(mov_img.GetOrigin()))
    # Set the center of rotation to the center of the fixed image
    # transform.SetCenter(fix_img.TransformContinuousIndexToPhysicalPoint([index / 2.0 for index in fix_img.GetSize()]))
    # Set the rotation matrix
    fix_img_direction_cosines = np.array(fix_img.GetDirection()).reshape((3, 3))
    mov_img_direction_cosines = np.array(mov_img.GetDirection()).reshape((3, 3))
    # WRONG? rotation_matrix = np.dot(np.linalg.inv(fix_img_direction_cosines), mov_img_direction_cosines)
    rotation_matrix = np.dot(mov_img_direction_cosines, np.linalg.inv(fix_img_direction_cosines))
    transform.SetMatrix(rotation_matrix.flatten())
    # resample the moving image (the brain atlas) to fit the fixed image (MR image) space
    mov_img = sitk.Resample(image1=mov_img,  # image to resample
                            referenceImage=fix_img,  # reference image
                            transform=transform,
                            interpolator=sitk.sitkLinear,
                            defaultPixelValue=0.0)  # type of interpolation
    sitk.WriteImage(mov_img, "E:/2021_local_data/2023_Gd_synthesis/atlas/canine transformed.nii.gz")

    # 2. MATCH INTENSITY HISTOGRAMS
    mov_img = sitk.HistogramMatching(image=mov_img, referenceImage=fix_img)
    check_registration(fix_img, mov_img)
    plt.show()

    brain_aligner = BrainAligner(fix_img, mov_img)
    brain_aligner.execute()
    check_registration(fix_img, sitk.Resample(mov_img, brain_aligner.transform))
    plt.show()

    # brain_aligner.transform

    # # 6. REGISTRATION
    # elastixImageFilter = sitk.ElastixImageFilter()
    # elastixImageFilter.SetFixedImage(fix_img)
    # elastixImageFilter.SetMovingImage(mov_img)
    # elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
    # elastixImageFilter.Execute()
    # reg_img = elastixImageFilter.GetResultImage()
    #
    # fix_img_slice_xy = sitk.Extract(fix_img, [fix_img.GetSize()[0], fix_img.GetSize()[1], 0], [0, 0, 50])
    # reg_img_slice_xy = sitk.Extract(reg_img, [reg_img.GetSize()[0], reg_img.GetSize()[1], 0], [0, 0, 50])
    # plt.imshow(sitk.GetArrayViewFromImage(fix_img_slice_xy), cmap="grey")
    # plt.imshow(sitk.GetArrayViewFromImage(reg_img_slice_xy), cmap="jet", alpha=0.3)
    # plt.show()

    return


def extract_sagittal_section(img: sitk.Image, n=None):
    """It assumes a 3D image"""
    size = img.GetSize()
    spacing = img.GetSpacing()
    if n is None:
        n = int(size[0]/2)
    img_slice = sitk.Extract(img, [0, size[1], size[2]], [n, 0, 0])
    plt.figure()
    plt.imshow(sitk.GetArrayFromImage(img_slice), cmap='gray', aspect=spacing[2] / spacing[1])
    plt.axis("off")
    plt.title("sagittal")


def extract_coronal_section(img: sitk.Image, n=None):
    """It assumes a 3D image"""
    size = img.GetSize()
    spacing = img.GetSpacing()
    if n is None:
        n = int(size[1]/2)
    img_slice = sitk.Extract(img, [size[0], 0, size[2]], [0, n, 0])
    plt.figure()
    plt.imshow(sitk.GetArrayFromImage(img_slice), cmap='gray', aspect=spacing[2] / spacing[0])
    plt.axis("off")
    plt.title("coronal")


def extract_axial_section(img: sitk.Image, n=None):
    """It assumes a 3D image"""
    size = img.GetSize()
    spacing = img.GetSpacing()
    if n is None:
        n = int(size[2] / 2)
    img_slice = sitk.Extract(img, [size[0], size[1], 0], [0, 0, n])
    plt.figure()
    plt.imshow(sitk.GetArrayFromImage(img_slice), cmap='gray', aspect=spacing[1] / spacing[0])
    plt.axis("off")
    plt.title("axial")


def check_registration(fix_img: sitk.Image, mov_img: sitk.Image):
    """It assumes that the """
    slice = [int(x // 2) for x in fix_img.GetSize()]
    fig, ax = plt.subplots(1, 3)
    for item in ax.flatten():
        item.set_axis_off()

    ax[0].set_title("xy - axial")
    fix_img_slice = sitk.Extract(fix_img, [fix_img.GetSize()[0], fix_img.GetSize()[1], 0], [0, 0, slice[2]])
    mov_img_slice = sitk.Extract(mov_img, [mov_img.GetSize()[0], mov_img.GetSize()[1], 0], [0, 0, slice[2]])
    fix_img_extent = [0,
                      (0 + fix_img_slice.GetSize()[0]) * fix_img_slice.GetSpacing()[0],
                      (0 - fix_img_slice.GetSize()[1]) * fix_img_slice.GetSpacing()[1],
                      0]
    mov_img_extent = [0,
                      (0 + mov_img_slice.GetSize()[0]) * mov_img_slice.GetSpacing()[0],
                      (0 - mov_img_slice.GetSize()[1]) * mov_img_slice.GetSpacing()[1],
                      0]
    ax[0].imshow(sitk.GetArrayFromImage(fix_img_slice), cmap='gray', extent=fix_img_extent)
    ax[0].imshow(sitk.GetArrayFromImage(mov_img_slice), cmap='jet', alpha=0.3, extent=mov_img_extent)

    ax[1].set_title("xz - coronal")
    fix_img_slice = sitk.Extract(fix_img, [fix_img.GetSize()[0], 0, fix_img.GetSize()[2]], [0, slice[1], 0])
    mov_img_slice = sitk.Extract(mov_img, [mov_img.GetSize()[0], 0, mov_img.GetSize()[2]], [0, slice[1], 0])
    fix_img_extent = [0,
                      (0 + fix_img_slice.GetSize()[0]) * fix_img_slice.GetSpacing()[0],
                      (0 - fix_img_slice.GetSize()[1]) * fix_img_slice.GetSpacing()[1],
                       0]
    mov_img_extent = [0,
                      (0 + mov_img_slice.GetSize()[0]) * mov_img_slice.GetSpacing()[0],
                      (0 - mov_img_slice.GetSize()[1]) * mov_img_slice.GetSpacing()[1],
                      0]
    ax[1].imshow(sitk.GetArrayFromImage(fix_img_slice), cmap='gray', extent=fix_img_extent)
    ax[1].imshow(sitk.GetArrayFromImage(mov_img_slice), cmap='jet', alpha=0.3, extent=mov_img_extent)

    ax[2].set_title("yz - sagittal")
    fix_img_slice = sitk.Extract(fix_img, [0, fix_img.GetSize()[1], fix_img.GetSize()[2]], [slice[0], 0, 0])
    mov_img_slice = sitk.Extract(mov_img, [0, mov_img.GetSize()[1], mov_img.GetSize()[2]], [slice[0], 0, 0])
    fix_img_extent = [0,
                      (0 + fix_img_slice.GetSize()[0]) * fix_img_slice.GetSpacing()[0],
                      (0 - fix_img_slice.GetSize()[1]) * fix_img_slice.GetSpacing()[1],
                       0]
    mov_img_extent = [0,
                      (0 + mov_img_slice.GetSize()[0]) * mov_img_slice.GetSpacing()[0],
                      (0 - mov_img_slice.GetSize()[1]) * mov_img_slice.GetSpacing()[1],
                      0]
    ax[2].imshow(sitk.GetArrayFromImage(fix_img_slice), cmap='gray', extent=fix_img_extent)
    ax[2].imshow(sitk.GetArrayFromImage(mov_img_slice), cmap='jet', alpha=0.3, extent=mov_img_extent)

    plt.tight_layout()


# Function to display slices and allow user to mark a point
def mark_slice(img: sitk.Image, n0, n, dn, direction="axial"):
    """Plot a number n of slices, separated by dn slices, where the central slice is centered on
    slice number n0. If you want to have n0 in the center of the image, this must be calculated. The
    slice can be:
    - axial: xy plane or separating superior (head) from inferior (feet),
    - coronal: xz plan or separating anterior (front) from posterior (back)
    - sagittal: yz plane or separating left from right"""

    plt.ion()
    fig, axes = plt.subplots(int(np.ceil(n / 5)), 5)
    axes = axes.flatten()

    for i in range(n):
        slice_num = n0 - (n // 2) * dn + i * dn
        if direction == "axial":
            img_slice = sitk.Extract(img, [img.GetSize()[0], img.GetSize()[1], 0], [0, 0, slice_num])
            axes[i].imshow(sitk.GetArrayFromImage(img_slice), cmap='gray', aspect=img.GetSpacing()[1] / img.GetSpacing()[0])
        if direction == "coronal":
            img_slice = sitk.Extract(img, [img.GetSize()[0], 0,  img.GetSize()[2]], [0, slice_num, 0])
            axes[i].imshow(sitk.GetArrayFromImage(img_slice), cmap='gray', aspect=img.GetSpacing()[2] / img.GetSpacing()[0])
        if direction == "sagittal":
            img_slice = sitk.Extract(img, [0, img.GetSize()[1], img.GetSize()[2]], [slice_num, 0, 0])
            axes[i].imshow(sitk.GetArrayFromImage(img_slice), cmap='gray', aspect=img.GetSpacing()[2] / img.GetSpacing()[1])
        axes[i].set_title(f'Slice {slice_num}')
        axes[i].set_axis_off()
    plt.tight_layout()
    plt.show()

    point = plt.ginput(1, timeout=0, show_clicks=True)[0]
    plt.ioff()
    plt.close()

    return point
