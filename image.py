import sys
import matplotlib.pyplot as plt
from numpy import ones, min, max, histogram, linspace
import os
import SimpleITK as sitk
from skimage import data, color, io
from skimage.feature import canny
from skimage.filters import try_all_threshold
from scipy import ndimage
import skimage.exposure
from skimage.color import rgb2gray
from image_utils import *
import random

os.chdir(r"C:\tierspital")  # set current working directory
files = os.listdir(rf"{os.getcwd()}\data raw\photos")
n_bins_rgb = 50
n_bins_greyscale = n_bins_rgb
n = random.randint(1, 14)  # select a random picture to display and process

# region ----- IMAGE PIXELS STATISTICS -----
"""IMAGE PIXELS STATISTICS. Plot RGB and grayscale images and pixel distributions of (i) a random image
and (ii) of the whole image set."""
fig1, ax1 = plt.subplots(1, 1, figsize=(15/2.54, 10/2.54))
ax1.set_title(f"Grayscale pixel statistics - n. images: {len(os.listdir(os.getcwd()))}")
for idx, file in enumerate(files):
    print(f"Processing {file}... ", end="")
    image = io.imread(rf"{os.getcwd()}\data raw\photos\{file}")
    image_gray = color.rgb2gray(image)
    stats = pixel_stats(image, image_gray, n_bins_rgb, n_bins_greyscale, plot=True, save=(True, file[:-4]))
    ax1.fill_between(stats["x_gray"], stats["y_gray"], y2=0, alpha=0.25, color="gray")
    ax1.plot(stats["x_gray"], stats["y_gray"], color="black")
    print("Done.")
fig1.savefig(rf"{os.getcwd()}\data processed\photos\all_statistics_rgb_grayscale.jpg", dpi=1200)
# endregion

#region ----- SEGMENTATION BY THRESHOLD -----
"""SEGMENTATION BY THRESHOLD. All gray pictures show histograms with a singluar feature around 0.4.
Let's try to mask out everything with greay value > 0.4 and try all thresholding algorithm provided by the library, which include:"""
for idx, file in enumerate(files):
    image = io.imread(rf"{os.getcwd()}\data raw\photos\{file}")
    image_gray = color.rgb2gray(image)
    print(f"Figure {file} segmentation - Threshold Mean - ...", end="")
    mask_mean = segmentation_threshold_mean(image=image_gray, plot=True, save=(True, file[:-4]))
    print("Done.")
    print(f"Figure {file} segmentation - Threshold Value - ...", end="")
    mask_threshold = segmentation_threshold_value(image=image_gray, threshold=0.4, plot=True, save=(True, file[:-4]))
    print("Done.")
    print(f"Figure {file} segmentation - Threshold Minimum - ...", end="")
    mask_min = segmentation_threshold_minimum(image=image_gray, plot=True, save=(True, file[:-4]))
    print("Done.")
    print(f"Figure {file} segmentation - Threshold Otsu - ...", end="")
    mask_otsu = segmentation_threshold_otsu(image=image_gray, plot=True, save=(True, file[:-4]))
    print("Done.")
    print(f"Figure {file} segmentation - Threshold Local - ...", end="")
    mask_local = segmentation_threshold_local(image=image_gray, block_size=35, offset=0, plot=True, save=(True, file[:-4]))
    print("Done.")
    print(f"Figure {file} segmentation - Threshold Multi Otsu - ...", end="")
    mask_multiotsu = segmentation_threshold_multiotsu(image=image_gray, classes=4, plot=True, save=(True, file[:-4]))
    print("Done.")
# endregion

# region ----- SEGMENTATION VIA EDGE-BASED ALGORITHM -----
"""The segmentation of the coins cannot be done directly and solely via thresholding and/or from the histogram of gray values, 
because the background shares enough gray levels with the worms. Since every picture will have a different exposure 
gamma correction would be necessary to make two images comparable and therefore make possible to apply the same code  
A first idea is to take advantage of the local contrast, that is, to use the gradients rather than the gray values.
SEGMENTATION VIA EDGE-BASED ALGORITHM"""
image = io.imread(rf"{os.getcwd()}\data raw\photos\1.jpg")
image_gray = color.rgb2gray(image)
fig, ax = plt.subplots(1, 2, figsize=(20/2.54, 15/2.54))
ax[0].set_title(f"Edge detection through Canny algorithm")
edges = canny(image_gray, mask=mask)
ax[0].imshow(edges)
plt.pause(0.01)
#endregion

"""Now that we have the coutours of the worms, let's fill the space to check if the segmentation is robust"""
# fill_worms = ndimage.binary_fill_holes(edges)
# ax[1].imshow(fill_worms)

#label_objects, nb_labels = ndimage.label(fill_worms)
#sizes = np.bincount(label_objects.ravel())
#mask_sizes = sizes > 20
#mask_sizes[0] = 0
#coins_cleaned = mask_sizes[label_objects]
#plt.show(block=True)
