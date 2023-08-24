import SimpleITK as sitk
import os
from utils import WormCounter
from utils import alpha_blend, mask_image_multiply, threshold_filters
import matplotlib.pyplot as plt
import random
from numpy import count_nonzero
import numpy.ma as ma


morph_stats = {'id': [], 'max_length (mm)': []}
os.chdir("C:/tierspital/")  # set current working directory
image = sitk.ReadImage(os.getcwd()+"/data raw/cropped_volumes/3 Lunge_corner_01.nii.gz")  # Load image
data_min = sitk.GetArrayViewFromImage(image).min()  # Get min value of CT scan
data_max = sitk.GetArrayViewFromImage(image).max()  # Get max value of CT scan
print("\n"
      f"Image data shape (x, y, z): {image.GetSize()}\n"
      f"Spacing (dx, dy, dz): {image.GetSpacing()}\n"
      f"(min, max) values: {data_min, data_max}"
      f"\n")

print("Initializing figures... ", end="")
fig0 = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
ax0 = fig0.add_subplot()
fig1 = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
ax1 = fig1.add_subplot()
# fig_int = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
# ax_int = fig_int.add_subplot()
# self.grid = GridSpec(1, 1)
# self.grid.update(wspace=0.4, hspace=2)
# ax.set_xlabel("Time (s)")
# ax.set_ylabel(ylabel)
# ax.set_title(f"{', '.join(labels)} vs time", fontsize=10, fontstyle="italic")
# ax.set_xlim([0, duration])
plt.show(block=False)
print("Done.")

print("Initializing 'worm object'... ", end="")
worm_counter = WormCounter(image, os.getcwd()+"/data processed")  # Initate object
print("Done.")

print(f"Plotting y-z section at random x-coordinate... ", end="")
random_x = random.randint(0, sitk.GetArrayViewFromImage(image).shape[0])
ax0.imshow(sitk.GetArrayViewFromImage(image)[random_x, :, :], cmap="gray", vmin=data_min, vmax=data_max)
plt.pause(0.01)
print("Done.")

# print("Setting filters... ", end="")
# #no_filter = sitk.Cast(data*0+1, sitk.sitkUInt8)
# box_filter = worm_counter.box_filter(x_min=35, x_max=995, y_min=240, y_max=450, z_min=20, z_max=1010)
# # box_filter = no_filter
# print("Done.")

"""SEGMENTATION OF THE BOX"""
print("Plotting distribution of bright pixels... ", end="")
ax1.hist(sitk.GetArrayViewFromImage(image).flatten(), bins=100, log=False)
plt.pause(0.001)
print("Done.")
print("Removing air... ", end="")
label_air = worm_counter.air_filter(threshold=-950, minimum_object_size=20000)
print("Plotting air overlay... ", end="")
image_air = sitk.LabelOverlay(image=image, labelImage=label_air)
#label_air = sitk.BinaryOpeningByReconstruction(label_air, [10, 10, 10])
#label_air = sitk.BinaryClosingByReconstruction(label_air, [100, 100, 100])
ax0.imshow(sitk.GetArrayViewFromImage(image_air)[random_x, :, :], cmap="jet", alpha=0.5)
plt.pause(0.01)
print("Done.")


print("Segmentation of the box 'walls' (vertically aligned box sides).. ", end="")
wall = worm_counter.box_segmenter(erosion_matrix=[1, 8, 1], dilation_matrix=[2, 9, 2], selection_filter=None, threshold=-300, minimum_object_size=500)
print(f"{count_nonzero(sitk.GetArrayFromImage(wall)==1)} pixels segmented... ", end="")
pink= [255,105,180]; green = [0,255,0]; gold = [255,215,0]
rgb = sitk.LabelOverlay(image=image, labelImage=wall, opacity=0.5, backgroundValue= -1.0, colormap=pink+green+gold)

# Let's color the image and then alpha blend it
#image_rgb = sitk.ScalarToRGBColormap(image)
#image_with_wall = alpha_blend(image1=image, image2=image_rgb, mask1=None, mask2=wall)
#ax0.imshow(sitk.GetArrayViewFromImage(rgb)[random_x, :, :])
#plt.pause(0.1)
#image_with_wall = sitk.LabelOverlay(image=image, labelImage=wall, opacity=0.5)
#overlay = sitk.LabelOverlayImageFilter()
#test = overlay.Execute(image=image, labelImage=wall)
#ax0.imshow(sitk.GetArrayViewFromImage(test)[random_x, :, :], cmap="gray", vmin=data_min, vmax=data_max)
#mask = ma.masked_where(wall==0, image)
#image_mask = ma.masked_array(sitk.GetArrayFromImage(image), sitk.GetArrayFromImage(wall))
plt.pause(0.1)

sitk.LabelToRGB()
print("Done.")
print("Segmentation of the box 'floor' (horizontally aligned box sides)... ", end="")
floor = worm_counter.box_segmenter(erosion_matrix=[6, 1, 6], dilation_matrix=[7, 2, 7], selection_filter=sitk.And(sitk.Cast(image * 0 + 1, sitk.sitkUInt8), sitk.Not(wall)), threshold=-300, minimum_object_size=100)
print("Done.")
print('Separation of the bright spots')
bright = worm_counter.bright_remover(selection_filter=None, threshold_small=150, threshold_large=-500)

# data_blended = alpha_blend(image1=data, image2=wall, mask1=None, mask2=wall)
# ax1.imshow(data_blended[random_x, :, :], cmap="gray", vmin=0, vmax=1)
# plt.pause(0.001)
# print("Done")
#
# box = sitk.BinaryDilate(sitk.Or(floor, wall), [1, 1, 1])
#
# plt.show()

# filter_selection = "Otsu"
# thresh_filter = threshold_filters[filter_selection]
# thresh_filter.SetInsideValue(0)
# thresh_filter.SetOutsideValue(1)
# thresh_img = thresh_filter.Execute(data)
# thresh_value = thresh_filter.GetThreshold()
# print("Threshold used: " + str(thresh_value))
# output = sitk.LabelOverlay(data, thresh_img)
# plt.imshow(sitk.GetArrayViewFromImage(output)[random_x, :, :], cmap="gray", vmin=data_min, vmax=data_max)
# plt.axis("off")
# plt.show()


#gui.MultiImageDisplay(image_list = [sitk.LabelOverlay(img, thresh_img)],
 #                     title_list = ['Binary Segmentation'], figure_size=(8,4))
#endregion





#wall = worm_counter.wall_remover(selection_filter=sitk.Cast(data,), threshold=-300, minimal_size=2500)

# print("Segmentation of the box wall... ", end="")
# wall = worm_counter.wall_remover(selection_filter=box_filter, threshold=-300, minimal_size=2500)
# print("Segmentation of the floor... ", end="")
# floor = worm_counter.floor_remover(selection_filter=sitk.And(no_filter, sitk.Not(wall)), threshold=-350, minimal_size=50)
# box = sitk.BinaryDilate(sitk.Or(floor, wall), [1, 1, 1])
# sitk.WriteImage(box, os.path.join(working_dir, 'box_seg.nii.gz'))
