import numpy as np
import SimpleITK as sitk


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


def convert_dicom_to_nifti(path_dicom_series, path_nifti):
    """Read a DICOM series and convert it to 3D nifti image"""
    # Read the DICOM file
    dicom_image = sitk.ReadImage(path_dicom_series)
    # Save the DICOM image as a NIfTI file
    sitk.WriteImage(dicom_image, path_nifti)


def resample_brain_to_mri(atlas, image):
    """ This function takes an input image (atlas) and a target image (image).
    It calculates the resizing factor based on the original and target spacing,
    computes the new size, and then uses sitk.Resample to perform the actual resizing. """
    # get spacing and size of brain atlas and mr image
    atlas_spacing = atlas.GetSpacing()
    atlas_size = atlas.GetSize()
    image_spacing = image.GetSpacing()
    image_size = image.GetSize()
    # Calculate the resizing factor
    resizing_factor = [x / y for x, y in zip(atlas_spacing, image_spacing)]
    # Calculate the new size
    new_size = [int(round(x * f)) for x, f in zip(atlas_size, resizing_factor)]
    # Create a transform
    transform = sitk.Transform()
    transform.SetIdentity()
    # Set the output image spacing
    output_spacing = image_spacing
    output_origin = image.GetOrigin()
    output_direction = image.GetDirection()

    # Perform resampling
    resized_image = sitk.Resample(image, new_size, transform, sitk.sitkLinear,
                                  output_origin, output_spacing, output_direction)
    sitk.Resample(image=atlas)

    return resized_image


# Load the original image
original_image = sitk.ReadImage('path/to/original_image.nii.gz')