import os
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
from numpy import unique

IMAGE_PATH = 'T:/data processed/optical images/segmentation sam/batch01'
FILES = [f'{IMAGE_PATH}/{x}' for x in os.listdir(IMAGE_PATH) if x.endswith('.dat')]
for FILE in FILES:
    with open(f"{FILE}", 'rb') as reader:
        data = pickle.load(reader)

    plt.figure(0)
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

    plt.figure(1)
    data.labels = clear_border(data.labels)
    data.thresh_area = 500
    regions = regionprops(data.labels)
    for region in regions:
        if not 500 <= region.area <= 5000:
            data.labels[data.labels==region.label] = 0
    data.labels = label(data.labels, connectivity=1)  # re-label label matrix
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
    plt.show()







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