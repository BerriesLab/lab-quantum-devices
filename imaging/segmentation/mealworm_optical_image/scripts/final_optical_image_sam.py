import os
import cv2
import numpy as np
from skimage.color import label2rgb, rgb2gray
from imaging.segmentation.mealworm_optical_image.tools.classes import SegmentationWithSAM
from imaging.segmentation.mealworm_optical_image.tools.image_utils import pixel_stats
import matplotlib.pyplot as plt
import pickle
from skimage.measure import label, regionprops
from skimage.color import label2rgb, rgb2gray
import matplotlib.patches as mpatches
from skimage.segmentation import find_boundaries, clear_border
from numpy import unique, argwhere, argmax, array, sort
import numpy as np
from skimage.feature import canny
from skimage.exposure import equalize_hist, rescale_intensity
from skimage.filters import gaussian
from skimage.transform import hough_line, hough_line_peaks

IMAGE_PATH = 'T:/data processed/optical images/segmentation sam/batch01'
FILES = [f'{IMAGE_PATH}/{x}' for x in os.listdir(IMAGE_PATH) if x.endswith('.dat')]
for FILE in FILES:
    with open(f"{FILE}", 'rb') as reader:
        data = pickle.load(reader)

    area, ecce = data.hist_labels_geometry(plot=False)
    plt.figure()
    image_label_overlay = label2rgb(data.labels, data.image, alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
    plt.imshow(image_label_overlay)
    plt.axis("off")
    ax = plt.gca()
    regions = regionprops(data.labels)
    for region in regions:
        minr, minc, maxr, maxc = region.bbox
        rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=1)
        ax.add_patch(rect)
    print(len(unique(data.labels)))

    gra = rgb2gray(data.image)
    grad = canny(gra, sigma=5)
    #grad[int(data.image_lx*0.1):int(data.image_lx*0.9), int(data.image_ly*0.1):int(data.image_ly*0.9)] = 0
    plt.figure()
    plt.imshow(grad, cmap='gray')
    hspace, angles, dists = hough_line(grad)
    accum, angles, dists = hough_line_peaks(hspace, angles, dists, min_distance=0, min_angle=0, num_peaks=4, threshold=0.1*hspace.max())
    plt.figure()
    plt.imshow(data.image)
    for angle, dist in zip(angles, dists):
        (x0, y0) = dist * np.array([np.cos(angle), np.sin(angle)])
        plt.axline((x0, y0), slope=np.tan(angle + np.pi/2),linewidth=2, color='red')

    #hist = plt.hist(smo.flatten(), range=(0, 1), bins=100, log=False)
    #floor_val = hist[1][argmax(hist[0])]
    #mask = smo <= floor_val
    #self.labels[mask] = 0

    plt.show()


    # plt.figure()
    # data.labels = clear_border(data.labels)
    # data.thresh_area = 500
    # regions = regionprops(data.labels)
    # for region in regions:
    #     if not 500 <= region.area <= 5000:
    #         data.labels[data.labels==region.label] = 0
    # data.labels = label(data.labels, connectivity=1)  # re-label label matrix
    # area, ecce = data.hist_labels_geometry(plot=False)
    # plt.figure()
    # image_label_overlay = label2rgb(data.labels, data.image, alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
    # plt.imshow(image_label_overlay)
    # plt.axis("off")
    # ax = plt.gca()
    # regions = regionprops(data.labels)
    # for region in regions:
    #     minr, minc, maxr, maxc = region.bbox
    #     rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=1)
    #     ax.add_patch(rect)
    # print(len(unique(data.labels)))
    #plt.show()







    # sam.image = img_as_ubyte(rescale(sam.image, 0.25, channel_axis=2, anti_aliasing=False))
    # #sam.image = sam.image.astype(float16)
    # sam.update()
    # plt.imshow(sam.image)
    # plt.show()
    # sam.path_output = "/content/gdrive/MyDrive/data processed/optical images/batch01"
    # sam.path_checkpoint = "/content/gdrive/MyDrive/models"
    # sam.model_type = "vit_l"
    # sam.points_per_side = 64
    # sam.characteristic_dimension = 25
    # sam.get_image_info()
    # sam.slice_image() # slice image in several image crops
    # sam.run_sam_on_sliced_image(flag_print=True)
    # sam.filter_by_shape() # filter the labels by area and eccentricity
    # sam.filter_box_walls() # filter labels on the box walls.
    # sam.save_figure_to_disc()