import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import mplcursors
import SimpleITK as sitk


class BrainAligner:

    def __init__(self, fix_img: sitk.Image, mov_img: sitk.Image):

        self.fix_img = fix_img
        self.mov_img = mov_img
        self.fix_img_spacings = fix_img.GetSpacing()
        self.mov_img_spacings = mov_img.GetSpacing()
        self.fix_img_size = fix_img.GetSize()
        self.mov_img_size = mov_img.GetSize()
        self.click1 = None
        self.click2 = None
        self.ax_fix_img = None
        self.ax_mov_img = None

        # Create a figure and axis
        self.fig, self.ax = plt.subplots()
        self.ax.set_axis_off()

        # Display the fixed image
        img_slice = sitk.Extract(self.fix_img, [self.fix_img.GetSize()[0], self.fix_img.GetSize()[1], 0], [0, 0, self.fix_img.GetSize()[2] // 2])
        extent = [0, self.fix_img.GetSize()[0], -self.fix_img.GetSize()[1], 0]  # left, right, bottom, top
        self.ax_fix_img = self.ax.imshow(sitk.GetArrayFromImage(img_slice), cmap='gray', extent=extent)

        # Display the moving image using OffsetImage
        img_slice = sitk.Extract(self.mov_img, [self.mov_img.GetSize()[0], self.mov_img.GetSize()[1], 0], [0, 0, self.mov_img.GetSize()[2] // 2])
        extent = [0, self.mov_img.GetSize()[0], -self.mov_img.GetSize()[1], 0]  # left, right, bottom, top
        self.ax_mov_img = self.ax.imshow(sitk.GetArrayFromImage(img_slice), cmap='jet', extent=extent, alpha=0.3)

        # Connect the onclick event to the function
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        # Enable cursor hover text to display coordinates
        mplcursors.cursor(hover=True)

        plt.show()

    def onclick(self, event):

        if self.click1 is None:
            self.click1 = (event.xdata, event.ydata)
            print(f'First click at ({self.click1[0]}, {self.click1[1]})')
        else:
            self.click2 = (event.xdata, event.ydata)
            print(f'Second click at ({self.click2[0]}, {self.click2[1]})')
            self.fig.canvas.mpl_disconnect(self.cid)
            self.move_image()

    def move_image(self):
        # Calculate the offset
        offset_x = self.click2[0] - self.click1[0]
        offset_y = self.click2[1] - self.click1[1]

        # Display the moving image using OffsetImage
        img_slice = sitk.Extract(self.mov_img, [self.mov_img.GetSize()[0], self.mov_img.GetSize()[1], 0], [0, 0, self.mov_img.GetSize()[2] // 2])
        extent = [self.click1[0] + offset_x,
                  self.click1[0] + offset_x + img_slice.GetSize()[0],
                  self.click1[1] + offset_y + img_slice.GetSize()[1],
                  self.click1[1] + offset_y]
        self.ax_mov_img.set_array(sitk.GetArrayFromImage(img_slice))
        self.ax_mov_img.set_extent(extent)
        self.fig.canvas.draw()

        # Reset the click variables
        self.click1 = None
        self.click2 = None


