import SimpleITK as sitk
import numpy as np
from class_BrainAligner import BrainAligner
from utilities import check_registration


class BrainRegisterer:
    """
    This class includes methods and attributes to register a brain atlas (moving image) to an MR image (fixed image).
    The registration it executed by running the 'execute()' method.
    """

    def __init__(self, mri0: sitk.Image, mri1: sitk.Image, mri2: sitk.Image, atlas: sitk.Image, patient_id: int, d: float = 5e-3):

        self.patient_id = patient_id

        self.mri0 = mri0  # T1w
        self.mri1 = mri1  # T1wC0.5
        self.mri2 = mri2  # T1wC1.0
        self.atlas = atlas

        self.msk0 = None
        self.msk1 = None
        self.msk2 = None

        self.mri2_0 = None  # mri2 - mri0
        self.mri1_0 = None  # mri1 - mri0

        self.origin = [0, 0, 0]
        self.spacing = [0.2, 0.2, 0.8]
        self.direction = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=float).flatten()
        self.size = [512, 512, 128]

        self.mask = None
        self.mask_contour = None
        self.d = d  # the dilation radius to constrain the elastic registration (in mm)

    def execute(self):
        """
        The registration consists in the following five steps:

        1. Rescale intensity of fixed and moving image in the range [0, 1], and resample the moving image to the fixed image
        with a 3D affine transformation. The resulting moving image has same spacings, origin and direction cosines as the fixed image,
        i.e. the fixed and moving image now share the same space.

        2. Match the intensity histogram of the moving image to the intensity histogram of the fixed image. This is
        necessary to make the image intensities comparable.

        3. Initialize the registration by (i) aligning the brain atlas center with the MR image brain center, and (ii) rescaling the brain atlas
        to match approximately the brain in the MR image.

        4. Registration. Register the brain atlas with a rigid and elastic transformation. A mask is used to limit the region available for
        registration. The mask is defined as the atlas brain mask dilated with a 3D ball structuring element of radius D (in mm).

        5. Calculate brain region in the MR image.

        6. Co-register the three MR images, using their brain masks to limit the registration to the actual brain volume.
        """

        # 1 --------------------------------------------------------------------
        self.atlas = self.project_img_in_custom_space(self.atlas)
        self.mri0 = self.project_img_in_custom_space(self.mri0)
        self.mri1 = self.project_img_in_custom_space(self.mri1)
        self.mri2 = self.project_img_in_custom_space(self.mri2)

        print(f"T1w - New Direction Cosines: {self.mri0.GetDirection()}\n"
              f"T1w - New Origin: {self.mri0.GetOrigin()}\n"
              f"1/2T1w - New Direction Cosines: {self.mri1.GetDirection()}\n"
              f"1/2T1w - New Origin: {self.mri1.GetOrigin()}\n"
              f"1T1w - New Direction Cosines: {self.mri2.GetDirection()}\n"
              f"1T1w - New Origin: {self.mri2.GetOrigin()}\n"
              f"1/2T1w - New Direction Cosines: {self.mri1.GetDirection()}\n"
              f"1/2T1w - New Origin: {self.mri1.GetOrigin()}\n"
              f"atlas - New Direction Cosines: {self.atlas.GetDirection()}\n"
              f"atlas - New Origin: {self.atlas.GetOrigin()}\n")

        # 2 --------------------------------------------------------------------
        print("Matching Histograms... ", end="")
        self.mri1 = sitk.HistogramMatching(image=self.mri1, referenceImage=self.mri0)
        self.mri2 = sitk.HistogramMatching(image=self.mri2, referenceImage=self.mri0)
        self.atlas = sitk.HistogramMatching(image=self.atlas, referenceImage=self.mri0)
        print("Done.")

        # Note: we need a copy of the atlas to start over with each alignment, because the atlas gets deformed at every iteration otherwise
        # 3.0 --------------------------------------------------------------------
        print("Starting Aligner...")
        brain_aligner = BrainAligner(self.mri0, self.atlas)
        brain_aligner.execute()
        self.atlas = sitk.Resample(self.atlas, brain_aligner.transform)

        # 4.0 --------------------------------------------------------------------
        print("Starting Registration...")
        self.generate_mask()
        self.register_atlas(self.mri0)
        check_registration(self.mri0, self.atlas, self.mask_contour, [brain_aligner.i, brain_aligner.j, brain_aligner.k], [10, 10, 5], 3)

        # 5.0 --------------------------------------------------------------------
        self.msk0 = sitk.BinaryThreshold(self.atlas, lowerThreshold=0.001, insideValue=1)

        # 3.1 --------------------------------------------------------------------
        print("Starting Aligner...")
        brain_aligner = BrainAligner(self.mri1, self.atlas)
        brain_aligner.execute()
        self.atlas = sitk.Resample(self.atlas, brain_aligner.transform)

        # 4.1 --------------------------------------------------------------------
        print("Starting Registration...")
        self.generate_mask()
        self.register_atlas(self.mri1)
        check_registration(self.mri1, self.atlas, self.mask_contour, [brain_aligner.i, brain_aligner.j, brain_aligner.k], [10, 10, 5], 3)

        # 5.1 --------------------------------------------------------------------
        self.msk1 = sitk.BinaryThreshold(self.atlas, lowerThreshold=0.001, insideValue=1)

        # 3.2 --------------------------------------------------------------------
        print("Starting Aligner...")
        brain_aligner = BrainAligner(self.mri2, self.atlas)
        brain_aligner.execute()
        self.atlas = sitk.Resample(self.atlas, brain_aligner.transform)

        # 4.2 --------------------------------------------------------------------
        print("Starting Registration...")
        self.generate_mask()
        self.register_atlas(self.mri2)
        check_registration(self.mri2, self.atlas, self.mask_contour, [brain_aligner.i, brain_aligner.j, brain_aligner.k], [10, 10, 5], 3)

        # 5.2 --------------------------------------------------------------------
        self.msk2 = sitk.BinaryThreshold(self.atlas, lowerThreshold=0.001, insideValue=1)

        # 6. --------------------------------------------------------------------
        self.register_mri()

        # 7. --------------------------------------------------------------------
        self.mri2_0 = sitk.Subtract(self.mri2, self.mri0)
        self.mri1_0 = sitk.Subtract(self.mri1, self.mri0)

        # 8. --------------------------------------------------------------------
        sitk.WriteImage(self.mri0, f"E:/2021_local_data/2023_Gd_synthesis/tests/{self.patient_id}_T1wR.nii.gz")
        sitk.WriteImage(self.msk0, f"E:/2021_local_data/2023_Gd_synthesis/tests/{self.patient_id}_T1wR.msk.nii.gz")
        sitk.WriteImage(self.mri1, f"E:/2021_local_data/2023_Gd_synthesis/tests/{self.patient_id}_T1wC0.5R.nii.gz")
        sitk.WriteImage(self.msk1, f"E:/2021_local_data/2023_Gd_synthesis/tests/{self.patient_id}_T1wC0.5R.msk.nii.gz")
        sitk.WriteImage(self.mri2, f"E:/2021_local_data/2023_Gd_synthesis/tests/{self.patient_id}_T1wC1.0R.nii.gz")
        sitk.WriteImage(self.msk2, f"E:/2021_local_data/2023_Gd_synthesis/tests/{self.patient_id}_T1wC1.0R.msk.nii.gz")
        sitk.WriteImage(self.mri1_0, f"E:/2021_local_data/2023_Gd_synthesis/tests/{self.patient_id}_T1wC0.5RD.nii.gz")
        sitk.WriteImage(self.mri2_0, f"E:/2021_local_data/2023_Gd_synthesis/tests/{self.patient_id}_T1wC1.0RD.nii.gz")

    def project_img_in_custom_space(self, img):
        """This method rescale the intensity in the range [0, 1], and then project the passed image in the physical space
        defined by the object attributes. By default, the image is resampled in order to have its physical origin at (0,0,0),
        spacing of [0.2, 0.2, 0.8] mm, and direction cosines [(1, 0, 0), (0, 1, 0), (0, 0, 1)]."""

        img = sitk.RescaleIntensity(img, 0, 1)

        # Define the Transform (translation and rotation) necessary to resample the image after setting a new origin and new direction cosines
        transform = sitk.AffineTransform(3)
        transform.SetTranslation(-(self.origin - np.array(img.GetOrigin())))
        output_direction = np.array(self.direction).reshape((3, 3))
        input_direction = np.array(img.GetDirection()).reshape((3, 3))
        rotation_matrix = np.dot(input_direction, np.linalg.inv(output_direction))
        transform.SetMatrix(rotation_matrix.flatten())

        # Define the Resampler Filter
        resampler = sitk.ResampleImageFilter()
        resampler.SetTransform(transform)
        resampler.SetInterpolator(sitk.sitkLinear)
        resampler.SetSize(self.size)
        resampler.SetOutputOrigin(self.origin)
        resampler.SetOutputDirection(self.direction.flatten())
        resampler.SetOutputSpacing(self.spacing)
        resampler.SetDefaultPixelValue(0.0)
        resampler.SetOutputPixelType(sitk.sitkFloat32)
        img = resampler.Execute(img)

        return img

    def match_intensity_histograms(self):
        """Match intensity histogram of moving image to intensity histogram of fixed image"""
        self.atlas = sitk.HistogramMatching(image=self.atlas, referenceImage=self.mri0)

    def generate_mask(self):
        self.mask = sitk.BinaryThreshold(self.atlas, lowerThreshold=0.001, insideValue=1)
        r = np.array([self.d * 1e3 / self.mask.GetSpacing()[0],
                      self.d * 1e3 / self.mask.GetSpacing()[1],
                      self.d * 1e3 / self.mask.GetSpacing()[2]],
                     dtype=int)
        self.mask = sitk.BinaryDilate(self.mask, [int(x) for x in r])
        self.mask_contour = sitk.BinaryDilate(sitk.BinaryContour(self.mask), [2, int(2 * r[1] / r[0]), int(2 * r[2] / r[0])])

    def register_atlas(self, img):
        """This method register the brain atlas to the passed mri image, using a user defined mask that
        prevents the brain atlas to exceed the actual brain volume."""
        elastixImageFilter = sitk.ElastixImageFilter()
        elastixImageFilter.SetFixedImage(img)
        elastixImageFilter.SetMovingImage(self.atlas)
        elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
        elastixImageFilter.SetFixedMask(self.mask)
        elastixImageFilter.Execute()
        self.atlas = elastixImageFilter.GetResultImage()

        elastixImageFilter.SetFixedImage(img)
        elastixImageFilter.SetMovingImage(self.atlas)
        elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("bspline"))
        elastixImageFilter.SetFixedMask(self.mask)
        elastixImageFilter.Execute()
        self.atlas = elastixImageFilter.GetResultImage()

    def register_mri(self):
        """This method register the mri1 and mri2 to mri0, using their masks to limit the registration to the
        actual brain volume."""
        elastixImageFilter = sitk.ElastixImageFilter()
        elastixImageFilter.SetFixedImage(self.mri0)
        elastixImageFilter.SetMovingImage(self.mri1)
        elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
        elastixImageFilter.SetFixedMask(self.msk0)
        elastixImageFilter.SetMovingMask(self.msk1)
        elastixImageFilter.Execute()
        self.mri1 = elastixImageFilter.GetResultImage()

        elastixImageFilter = sitk.ElastixImageFilter()
        elastixImageFilter.SetFixedImage(self.mri0)
        elastixImageFilter.SetMovingImage(self.mri2)
        elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
        elastixImageFilter.SetFixedMask(self.msk0)
        elastixImageFilter.SetMovingMask(self.msk2)
        elastixImageFilter.Execute()
        self.mri2 = elastixImageFilter.GetResultImage()

    def subtract_mri(self):

        sitk.Subtract(self.mri0, self.mri1)

