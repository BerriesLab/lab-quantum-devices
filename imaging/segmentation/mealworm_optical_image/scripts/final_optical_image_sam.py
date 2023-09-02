import os
import numpy as np
from skimage.color import label2rgb, rgb2gray
from imaging.segmentation.mealworm_optical_image.tools.classes import SegmentationWithSAM
from imaging.segmentation.mealworm_optical_image.tools.image_utils import pixel_stats
import matplotlib.pyplot as plt

IMAGE_PATH = 'T:/data raw/optical images/batch01'
FILES = [f'{IMAGE_PATH}/{x}' for x in os.listdir(IMAGE_PATH) if x.endswith('.jpg') or x.endswith('.png')]
for FILE in FILES[1:2]:
    sam = SegmentationWithSAM(FILE) # create object instance

    sam.filter_box_walls_a_priori()



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