import os
from imaging.segmentation.mealworm_optical_image.tools.classes import SegmentationWithSAM
import matplotlib.pyplot as plt

IMAGE_PATH = "T:/data raw/optical images/batch01"
IMAGE_PATH = "T:/data raw/optical images/test"
FILES = [rf"{IMAGE_PATH}/{x}" for x in os.listdir(IMAGE_PATH) if x.endswith(".jpg") or x.endswith(".png")]
for FILE in FILES[0:1]:
    sam = SegmentationWithSAM(FILE)
    sam.characteristic_dimension = 100
    sam.remove_trasparency_from_png_images()
    sam.path_checkpoint = r"T:/sam models"
    sam.path_output = r"T:/data processed/optical images/segmentation sam/test"
    sam.make_mask_to_remove_background_by_polygon_input()
    sam.slice_image()
    sam.run_sam_on_sliced_image(mask=True)
    sam.plot_figure_label_overlay()
    plt.show()

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
