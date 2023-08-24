from natsort import natsorted
import SimpleITK as sitk
import os
import copy
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


class BeeCounter:

    def __init__(self, input_im, working_dir):
        self.im = input_im
        self.thresh_value = -700
        self.working_dir = working_dir

        Path.mkdir(Path(self.working_dir), exist_ok=True, parents=True)

    def thresh_and_clean(self):
        thresh_img = self.im > self.thresh_value
        cleaned_thresh_img = sitk.BinaryOpeningByReconstruction(thresh_img, [2, 2, 2])
        cleaned_thresh_img = sitk.BinaryDilate(cleaned_thresh_img, [1, 1, 1])
        cleaned_thresh_img = sitk.BinaryOpeningByReconstruction(cleaned_thresh_img, [2, 2, 2])

        return thresh_img, cleaned_thresh_img

    def floor_remover(self, thresh_img):
        floor = sitk.BinaryErode(thresh_img, [6, 0, 6])
        floor = sitk.BinaryDilate(floor, [2, 2, 2])
        floor = sitk.ConnectedComponent(floor)
        floor = sitk.RelabelComponent(floor, minimumObjectSize=1500)
        floor /= floor
        floor = sitk.Cast(floor, sitk.sitkUInt8)
        sitk.WriteImage(floor, os.path.join(self.working_dir, 'floor_seg.nii.gz'))

        return floor

    def wall_remover(self, thresh_img):
        wand = sitk.BinaryErode(thresh_img, [0, 5, 0])
        wand = sitk.ConnectedComponent(wand)
        wand = sitk.RelabelComponent(wand, minimumObjectSize=1500)
        wand /= wand
        wand = sitk.Cast(wand, sitk.sitkUInt8)
        wand = sitk.BinaryClosingByReconstruction(wand, [25, 25, 25])
        wand = sitk.BinaryDilate(wand, [2, 8, 2])
        sitk.WriteImage(wand, os.path.join(self.working_dir, 'wand_seg.nii.gz'))

        return wand

    def water_shedder(self, input_im, radius=1, split_twins=False, min_object_sz=10):
        dist_img = sitk.SignedMaurerDistanceMap(input_im != 0, insideIsPositive=False, squaredDistance=False,
                                                useImageSpacing=False)
        seeds = sitk.ConnectedComponent(dist_img < -radius)
        seeds = sitk.RelabelComponent(seeds, minimumObjectSize=min_object_sz)

        ws = sitk.MorphologicalWatershedFromMarkers(dist_img, seeds, markWatershedLine=True)
        ws = sitk.Mask(ws, sitk.Cast(input_im, ws.GetPixelID()))

        sitk.WriteImage(ws, os.path.join(self.working_dir,
                                         "ws_image.nii.gz"))
        ws_insert = sitk.Cast(copy.deepcopy(ws), sitk.sitkUInt32)

        if split_twins:
            intensity_islands = sitk.LabelStatisticsImageFilter()
            intensity_islands.Execute(self.im, ws_insert)
            median_bee_sz = np.median([intensity_islands.GetCount(x) for x in intensity_islands.GetLabels()]) \
                            * float(1.5)

            for label in natsorted(intensity_islands.GetLabels()):
                if intensity_islands.GetCount(label) > median_bee_sz and not label == 0:
                    bbox = intensity_islands.GetBoundingBox(label)
                    twin_region = ws_insert[bbox[0]:bbox[1],
                                  bbox[2]:bbox[3],
                                  bbox[4]:bbox[5]]
                    biggest_island = twin_region == label
                    background = (twin_region != 0) - biggest_island

                    biggest_island = sitk.Cast(biggest_island, sitk.sitkUInt32)
                    background = sitk.Cast(background, sitk.sitkUInt32)

                    biggest_island *= sitk.Cast((self.im[bbox[0]:bbox[1],
                                                 bbox[2]:bbox[3],
                                                 bbox[4]:bbox[5]] > (self.thresh_value + split_twins)),
                                                sitk.sitkUInt32)
                    biggest_island = sitk.BinaryDilate(biggest_island, [1, 1, 1])

                    ws_insert[bbox[0]:bbox[1],
                    bbox[2]:bbox[3],
                    bbox[4]:bbox[5]] = biggest_island + background
        return ws_insert

    def perform_count(self, ws_im, ground_truth=False, individual=None):
        shape_stats = sitk.LabelShapeStatisticsImageFilter()
        shape_stats.ComputeOrientedBoundingBoxOn()
        shape_stats.Execute(ws_im)

        intensity_stats = sitk.LabelIntensityStatisticsImageFilter()

        if ground_truth or individual:
            intensity_stats.Execute(ws_im, ws_im)
        else:
            intensity_stats.Execute(ws_im, self.im)

        stats_list = [(shape_stats.GetPhysicalSize(i),
                       shape_stats.GetElongation(i),
                       shape_stats.GetFlatness(i),
                       shape_stats.GetOrientedBoundingBoxSize(i)[0],
                       shape_stats.GetOrientedBoundingBoxSize(i)[2],
                       intensity_stats.GetMean(i),
                       intensity_stats.GetStandardDeviation(i),
                       intensity_stats.GetSkewness(i)) for i in shape_stats.GetLabels()]
        cols = ["Volume (nm^3)",
                "Elongation",
                "Flatness",
                "Oriented Bounding Box Minimum Size(nm)",
                "Oriented Bounding Box Maximum Size(nm)",
                "Intensity Mean",
                "Intensity Standard Deviation",
                "Intensity Skewness"]

        stats = pd.DataFrame(data=stats_list, index=shape_stats.GetLabels(), columns=cols)
        stats.describe()

        csv_file_name = os.path.join(self.working_dir,
                                     f"stats_count_demofile.csv")

        stats.describe().to_csv(csv_file_name, sep=';')

        return shape_stats, csv_file_name


