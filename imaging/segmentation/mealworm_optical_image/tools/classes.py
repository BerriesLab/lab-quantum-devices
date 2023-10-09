import os
import random
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import cm
import numpy as np
from numpy import unique, zeros, argwhere, uint8, array, cos, sin, tan, pi, random
import pickle
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
from skimage import io, color
from skimage.measure import label, regionprops
from skimage.color import label2rgb, rgb2gray
from skimage.segmentation import find_boundaries, clear_border
from skimage.draw import polygon, polygon2mask
from skimage.feature import canny
from skimage.transform import hough_line, hough_line_peaks
from skimage.draw import ellipse
import torch

class Line:
    def __init__(self, m, c):
        self.c:float = m
        self.m:float = c

    def get_rnd_point_along_the_line(self):
        x = random.rand() * 10
        y = self.m * x + self.c
        return x, y

class LineHesse:
    def __init__(self, dist, angle):
        self.dist:float = dist
        self.angle:float = angle
        self.x0: float = self.get_x0()
        self.y0: float = self.get_y0()
        self.m: float = self.get_m()

    def get_x0(self):
        return self.dist * array(cos(self.angle))

    def get_y0(self):
        return self.dist * array(sin(self.angle))

    def get_m(self):
        return tan(self.angle + pi/2)

    def convert_to_class_line(self, xref:int=0):
        m = self.m
        c = self.y0 + (xref - self.x0) * self.m
        return Line(m, c)

