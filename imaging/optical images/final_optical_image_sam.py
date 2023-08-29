import os
from classes import SegmentationWithSAM

IMAGE_PATH = r"T:\data raw\photos"
FILES = [rf"{IMAGE_PATH}\{x}" for x in os.listdir(IMAGE_PATH) if x.endswith(".jpg")]
sam = SegmentationWithSAM(FILES[0]) # create object instance
sam.path_output = r"T:\data processed\optical images"
sam.path_checkpoint = r"T:\sam models"
sam.model_type = "vit_b"
sam.points_per_side = 32
sam.get_image_info()
sam.slice_image() # slice image in several image crops
sam.run_sam_on_sliced_image(flag_print=True)
sam.filter_by_shape() # filter the labels by area and eccentricity
sam.filter_box_walls() # filter labels on the box walls.