class WormCounter:

    def __init__(self, input_im, working_dir):
        """
        Inicialization of the tool
        :param input_im:  the input float-valued image
        :param working_dir: the working directory
        """
        self.im = input_im
        # self.thresh_value = thresh_value  # max. -125
        self.working_dir = working_dir

        Path.mkdir(Path(self.working_dir), exist_ok=True, parents=True)

    def box_filter(self, x_min, x_max, y_min, y_max, z_min, z_max):
        """
        Creating a box filter binary image with values 1 within the box and 0 outside the box
        :param x_min: x lower bound
        :param x_max: x upper bound
        :param y_min: y lower bound
        :param y_max: y upper bound
        :param z_min: z lower bound
        :param z_max: z upper bound
        :return: the binary image
        """
        img = self.im * 0
        img[x_min:x_max, y_min:y_max, z_min:z_max] = 1
        img = sitk.Cast(img, sitk.sitkUInt8)
        return img

    def air_filter(self, threshold, minimum_object_size=0):
        """
        :param threshold:
        :param minimal_size:
        :return:
        """
        #selection_filter = sitk.Cast(self.im * 0 + 1, sitk.sitkUInt8)
        air = sitk.Image(self.im < threshold)
        if minimum_object_size > 0:
            air = sitk.ConnectedComponent(air)  # binary image with adjacent elements
            air = sitk.RelabelComponent(air, minimumObjectSize=minimum_object_size)
            air /= air  # To assign the same label to each segmented element
            air = sitk.Cast(air, sitk.sitkUInt8)
        return air

    def thresh_and_clean(self, selection_filter, threshold, minimal_size=0):
        """
        The general segmentation by the threshold value and the size of the objects
        :param selection_filter: the binary image selecting the region, that should be segmented (1) and the ignored region (0)
        :param threshold: the threshold value for the segmentation
        :param minimal_size: the minimal size of the objects chosen for the segmentation
        :return: the binary segmented image
        """
        thresh_img = sitk.And(self.im > threshold, selection_filter)
        if minimal_size > 0:
            thresh_img = sitk.ConnectedComponent(thresh_img)
            thresh_img = sitk.RelabelComponent(thresh_img, minimumObjectSize=minimal_size)
            thresh_img /= thresh_img
            thresh_img = sitk.Cast(thresh_img, sitk.sitkUInt8)

        return thresh_img

    def box_segmenter(self, erosion_matrix, dilation_matrix, selection_filter=None, threshold=-np.inf, minimum_object_size=0):
        """
        :param erosion_matrix: [binary matrix] structuring element for binary erosion
        :param dilation_matrix: [binary matrix] structuring element for binary dilation
        :param selection_filter: [binary matrix] image filter, where 1-regions are segmented and 0-regions are ignored. If none uses 'self.im * 0 + 1'
        :param threshold: [int] (minimum) threshold value for the segmentation
        :param minimum_object_size: [int] minimum size of the object for the segmentation to take place (number of elements?)
        :return: [binary matrix] segmented image
        """
        if selection_filter is None:
            selection_filter = sitk.Cast(self.im * 0 + 1, sitk.sitkUInt8)
        box = sitk.And(self.im > threshold, selection_filter)
        box = sitk.BinaryErode(box, erosion_matrix)
        if minimum_object_size > 0:
            box = sitk.ConnectedComponent(box)  # binary image with adjacent elements
            box = sitk.RelabelComponent(box, minimumObjectSize=minimum_object_size)
            box /= box  # To assign the same label to each segmented element
            box = sitk.Cast(box, sitk.sitkUInt8)
        box = sitk.BinaryDilate(box, dilation_matrix)
        box = sitk.And(box, selection_filter)
        return box

    def wall_remover(self, selection_filter=None, threshold=-np.inf, minimal_size=0):
        """
        The segmentation of the wall determined by a threshold value and the size
        :param selection_filter: the binary image selecting the region, that should be segmented (1) and the ignored region (0).
        If None then the selection filter is set equal to the whole image.
        :param threshold: the threshold value for the segmentation of the wall
        :param minimal_size: the minimal size of the objects chosen for the segmentation
        :return: the binary segmented image
        """
        if selection_filter is None:
            selection_filter = sitk.Cast(self.im * 0 + 1, sitk.sitkUInt8)
        wall = sitk.And(self.im > threshold, selection_filter)
        wall = sitk.BinaryErode(wall, [1, 8, 1])
        if minimal_size > 0:
            wall = sitk.ConnectedComponent(wall)
            wall = sitk.RelabelComponent(wall, minimumObjectSize=minimal_size)
            wall /= wall
            wall = sitk.Cast(wall, sitk.sitkUInt8)
        wall = sitk.BinaryDilate(wall, [2, 9, 2])
        wall = sitk.And(wall, selection_filter)

        sitk.WriteImage(wall, os.path.join(self.working_dir, 'wall_seg.nii.gz'))

        return wall

    def floor_remover(self, selection_filter, threshold, minimal_size=0):
        """
        The segmentation of the floor determined by a threshold value and the size
        :param selection_filter: the binary image selecting the region, that should be segmented (1) and the ignored region (0)
        :param threshold: the threshold value for the segmentation of the floor
        :param minimal_size: the minimal size of the objects chosen for the segmentation
        :return: the binary segmented image
        """
        floor = sitk.And(self.im > threshold, selection_filter)
        floor = sitk.BinaryErode(floor, [6, 1, 6])
        if minimal_size > 0:
            floor = sitk.ConnectedComponent(floor)
            floor = sitk.RelabelComponent(floor, minimumObjectSize=minimal_size)
            floor /= floor
            floor = sitk.Cast(floor, sitk.sitkUInt8)
        floor = sitk.BinaryDilate(floor, [7, 2, 7])
        floor = sitk.And(floor, selection_filter)

        sitk.WriteImage(floor, os.path.join(self.working_dir, 'floor_seg.nii.gz'))

        return floor

    def bright_remover(self, selection_filter, threshold_small, threshold_large):
        """
        The segmentation of the bright spots determined by 2 threshold values
        :param selection_filter: [binary matrix] the binary image selecting the regions that should be segmented (1) and ignored (0)
        :param threshold_1: [int] the threshold value for the segmentation of the seeds (small features)
        :param threshold_2: [int] the threshold value for the segmentation of the bright spots (large features)
        :return: [binary matrix] the binary segmented image
        """
        if selection_filter is None:
            selection_filter = sitk.Cast(self.im * 0 + 1, sitk.sitkUInt8)
        small_features = self.im > threshold_small
        small_features = sitk.BinaryDilate(small_features, [2, 2, 2])
        large_features = self.im > threshold_large
        bright = sitk.And(sitk.And(small_features, large_features), selection_filter)

        # sitk.WriteImage(bright, os.path.join(self.working_dir, 'bright_seg.nii.gz'))

        return bright

    def substrate_remover(self, selection_filter, box, box_filter, threshold, minimal_size=0):
        """
        The segmentation of the substrate determined by a box, a threshold value and the size
        :param selection_filter: the binary image selecting the region, that should be segmented (1) and the ignored region (0)
        :param box: the segmentation of the box
        :param box_filter: the binary image marking the region, where the substrate should appear (1) and the ignored region (0)
        :param threshold: the threshold value for the segmentation of the substrate
        :param minimal_size: the minimal size of the objects chosen for the segmentation
        :return: the binary segmented image
        """
        box_content = sitk.And(self.im > -950, box_filter)
        box_content = sitk.BinaryErode(box_content, [1, 1, 1])

        box_content = sitk.SignedMaurerDistanceMap(box_content, insideIsPositive=False, squaredDistance=False, useImageSpacing=False) < 20
        box_content = sitk.SignedMaurerDistanceMap(box_content, insideIsPositive=False, squaredDistance=False, useImageSpacing=False) < -20 + 1
        box_content = sitk.And(box_content, sitk.Not(box))
        box_content = sitk.SignedMaurerDistanceMap(box_content, insideIsPositive=False, squaredDistance=False, useImageSpacing=False) < -3 + 1
        box_content = sitk.ConnectedComponent(box_content)
        box_content = sitk.RelabelComponent(box_content, sortByObjectSize=True)
        box_content = box_content == 1
        box_content = sitk.BinaryDilate(box_content, [4, 4, 4])

        sitk.WriteImage(box_content, os.path.join(self.working_dir, 'box_content_seg.nii.gz'))

        substrate = sitk.And(self.im > threshold, sitk.And(selection_filter, box_content))
        substrate = sitk.BinaryErode(substrate, [1, 1, 1])
        if minimal_size > 0:
            substrate = sitk.ConnectedComponent(substrate)
            substrate = sitk.RelabelComponent(substrate, minimumObjectSize=minimal_size)
            substrate /= substrate
            substrate = sitk.Cast(substrate, sitk.sitkUInt8)

        substrate = sitk.BinaryDilate(substrate, [1, 1, 1])

        sitk.WriteImage(substrate, os.path.join(self.working_dir, 'substrate_seg.nii.gz'))

        return substrate

    def ws(self, worms, seeds, radius=1, minimal_size=0):
        """
        Division of the worms based on the seeds using water_shed algorithm
        :param worms: the binary image of the segmented worms
        :param seeds: the labeled image of the seeds
        :param radius: the radius of area around the seeds that is also included into segmentation
        :param minimal_size: the minimal size of objects after ws
        :return: the labeled image of worms and the binary image of unused segmented area
        """
        seeds_true = seeds > 0

        worms_objects = sitk.ConnectedComponent(worms)
        worms_filter = worms_objects * sitk.Cast(seeds_true, sitk.sitkUInt32)
        intensity_islands = sitk.LabelStatisticsImageFilter()
        intensity_islands.Execute(self.im, worms_filter)
        worm_sep = worms * 0
        for label in intensity_islands.GetLabels():
            if label > 0:
                worm_sep += worms_objects == label

        worm_sep = sitk.BinaryDilate(worm_sep, [radius, radius, radius])

        worm_leftover = sitk.And(worms, sitk.Not(worm_sep))
        dist_img = sitk.SignedMaurerDistanceMap(worm_sep != 0, insideIsPositive=False, squaredDistance=False, useImageSpacing=False)

        ws = sitk.MorphologicalWatershedFromMarkers(dist_img, seeds, markWatershedLine=True)
        ws = sitk.Mask(ws, sitk.Cast(worm_sep, ws.GetPixelID()))
        ws = sitk.ConnectedComponent(ws)

        if minimal_size > 0:
            ws = sitk.RelabelComponent(ws, minimumObjectSize=minimal_size)

        return ws, worm_leftover

    def split(self, seg, cut_limit):
        """
        Splitting the segmented image into 2 images given by the cutting limit
        :param seg: the input binary (or non-negative valued) image
        :param cut_limit: the cutting limit
        :return: 2 the binary images (the small objects and the big objects)
        """
        seg = sitk.ConnectedComponent(seg)
        seg2 = sitk.RelabelComponent(seg, minimumObjectSize=cut_limit)
        seg2 /= seg2
        seg2 = sitk.Cast(seg2, sitk.sitkUInt8)
        seg1 = sitk.And(seg > 0, sitk.Not(seg2))

        return seg1, seg2

    def divide(self, input_im, cutting_size=100, threshold_old=0, split_twins=False, min_object_sz=10):
        """
        The division of connected objects in the segmented image driven by the cutting size and the threshold value
        :param input_im: the input segmented binary image
        :param cutting_size: the lower bound for the size of objects to be proposed for dividing
        :param threshold_old: the old threshold value
        :param split_twins: the threshold value difference used to divide the connected objects
        :param min_object_sz: the minimal size of the objects chosen for the segmentation
        :return: the labelled object image
        """
        objects = sitk.ConnectedComponent(input_im)
        objects = sitk.RelabelComponent(objects, minimumObjectSize=min_object_sz)

        objects_divide = sitk.Cast(copy.deepcopy(objects), sitk.sitkUInt32)

        if split_twins:
            intensity_islands = sitk.LabelStatisticsImageFilter()
            intensity_islands.Execute(self.im, objects_divide)

            for label in natsorted(intensity_islands.GetLabels()):
                if intensity_islands.GetCount(label) > cutting_size and not label == 0:
                    bbox = intensity_islands.GetBoundingBox(label)
                    twin_region = objects_divide[bbox[0]:bbox[1],
                                                 bbox[2]:bbox[3],
                                                 bbox[4]:bbox[5]]
                    biggest_island = twin_region == label
                    background = (twin_region != 0) - biggest_island

                    biggest_island = sitk.Cast(biggest_island, sitk.sitkUInt32)
                    background = sitk.Cast(background, sitk.sitkUInt32)

                    biggest_island *= sitk.Cast((self.im[bbox[0]:bbox[1],
                                                         bbox[2]:bbox[3],
                                                         bbox[4]:bbox[5]] > (threshold_old + split_twins)), sitk.sitkUInt32)
                    # biggest_island = sitk.BinaryDilate(biggest_island, [1, 1, 1])

                    objects_divide[bbox[0]:bbox[1],
                                   bbox[2]:bbox[3],
                                   bbox[4]:bbox[5]] = biggest_island + background

        return objects_divide

    def combine(self, seg1, seg2, min_object_sz=0):
        """
        Combining 2 segmentations into 1
        :param seg1: the input binary (or non-negative valued) image No. 1
        :param seg2: the input binary (or non-negative valued) image No. 2
        :param min_object_sz: the minimal size of the objects chosen for the segmentation
        :return: the labeled image
        """
        seg = sitk.Xor(seg1 > 0, seg2 > 0)
        seg = sitk.BinaryErode(seg, [1, 1, 1])
        if min_object_sz > 0:
            seg = sitk.ConnectedComponent(seg)
            seg = sitk.RelabelComponent(seg, minimumObjectSize=min_object_sz)
            seg /= seg
            seg = sitk.Cast(seg, sitk.sitkUInt8)
        seg = sitk.BinaryDilate(seg, [1, 1, 1])
        seg = sitk.ConnectedComponent(seg)

        return seg

    def split_divide_combine(self, worms_seg, cut_limit, threshold, minimal_size, minimal_size_ws):
        """
        Improving segmentation by selecting only objects larger than cut_limit, choosing the new threshold value
        :param worms_seg: original input labeled image
        :param cut_limit: the size limit for the further segmentation
        :param threshold: new threshold value for the seeds
        :param minimal_size: the minimal size of the seeds
        :param minimal_size_ws: the minimal size after the ws
        :return: the labeled image
        """
        worms_done, worms_big = self.split(worms_seg, cut_limit=cut_limit)
        seeds_worm_big = self.thresh_and_clean(selection_filter=worms_big, threshold=threshold, minimal_size=minimal_size)
        seeds_worm_big = self.divide(seeds_worm_big, min_object_sz=0)
        worms_seg2, worm_leftover2 = self.ws(worms_big, seeds_worm_big, radius=0, minimal_size=minimal_size_ws)
        worms_seg2 = self.combine(worms_seg2, worm_leftover2)

        return worms_done, worms_seg2

    def stats(self, im):
        """
        Generates the statistics for the given labeled image
        :param im: the labeled image
        :return: list of statistics
        """
        shape_stats = sitk.LabelShapeStatisticsImageFilter()
        shape_stats.ComputeOrientedBoundingBoxOn()
        shape_stats.Execute(im)

        intensity_stats = sitk.LabelIntensityStatisticsImageFilter()
        intensity_stats.Execute(im, self.im)

        stats_list = [(shape_stats.GetPhysicalSize(i),
                       shape_stats.GetElongation(i),
                       shape_stats.GetFlatness(i),
                       shape_stats.GetOrientedBoundingBoxSize(i)[0],
                       shape_stats.GetOrientedBoundingBoxSize(i)[2],
                       intensity_stats.GetMean(i),
                       intensity_stats.GetStandardDeviation(i),
                       intensity_stats.GetSkewness(i),
                       i) for i in shape_stats.GetLabels()]

        return stats_list

    def split_by_stats(self, seg, stat_id, cut_limit):
        '''
        Splitting the set based on the selected statistics and the cut-off value
        :param seg: the input binary (or non-negative valued) image
        :param stat_id: the id of the selected statistics
        :param cut_limit: the cut-off value to divide the set
        :return: 2 binary images with values of the selected statistics lower (seg1) or higher (seg2) than the limit
        '''
        seg = sitk.ConnectedComponent(seg)
        shape_stats = sitk.LabelShapeStatisticsImageFilter()
        shape_stats.ComputeOrientedBoundingBoxOn()
        shape_stats.Execute(seg)
        if 0 <= stat_id <= 4:
            if stat_id == 0:
                stats_list = [[shape_stats.GetPhysicalSize(i), i] for i in shape_stats.GetLabels()]
            elif stat_id == 1:
                stats_list = [[shape_stats.GetElongation(i), i] for i in shape_stats.GetLabels()]
            elif stat_id == 2:
                stats_list = [[shape_stats.GetFlatness(i), i] for i in shape_stats.GetLabels()]
            elif stat_id == 3:
                stats_list = [[shape_stats.GetOrientedBoundingBoxSize(i)[0], i] for i in shape_stats.GetLabels()]
            elif stat_id == 4:
                stats_list = [[shape_stats.GetOrientedBoundingBoxSize(i)[2], i] for i in shape_stats.GetLabels()]
        elif 5 <= stat_id <= 7:
            intensity_stats = sitk.LabelIntensityStatisticsImageFilter()
            intensity_stats.Execute(seg, self.im)
            if stat_id == 5:
                stats_list = [[intensity_stats.GetMean(i), i] for i in shape_stats.GetLabels()]
            elif stat_id == 6:
                stats_list = [[intensity_stats.GetStandardDeviation(i), i] for i in shape_stats.GetLabels()]
            elif stat_id == 7:
                stats_list = [[intensity_stats.GetSkewness(i), i] for i in shape_stats.GetLabels()]

        seg1 = (seg > 0) * 0
        seg2 = (seg > 0) * 0

        for [stat, i] in stats_list:
            if not i == 0:
                if stat < cut_limit:
                    seg1 += seg == i
                else:
                    seg2 += seg == i

        seg1 = sitk.Cast(seg1, sitk.sitkUInt8)
        seg2 = sitk.Cast(seg2, sitk.sitkUInt8)

        return seg1, seg2

    def show_count(self, input_im, minimum=0, maximum=10):
        """
        Assigning the value of the size of the objects of the segmented image
        :param input_im: the input binary (or non-negative valued) image
        :param minimum: the lower bound for the shown size of islands
        :param maximum: the upper bound for the shown size of islands
        :return: the image with the value of the size of the island
        """
        non_zero = input_im > 0
        non_zero = sitk.Cast(non_zero, sitk.sitkUInt32)
        seg_w_index = sitk.ConnectedComponent(non_zero)
        islands = sitk.LabelStatisticsImageFilter()
        islands.Execute(self.im, seg_w_index)
        index = np.array(islands.GetLabels())
        count = np.array([islands.GetCount(x) for x in islands.GetLabels()])

        fil = seg_w_index < 0
        for i in range(len(index)):
            if not index[i] == 0 and (count[i] < minimum or count[i] > maximum):
                fil += (seg_w_index == index[i])
        fil = sitk.Cast(fil, sitk.sitkUInt32)
        non_zero *= (fil * -1 + 1)
        for i in range(len(index)):
            if not index[i] == 0 and (minimum <= count[i] <= maximum):
                fil = sitk.Cast((seg_w_index == index[i]), sitk.sitkUInt32)
                non_zero += fil * (count[i] - 1)

        return non_zero

    def perform_count(self, ws_im, ground_truth=False, individual=None, name_csv="stats_count_demofile.csv", name_png="stats_plot_demofile.png"):
        """
        Calculation of the statistics including generating histograms
        :param ws_im: the labeled image
        :param ground_truth:
        :param individual:
        :param name_csv: the name of the output csv file
        :param name_png: the name of the output png file
        :return: shape statistics and the csv file name
        """
        shape_stats = sitk.LabelShapeStatisticsImageFilter()
        shape_stats.ComputeOrientedBoundingBoxOn()
        shape_stats.Execute(ws_im)

        intensity_stats = sitk.LabelIntensityStatisticsImageFilter()

        if ground_truth or individual:
            intensity_stats.Execute(ws_im, ws_im)
        else:
            intensity_stats.Execute(ws_im, self.im)

        stats_list = [(shape_stats.GetPhysicalSize(i),
                       shape_stats.GetElongation(i),
                       shape_stats.GetFlatness(i),
                       shape_stats.GetOrientedBoundingBoxSize(i)[0],
                       shape_stats.GetOrientedBoundingBoxSize(i)[2],
                       intensity_stats.GetMean(i),
                       intensity_stats.GetStandardDeviation(i),
                       intensity_stats.GetSkewness(i)) for i in shape_stats.GetLabels()]
        cols = ["Volume (nm^3)",
                "Elongation",
                "Flatness",
                "Oriented Bounding Box Minimum Size(nm)",
                "Oriented Bounding Box Maximum Size(nm)",
                "Intensity Mean",
                "Intensity Standard Deviation",
                "Intensity Skewness"]

        stats = pd.DataFrame(data=stats_list, index=shape_stats.GetLabels(), columns=cols)
        stats.describe()

        csv_file_name = os.path.join(self.working_dir, name_csv)

        stats.describe().to_csv(csv_file_name, sep=';')

        # plotting
        fig, axes = plt.subplots(nrows=len(cols), ncols=2, figsize=(6, 4 * len(cols)))
        axes[0, 0].axis('off')

        stats.loc[:, cols[0]].plot.hist(ax=axes[0, 1], bins=25)
        axes[0, 1].set_xlabel(cols[0])
        axes[0, 1].xaxis.set_label_position("top")

        for i in range(1, len(cols)):
            c = cols[i]
            bar = stats.loc[:, [c]].plot.hist(ax=axes[i, 0], bins=20, orientation='horizontal', legend=False)
            bar.set_ylabel(stats.loc[:, [c]].columns.values[0])
            scatter = stats.plot.scatter(ax=axes[i, 1], y=c, x=cols[0])
            scatter.set_ylabel('')
            # Remove axis labels from all plots except the last (they all share the labels)
            if i < len(cols) - 1:
                bar.set_xlabel('')
                scatter.set_xlabel('')
        # Adjust the spacing between plot columns and set the plots to have a tight
        # layout inside the figure.
        plt.subplots_adjust(wspace=0.4)
        plt.tight_layout()
        plt.savefig(os.path.join(self.working_dir, name_png), bbox_inches='tight')

        return shape_stats, csv_file_name


