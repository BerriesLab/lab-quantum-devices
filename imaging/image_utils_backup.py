import os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from scipy import ndimage as ndi
from numpy import ones, zeros, min, max, mean, std, histogram, linspace, digitize, unique, quantile, inf, log10, floor, logspace, sqrt, zeros_like
from scipy.interpolate import make_interp_spline
from skimage.filters import threshold_mean, threshold_minimum, threshold_otsu, threshold_local, threshold_multiotsu
from skimage.feature import canny, peak_local_max
from skimage.exposure import equalize_hist, rescale_intensity
from skimage.segmentation import clear_border, watershed
from skimage.measure import label, regionprops, regionprops_table
from skimage.morphology import closing, square, dilation, erosion
from skimage.color import label2rgb
from skimage.util import invert
matplotlib.rcParams.update({'font.size': 10})
fig_size = (30/2.54, 10/2.54)

def pixel_stats(image, image_gray, n_bins_rgb=50, n_bins_grayscale=50, plot=True, save=(False, None)):
    y_r, bin_edges_r = histogram(image[:, :, 0].flatten(), bins=n_bins_rgb, range=(0, 255))
    y_g, bin_edges_g = histogram(image[:, :, 1].flatten(), bins=n_bins_rgb, range=(0, 255))
    y_b, bin_edges_b = histogram(image[:, :, 2].flatten(), bins=n_bins_rgb, range=(0, 255))
    bincenters_r = 0.5 * (bin_edges_r[1:] + bin_edges_r[:-1])
    bincenters_g = 0.5 * (bin_edges_g[1:] + bin_edges_g[:-1])
    bincenters_b = 0.5 * (bin_edges_b[1:] + bin_edges_b[:-1])
    spl_r = make_interp_spline(bincenters_r, y_r, k=3)  # type: BSpline
    spl_g = make_interp_spline(bincenters_g, y_g, k=3)  # type: BSpline
    spl_b = make_interp_spline(bincenters_b, y_b, k=3)  # type: BSpline
    x_rgb = linspace(0, 255, 300)
    power_smooth_r = spl_r(x_rgb)
    power_smooth_g = spl_g(x_rgb)
    power_smooth_b = spl_b(x_rgb)
    x_gray = linspace(0, 1, 300)
    y, bin_edges = histogram(image_gray.flatten(), bins=n_bins_grayscale, range=(0, 1))
    bincenters = 0.5 * (bin_edges[1:] + bin_edges[:-1])
    spl = make_interp_spline(bincenters, y, k=3)  # type: BSpline
    power_smooth = spl(x_gray)
    if plot is True:
        fig, ax = plt.subplots(2, 2, figsize=(20/2.54, 15/2.54))
        ax[0, 0].set_title("Original")
        ax[0, 0].imshow(image)
        ax[0, 0].axis("off")
        ax[0, 1].set_title("Original RGB Hist.")
        ax[0, 1].hist(image[:, :, 0].flatten(), bins=n_bins_rgb, log=False, alpha=0.25, color="red")
        ax[0, 1].hist(image[:, :, 1].flatten(), bins=n_bins_rgb, log=False, alpha=0.25, color="green")
        ax[0, 1].hist(image[:, :, 2].flatten(), bins=n_bins_rgb, log=False, alpha=0.25, color="blue")
        ax[0, 1].plot(x_rgb, power_smooth_r, c="red")
        ax[0, 1].plot(x_rgb, power_smooth_g, c="green")
        ax[0, 1].plot(x_rgb, power_smooth_b, c="blue")
        ax[1, 0].set_title("Grayscale")
        ax[1, 0].imshow(image_gray, cmap=plt.cm.gray)
        ax[1, 0].axis("off")
        ax[1, 1].set_title("Greyscale Hist.")
        ax[1, 1].hist(image_gray.flatten(), bins=n_bins_grayscale, log=False, alpha=0.25)
        ax[1, 1].plot(x_gray, power_smooth, c="black")
        fig.tight_layout()
        if save[0] is True:
            fig.savefig(rf"{os.getcwd()}\data processed\photos\{save[1]} - statistics - rgb grayscale.jpg", dpi=1200)
    return {"x_rgb": x_rgb, "y_rgb":[power_smooth_r, power_smooth_g, power_smooth_b], "x_gray": x_gray, "y_gray": power_smooth_g}

