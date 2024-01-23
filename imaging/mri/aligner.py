import matplotlib.pyplot as plt
import numpy as np
import mplcursors
import SimpleITK as sitk


class BrainAligner:

    def __init__(self, fix_img: sitk.Image, mov_img: sitk.Image):
        """
        The physical space is described by the (x, y, z) coordinate system
        The image space is described by the (i, j, k) coordinate system
        """

        self.ax = None
        self.fig = None
        self.ax_mov_img_yz = None
        self.ax_mov_img_xz = None
        self.ax_mov_img_xy = None
        self.ax_fix_img_yz = None
        self.ax_fix_img_xz = None
        self.ax_fix_img_xy = None
        self.fix_img = fix_img
        self.mov_img = mov_img
        self.click1 = None
        self.click2 = None

        # Initial image slice
        self.i0, self.j0, self.k0 = fix_img.GetSize()[0] // 2, fix_img.GetSize()[1] // 2, fix_img.GetSize()[2] // 2
        self.i, self.j, self.k = self.i0, self.j0, self.k0

        # self.fix_img_slice = np.array([fix_img.GetSize()[0] // 2, fix_img.GetSize()[1] // 2, fix_img.GetSize()[2] // 2], dtype=sitk.VectorUInt32)
        # self.fix_img_slice_physical_space = self.fix_img.TransformIndexToPhysicalPoint(self.fix_img_slice)
        # Initial (x0, y0, z0) and new (x, y, z) coordinates of moving image center
        # self.mov_img_x0y0z0 = np.array([mov_img.GetSize()[0] // 2, mov_img.GetSize()[1] // 2, mov_img.GetSize()[2] // 2], dtype=sitk.VectorUInt32)  # current coordinates of moving image center

    def execute(self):
        """In the order, the function creates a figure with 3 subplots (xy, xz and yz planes). Then, plots sections of the fixed image (MR image)
        and lets the user find the brain center by clicking on the MR sections. For example, the user can find the center on the z-axis by
        clicking on the xz sections. This automatically acquires the x and y coordinates, and set them as the new origin. Then, it updates the plots
        with the sections passing through the new coordinates. The centering continues until the user is satisfied with their selection of
        coordinates and press "Return". Then the functions plots an"""
        self.create_figure()
        self.place_img(self.fix_img, self.i0, self.j0, self.k0)
        plt.tight_layout()

        self.fig.canvas.mpl_connect('button_press_event', self.on_click_center)
        plt.show(block=False)
        mplcursors.cursor(hover=True)
        plt.show()

        flag = 0
        while flag == 0:

            # flag = self.fig.canvas.mpl_connect('key_press_event', self.on_key_return)
            mplcursors.cursor(hover=True)

        #self.fig.canvas.start_event_loop()

        # self.fig.canvas.mpl_connect('button_press_event', self.on_click_move)
        # self.fig.canvas.mpl_connect('close_event', self.on_close)
        # mplcursors.cursor(hover=True)
        # plt.tight_layout()
        # plt.show(block=False)

    def create_figure(self):
        # Create a figure and axis
        self.fig, self.ax = plt.subplots(1, 3)
        for idx, item in enumerate(self.ax.flatten()):
            item.set_axis_off()
        # label axes - necessary for identifying the axes
        self.ax[0].set_label("xy")
        self.ax[1].set_label("xz")
        self.ax[2].set_label("yz")

    def place_img(self, img, i, j, k):

        # Display fixed image - xy plane - Extent order: left, right, bottom, top
        img_slice = sitk.Extract(img, [img.GetSize()[0], img.GetSize()[1], 0], [0, 0, k])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[0].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='gray', extent=extent)

        # Display fixed image - xz plane
        img_slice = sitk.Extract(img, [img.GetSize()[0], 0, img.GetSize()[2]], [0, j, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[1].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='gray', extent=extent)

        # Display fixed image - xy plane
        img_slice = sitk.Extract(img, [0, img.GetSize()[1], img.GetSize()[2]], [i, 0, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[2].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='gray', extent=extent)

    def place_mov_img(self,):
        # Display moving image - xy plane - Extent order: left, right, bottom, top
        img_slice = sitk.Extract(self.mov_img, [self.mov_img.GetSize()[0], self.mov_img.GetSize()[1], 0], [0, 0, self.mov_img_xyz[2]])
        extent = [0, (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0], (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1], 0]
        self.ax_mov_img_xy = self.ax[0].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='jet', extent=extent, alpha=0.3)

        # Display moving image - xz plane
        img_slice = sitk.Extract(self.mov_img, [self.mov_img.GetSize()[0], 0, self.mov_img.GetSize()[2]], [0, self.mov_img_xyz[1], 0])
        extent = [0, (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0], (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1], 0]
        self.ax_mov_img_xz = self.ax[1].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='jet', extent=extent, alpha=0.3)

        # Display moving image - xy plane
        img_slice = sitk.Extract(self.mov_img, [0, self.mov_img.GetSize()[1], self.mov_img.GetSize()[2]], [self.mov_img_xyz[0], 0, 0])
        extent = [0, (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0], (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1], 0]
        self.ax_mov_img_yz = self.ax[2].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='jet', extent=extent, alpha=0.3)

    def on_close(self,):
        self.fig.canvas.stop_event_loop()

    def on_click_move(self, event):
        if self.click1 is None:
            self.click1 = (event.xdata, event.ydata, event.inaxes.get_label())
            print(f'Click 1 at ({self.click1[0]}, {self.click1[1]}) on {self.click1[2]}')
        else:
            self.click2 = (event.xdata, event.ydata, event.inaxes.get_label())
            print(f'Click 2 at ({self.click2[0]}, {self.click2[1]}) on {self.click2[2]}')
            if self.click1[2] != self.click2[2]:
                print("Clicks must be oin the same section.")
                self.on_click_move()
            self.move_image()

    def on_click_center(self, event, layer=0):
        self.click1 = (event.xdata, event.ydata, event.inaxes.get_label())
        print(f'Click 1 at ({self.click1[0]}, {self.click1[1]}) on {self.click1[2]}')
        if self.click1[2] == "xy":
            self.i, self.j = int(self.click1[0]//self.fix_img.GetSpacing()[0]), int(-1 * self.click1[1]//self.fix_img.GetSpacing()[1])
        if self.click1[2] == "xz":
            self.i, self.k = int(self.click1[0]//self.fix_img.GetSpacing()[0]), int(-1 * self.click1[1]//self.fix_img.GetSpacing()[2])
        if self.click1[2] == "yz":
            self.j, self.k = int(self.click1[0]//self.fix_img.GetSpacing()[1]), int(-1 * self.click1[1]//self.fix_img.GetSpacing()[2])
        self.update_plot(self.fix_img, 0)
        self.click1 = None

    def on_key_return(self, event):
        if event.key == "enter":
            print(f"Center slice: {self.i, self.j, self.k}")
            return 1
        return 0

    def move_image(self):
        """"""
        # Calculate the offset: target location - starting location
        if self.click1[2] == self.click2[2] == "xy":
            dx = int(self.click2[0] - self.click1[0])
            dy = int(self.click2[1] - self.click1[1])
            dz = 0
            print(f"dx, dy, dz: {dx}, {dy}, {dz}")
            self.update_plot(dx, dy, dz)

        if self.click1[2] == self.click2[2] == "xz":
            dx = int(self.click2[0] - self.click1[0])
            dy = 0
            dz = int(self.click2[1] - self.click1[1])
            print(f"dx, dy, dz: {dx}, {dy}, {dz}")
            self.update_plot(dx, dy, dz)

        if self.click1[2] == self.click2[2] == "yz":
            dx = 0
            dy = int(self.click2[0] - self.click1[0])
            dz = int(self.click2[1] - self.click1[1])
            print(f"dx, dy, dz: {dx}, {dy}, {dz}")
            self.update_plot(dx, dy, dz)

        # Reset the click variables
        self.click1 = None
        self.click2 = None

    def update_plot(self, img: sitk.Image, layer=0):
        """Update the displayed slices. The layer is the number of the overlayed image: 0 for the fixed image,
        and 1 for the moving image on top."""
        if layer == 0:
            n = 0
        elif layer == 1:
            n = 1
        # update xy
        img_slice = sitk.Extract(img, [img.GetSize()[0], img.GetSize()[1], 0], [0, 0, self.k])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[0].images[n].set_data(sitk.GetArrayFromImage(img_slice))
        self.ax[0].images[n].set_extent(extent)

        # update xz
        img_slice = sitk.Extract(img, [img.GetSize()[0], 0, img.GetSize()[2]], [0, self.j, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[1].images[n].set_data(sitk.GetArrayFromImage(img_slice))
        self.ax[1].images[n].set_extent(extent)

        # update yz
        img_slice = sitk.Extract(img, [0, img.GetSize()[1], img.GetSize()[2]], [self.i, 0, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[2].images[n].set_data(sitk.GetArrayFromImage(img_slice))
        self.ax[2].images[n].set_extent(extent)

        self.fig.canvas.draw()

    # def update_plot(self, img: sitk.Image):
    #
    #     # update xy
    #     img_slice = sitk.Extract(img, [img.GetSize()[0], img.GetSize()[1], 0], [0, 0, img.()[2]])
    #     extent = [0 - dx, (0 + img_slice.GetSize()[0] - dx) * img_slice.GetSpacing()[0], (0 - img_slice.GetSize()[1] - dy) * img_slice.GetSpacing()[1], 0 - dy]
    #     self.ax_mov_img_xy.set_array(sitk.GetArrayFromImage(img_slice))
    #     self.ax_mov_img_xy.set_extent(extent)
    #
    #     # update xz
    #     img_slice = sitk.Extract(img, [img.GetSize()[0], 0, img.GetSize()[2]], [0, img.GetOrigin()[1] + dy, 0])
    #     extent = [0 - dx, (0 + img_slice.GetSize()[0] - dx) * img_slice.GetSpacing()[0], (0 - img_slice.GetSize()[1] - dz) * img_slice.GetSpacing()[1], 0 - dz]
    #     self.ax_mov_img_xz.set_array(sitk.GetArrayFromImage(img_slice))
    #     self.ax_mov_img_xz.set_extent(extent)
    #
    #     # update yz
    #     img_slice = sitk.Extract(img, [0, img.GetSize()[1], img.GetSize()[2]], [img.GetOrigin() + dx, 0, 0])
    #     extent = [0 - dy, (0 + img_slice.GetSize()[0] - dy) * img_slice.GetSpacing()[0], (0 - img_slice.GetSize()[1] - dz) * img_slice.GetSpacing()[1], 0 - dz]
    #     self.ax_mov_img_yz.set_array(sitk.GetArrayFromImage(img_slice))
    #     self.ax_mov_img_yz.set_extent(extent)
    #
    #     self.fig.canvas.draw()

