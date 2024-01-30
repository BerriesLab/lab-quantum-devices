import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap


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


def extract_axial_section(ax: plt.Axes, img: sitk.Image, n, cmap):
    """Extract slice from sitk.Image in the xy plane."""
    img_slice = sitk.Extract(img, [img.GetSize()[0], img.GetSize()[1], 0], [0, 0, n])
    img_extent = (0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0)
    ax.imshow(sitk.GetArrayFromImage(img_slice), cmap=cmap, extent=img_extent)
    ax.set_axis_off()


def extract_coronal_section(ax: plt.Axes, img: sitk.Image, n, cmap):
    """Extract slice from sitk.Image in the xz plane."""
    img_slice = sitk.Extract(img, [img.GetSize()[0], 0, img.GetSize()[2]], [0, n, 0])
    img_extent = (0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0)
    ax.imshow(sitk.GetArrayFromImage(img_slice), cmap=cmap, extent=img_extent)
    ax.set_axis_off()


def extract_sagittal_section(ax: plt.Axes, img: sitk.Image, n, cmap):
    """Extract slice from sitk.Image in the yz plane."""
    img_slice = sitk.Extract(img, [0, img.GetSize()[1], img.GetSize()[2]], [n, 0, 0])
    img_extent = (0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0)
    ax.imshow(sitk.GetArrayFromImage(img_slice), cmap=cmap, extent=img_extent)
    ax.set_axis_off()








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


# Create a custom colormap with 0 mapped to fully transparent
def custom_colormap():
    # Create a custom colormap based on "jet"
    cmap_jet = plt.colormaps.get_cmap("afmhot")
    n = 256  # Number of values in the colormap
    jet_colors = cmap_jet(np.linspace(0, 1, n))
    # Set alpha channel to 0 where the value is 0
    jet_colors[:, 3] = np.where(np.linspace(0, 1, n) == 0, 0, 0.4)
    return LinearSegmentedColormap.from_list("custom_jet", jet_colors, n)


def custom_colormap_for_mask():
    # Define the colors and corresponding values
    colors = np.array([(0, 0, 0, 0), (0.8, 0, 0, 0.8)])  # (R, G, B, Alpha)
    # Create a ListedColormap
    custom_cmap = ListedColormap(colors)
    return custom_cmap
