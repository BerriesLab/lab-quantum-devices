import SimpleITK as sitk

fixImage = sitk.ReadImage("pre_contrast_image.nii")  # "fixed" or "pre-contrast" image
movImage = sitk.ReadImage("pst_contrast_image.nii")  # "moving" or "post-contrast" image
# regImage = sitk.Elastix(fixImage, movImage, "rigid")  # or registered image
# parameterMap = sitk.GetDefaultParameterMap("rigid")  # define the parameters for the registration

# object-oriented programming of registration
elastixImageFilter = sitk.ElastixImageFilter()
elastixImageFilter.SetFixedImage(fixImage)
elastixImageFilter.SetMovingImage(movImage)
elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
# sitk.PrintParameterMap(sitk.GetDefaultParameterMap("rigid"))
elastixImageFilter.Execute()
regImage = elastixImageFilter.GetResultImage()