def segmentation_threshold_mean_steps(image, footprint=square(1), area_thresh=None):
    """Uses mean value of pixel intensity to threshold the image. Brighter pixels are considered background. Perform a
    morphological closing operation to fill the dark holes, generates labels and remove the labels toching the image border. Finally filter
    out all labels with a pixel area outside the passe range."""
    threshold = threshold_mean(image)
    mask = closing(image < threshold, footprint)
    labels, num = label(label_image=mask, background=0, return_num=True, connectivity=1)
    labels = clear_border(labels=labels, bgval=0)
    if area_thresh is not None and isinstance(area_thresh, tuple):
        for region in regionprops(labels):
            if region.area < area_thresh[0] or region.area > area_thresh[1]:    # if area outside passed range
                labels[labels == region.label] = 0                              # set the label equal to background (zero)
    image_label_overlay = label2rgb(labels, image, alpha=0.5, bg_label=0, bg_color=None, kind="overlay")
    return threshold, mask, labels, image_label_overlay

def segmentation_threshold_value_steps(image, threshold=0, footprint=square(1), area_thresh=None):
    """Uses the passed 'threshold' value as threshold for the pixel intensities. Brighter pixels are considered background. Perform a
    morphological closing operation to fill the dark holes, generates labels and remove the labels toching the image border. Finally filter
    out all labels with a pixel area outside the passe range."""
    mask = closing(image < threshold, footprint)
    labels, num = label(label_image=mask, background=0, return_num=True, connectivity=1)
    labels = clear_border(labels=labels, bgval=0)
    if area_thresh is not None and isinstance(area_thresh, tuple):
        for region in regionprops(labels):
            if region.area < area_thresh[0] or region.area > area_thresh[1]:    # if area outside passed range
                labels[labels == region.label] = 0                              # set the label equal to background (zero)
    image_label_overlay = label2rgb(labels, image, alpha=0.5, bg_label=0, bg_color=None, kind="overlay")
    return threshold, mask, labels, image_label_overlay

def segmentation_threshold_minimum_steps(image, footprint=square(1), area_thresh=None):
    """Uses mean minimum variance alogorithm to threshold the image. Brighter pixels are considered background. Perform a
    morphological closing operation to fill the dark holes, generates labels and remove the labels toching the image border. Finally filter
    out all labels with a pixel area outside the passe range."""
    threshold = threshold_minimum(image)
    mask = closing(image < threshold, footprint)
    labels, num = label(label_image=mask, background=0, return_num=True, connectivity=1)
    labels = clear_border(labels=labels, bgval=0)
    if area_thresh is not None and isinstance(area_thresh, tuple):
        for region in regionprops(labels):
            if region.area < area_thresh[0] or region.area > area_thresh[1]:    # if area outside passed range
                labels[labels == region.label] = 0                              # set the label equal to background (zero)
    image_label_overlay = label2rgb(labels, image, alpha=0.5, bg_label=0, bg_color=None, kind="overlay")
    return threshold, mask, labels, image_label_overlay

def segmentation_threshold_otsu_steps(image, footprint=square(1), area_thresh=None):
    """Otsu’s method calculates an “optimal” threshold (marked by a red line in the histogram below)
    by maximizing the variance between two mealworm_optical_image of pixels, which are separated by the threshold.
    Equivalently, this threshold minimizes the intra-class variance. Brighter pixels are considered background. Perform a
    morphological closing operation to fill the dark holes, generates labels and remove the labels toching the image border. Finally filter
    out all labels with a pixel area outside the passe range."""
    threshold = threshold_otsu(image)
    mask = closing(image < threshold, footprint)
    labels, num = label(label_image=mask, background=0, return_num=True, connectivity=1)
    labels = clear_border(labels=labels, bgval=0)
    if area_thresh is not None and isinstance(area_thresh, tuple):
        for region in regionprops(labels):
            if region.area < area_thresh[0] or region.area > area_thresh[1]:    # if area outside passed range
                labels[labels == region.label] = 0                              # set the label equal to background (zero)
    image_label_overlay = label2rgb(labels, image, alpha=0.5, bg_label=0, bg_color=None, kind="overlay")
    return threshold, mask, labels, image_label_overlay

