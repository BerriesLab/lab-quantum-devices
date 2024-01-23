import matplotlib.pyplot as plt
import numpy as np
import mplcursors
import SimpleITK as sitk


class BrainAligner:

    def __init__(self, fix_img: sitk.Image, mov_img: sitk.Image):
        """
        The physical space is described by the (x, y, z) coordinate system
        The fixed image space is described by the (i, j, k) coordinate system
        The moving image space is described by the (l, m, n) coordinate system
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

        # Fixed image slice
        self.i0, self.j0, self.k0 = fix_img.GetSize()[0] // 2, fix_img.GetSize()[1] // 2, fix_img.GetSize()[2] // 2
        self.i, self.j, self.k = self.i0, self.j0, self.k0
        # Moving image slice
        self.l0, self.m0, self.n0 = mov_img.GetSize()[0] // 2, mov_img.GetSize()[1] // 2, mov_img.GetSize()[2] // 2
        self.l, self.m, self.n = self.l0, self.m0, self.n0

    def execute(self):
        """In the order, the function creates a figure with 3 subplots (xy, xz and yz planes). Then, plots sections of the fixed image (MR image)
        and lets the user find the brain center by clicking on the MR sections. For example, the user can find the center on the z-axis by
        clicking on the xz sections. This automatically acquires the x and y coordinates, and set them as the new origin. Then, it updates the plots
        with the sections passing through the new coordinates. The centering continues until the user is satisfied with their selection of
        coordinates and press "Return". Then the functions plots an"""
        self.create_figure("Click to center the image. Press 'Return' to store the coordinates")

        self.place_img(self.fix_img, self.i0, self.j0, self.k0, self.mov_img, self.l0, self.m0, self.n0)
        plt.tight_layout()
        self.fig.canvas.mpl_connect('button_press_event', self.on_click_center)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_return)
        plt.show(block=False)
        mplcursors.cursor(hover=True)
        plt.show()

    def create_figure(self, title):
        # Create a figure and axis
        self.fig, self.ax = plt.subplots(2, 3)
        for idx, item in enumerate(self.ax.flatten()):
            item.set_axis_off()
        # label axes - necessary for identifying the axes
        self.ax[0, 0].set_label("xy fix")
        self.ax[0, 1].set_label("xz fix")
        self.ax[0, 2].set_label("yz fix")
        self.ax[1, 0].set_label("xy mov")
        self.ax[1, 1].set_label("xz mov")
        self.ax[1, 2].set_label("yz mov")
        self.fig.suptitle(title)

    def place_img(self, img1: sitk.Image, i, j, k, img2: sitk.Image, l, m, n):

        # Display fixed image - xy plane - Extent order: left, right, bottom, top
        img_slice = sitk.Extract(img1, [img1.GetSize()[0], img1.GetSize()[1], 0], [0, 0, k])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[0, 0].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='gray', extent=extent)

        # Display fixed image - xz plane
        img_slice = sitk.Extract(img1, [img1.GetSize()[0], 0, img1.GetSize()[2]], [0, j, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[0, 1].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='gray', extent=extent)

        # Display fixed image - xy plane
        img_slice = sitk.Extract(img1, [0, img1.GetSize()[1], img1.GetSize()[2]], [i, 0, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[0, 2].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='gray', extent=extent)

        # Display moving image - xy plane - Extent order: left, right, bottom, top
        img_slice = sitk.Extract(img2, [img2.GetSize()[0], img2.GetSize()[1], 0], [0, 0, n])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[1, 0].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='gray', extent=extent)

        # Display fixed image - xz plane
        img_slice = sitk.Extract(img2, [img2.GetSize()[0], 0, img2.GetSize()[2]], [0, m, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[1, 1].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='gray', extent=extent)

        # Display fixed image - xy plane
        img_slice = sitk.Extract(img2, [0, img2.GetSize()[1], img2.GetSize()[2]], [l, 0, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[1, 2].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='gray', extent=extent)

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

    def on_click_center(self, event):
        self.click1 = (event.xdata, event.ydata, event.inaxes.get_label())
        print(f'Click 1 at ({self.click1[0]}, {self.click1[1]}) on {self.click1[2]}')
        if self.click1[2] == "xy fix":
            self.i, self.j = int(self.click1[0]//self.fix_img.GetSpacing()[0]), int(-1 * self.click1[1]//self.fix_img.GetSpacing()[1])
        if self.click1[2] == "xz fix":
            self.i, self.k = int(self.click1[0]//self.fix_img.GetSpacing()[0]), int(-1 * self.click1[1]//self.fix_img.GetSpacing()[2])
        if self.click1[2] == "yz fix":
            self.j, self.k = int(self.click1[0]//self.fix_img.GetSpacing()[1]), int(-1 * self.click1[1]//self.fix_img.GetSpacing()[2])
        if self.click1[2] == "xy mov":
            self.l, self.m = int(self.click1[0]//self.mov_img.GetSpacing()[0]), int(-1 * self.click1[1]//self.mov_img.GetSpacing()[1])
        if self.click1[2] == "xz mov":
            self.l, self.n = int(self.click1[0]//self.mov_img.GetSpacing()[0]), int(-1 * self.click1[1]//self.mov_img.GetSpacing()[2])
        if self.click1[2] == "yz mov":
            self.m, self.n = int(self.click1[0]//self.mov_img.GetSpacing()[1]), int(-1 * self.click1[1]//self.mov_img.GetSpacing()[2])
        self.update_plot(self.fix_img, self.mov_img)
        self.click1 = None

    def on_key_return(self, event):
        if event.key == "enter":
            print("Centering completed.")
            print(f"Fix image center: {self.i, self.j, self.k}")
            print(f"Mov image center: {self.l, self.m, self.n}")

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

    def update_plot(self, img1: sitk.Image, img2: sitk.Image):
        """Update the displayed slices. The layer is the number of the overlayed image: 0 for the fixed image,
        and 1 for the moving image on top."""
        # update xy
        img_slice = sitk.Extract(img1, [img1.GetSize()[0], img1.GetSize()[1], 0], [0, 0, self.k])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[0, 0].images[0].set_data(sitk.GetArrayFromImage(img_slice))
        self.ax[0, 0].images[0].set_extent(extent)

        # update xz
        img_slice = sitk.Extract(img1, [img1.GetSize()[0], 0, img1.GetSize()[2]], [0, self.j, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[0, 1].images[0].set_data(sitk.GetArrayFromImage(img_slice))
        self.ax[0, 1].images[0].set_extent(extent)

        # update yz
        img_slice = sitk.Extract(img1, [0, img1.GetSize()[1], img1.GetSize()[2]], [self.i, 0, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[0, 2].images[0].set_data(sitk.GetArrayFromImage(img_slice))
        self.ax[0, 2].images[0].set_extent(extent)

        img_slice = sitk.Extract(img2, [img2.GetSize()[0], img2.GetSize()[1], 0], [0, 0, self.n])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[1, 0].images[0].set_data(sitk.GetArrayFromImage(img_slice))
        self.ax[1, 0].images[0].set_extent(extent)

        # update xz
        img_slice = sitk.Extract(img2, [img2.GetSize()[0], 0, img2.GetSize()[2]], [0, self.m, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[1, 1].images[0].set_data(sitk.GetArrayFromImage(img_slice))
        self.ax[1, 1].images[0].set_extent(extent)

        # update yz
        img_slice = sitk.Extract(img2, [0, img1.GetSize()[1], img2.GetSize()[2]], [self.l, 0, 0])
        extent = [0,
                  (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0],
                  (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1],
                  0]
        self.ax[1, 2].images[0].set_data(sitk.GetArrayFromImage(img_slice))
        self.ax[1, 2].images[0].set_extent(extent)

        self.fig.canvas.draw()