class SegmentationWithSAM:

    def __init__(self, path_image: str):
        self.path_image = path_image
        self.path_checkpoint = r"/content/models" # path where models are stored
        self.path_output = r"/content/data" # path where to save data output
        self.dict_checkpoint = {"vit_h": "sam_vit_h_4b8939.pth", "vit_b": "sam_vit_b_01ec64.pth", "vit_l": "sam_vit_l_0b3195.pth"}
        self.image_name = path_image.split("/")[-1]
        """Image"""
        self.image = io.imread(self.path_image) # image in ndarray format
        self.image_lx = self.image.shape[0]
        self.image_ly = self.image.shape[1]
        self.image_dx = (1-0)/self.image.shape[0]
        self.image_dy = (1-0)/self.image.shape[1]
        self.image_aspect_ratio = self.image.shape[0] / self.image.shape[1]
        self.mask:np.array = None
        """SAM attributes"""
        self.model_type = "vit_h" # model type in string
        self.points_per_side = 128 # maximum value is 128
        self.crop_n_layers = 0
        self.downscale_factor = 1
        self.points_per_batch = 128 # the larger the faster SAM is, but also the larger RAM uses
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        """Parameters for cropping purposes"""
        self.characteristic_dimension = 25 # characteristic dimension of the feature to segment
        self.threshold = 1 # everything above threshold (0-1) is set to white (255, 255, 255)
        self.slice_bboxes: list[tuple, tuple] = None # list of slice bboxes coordinates in the format [(xmin, ymin), (xmax, ymax)]
        self.overlap = 20  # Number of pixels removed from each image crop border (must be > 0 as the outest labels are not touching the picture borders)
        self.connectivity = 1
        """Parameters for filtering purposes"""
        self.thresh_area = (500, 5000) # segments with area outisde the boundaries are discarded
        self.thresh_eccentricity = 0.5 # # segments with eccentricity smaller than tresh_eccentricitiy are discarded
        self.box_safe_margin: int = 5 # For 'filter_box_walls' method: number of pixel to extend the approximate polygon representing the sample box
        """Output"""
        self.labels = None
        self.segments = None

    '''Methods: *** SEGMENTATION WITH SAM ***'''

    def run_sam(self, mask: bool = False):
        """Note: the method overwrite the attribute labels"""
        mask_generator = SamAutomaticMaskGenerator(
            model = self.model_type,
            points_per_side = self.points_per_side,
            points_per_batch = self.points_per_batch,
            # pred_iou_thresh=0.88,
            # stability_score_thresh=0.95,
            # stability_score_offset= 1.0,
            # box_nms_thresh: float = 0.7,
            crop_n_layers = self.crop_n_layers,
            # crop_nms_thresh: float = 0.7,
            # crop_overlap_ratio: float = 512 / 1500,
            crop_n_points_downscale_factor = self.downscale_factor)
        if mask:
            masks = mask_generator.generate(self.apply_mask_to_image(copy=True))
        if not mask:
            masks = mask_generator.generate(self.image)
        self.labels = self.labels_from_sam_masks(self.image, masks)
        self.segments = self.count_segments()

    def slice_image(self):
        """Features are nicely segmented when their characheristic length is about
        max 1/10th of the image size. It comes therefore necessary to run SAM on
        image crops to ensure that the condition on the ratio is met."""
        slice_lx = 10 * self.characteristic_dimension
        slice_ly = 10 * self.characteristic_dimension
        slice_bboxes = self.calculate_slice_bboxes(self.image_ly, self.image_lx, slice_ly, slice_lx, 0.2, 0.2)
        print(f"Number of slices: {int(len(slice_bboxes))}")
        self.slice_bboxes = slice_bboxes

    def run_sam_on_sliced_image(self, mask: bool = False, flag_print: bool = False, flag_plot: bool = False, flag_bin: bool = False):
        """Run SAM on all image crops separately. Switch the flag on to print SAM status,
        and to save to disc plots and/or binary files. Note: the method overwrite the attribute labels, and
        the data of each image crop are appended to the object attribute 'labels'."""
        if self.slice_bboxes is None:
            print("'slice_bboxes' is empty. Please slice the image with 'slice_image' method.")
            return
        sam = sam_model_registry[self.model_type](checkpoint = f"{self.path_checkpoint}/{self.dict_checkpoint[self.model_type]}")
        sam.to(device = self.device)
        for idx, slice_box in enumerate(self.slice_bboxes):
            print(f'Running SAM on slice {idx}... ', end='')
            xmin, ymin = slice_box[0]
            xmax, ymax = slice_box[1]
            if mask:
                image_crop = self.apply_mask_to_image(copy=True)[xmin:xmax, ymin:ymax]
            if not mask:
                image_crop = self.image[xmin:xmax, ymin:ymax]

            if flag_print is True: # print segmentation status
                print(f"{idx+1} out of {len(self.slice_bboxes)}, {self.image_name}, size {self.image.shape}, crop {slice_box}, thresholding {self.threshold}, model {self.model_type}, points per side {self.points_per_side}, crop layers {self.crop_n_layers}, downscale factor {self.downscale_factor}... ", end="")

            # run segmentation on image crop
            mask_generator = SamAutomaticMaskGenerator(
                model = sam,
                points_per_side = self.points_per_side,
                points_per_batch = self.points_per_batch,
                crop_n_layers = self.crop_n_layers,
                crop_n_points_downscale_factor = self.downscale_factor)
            masks = mask_generator.generate(image_crop)
            labels_crop = self.labels_from_sam_masks(image_crop, masks)

            # define a filename for the image crop for saving purposes
            filename = f"{self.path_output}/{self.image_name}, size {self.image.shape}, crop {slice_box}, thresholding {self.threshold}, model {self.model_type}, points per side {self.points_per_side}, crop layers {self.crop_n_layers}, downscale factor {self.downscale_factor}, segments {len(unique(labels_crop))}"

            if flag_print is True: # print number of segments in image crop
                print(f"segments {len(unique(labels_crop))}")

            data = {"image": self.image_name,
                    "crop": slice_box,
                    "segments": len(unique(labels_crop)),
                    "labels": labels_crop}
            if idx == 0:
                self.labels = [data]
            else:
                self.labels.append(data)

            if flag_bin is True: # save binary copy to disc
                with open(f"{filename}.dat", "wb") as writer:
                    pickle.dump(data, writer)

            if flag_plot is True:
                plt.figure() # generate and save segmentation figure to disc
                image_label_overlay = label2rgb(labels_crop, image_crop, alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
                plt.imshow(image_label_overlay)
                plt.axis("off")
                plt.tight_layout()
                plt.savefig(f"{filename}.png", bbox_inches="tight")

                ax = plt.gca()  # generate and save segmentation with bboxes figure to disc
                regions = regionprops(labels_crop)
                for region in regions:
                    minr, minc, maxr, maxc = region.bbox
                    rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=1)
                    ax.add_patch(rect)
                plt.axis("off")
                plt.tight_layout()
                plt.savefig(f"{filename}, bboxes.png", bbox_inches="tight")
                plt.close()
            print("Done.")
        self.labels = self.stitch_labels(flag_print=flag_print)
        self.segments = self.count_segments()

    def stitch_labels(self, flag_print: bool = False):
        if len(self.labels) <= 1:
            print("There is nothing to stitch.")
            return

        # create empty matrix for labeling
        labels = zeros((self.image_lx, self.image_ly))

        for n, val in enumerate(self.labels):

            if flag_print:
                print(f"Stitching {n+1} out of {len(self.slice_bboxes)}, crop {val['crop']}... ", end="")

            (xmin, ymin), (xmax, ymax) = val["crop"] # Get crop coordinates. Data format is [(x_min, y_min), (x_max, y_max)]
            labels_crop = val["labels"]  # Get image crop labels
            # Create a background (=0) border to separate touching labels. This is necessary because of the stitching operation
            # Otherwise, adjacent labels would be merged together and relabeled as one.
            boundary_matrix = find_boundaries(labels_crop, connectivity=1, mode="inner", background=0)
            labels_crop[boundary_matrix > 0] = 0

            if xmin == ymin == 0:
                labels[xmin:xmax, ymin:ymax] = labels_crop
            if xmin > 0 and ymin == 0:
                labels[xmin+self.overlap:xmax, ymin:ymax] = labels_crop[self.overlap:, :]
            if xmin == 0 and ymin > 0:
                labels[xmin:xmax, ymin+self.overlap:ymax] = labels_crop[:, self.overlap:]
            if xmin > 0 and ymin > 0:
                labels[xmin+self.overlap:xmax, ymin+self.overlap:ymax] = labels_crop[self.overlap:, self.overlap:]

            labels = label(labels, connectivity=self.connectivity)  # re-label label matrix
            labels = self.merge_labels_after_stitching(labels)
            labels = label(labels, connectivity=self.connectivity)  # re-label label matrix

            if flag_print:
                print(f"Done.")

        return labels

    def count_segments(self):
        return len(unique(self.labels))

    '''Methods: *** LABELS FILTERING ***'''

    def filter_labels_by_shape(self):
        regions = regionprops(self.labels)
        for region in regions:
            if not self.thresh_area[0] <= region.area <= self.thresh_area[1]:
                self.labels[self.labels == region.label] = 0
            if region.eccentricity < self.thresh_eccentricity:
                self.labels[self.labels == region.label] = 0
        self.labels = label(self.labels, connectivity=1)  # re-label label matrix
        self.segments = self.count_segments()

    def filter_labels_on_the_border(self):
        """Note: the method overwrite the attribute labels"""
        self.labels = clear_border(self.labels)
        self.segments = self.count_segments()

    def filter_labels_outside_box_by_canny(self, sigma:int=1):
        """This method is meant to be used to remove all labels on the box walls that result from
        non-homogeneous illumination. Note: the method overwrite the label matrix with a new label, where
        all segments on the box walls are discarded (or set to background value)"""
        gra = rgb2gray(self.image)
        edge_map = canny(gra, sigma=1, low_threshold=0, high_threshold=1, mask=None)
        idxs = argwhere(edge_map == 1)
        box_xmin = min(idxs[:, 0]) - self.box_safe_margin
        box_xmax = max(idxs[:, 0]) + self.box_safe_margin
        box_ymin = min(idxs[:, 1]) - self.box_safe_margin
        box_ymax = max(idxs[:, 1]) + self.box_safe_margin
        box_x = array([box_xmin, box_xmin, box_xmax, box_xmax])
        box_y = array([box_ymin, box_ymax, box_ymax, box_ymin])
        polygon(box_x, box_y)
        box = polygon2mask(gra.shape, list(zip(box_x, box_y)))
        self.labels[box == 0] = 0

    '''Methods: *** MASK TO REMOVE BACKGROUND - BEFORE SAM ***'''

    def make_mask_to_remove_background_by_hist(self, epsilon=5):
        """The method finds the most recurring pixel color, and mask out everything else."""
        hist_r = np.histogram(self.image[:, :, 0].flatten(), 100)
        hist_g = np.histogram(self.image[:, :, 1].flatten(), 100)
        hist_b = np.histogram(self.image[:, :, 2].flatten(), 100)
        max_hist_r = hist_r[1][np.argmax(hist_r[0])]
        max_hist_g = hist_g[1][np.argmax(hist_g[0])]
        max_hist_b = hist_b[1][np.argmax(hist_b[0])]
        range_r = (max_hist_r * (1-epsilon/100), max_hist_r * (1+epsilon/100))
        range_g = (max_hist_g * (1-epsilon/100), max_hist_g * (1+epsilon/100))
        range_b = (max_hist_b * (1-epsilon/100), max_hist_b * (1+epsilon/100))
        mask = (self.image[:, :, 0] <= range_r[1]) * (self.image[:, :, 0] >= range_r[0]) * \
               (self.image[:, :, 1] <= range_g[1]) * (self.image[:, :, 1] >= range_g[0]) * \
               (self.image[:, :, 2] <= range_b[1]) * (self.image[:, :, 2] >= range_b[0])
        return mask

    def make_mask_to_remove_background_by_hough(self, sigma:int=2, n:int=4, crop:float=0.1, hough_threshold:float=0.1, epsilon_dist:int=1000):
        """THIS METHOD IS NOT IMPLEMENTED YET
        The moethod calculates the gradient from a blurred grayscale image. Then apply the Hough transform and
        select a number of line specified by the user. It groups the lines into parallels, filter out the parallels
        that are close to each other to leave one parallel per group. Then it finds the intersection of the
        parallels, order the vertex and build a rectangle polygon. The pixel inside the rectangel are the mask:
        everything outside the mask is set to 0."""
        plt.figure()
        mask = self.filter_box_by_hist()
        plt.imshow(self.image, cmap='gray')
        image_g = rgb2gray(self.image)
        image_g[mask] = 0
        grad = canny(image_g, sigma=sigma)
        grad[ellipse(r=int(self.image_lx/2), c=int(self.image_ly/2), r_radius=int(self.image_lx/3), c_radius=int(self.image_ly/3), shape=None, rotation=0.0)]=0
        plt.figure()
        plt.imshow(grad, cmap='gray')
        #plt.imshow(self.image, cmap='gray')
        plt.show()
        hspace, angles, dists = hough_line(grad)
        accum, angles, dists = hough_line_peaks(hspace, angles, dists, min_distance=0, min_angle=0, num_peaks=n, threshold=hough_threshold*hspace.max())
        # Notes on the Hough transform: The origin is the top left corner of the original image.
        # X and Y axis are horizontal and vertical edges respectively.
        # The distance is the minimal algebraic distance from the origin to the detected line.
        lines = []
        for i, (angle, dist) in enumerate(zip(angles, dists)):
            print(f"Found line {i}: dist = {dist}, angle = {angle}")
            lines.append(LineHesse(dist, angle))

        # group lines in parallels. Save them in a list of list [[l11, l12, ...], [l21, l22, ...], ...]
        tracker = []
        plines = []
        k = 0
        for i in range(n):
            if i not in tracker:
                plines.append([])
                plines[k].append(lines[i])
                tracker.append(i)
                for j in range(n):
                    if j > i and j not in tracker and self.lines_parallel(lines[i], lines[j], epsilon=np.radians(5)):
                        plines[k].append(lines[j])
                        tracker.append(j)
                k = k + 1
        print('\nGroup of parallel lines:')
        for grp in plines:
            for x in grp:
                print(f'({x.dist:.2f}, {x.angle:.2f})', end=', ')
            print("")

        # filter lines that are too close to each other. This leaves two lines per parallel
        print("\nFiltering lines close to each other")
        for k, val in enumerate(plines):
            for i, vali in enumerate(val):
                for j, valj in enumerate(val):
                    if j > i:
                        if abs(vali.dist - valj.dist) < epsilon_dist:
                            plines[k].remove(valj)
        print('Group of parallel lines:')
        for grp in plines:
            for x in grp:
                print(f'({x.dist:.2f}, {x.angle:.2f})', end=', ')
            print("")

        # filter lines that have no parallels. This removes all lines that do not define a rectangular shape
        print("\nFilter group of lines that have no parallels")
        for k, val in enumerate(plines):
            if len(val) < 2:
                plines.remove(val)
        print('Group of parallel lines:')
        for grp in plines:
            for x in grp:
                print(f'({x.dist:.2f}, {x.angle:.2f})', end=', ')
            print("")

        # plot results
        color = iter(cm.tab10(np.linspace(0, 1, n)))
        for val in plines:
            c = next(color)
            for idx, subval in enumerate(val):
                plt.axline((subval.x0, subval.y0), slope=subval.m, linewidth=2, color=c)

        # check if the algorithm has produced two pairs of parallel lines that could define a rectangle. If not return -1
        if len(plines) > 2:
            print("More than two pairs of parallel lines resulting. Cannot remove the background.")
            return -1

        # find lines crossing points
        x00, y00 = self.find_intersection_of_two_lines_in_hesse_form(plines[0][0], plines[1][0])
        x01, y01 = self.find_intersection_of_two_lines_in_hesse_form(plines[0][0], plines[1][1])
        x02, y02 = self.find_intersection_of_two_lines_in_hesse_form(plines[0][1], plines[1][0])
        x03, y03 = self.find_intersection_of_two_lines_in_hesse_form(plines[0][1], plines[1][1])
        plt.plot(x00, y00, marker='o', color='none', markersize=10, markeredgecolor='red')
        plt.plot(x01, y01, marker='o', color='none', markersize=10, markeredgecolor='red')
        plt.plot(x02, y02, marker='o', color='none', markersize=10, markeredgecolor='red')
        plt.plot(x03, y03, marker='o', color='none', markersize=10, markeredgecolor='red')
        xys = [(x00, y00), (x01, y01), (x02, y02), (x03, y03)]
        xys = self.order_coordinates_by_graham_scan(xys)
        box = polygon2mask(self.image.shape[0:2], np.flip(np.array(xys), axis=1))
        self.mask = box
        plt.imshow(self.image)

    def make_mask_to_remove_background_by_polygon_input(self):
        """The method asks the user to select the vertex of a polygon that would contain all
        features to segment. Then, it convert the vertex into a polygon and the polygon into a mask,
        which is stored in the object attribute."""
        # Display the image using imshow
        plt.imshow(self.image)
        plt.title('Click to Define Polygon (Right-click to Delete, Middle-click to Finish)')
        # Ask the user to click on the image to define polygon vertices
        print("Click on the image to define the polygon vertices. Right-click to finish.")
        vertices = plt.ginput(n=-1, timeout=0, show_clicks=True)
        # Close the image plot
        plt.close()
        # Display the extracted polygon coordinates
        print("Polygon vertices:")
        for vertex in vertices:
            print(f"X: {vertex[0]}, Y: {vertex[1]}")
        # Create a mask using polygon2mask
        mask = polygon2mask(self.image.shape[0:2], np.flip(vertices, axis=1))
        self.mask = np.logical_not(mask)
        #self.image[np.logical_not(mask)] = 0, 0, 0
        #plt.imshow(self.image)

    def apply_mask_to_image(self, copy:bool=True):
        """Retunr a copy of the image where everything outside the mask is set to black"""
        if copy:
            masked_image = self.image
            masked_image[np.logical_not(self.mask)] = 0, 0, 0
            return masked_image
        if not copy:
            self.image[np.logical_not(self.mask)] = 0, 0, 0

    '''Methods: *** IMAGE INFO & STATISTICS ***'''

    def get_image_info(self):
            print(f"Image path: {self.path_image}\n"
                  f"Aspect ratio {self.image_aspect_ratio:.1f}\n"
                  f"Lenght X: {self.image_lx} px, Delta X: {self.image_dx:.4f} px\n"
                  f"Length Y: {self.image_ly} px, Delta Y: {self.image_dy:.4f} px\n"
                  f"Characteristic dimension: {self.characteristic_dimension} px")

    def pixel_stats_rgb(self, n_bins_rgb=100, plot:bool=False, save:bool=False):
        plt.figure()
        r = plt.hist(self.image[:, :, 0].flatten(), range=(0, 255), bins=n_bins_rgb, log=False, alpha=0.25, color="red")
        g = plt.hist(self.image[:, :, 1].flatten(), range=(0, 255), bins=n_bins_rgb, log=False, alpha=0.25, color="green")
        b = plt.hist(self.image[:, :, 2].flatten(), range=(0, 255), bins=n_bins_rgb, log=False, alpha=0.25, color="blue")
        if save:
            plt.savefig(f"{os.getcwd()}/{self.image_name}, pixel rgb histogram.png", dpi=1200)
        if plot:
            plt.show()
        plt.close()
        return r, g, b

    def pixel_stats_grayscale(self, n_bins_grayscale=100, plot:bool=False, save:bool=False):
        g = plt.hist(rgb2gray(self.image).flatten(), range=(0, 1), bins=n_bins_grayscale, log=False)
        if save:
            plt.savefig(f"{os.getcwd()}/{self.image_name}, pixel grayscale histogram.png", dpi=1200)
        if plot:
            plt.show()
        plt.close()
        return g

    '''Methods: *** LABELS STATISTICS ***'''

    def hist_labels_geometry(self, plot:bool=True):
        """Generate histrograms data and plots for labels area and eccentricity"""
        regions = regionprops(self.labels)
        area = zeros(len(regions))
        ecce = zeros(len(regions))
        for idx, region in enumerate(regions):
            area[idx] = region.area
            ecce[idx] = region.eccentricity
        if plot is True:
            plt.figure()
            plt.hist(x=area, bins=100)
            plt.figure()
            plt.hist(x=ecce, bins=100)
        return area, ecce

    '''Methods: *** UTILITIES ***'''

    def remove_trasparency_from_png_images(self):
        self.image = self.image[:, :, 0:3]

    @staticmethod
    def lines_parallel(l1:LineHesse, l2:LineHesse, epsilon:float=3.0):
        if abs(l1.m - l2.m) < epsilon:
            return True
        else:
            return False

    @staticmethod
    def lines_perpendicular(l1:Line, l2:Line, epsilon:float=1):
        """Build two vectors from two random points belonging to the passed Line objects,
        then check if the dot product is zero."""
        x11, y11 = l1.get_rnd_point_along_the_line()
        x12, y12 = l1.get_rnd_point_along_the_line()
        x21, y21 = l2.get_rnd_point_along_the_line()
        x22, y22 = l2.get_rnd_point_along_the_line()
        v1 = np.array([y11, y12])
        v2 = np.array([y21, y22])
        if np.dot(v1, v2) < epsilon:
            return True
        else:
            return False

    @staticmethod
    def find_intersection_of_two_lines(l1:Line, l2:Line):
        """Find the intersection point of two straight lines, given the latter in the form y = mx + c"""
        x = - (l1.c - l2.c) / (l1.m - l2.m)
        y = l1.m * x + l1.c
        return x, y

    @staticmethod
    def find_intersection_of_two_lines_in_hesse_form(l1:LineHesse, l2:LineHesse):
        """Finds the intersection of two lines given in Hesse normal form.
        Returns closest integer pixel locations.
        """
        rho1, theta1 = l1.dist, l1.angle
        rho2, theta2 = l2.dist, l2.angle
        A = np.array([
            [np.cos(theta1), np.sin(theta1)],
            [np.cos(theta2), np.sin(theta2)]
        ])
        b = np.array([[rho1], [rho2]])
        x0, y0 = np.linalg.solve(A, b)
        x0, y0 = int(np.round(x0)), int(np.round(y0))
        return x0, y0

    def get_rectangle_vertex_from_edges(self, l1:Line, l2:Line, l3:Line, l4:Line):
        """Find vertexes of rectangle. First find parallel lines and group them. Then find
        intersection points between lines that are not parallel"""
        ls = [l1, l2, l3, l4]
        ls_prl = []
        for i in range(4):
            for j in range(4):
                if j <= i:
                    continue
                if self.lines_parallel(ls[i], ls[j]):
                    ls_prl.append((ls[i], ls[j]))

        if len(ls_prl) != 2:
            print("There are more than two groups of parallel lines. Execution terminates here.")
            exit()

        x1, y1 = self.find_intersection_of_two_lines(ls_prl[0][0], ls_prl[1][0])
        x2, y2 = self.find_intersection_of_two_lines(ls_prl[0][0], ls_prl[1][1])
        x3, y3 = self.find_intersection_of_two_lines(ls_prl[0][1], ls_prl[1][0])
        x4, y4 = self.find_intersection_of_two_lines(ls_prl[0][1], ls_prl[1][1])
        return (x1, y1), (x2, y2), (x3, y3), (x4, y4)

    @staticmethod
    def order_coordinates_by_graham_scan(xys:list[tuple]):
        # find coordinates of the center
        xc = xys[0][0]
        yc = xys[0][1]
        ic = 0
        for idx, xy in enumerate(xys):
            if xy[1] < yc:
                yc = xy[1]
                xc = xy[0]
                ic = idx
        for idx, xy in enumerate(xys):
            if xy[1] == yc and xy[0] < xc:
                yc = xy[1]
                xc = xy[0]
                ic = idx
        # calculate angles, distance.
        i, theta, d = [idx], [0], [0]
        for idx, xy in enumerate(xys):
            if idx == ic:
                continue
            i.append(idx)
            if xy[0]==xc and xy[1]-yc >= 0:
                theta.append(np.pi/2)
            else:
                theta.append(np.arctan2((xy[1]-yc), (xy[0]-xc)))
            d.append(((xy[0]-xc)**2 + (xy[1]-yc)**2)**0.5)
        points = list(zip(i, theta, d))
        points.sort(key=lambda x: x[1])
        points = np.asarray(points)
        return [xys[int(x)] for x in points[:, 0]]

    @staticmethod
    def calculate_slice_bboxes(image_height: int, image_width: int, slice_height: int = 512, slice_width: int = 512, overlap_height_ratio: float = 0.2, overlap_width_ratio: float = 0.2):
        """Given the height and width of an image, calculates how to divide the image into
        overlapping slices according to the height and width provided. These slices are returned
        as bounding boxes in xyxy format.
        :param image_height: Height of the original image.
        :param image_width: Width of the original image.
        :param slice_height: Height of each slice
        :param slice_width: Width of each slice
        :param overlap_height_ratio: Fractional overlap in height of each slice (e.g. an overlap of 0.2 for a slice of size 100 yields an overlap of 20 pixels)
        :param overlap_width_ratio: Fractional overlap in width of each slice (e.g. an overlap of 0.2 for a slice of size 100 yields an overlap of 20 pixels)
        :return: a list of bounding boxes in xyxy format
        """
        slice_bboxes = []
        y_max = y_min = 0
        y_overlap = int(overlap_height_ratio * slice_height)
        x_overlap = int(overlap_width_ratio * slice_width)
        while y_max < image_height:
            x_min = x_max = 0
            y_max = y_min + slice_height
            while x_max < image_width:
                x_max = x_min + slice_width
                if y_max > image_height or x_max > image_width:
                    xmax = min((image_width, x_max))
                    ymax = min((image_height, y_max))
                    xmin = max((0, xmax - slice_width))
                    ymin = max((0, ymax - slice_height))
                    slice_bboxes.append([(xmin, ymin), (xmax, ymax)])
                else:
                    slice_bboxes.append([(x_min, y_min), (x_max, y_max)])
                x_min = x_max - x_overlap
            y_min = y_max - y_overlap
        return slice_bboxes

    @staticmethod
    def labels_from_sam_masks(image, masks):
        if len(masks) == 0:
            return
        labels = zeros((image.shape[0], image.shape[1]), dtype=uint8)
        """Sorting is fundamental because some labels overlap. Therefore the user will want
        to label first the largest regions, and only then the smaller ones."""
        sorted_masks = sorted(masks, key=(lambda x: x["area"]), reverse=True)
        for idx, mask in enumerate(sorted_masks):
            m = mask["segmentation"]
            labels[m] = idx
        return labels

    @staticmethod
    def merge_labels_after_stitching(labels):
        """Check if neighbor elements are != 0 and != from (r, c) element. If so, then merge the labels"""
        rmin, rmax, cmin, cmax = 0, labels.shape[0], 0, labels.shape[1]
        # run through all label matrix elements
        for r in range(rmax):
            for c in range(cmax):
                # check all neighbour of element r, c with connectivity = 2
                if 0 < r < rmax - 1 and 0 < c < cmax-1 and labels[r, c] > 0:
                    for subr in [r-1, r, r+1]:
                        for subc in [c-1, c, c+1]:
                            if labels[subr, subc] != 0 and labels[subr, subc] != labels[r, c]:
                                target = labels[subr, subc]
                                labels[labels == target] = labels[r, c]
        return labels

    def update_attributes(self):
        """Update image attributes. Might be useful if: e.g. the image is rescaled."""
        self.image_lx = self.image.shape[0]
        self.image_ly = self.image.shape[1]
        self.image_dx = (1-0)/self.image.shape[0]
        self.image_dy = (1-0)/self.image.shape[1]
        self.image_aspect_ratio = self.image.shape[0] / self.image.shape[1]

    def threshold(self):
        """Note: this method overwrites the image originally stored in the object
        with a thresholded copy of the image, where all pixels with grayscale value
        larger than threshold are set to white."""
        image_gs = color.rgb2gray(self.image)
        mask = image_gs > self.threshold
        self.image[mask] = [255, 255, 255]

    '''Methods: *** PLOT ***'''

    def plot_figure_label_overlay(self, bboxes:bool = True):
        # save segmented image without boundary boxes to disc
        plt.figure()
        image_label_overlay = label2rgb(self.labels, self.image, alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
        plt.imshow(image_label_overlay)
        plt.axis("off")
        if bboxes is True:
            ax = plt.gca()
            regions = regionprops(self.labels)
            for region in regions:
                minr, minc, maxr, maxc = region.bbox
                rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=1)
                ax.add_patch(rect)
        plt.show()

    '''Methods: *** SAVE ***'''

    def save_bin_to_disc(self):
        # save labels to disc in binary format
        with open(f"{self.path_output}/{self.image_name}, {self.model_type}, {self.points_per_side}, labels.dat", "wb") as writer:
            #pickle.dump(vars(self), writer)
            pickle.dump(self, writer)

    def save_figure_label_overlay_to_disc(self):
        # save segmented image without boundary boxes to disc
        plt.figure()
        image_label_overlay = label2rgb(self.labels, self.image, alpha=0.3, bg_label=0, bg_color=None, kind="overlay", saturation=0.6)
        plt.imshow(image_label_overlay)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(f"{self.path_output}/{self.image_name}, {self.model_type}, {self.points_per_side}, segmentation.png", bbox_inches="tight", dpi=1200)
        # save segmented image with boundary boxes to disc
        ax = plt.gca()
        regions = regionprops(self.labels)
        for region in regions:
            minr, minc, maxr, maxc = region.bbox
            rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr, fill=False, edgecolor='red', linewidth=1)
            ax.add_patch(rect)
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(f"{self.path_output}/{self.image_name}, {self.model_type}, {self.points_per_side}, segmentation with bboxes.png", bbox_inches="tight", dpi=1200)
        plt.close()
