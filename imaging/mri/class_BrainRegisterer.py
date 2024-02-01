import SimpleITK as sitk
import numpy as np
from class_BrainAligner import BrainAligner
from utilities import check_registration


class BrainRegisterer:
    """
    This class includes methods and attributes to register a brain atlas (moving image) to an MR image (fixed image).
    The registration it executed by running the 'execute()' method.
    """

    def __init__(self, mri0: sitk.Image, mri1: sitk.Image, mri2: sitk.Image, atlas: sitk.Image, d: float = 5e-3):

        self.mri0 = mri0  # T1w
        self.mri1 = mri1  # 1/2T1w
        self.mri2 = mri2  # 1T1w
        self.atlas = atlas

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

        4. Registration. Register the brain atlas with a rigid and elastic transformation. A mask is usd to limit the region available for
        registration. The mask is defined as the atlas brain mask dilated with a 3D ball structuring element of radius D (in mm).

        5. Calculate brain region in the MR image.
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

        # 3 --------------------------------------------------------------------
        print("Starting Aligner...")
        brain_aligner = BrainAligner(self.mri0, self.atlas)
        brain_aligner.execute()
        self.atlas = sitk.Resample(self.atlas, brain_aligner.transform)
        check_registration(self.mri0, self.atlas, None, [256, 256, 64], [5, 5, 5], 3)

        # 4. --------------------------------------------------------------------
        mask = sitk.BinaryThreshold(self.atlas, lowerThreshold=0.001, insideValue=1)
        r = np.array([self.d * 1e3 / mask.GetSpacing()[0],
                      self.d * 1e3 / mask.GetSpacing()[1],
                      self.d * 1e3 / mask.GetSpacing()[2]],
                     dtype=int)
        mask = sitk.BinaryDilate(mask, [int(x) for x in r])
        mask_contour = sitk.BinaryDilate(sitk.BinaryContour(mask), [2, int(2 * r[1] / r[0]), int(2 * r[2] / r[0])])

        elastixImageFilter = sitk.ElastixImageFilter()
        elastixImageFilter.SetFixedImage(self.mri0)
        elastixImageFilter.SetMovingImage(self.atlas)
        elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
        elastixImageFilter.SetFixedMask(mask)
        elastixImageFilter.Execute()
        self.atlas = elastixImageFilter.GetResultImage()
        check_registration(self.mri0, self.atlas, mask_contour, [256, 256, 64], [5, 5, 5], 3)

        elastixImageFilter.SetFixedImage(self.mri0)
        elastixImageFilter.SetMovingImage(self.atlas)
        elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("bspline"))
        elastixImageFilter.SetFixedMask(mask)
        elastixImageFilter.Execute()
        self.atlas = elastixImageFilter.GetResultImage()
        check_registration(self.mri0, self.atlas, mask_contour, [256, 256, 64], [5, 5, 5], 3)



        #brain, mask, contour = self.register_atlas(self.mri0, self.atlas)

        check_registration(fix_img=self.mri1,
                           mov_img=brain,
                           mask=contour,
                           slice=[brain_aligner.i, brain_aligner.j, brain_aligner.k],
                           delta_slice=[10, 10, 5],
                           n_slice=3)









        # # 4 --------------------------------------------------------------------
        # self.register_atlas()
        # # 5 --------------------------------------------------------------------
        # brain = sitk.BinaryThreshold(self.mov_img, lowerThreshold=0.001, insideValue=1)

        #sitk.WriteImage(brain_0t1w, f"E:/2021_local_data/2023_Gd_synthesis/tests/{key[1]}_0t1w_mask.nii.gz")
        #sitk.WriteImage(mri_0t1w, f"E:/2021_local_data/2023_Gd_synthesis/tests/{key[1]}_0t1w.nii.gz")



    def project_img_in_custom_space(self, img):
        """This method rescale the intensity in the range [0, 1], and then project the passed image in the physical space
        defined by the object attributes. By default, the image is resampled in order to have its physical origin at (0,0,0) and
        spacing of [0.2, 0.2, 0.8] mm, while the direction cosines are left as is: the radiologist typically aligns the images
        with respect to the patient, resulting in an approximate alignment."""

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
        resampler.SetOutputPixelType(sitk.sitkFloat64)
        img = resampler.Execute(img)

        return img

    def match_intensity_histograms(self):
        """Match intensity histogram of moving image to intensity histogram of fixed image"""
        self.atlas = sitk.HistogramMatching(image=self.atlas, referenceImage=self.mri0)

    def register_atlas(self, fix_img, mov_img):

        mask = sitk.BinaryThreshold(mov_img, lowerThreshold=0.001, insideValue=1)
        r = np.array([self.d * 1e3 / mask.GetSpacing()[0],
                      self.d * 1e3 / mask.GetSpacing()[1],
                      self.d * 1e3 / mask.GetSpacing()[2]],
                     dtype=int)
        mask = sitk.BinaryDilate(mask, [int(x) for x in r])
        mask_contour = sitk.BinaryDilate(sitk.BinaryContour(mask), [2, int(2 * r[1] / r[0]), int(2 * r[2] / r[0])])

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

        return mov_img, mask, mask_contour

    def save_images(self):
        sitk.WriteImage(self.fix_img, "E:/2021_local_data/2023_Gd_synthesis/tests/fix img.nii.gz")
        sitk.WriteImage(self.mov_img, "E:/2021_local_data/2023_Gd_synthesis/tests/mov img.nii.gz")