def segmentation_threshold_multiotsu_steps(image, classes=2, footprint=square(1), area_thresh=None):
    """Multi Otsu’s method calculates a number of “optimal” threshold (marked by a red line in the histogram below)
    by maximizing the variance between two mealworm_optical_image pairs of pixels, which are separated by the threshold. Brighter pixels are considered background.
    Perform a morphological closing operation to fill the dark holes, generates labels and remove the labels toching the image border. Finally filter
    out all labels with a pixel area outside the passe range."""
    thresholds = threshold_multiotsu(image=image, classes=classes)
    regions = digitize(image, bins=thresholds)  # Using the threshold values, we generate the three regions.
    for idx, val in enumerate(thresholds):
        if idx == 0:
            mask = closing(image < val, footprint)
        elif idx == len(thresholds) - 1:
            mask = closing(image >= thresholds[idx-1], footprint)
        else:
            mask = closing((thresholds[idx-1] <= image) * (image < thresholds[idx]), footprint)
    labels, num = label(label_image=regions, background=0, return_num=True, connectivity=1)
    labels = clear_border(labels=labels, bgval=0)
    if area_thresh is not None and isinstance(area_thresh, tuple):
        for region in regionprops(labels):
            if region.area < area_thresh[0] or region.area > area_thresh[1]:    # if area outside passed range
                labels[labels == region.label] = 0                              # set the label equal to background (zero)
    image_label_overlay = label2rgb(labels, image, alpha=0.5, bg_label=0, bg_color=None, kind="overlay")
    return thresholds, mask, labels, image_label_overlay

def segmentation_threshold_local_steps(image, block_size=35, offset=0, footprint=square(1), area_thresh=None):
    """Compute a threshold mask image based on local pixel neighborhood. Also known as adaptive or dynamic thresholding.
    The threshold value is the weighted mean for the local neighborhood of a pixel subtracted by a constant.
    Alternatively the threshold can be determined dynamically by a given function, using the ‘generic’ method."""
    threshold = threshold_local(image, block_size, method='gaussian', offset=offset)
    mask = closing(image < threshold, footprint)
    labels, num = label(label_image=mask, background=0, return_num=True, connectivity=1)
    labels = clear_border(labels=labels, bgval=0)
    if area_thresh is not None and isinstance(area_thresh, tuple):
        for region in regionprops(labels):
            if region.area < area_thresh[0] or region.area > area_thresh[1]:    # if area outside passed range
                labels[labels == region.label] = 0                              # set the label equal to background (zero)
    image_label_overlay = label2rgb(labels, image, alpha=0.5, bg_label=0, bg_color=None, kind="overlay")
    return threshold, mask, labels, image_label_overlay

def segmentation_edge_canny(image, threshold, sigma=1, structuring_element=square(1), area_thresh=None):
    """Segmentation by edge-recognition via Canny filter. In sequence,
    (1) define a mask with the passed threshold value (everything above threshold is considered background) and rescale the pixel intensity
    (2) apply Canny filter to the masked image
    (3) close features
    (4) label regions,
    (5) discard small regions."""
    if threshold is not None:
        image = rescale_intensity(image=image, in_range=(0, threshold))
    edge_map = canny(image, sigma=sigma, low_threshold=None, high_threshold=None, mask=None, use_quantiles=False, mode='constant', cval=0.0)
    edge_map_closed = closing(edge_map, structuring_element)
    edge_map_closed_and_filled = ndi.binary_fill_holes(edge_map_closed)
    labels, num = label(label_image=edge_map_closed_and_filled, background=0, return_num=True, connectivity=1)
    labels = clear_border(labels=labels, bgval=0)
    if area_thresh is not None and isinstance(area_thresh, tuple):
        for region in regionprops(labels):
            if region.area < area_thresh[0] or region.area > area_thresh[1]:    # if area outside passed range
                labels[labels == region.label] = 0                              # set the label equal to background (zero)
    image_label_overlay = label2rgb(labels, image, alpha=0.5, bg_label=0, bg_color=None, kind="overlay")
    return edge_map_closed_and_filled, labels, image_label_overlay

