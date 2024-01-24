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
        # Figure and Axes objects for
        self.fig1, self.ax1 = self.create_figure1()
        self.fig2, self.ax2 = self.create_figure2()

        self.fix_img = fix_img
        self.mov_img = mov_img
        self.click1 = None
        self.click2 = None

        # Fixed image slice, initial (0) and current
        self.i0, self.j0, self.k0 = fix_img.GetSize()[0] // 2, fix_img.GetSize()[1] // 2, fix_img.GetSize()[2] // 2
        self.i, self.j, self.k = self.i0, self.j0, self.k0
        # Moving image slice, initial (0), and current
        self.l0, self.m0, self.n0 = mov_img.GetSize()[0] // 2, mov_img.GetSize()[1] // 2, mov_img.GetSize()[2] // 2
        self.l, self.m, self.n = self.l0, self.m0, self.n0
        # Delta slice for alignment
        self.di, self.dj, self.dk = 0, 0, 0

    def execute(self):
        """In the order, the function creates a figure with 3 subplots (xy, xz and yz planes). Then, plots sections of the fixed image (MR image)
        and lets the user find the brain center by clicking on the MR sections. For example, the user can find the center on the z-axis by
        clicking on the xz sections. This automatically acquires the x and y coordinates, and set them as the new origin. Then, it updates the plots
        with the sections passing through the new coordinates. The centering continues until the user is satisfied with their selection of
        coordinates and press "Return". Then the functions plots an"""

        self.plot_slices(self.i0, self.j0, self.k0, self.l0, self.m0, self.n0)
        plt.tight_layout()
        self.fig1.canvas.mpl_connect("button_press_event", self.on_click1)
        self.fig2.canvas.mpl_connect("button_press_event", self.on_click2)
        # self.fig1.canvas.mpl_connect('key_press_event', self.on_key_return)
        plt.show(block=False)
        mplcursors.cursor(hover=True)
        plt.show()

    @staticmethod
    def create_figure1():
        """Create figure and axes for brain centering"""
        fig, ax = plt.subplots(2, 3)
        for idx, item in enumerate(ax.flatten()):
            item.set_axis_off()
        # label axes - necessary for identifying the axes
        ax[0, 0].set_label("xy fix")
        ax[0, 1].set_label("xz fix")
        ax[0, 2].set_label("yz fix")
        ax[1, 0].set_label("xy mov")
        ax[1, 1].set_label("xz mov")
        ax[1, 2].set_label("yz mov")
        fig.suptitle("Click to center the image. Press 'Return' to store the coordinates")
        ax[0, 0].set_title("x-y plane")
        ax[0, 1].set_title("x-z plane")
        ax[0, 2].set_title("y-z plane")
        return fig, ax

    @staticmethod
    def create_figure2():
        """Create figure and axes for brain alignment"""
        fig, ax = plt.subplots(1, 3)
        for idx, item in enumerate(ax.flatten()):
            item.set_axis_off()
        # label axes - necessary for identifying the axes
        ax[0].set_label("xy")
        ax[1].set_label("xz")
        ax[2].set_label("yz")
        fig.suptitle("Click to center the image. Press 'Return' to store the coordinates")
        ax[0].set_title("x-y plane")
        ax[1].set_title("x-z plane")
        ax[2].set_title("y-z plane")
        return fig, ax

    def plot_slices(self, i, j, k, l, m, n):
        """This function cuts slices of fixed and moving images passing through (i, j, k) and (l, m, n), respectively.
        Then, it plots the fixed and moving image slices on separate rows in figure 1, for brain(s) centering, and
        the fixed and moving image overlaid in Figure 2 for brain alignment."""
        # -----------------------------------------------------------------------
        # Display fixed image - xy plane - Extent order: left, right, bottom, top
        fix_img_xy_slice = sitk.Extract(self.fix_img, [self.fix_img.GetSize()[0], self.fix_img.GetSize()[1], 0], [0, 0, k])
        extent = [0,
                  (0 + fix_img_xy_slice.GetSize()[0]) * fix_img_xy_slice.GetSpacing()[0],
                  (0 - fix_img_xy_slice.GetSize()[1]) * fix_img_xy_slice.GetSpacing()[1],
                  0]
        self.ax1[0, 0].imshow(sitk.GetArrayViewFromImage(fix_img_xy_slice), cmap='gray', extent=extent)

        # Display fixed image - xz plane
        fix_img_xz_slice = sitk.Extract(self.fix_img, [self.fix_img.GetSize()[0], 0, self.fix_img.GetSize()[2]], [0, j, 0])
        extent = [0,
                  (0 + fix_img_xz_slice.GetSize()[0]) * fix_img_xz_slice.GetSpacing()[0],
                  (0 - fix_img_xz_slice.GetSize()[1]) * fix_img_xz_slice.GetSpacing()[1],
                  0]
        self.ax1[0, 1].imshow(sitk.GetArrayViewFromImage(fix_img_xz_slice), cmap='gray', extent=extent)

        # Display fixed image - xy plane
        fix_img_yz_slice = sitk.Extract(self.fix_img, [0, self.fix_img.GetSize()[1], self.fix_img.GetSize()[2]], [i, 0, 0])
        extent = [0,
                  (0 + fix_img_yz_slice.GetSize()[0]) * fix_img_yz_slice.GetSpacing()[0],
                  (0 - fix_img_yz_slice.GetSize()[1]) * fix_img_yz_slice.GetSpacing()[1],
                  0]
        self.ax1[0, 2].imshow(sitk.GetArrayViewFromImage(fix_img_yz_slice), cmap='gray', extent=extent)

        # -----------------------------------------------------------------------
        # Display moving image - xy plane - Extent order: left, right, bottom, top
        mov_img_xy_slice = sitk.Extract(self.mov_img, [self.mov_img.GetSize()[0], self.mov_img.GetSize()[1], 0], [0, 0, n])
        extent = [0,
                  (0 + mov_img_xy_slice.GetSize()[0]) * mov_img_xy_slice.GetSpacing()[0],
                  (0 - mov_img_xy_slice.GetSize()[1]) * mov_img_xy_slice.GetSpacing()[1],
                  0]
        self.ax1[1, 0].imshow(sitk.GetArrayViewFromImage(mov_img_xy_slice), cmap='gray', extent=extent)

        # Display fixed image - xz plane
        mov_img_xz_slice = sitk.Extract(self.mov_img, [self.mov_img.GetSize()[0], 0, self.mov_img.GetSize()[2]], [0, m, 0])
        extent = [0,
                  (0 + mov_img_xz_slice.GetSize()[0]) * mov_img_xz_slice.GetSpacing()[0],
                  (0 - mov_img_xz_slice.GetSize()[1]) * mov_img_xz_slice.GetSpacing()[1],
                  0]
        self.ax1[1, 1].imshow(sitk.GetArrayViewFromImage(mov_img_xz_slice), cmap='gray', extent=extent)

        # Display fixed image - xy plane
        mov_img_yz_slice = sitk.Extract(self.mov_img, [0, self.mov_img.GetSize()[1], self.mov_img.GetSize()[2]], [l, 0, 0])
        extent = [0,
                  (0 + mov_img_yz_slice.GetSize()[0]) * mov_img_yz_slice.GetSpacing()[0],
                  (0 - mov_img_yz_slice.GetSize()[1]) * mov_img_yz_slice.GetSpacing()[1],
                  0]
        self.ax1[1, 2].imshow(sitk.GetArrayViewFromImage(mov_img_yz_slice), cmap='gray', extent=extent)

        # -----------------------------------------------------------------------
        # Display fixed and moving image overlaid in Figure 2.
        self.ax2[0].imshow(sitk.GetArrayViewFromImage(fix_img_xy_slice), cmap='gray', extent=extent)
        self.ax2[0].imshow(sitk.GetArrayViewFromImage(mov_img_xy_slice), cmap='jet', alpha=0.5, extent=extent)
        self.ax2[1].imshow(sitk.GetArrayViewFromImage(fix_img_xz_slice), cmap='gray', extent=extent)
        self.ax2[1].imshow(sitk.GetArrayViewFromImage(mov_img_xz_slice), cmap='jet', alpha=0.5, extent=extent)
        self.ax2[2].imshow(sitk.GetArrayViewFromImage(fix_img_yz_slice), cmap='gray', extent=extent)
        self.ax2[2].imshow(sitk.GetArrayViewFromImage(mov_img_yz_slice), cmap='jet', alpha=0.5, extent=extent)

    def update_plot(self):
        """Update the displayed slices."""
        # -----------------------------------------------------------------------
        # Update fixed image - xy plane
        fix_img_xy_slice = sitk.Extract(self.fix_img, [self.fix_img.GetSize()[0], self.fix_img.GetSize()[1], 0], [0, 0, self.k])
        extent = [0,
                  (0 + fix_img_xy_slice.GetSize()[0]) * fix_img_xy_slice.GetSpacing()[0],
                  (0 - fix_img_xy_slice.GetSize()[1]) * fix_img_xy_slice.GetSpacing()[1],
                  0]
        self.ax1[0, 0].images[0].set_data(sitk.GetArrayFromImage(fix_img_xy_slice))
        self.ax1[0, 0].images[0].set_extent(extent)

        # Update fixed image - xz plane
        fix_img_xz_slice = sitk.Extract(self.fix_img, [self.fix_img.GetSize()[0], 0, self.fix_img.GetSize()[2]], [0, self.j, 0])
        extent = [0,
                  (0 + fix_img_xz_slice.GetSize()[0]) * fix_img_xz_slice.GetSpacing()[0],
                  (0 - fix_img_xz_slice.GetSize()[1]) * fix_img_xz_slice.GetSpacing()[1],
                  0]
        self.ax1[0, 1].images[0].set_data(sitk.GetArrayFromImage(fix_img_xz_slice))
        self.ax1[0, 1].images[0].set_extent(extent)

        # Update fixed image - yz plane
        fix_img_yz_slice = sitk.Extract(self.fix_img, [0, self.fix_img.GetSize()[1], self.fix_img.GetSize()[2]], [self.i, 0, 0])
        extent = [0,
                  (0 + fix_img_yz_slice.GetSize()[0]) * fix_img_yz_slice.GetSpacing()[0],
                  (0 - fix_img_yz_slice.GetSize()[1]) * fix_img_yz_slice.GetSpacing()[1],
                  0]
        self.ax1[0, 2].images[0].set_data(sitk.GetArrayFromImage(fix_img_yz_slice))
        self.ax1[0, 2].images[0].set_extent(extent)

        # -----------------------------------------------------------------------
        # Update moving image - xy plane
        mov_img_xy_slice = sitk.Extract(self.mov_img, [self.mov_img.GetSize()[0], self.mov_img.GetSize()[1], 0], [0, 0, self.n])
        extent = [0,
                  (0 + mov_img_xy_slice.GetSize()[0]) * mov_img_xy_slice.GetSpacing()[0],
                  (0 - mov_img_xy_slice.GetSize()[1]) * mov_img_xy_slice.GetSpacing()[1],
                  0]
        self.ax1[1, 0].images[0].set_data(sitk.GetArrayFromImage(mov_img_xy_slice))
        self.ax1[1, 0].images[0].set_extent(extent)

        # Update moving image - xz plane
        mov_img_xz_slice = sitk.Extract(self.mov_img, [self.mov_img.GetSize()[0], 0, self.mov_img.GetSize()[2]], [0, self.m, 0])
        extent = [0,
                  (0 + mov_img_xz_slice.GetSize()[0]) * mov_img_xz_slice.GetSpacing()[0],
                  (0 - mov_img_xz_slice.GetSize()[1]) * mov_img_xz_slice.GetSpacing()[1],
                  0]
        self.ax1[1, 1].images[0].set_data(sitk.GetArrayFromImage(mov_img_xz_slice))
        self.ax1[1, 1].images[0].set_extent(extent)

        # Update moving image - yz plane
        mov_img_yz_slice = sitk.Extract(self.mov_img, [0, self.fix_img.GetSize()[1], self.mov_img.GetSize()[2]], [self.l, 0, 0])
        extent = [0,
                  (0 + mov_img_yz_slice.GetSize()[0]) * mov_img_yz_slice.GetSpacing()[0],
                  (0 - mov_img_yz_slice.GetSize()[1]) * mov_img_yz_slice.GetSpacing()[1],
                  0]
        self.ax1[1, 2].images[0].set_data(sitk.GetArrayFromImage(mov_img_yz_slice))
        self.ax1[1, 2].images[0].set_extent(extent)

        # -----------------------------------------------------------------------
        # Display fixed and moving image overlaid in Figure 2.
        self.ax2[0].imshow(sitk.GetArrayViewFromImage(fix_img_xy_slice), cmap='gray', extent=extent)
        self.ax2[0].imshow(sitk.GetArrayViewFromImage(mov_img_xy_slice), cmap='jet', alpha=0.5, extent=extent)
        self.ax2[1].imshow(sitk.GetArrayViewFromImage(fix_img_xz_slice), cmap='gray', extent=extent)
        self.ax2[1].imshow(sitk.GetArrayViewFromImage(mov_img_xz_slice), cmap='jet', alpha=0.5, extent=extent)
        self.ax2[2].imshow(sitk.GetArrayViewFromImage(fix_img_yz_slice), cmap='gray', extent=extent)
        self.ax2[2].imshow(sitk.GetArrayViewFromImage(mov_img_yz_slice), cmap='jet', alpha=0.5, extent=extent)

        self.fig1.canvas.draw()
        self.fig2.canvas.draw()

    def place_mov_img(self,):
        # Display moving image - xy plane - Extent order: left, right, bottom, top
        img_slice = sitk.Extract(self.mov_img, [self.mov_img.GetSize()[0], self.mov_img.GetSize()[1], 0], [0, 0, self.mov_img_xyz[2]])
        extent = [0, (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0], (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1], 0]
        self.ax1_mov_img_xy = self.ax1[0].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='jet', extent=extent, alpha=0.3)

        # Display moving image - xz plane
        img_slice = sitk.Extract(self.mov_img, [self.mov_img.GetSize()[0], 0, self.mov_img.GetSize()[2]], [0, self.mov_img_xyz[1], 0])
        extent = [0, (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0], (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1], 0]
        self.ax1_mov_img_xz = self.ax1[1].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='jet', extent=extent, alpha=0.3)

        # Display moving image - xy plane
        img_slice = sitk.Extract(self.mov_img, [0, self.mov_img.GetSize()[1], self.mov_img.GetSize()[2]], [self.mov_img_xyz[0], 0, 0])
        extent = [0, (0 + img_slice.GetSize()[0]) * img_slice.GetSpacing()[0], (0 - img_slice.GetSize()[1]) * img_slice.GetSpacing()[1], 0]
        self.ax1_mov_img_yz = self.ax1[2].imshow(sitk.GetArrayViewFromImage(img_slice), cmap='jet', extent=extent, alpha=0.3)

    def on_close(self,):
        self.fig1.canvas.stop_event_loop()

    def on_click_move(self, event):
        if self.click1 is None:
            self.click1 = (event.xdata, event.ydata, event.inaxes.get_label(), event.inaxes.figure.number())
            print(f'Click 1 at ({self.click1[0]}, {self.click1[1]}) on {self.click1[2]}')
        else:
            self.click2 = (event.xdata, event.ydata, event.inaxes.get_label())
            print(f'Click 2 at ({self.click2[0]}, {self.click2[1]}) on {self.click2[2]}')
            if self.click1[2] != self.click2[2]:
                print("Clicks must be oin the same section.")
                self.on_click_move()
            self.move_image()

    def on_click1(self, event):
        self.click1 = (event.xdata, event.ydata, event.inaxes.get_label(), event.inaxes.figure.number)
        print(f'Click 1 at ({self.click1[0]}, {self.click1[1]}) on {self.click1[2]}, fig {self.click1[3]}')

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
        self.update_plot()

        # reset the clicks
        self.click1 = None

    def on_click2(self, event):

        if event.inaxes:
            if self.click1 is None:
                self.click1 = (event.xdata, event.ydata, event.inaxes.get_label(), event.inaxes.figure.number)
                print(f'Click 1 at ({self.click1[0]}, {self.click1[1]}) on {self.click1[2]}, fig {self.click1[3]}')

            elif self.click1 is not None and self.click2 is None:
                self.click2 = (event.xdata, event.ydata, event.inaxes.get_label(), event.inaxes.figure.number)
                print(f'Click 2 at ({self.click2[0]}, {self.click2[1]}) on {self.click2[2]} on fig {self.click2[3]}')

                # if the clicks are on the same axis, execute alignment
                if self.click1[3] == self.click2[3] and self.click1[2] == self.click2[2]:

                    # Calculate the offset: target location - starting location
                    if self.click1[2] == self.click2[2] == "xy":
                        self.di = int(self.click2[0] // self.mov_img.GetSpacing()[0] - self.click1[0] // self.mov_img.GetSpacing()[0])
                        self.dj = int(-1 * (self.click2[1] // self.mov_img.GetSpacing()[1] - self.click1[1] // self.mov_img.GetSpacing()[1]))
                        self.dk = 0

                    if self.click1[2] == self.click2[2] == "xz":
                        self.di = int(self.click2[0] // self.mov_img.GetSpacing()[0] - self.click1[0] // self.mov_img.GetSpacing()[0])
                        self.dj = 0
                        self.dk = int(-1 * (self.click2[1] // self.mov_img.GetSpacing()[2] - self.click1[1] // self.mov_img.GetSpacing()[2]))

                    if self.click1[2] == self.click2[2] == "yz":
                        self.di = 0
                        self.dj = int(self.click2[1] // self.mov_img.GetSpacing()[1] - self.click1[1] // self.mov_img.GetSpacing()[1])
                        self.dk = int(-1 * (self.click2[1] // self.mov_img.GetSpacing()[2] - self.click1[1] // self.mov_img.GetSpacing()[2]))

                    print(f"di, dj, dk: {self.di}, {self.dj}, {self.dk}")
                    self.update_plot()

                    # reset the clicks
                    self.click1 = None
                    self.click2 = None
                else:
                    print("To align the brains, two clicks must occur on the same figure and axis. Resetting Clicks.")

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
            self.update_plot()

        if self.click1[2] == self.click2[2] == "xz":
            dx = int(self.click2[0] - self.click1[0])
            dy = 0
            dz = int(self.click2[1] - self.click1[1])
            print(f"dx, dy, dz: {dx}, {dy}, {dz}")
            self.update_plot()

        if self.click1[2] == self.click2[2] == "yz":
            dx = 0
            dy = int(self.click2[0] - self.click1[0])
            dz = int(self.click2[1] - self.click1[1])
            print(f"dx, dy, dz: {dx}, {dy}, {dz}")
            self.update_plot()