def mask_image_multiply(mask, image):
    components_per_pixel = image.GetNumberOfComponentsPerPixel()
    if  components_per_pixel == 1:
        return mask * image
    else:
        return sitk.Compose([mask*sitk.VectorIndexSelectionCast(image,channel) for channel in range(components_per_pixel)])


def alpha_blend(image1, image2, alpha=0.5, mask1=None, mask2=None):
    """
    Alaph blend two images, pixels can be scalars or vectors.
    The alpha blending factor can be either a scalar or an image whose
    pixel type is sitkFloat32 and values are in [0,1].
    The region that is alpha blended is controled by the given masks.
    """

    if not mask1:
        mask1 = sitk.Image(image1.GetSize(), sitk.sitkFloat32) + 1.0
        mask1.CopyInformation(image1)
    else:
        mask1 = sitk.Cast(mask1, sitk.sitkFloat32)
    if not mask2:
        mask2 = sitk.Image(image2.GetSize(), sitk.sitkFloat32) + 1
        mask2.CopyInformation(image2)
    else:
        mask2 = sitk.Cast(mask2, sitk.sitkFloat32)
    # if we received a scalar, convert it to an image
    if type(alpha) != sitk.SimpleITK.Image:
        alpha = sitk.Image(image1.GetSize(), sitk.sitkFloat32) + alpha
        alpha.CopyInformation(image1)
    components_per_pixel = image1.GetNumberOfComponentsPerPixel()
    if components_per_pixel > 1:
        img1 = sitk.Cast(image1, sitk.sitkVectorFloat32)
        img2 = sitk.Cast(image2, sitk.sitkVectorFloat32)
    else:
        img1 = sitk.Cast(image1, sitk.sitkFloat32)
        img2 = sitk.Cast(image2, sitk.sitkFloat32)

    intersection_mask = mask1 * mask2

    intersection_image = mask_image_multiply(
        alpha * intersection_mask, img1
    ) + mask_image_multiply((1 - alpha) * intersection_mask, img2)
    return (
            intersection_image
            + mask_image_multiply(mask2 - intersection_mask, img2)
            + mask_image_multiply(mask1 - intersection_mask, img1)
    )


def threshold_filters(filter_name="Otsu"):
    filter_dict = {"Otsu": sitk.OtsuThresholdImageFilter(),
                   "Triangle" : sitk.TriangleThresholdImageFilter(),
                   "Huang" : sitk.HuangThresholdImageFilter(),
                   "MaxEntropy" : sitk.MaximumEntropyThresholdImageFilter()}
    return filter_dict[filter_name]