def segmentation_edge_watershed(image, threshold, n_dilation, n_erosion, structuring_element_dilation=square(1), structuring_element_erosion=square(1), area_thresh=None,
                                peaks_min_distance=10, peaks_rel_thresh=0.01, peaks_footprint=square(10)):
    """Segmentation by edge-recognition via watershed algorithm. For the algorithm to work, it needs that the user defines
    a region that is 'for sure' background, one that is 'for sure' foregroun', and an ambiguous region. In sequence,
    (1) define a mask with the passed threshold value (everything above threshold is considered background) and rescale the pixel intensity
    (2) Dilate n times, then erode n times to'isolate' features
    (3) calculate distance matrix
    (4) apply watershed algorithm to the distance matrix, where 0 is the background
    (5) get labels and discard small regions."""
    if threshold is not None:
        image = rescale_intensity(image=image, in_range=threshold)
    image = invert(image)
    for idx in range(n_dilation):
        image = dilation(image, structuring_element_dilation)
    for idx in range(n_erosion):
        image = erosion(image, structuring_element_erosion)
    distance = ndi.distance_transform_edt(image)
    coords = peak_local_max(distance, min_distance=peaks_min_distance, threshold_rel=peaks_rel_thresh, footprint=peaks_footprint)
    mask = zeros(distance.shape, dtype=bool)
    mask[tuple(coords.T)] = True
    markers, n = ndi.label(mask)
    labels = watershed(-distance, markers, mask=image, watershed_line=True)
    labels = clear_border(labels=labels, bgval=0)
    if area_thresh is not None and isinstance(area_thresh, tuple):
        for region in regionprops(labels):
            if region.area < area_thresh[0] or region.area > area_thresh[1]:    # if area outside passed range
                labels[labels == region.label] = 0
    image_label_overlay = label2rgb(labels, image, alpha=0.5, bg_label=0, bg_color=None, kind="overlay")
    return labels, image_label_overlay

def segmentation_threshold_value(image, threshold=0, eq=0, footprint=square(1), area_thresh=None):
    """Uses the passed 'threshold' value as threshold for the pixel intensities. Brighter pixels are considered background. Perform a
    morphological closing operation to fill the dark holes, generates labels and remove the labels toching the image border. Finally filter
    out all labels with a pixel area outside the passe range."""
    # rescale_intensity(image=image, in_range=, out_range=
    # mask = closing(image < threshold, footprint)
    if eq == 0:
        image = equalize_hist(image=image, mask=image < threshold)
    elif eq == 1:
        image = rescale_intensity(image=image)
    mask = closing(image, footprint)
    labels, num = label(label_image=mask, background=0, return_num=True, connectivity=1)
    labels = clear_border(labels=labels, bgval=0)
    if area_thresh is not None and isinstance(area_thresh, tuple):
        for region in regionprops(labels):
            if region.area < area_thresh[0] or region.area > area_thresh[1]:    # if area outside passed range
                labels[labels == region.label] = 0                              # set the label equal to background (zero)
    image_label_overlay = label2rgb(labels, image, alpha=0.5, bg_label=0, bg_color=None, kind="overlay")
    return threshold, mask, labels, image_label_overlay

def plot_segmentation_steps(filename, image, mask, labels, image_label_overlay):
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=fig_size)
    ax[0].set_title("Original")
    ax[0].imshow(image)
    ax[0].axis("off")
    ax[1].set_title(f"Thresholded")
    ax[1].imshow(mask, cmap=plt.cm.gray)
    ax[1].axis("off")
    ax[2].set_title(f"Segmented n: {len(unique(labels))}")
    ax[2].imshow(image_label_overlay)
    ax[2].axis("off")
    fig.tight_layout()
    fig.savefig(rf"{os.getcwd()}\data processed\photos\{filename}", dpi=1200)
    plt.close(fig)
    # if plot_regions is True:
    #     for region in regionprops(labels):
    #         # take regions with large enough areas
    #         if region.area <= area_thresh:
    #             # draw rectangle around segmented coins
    #             minr, minc, maxr, maxc = region.bbox
    #             rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
    #             ax[2].add_patch(rect)

