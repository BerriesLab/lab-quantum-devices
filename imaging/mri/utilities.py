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


def resample_brain_to_mri(atlas, mri, registration="rigid"):
    """ This function takes an input image (atlas) and a target image (image).
    It calculates the resizing factor based on the original and target spacing,
    computes the new size, and then uses sitk.Resample to perform the actual resizing. """

    fixedImage = sitk.ReadImage(mri)
    movingImage = sitk.ReadImage(atlas)
    parameterMap = sitk.GetDefaultParameterMap(registration)

    # create an elastic object
    elastixImageFilter = sitk.ElastixImageFilter()
    # set fixed and moving images, and mapping parameters
    elastixImageFilter.SetFixedImage(fixedImage)
    elastixImageFilter.SetMovingImage(movingImage)
    elastixImageFilter.SetParameterMap(parameterMap)
    # execute registration
    elastixImageFilter.Execute()
    # get resulting image
    resultImage = elastixImageFilter.GetResultImage()
    # get transformation parameters
    transformParameterMap = elastixImageFilter.GetTransformParameterMap()

    return resultImage


# Load the original image
original_image = sitk.ReadImage('path/to/original_image.nii.gz')