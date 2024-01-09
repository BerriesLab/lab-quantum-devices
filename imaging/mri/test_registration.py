import SimpleITK as sitk

fixImage = sitk.ReadImage("pre_contrast_image.nii")  # "fixed" or "pre-contrast" image
fixMask = sitk.ReadImage("mask")
movImage = sitk.ReadImage("pst_contrast_image.nii")  # "moving" or "post-contrast" image
elastixImageFilter = sitk.ElastixImageFilter()  # create a SimpleElastix object
elastixImageFilter.SetFixedImage(fixImage)
elastixImageFilter.SetMovingImage(movImage)
elastixImageFilter.SetFixedMask(fixMask)  # here the mask is the brain
elastixImageFilter.SetParameterMap(sitk.GetDefaultParameterMap("rigid"))
# sitk.PrintParameterMap(sitk.GetDefaultParameterMap("rigid"))
elastixImageFilter.Execute()
regImage = elastixImageFilter.GetResultImage()