def plot_segmentation(filename, image, mask, labels, image_label_overlay):
    x, y = image.shape
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10/2.54, y/x*15/2.54))
    ax.set_title(f"Segmented n: {len(unique(labels))}")
    ax.imshow(image_label_overlay)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(rf"{os.getcwd()}\data processed\photos\{filename}", dpi=1200)
    plt.close(fig)
    # if plot_regions is True:
    #     for region in regionprops(labels):
    #         # take regions with large enough areas
    #         if region.area <= area_thresh:
    #             # draw rectangle around segmented coins
    #             minr, minc, maxr, maxc = region.bbox
    #             rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=2)
    #             ax[2].add_patch(rect)

def plot_pixel_stats_grayscale(filename, image_gray, thresh, n_bins_grayscale=50):
    x_gray = linspace(0, 1, 300)
    y, bin_edges = histogram(image_gray.flatten(), bins=n_bins_grayscale, range=(0, 1))
    bincenters = 0.5 * (bin_edges[1:] + bin_edges[:-1])
    spl = make_interp_spline(bincenters, y, k=3)  # type: BSpline
    power_smooth = spl(x_gray)
    fig, ax = plt.subplots(1, 1, figsize=(20/2.54, 15/2.54))
    ax.hist(image_gray.flatten(), bins=n_bins_grayscale, log=False, alpha=0.5, color="gray")
    ax.plot(x_gray, power_smooth, c="black", linewidth=2)
    ax.axvline(thresh, color="red", linestyle="--", linewidth=2, alpha=0.5)
    ax.set_xlabel("Pixel intensity")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(rf"{os.getcwd()}\data processed\photos\{filename}", dpi=1200)
    plt.close(fig)

def area_from_regionprops(labels):
    regions = regionprops(labels)
    data_label = zeros(len(regions))
    data_area = zeros_like(data_label)
    data_centroid = zeros_like(data_label)
    for idx, region in enumerate(regions):
        data_label[idx] = region.label
        data_area[idx] = region.area
        data_centroid[idx] = region.centroid
    return data_label, data_area, data_centroid

def plot_area_stats(filename, data):
    data = log10(data)
    n = int(sqrt(len(data)))
    fig, ax = plt.subplots(1, 1, figsize=(20/2.54, 15/2.54))
    x = linspace(1, floor(abs(max(data))+1), n)
    ax.hist(data, bins=x, log=False, color="gray", edgecolor='black', linewidth=1.2)
    ax.set_xlabel("Log10(area) [pixel^2]")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(rf"{os.getcwd()}\data processed\photos\{filename}", dpi=1200)
    plt.close(fig)

def customized_box_plot(n_box, percentiles, axes, *args, **kwargs):
    """
    Generates a customized boxplot based on the given percentile values
    """
    box_plot = axes.boxplot([[-9, -4, 2, 4, 9],]*n_box, *args, **kwargs)
    # Creates len(percentiles) no of box plots
    min_y, max_y = inf, -inf
    for box_no, (q1_start, q2_start, q3_start, q4_start, q4_end, fliers_xy) in enumerate(percentiles):
        box_plot['caps'][2*box_no].set_ydata([q1_start, q1_start])
        box_plot['whiskers'][2*box_no].set_ydata([q1_start, q2_start])
        box_plot['caps'][2*box_no + 1].set_ydata([q4_end, q4_end])
        box_plot['whiskers'][2*box_no + 1].set_ydata([q4_start, q4_end])
        box_plot['boxes'][box_no].set_ydata([q2_start, q2_start, q4_start, q4_start, q2_start])
        box_plot['medians'][box_no].set_ydata([q3_start, q3_start])
        if fliers_xy is not None and len(fliers_xy[0]) != 0:  # If outliers exist
            box_plot['fliers'][box_no].set(xdata = fliers_xy[0], ydata = fliers_xy[1])
            min_y = min(q1_start, min_y, fliers_xy[1].min())
            max_y = max(q4_end, max_y, fliers_xy[1].max())
        else:
            min_y = min(q1_start, min_y)
            max_y = max(q4_end, max_y)
        axes.set_ylim([min_y*1.1, max_y*1.1])
    return box_plot

def append_dataframes(path, output_filename):
    files = [x for x in os.listdir(path) if x.endswith(".csv")]
    for idx, file in enumerate(files):
        if idx == 0:
            df = pd.read_csv(rf"{path}\{file}", index_col=False)
        else:
            df = pd.concat((df, pd.read_csv(rf"{path}\{file}", index_col=False)))
    df.to_csv(rf"{path}\{output_filename}", sep=",", index=False)



