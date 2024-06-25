import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import matplotlib.cm
import itertools
from numpy import empty, nan, array

# now in measurement object
class PlotCalibration:

    """A class to plot calibration data. Based on Line2D objects. """

    def __init__(self, t, t_h, i_th, i_h, nrows=30, ncols=4, wait=0.001):

        self.wait = wait
        self.grid = GridSpec(nrows, ncols)
        self.fig = plt.figure(figsize=(45 / 2.54, 20 / 2.54))
        self.fig.subplots_adjust(top=0.93, bottom=0.1, left=0.05, right=0.98, hspace=1.0, wspace=0.3)
        self.norm = Normalize(min(t), max(t))
        self.xlim_i = [i_th.min() - (i_th.max() - i_th.min()) * 0.1, i_th.max() + (i_th.max() - i_th.min()) * 0.1]
        self.xlim_t = [t.min()-(t.max()-t.min()) * 0.1, t.max()+(t.max()-t.min()) * 0.1]
        self.xlim_h = [1e3 * (i_h.min()-(i_h.max()-i_h.min()) * 0.1), 1e3 * (i_h.max()+(i_h.max()-i_h.min()) * 0.1)]
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
        self.kwargsline = {"linewidth":2, "alpha":0.4}

        """ ***** Thermometer 1 ***** """
        self.iv1 = self.fig.add_subplot(self.grid[0:10, 0], label="Th1")
        self.iv1.set_xlabel("$I_{th}$ (A)")
        self.iv1.set_ylabel("V (V)")
        self.iv1.set_title("Thermometer 1 - $R(T)$", fontsize=10, fontstyle="italic")
        self.iv1.set_xlim(self.xlim_i)
        for idx, val in enumerate(t):
            self.iv1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.rt1 = self.fig.add_subplot(self.grid[12:24, 0], label="Th1")
        self.rt1.set_xlabel("T (K)")
        self.rt1.set_ylabel(r"R ($\Omega$)")
        self.rt1.set_xlim(self.xlim_t)
        self.rt1.xaxis.set_ticklabels([])
        for idx, val in enumerate(t):
            self.rt1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.rterr1 = self.fig.add_subplot(self.grid[24:30, 0], label="Th1")
        self.rterr1.set_xlabel("T (K)")
        self.rterr1.set_ylabel(r"$\delta$ ($\Omega$)")
        self.rterr1.set_xlim(self.xlim_t)
        for idx, val in enumerate(t):
            self.rterr1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.drx1 = self.fig.add_subplot(self.grid[0:7, 1], label="Th1")
        self.drx1.set_xlabel("$I_h$ (A)")
        self.drx1.set_ylabel(r"$R_{2\omega_1, 0}$ ($\Omega$)")
        self.drx1.set_xlim(self.xlim_h)
        self.drx1.xaxis.set_ticklabels([])
        self.drx1.set_title("Thermometer 1 - $R(I_h)$", fontsize=10, fontstyle="italic")
        for idx, val in enumerate(t_h):
            self.drx1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.drxerr1 = self.fig.add_subplot(self.grid[7:10, 1], label="Th1")
        self.drxerr1.set_xlabel("$I_h$ (A)")
        self.drxerr1.set_ylabel(r"$\delta$ ($\Omega$)")
        self.drxerr1.set_xlim(self.xlim_h)
        self.drxerr1.xaxis.set_ticklabels([])
        for idx, val in enumerate(t_h):
            self.drxerr1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.dry1 = self.fig.add_subplot(self.grid[10:17, 1], label="Th1")
        self.dry1.set_xlabel("$I_h$ (A)")
        self.dry1.set_ylabel(r"$R_{2\omega_1, \pi/2}$ ($\Omega$)")
        self.dry1.set_xlim(self.xlim_h)
        self.dry1.xaxis.set_ticklabels([])
        for idx, val in enumerate(t_h):
            self.dry1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.dryerr1 = self.fig.add_subplot(self.grid[17:20, 1], label="Th1")
        self.dryerr1.set_xlabel("$I_h$ (A)")
        self.dryerr1.set_ylabel(r"$\delta$ ($\Omega$)")
        self.dryerr1.set_xlim(self.xlim_h)
        self.dryerr1.xaxis.set_ticklabels([])
        for idx, val in enumerate(t_h):
            self.dryerr1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.drdc1 = self.fig.add_subplot(self.grid[20:27, 1], label="Th1")
        self.drdc1.set_xlabel("$I_h$ (A)")
        self.drdc1.set_ylabel(r"$\Delta R_{DC}$ ($\Omega$)")
        self.drdc1.set_xlim(self.xlim_h)
        self.drdc1.xaxis.set_ticklabels([])
        for idx, val in enumerate(t_h):
            self.drdc1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.drdcerr1 = self.fig.add_subplot(self.grid[27:30, 1], label="Th1")
        self.drdcerr1.set_xlabel("$I_h$ (mA)")
        self.drdcerr1.set_ylabel(r"$\delta$ ($\Omega$)")
        self.drdcerr1.set_xlim(self.xlim_h)
        for idx, val in enumerate(t_h):
            self.drdcerr1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        """ ***** Thermometer 2 ***** """
        self.iv2 = self.fig.add_subplot(self.grid[0:10, 2], label="Th2")
        self.iv2.set_xlabel("$I_{th}$ (A)")
        self.iv2.set_ylabel("V (V)")
        self.iv2.set_title("Thermometer 2 - $R(T)$", fontsize=10, fontstyle="italic")
        self.iv2.set_xlim(self.xlim_i)
        for idx, val in enumerate(t):
            self.iv2.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.rt2 = self.fig.add_subplot(self.grid[12:24, 2], label="Th2")
        self.rt2.set_xlabel("T (K)")
        self.rt2.set_ylabel(r"R ($\Omega$)")
        self.rt2.set_xlim(self.xlim_t)
        self.rt2.xaxis.set_ticklabels([])
        for idx, val in enumerate(t):
            self.rt2.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.rterr2 = self.fig.add_subplot(self.grid[24:30, 2], label="Th2")
        self.rterr2.set_xlabel("T (K)")
        self.rterr2.set_ylabel(r"$\delta$ ($\Omega$)")
        self.rterr2.set_xlim(self.xlim_t)
        for idx, val in enumerate(t):
            self.rterr2.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.drx2 = self.fig.add_subplot(self.grid[0:7, 3], label="Th2")
        self.drx2.set_xlabel("$I_h$ (A)")
        self.drx2.set_ylabel(r"$R_{2\omega_1, 0}$ ($\Omega$)")
        self.drx2.set_xlim(self.xlim_h)
        self.drx2.xaxis.set_ticklabels([])
        self.drx2.set_title("Thermometer 2 - $R(I_h)$", fontsize=10, fontstyle="italic")
        for idx, val in enumerate(t_h):
            self.drx2.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.drxerr2 = self.fig.add_subplot(self.grid[7:10, 3], label="Th2")
        self.drxerr2.set_xlabel("$I_h$ (A)")
        self.drxerr2.set_ylabel(r"$\delta$ ($\Omega$)")
        self.drxerr2.set_xlim(self.xlim_h)
        self.drxerr2.xaxis.set_ticklabels([])
        for idx, val in enumerate(t_h):
            self.drxerr2.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.dry2 = self.fig.add_subplot(self.grid[10:17, 3], label="Th2")
        self.dry2.set_xlabel("$I_h$ (A)")
        self.dry2.set_ylabel(r"$R_{2\omega_1, \pi/2}$ ($\Omega$)")
        self.dry2.set_xlim(self.xlim_h)
        self.dry2.xaxis.set_ticklabels([])
        for idx, val in enumerate(t_h):
            self.dry2.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.dryerr2 = self.fig.add_subplot(self.grid[17:20, 3], label="Th2")
        self.dryerr2.set_xlabel("$I_h$ (A)")
        self.dryerr2.set_ylabel(r"$\delta$ ($\Omega$)")
        self.dryerr2.set_xlim(self.xlim_h)
        self.dryerr2.xaxis.set_ticklabels([])
        for idx, val in enumerate(t_h):
            self.dryerr2.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.drdc2 = self.fig.add_subplot(self.grid[20:27, 3], label="Th2")
        self.drdc2.set_xlabel("$I_h$ (A)")
        self.drdc2.set_ylabel(r"$\Delta R_{DC}$ ($\Omega$)")
        self.drdc2.set_xlim(self.xlim_h)
        self.drdc2.xaxis.set_ticklabels([])
        for idx, val in enumerate(t_h):
            self.drdc2.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.drdcerr2 = self.fig.add_subplot(self.grid[27:30, 3], label="Th2")
        self.drdcerr2.set_xlabel("$I_h$ (mA)")
        self.drdcerr2.set_ylabel(r"$\delta$ ($\Omega$)")
        self.drdcerr2.set_xlim(self.xlim_h)
        for idx, val in enumerate(t_h):
            self.drdcerr2.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=val, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))
# now in measurement object
class PlotObsT:

    """A class to plot a set of observables vs time.
    Useful to monitor observables in real-time."""

    def __init__(self, labels, duration, semilogy=False):

        self.grid = GridSpec(1, 1)
        self.fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
        self.grid.update(wspace=0.4, hspace=2)

        self.ax = self.fig.add_subplot()
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Signal (a.u.)")
        self.ax.set_title(f"{', '.join(labels)} vs time", fontsize=10, fontstyle="italic")
        self.ax.set_xlim([0, duration])

        if semilogy is True:
            self.ax.set_yscale("log")

        self.axlg = []
        self.marker = itertools.cycle(("o", "D"))
        for idx, val in enumerate(labels):
            marker = next(self.marker)
            color = matplotlib.cm.Paired(idx)
            self.axlg.append(Line2D(xdata=[0], ydata=[0], color=color, marker=marker, markersize=6, markeredgecolor='black', markeredgewidth=0.2, linewidth=0, label=val))
            self.ax.add_line(Line2D(xdata=[None], ydata=[None], color=color, marker=marker, markeredgecolor='black', markeredgewidth=0.2, linewidth=0, alpha=0.4, label=val))
        self.ax.legend(self.axlg, labels)

class PlotSweepF:

    def __init__(self, t, f, i_h, nrows=2, ncols=2, wait=0.001):

        self.wait = wait
        self.grid = GridSpec(nrows, ncols)
        self.fig = plt.figure(figsize=(30 / 2.54, 20 / 2.54))
        self.grid.update(wspace=0.2, hspace=0.2)
        self.xlim = [f.min(), f.max()]
        self.norm = Normalize(min(i_h), max(i_h))
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")

        self.axx = self.fig.add_subplot(self.grid[0, 0])
        self.axx.set_title("x-y", fontsize=10, fontstyle="italic")
        self.axx.set_xlabel("Frequency (Hz)")
        self.axx.set_ylabel("x")
        self.axx.set_xscale("log")
        self.axx.set_xlim(self.xlim)
        for idx, val in enumerate(i_h):
            self.axx.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th1 {val}", marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))
            self.axx.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th2 {val}", marker="D", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.axy = self.fig.add_subplot(self.grid[1, 0])
        self.axy.set_xlabel("Frequency (Hz)")
        self.axy.set_ylabel("y")
        self.axy.set_xscale("log")
        self.axy.set_xlim(self.xlim)
        for idx, val in enumerate(i_h):
            self.axy.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th1 {val}", marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))
            self.axy.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th2 {val}", marker="D", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.axr = self.fig.add_subplot(self.grid[0, 1])
        self.axr.set_xlabel("Frequency (Hz)")
        self.axr.set_ylabel("R")
        self.axr.set_title("R-$\phi$", fontsize=10, fontstyle="italic")
        self.axr.set_xscale("log")
        self.axr.set_yscale("log")
        self.axr.set_xlim(self.xlim)
        for idx, val in enumerate(i_h):
            self.axr.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th1 {val}", marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))
            self.axr.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th2 {val}", marker="D", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.axp = self.fig.add_subplot(self.grid[1, 1])
        self.axp.set_xlabel("Frequency (Hz)")
        self.axp.set_ylabel(r"$\phi$")
        self.axp.set_xscale("log")
        self.axp.set_xlim(self.xlim)
        for idx, val in enumerate(i_h):
            self.axp.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th1 {val}", marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))
            self.axp.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th2 {val}", marker="D", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

# now in measurement object
class PlotStabilityDiagramI:

    def __init__(self, vg, vb):

        temp = empty((len(vb), len(vg)))
        temp[:] = nan

        self.fig = plt.figure(figsize=(45 / 2.54, 22.5 / 2.54))
        self.grid = GridSpec(nrows=2, ncols=4)
        self.fig.subplots_adjust(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0.19, wspace=0.315)
        self.norm_vg = Normalize(vmin=min(vg), vmax=max(vg))
        self.norm_vb = Normalize(vmin=min(vb), vmax=max(vb))
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
        self.cm2 = matplotlib.cm.get_cmap("inferno")

        self.ax00 = self.fig.add_subplot(self.grid[0, 0])
        self.ax00.set_title(r"$i_{\omega_G,0}$ vs DC bias")
        self.ax00.set_xlabel("DC bias (V)")
        self.ax00.set_ylabel(r"$i_{\omega_G,0}$ (A)")
        self.ax00.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax00.ticklabel_format(useOffset=False)
        self.ax00.set_xlim([min(vb), max(vb)])
        for idx, val in enumerate(vg):
            self.ax00.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax10 = self.fig.add_subplot(self.grid[1, 0], sharex=self.ax00)
        self.ax10.set_xlabel("DC bias (V)")
        self.ax10.set_ylabel(r"$i_{\omega_G,0}$ (A)")
        self.ax10.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vg):
            self.ax10.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax01 = self.fig.add_subplot(self.grid[0, 1], sharey=self.ax00)
        self.ax01.set_title(r"$i_{\omega_G,0}$ vs Gate")
        self.ax01.set_xlabel("Gate voltage (V)")
        self.ax01.set_ylabel(r"$i_{\omega_G,0}$ (A)")
        self.ax01.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax01.set_xlim([min(vg), max(vg)])
        for idx, val in enumerate(vb):
            self.ax01.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax11 = self.fig.add_subplot(self.grid[1, 1], sharex=self.ax01, sharey=self.ax10)
        self.ax11.set_xlabel("Gate voltage (V)")
        self.ax11.set_ylabel(r"$i_{\omega_G,0}$ (A)")
        self.ax11.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vb):
            self.ax11.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax02 = self.fig.add_subplot(self.grid[0, 2:])
        self.ax02.set_title(r"$i_{\omega_G,0}$ vs DC bias vs Gate")
        self.ax02.set_xlabel("Gate voltage (V)")
        self.ax02.set_ylabel("DC bias (V)")
        self.ax02.set_xlim([min(vg), max(vg)])
        self.ax02.set_ylim([min(vb), max(vb)])
        self.im02 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb02 = self.fig.colorbar(self.im02, ax=self.ax02)

        self.ax12 = self.fig.add_subplot(self.grid[1, 2:])
        self.ax12.set_xlabel("Gate voltage (V)")
        self.ax12.set_ylabel("DC bias (V)")
        self.ax12.set_xlim([min(vg), max(vg)])
        self.ax12.set_ylim([min(vb), max(vb)])
        self.im12 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb12 = self.fig.colorbar(self.im12, ax=self.ax12)
# now in measurement object
class PlotStabilityDiagramIGate:

    def __init__(self, vg, vb):

        temp = empty((len(vb), len(vg)))
        temp[:] = nan

        self.fig = plt.figure(figsize=(45 / 2.54, 22.5 / 2.54))
        self.grid = GridSpec(nrows=2, ncols=4)
        self.fig.subplots_adjust(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0.19, wspace=0.315)
        self.norm_vg = Normalize(vmin=min(vg), vmax=max(vg))
        self.norm_vb = Normalize(vmin=min(vb), vmax=max(vb))
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
        self.cm2 = matplotlib.cm.get_cmap("inferno")

        self.ax00 = self.fig.add_subplot(self.grid[0, 0])
        self.ax00.set_title(r"$i_{gate}$ vs DC bias")
        self.ax00.set_xlabel("DC bias (V)")
        self.ax00.set_ylabel(r"$i_{gate}$ (A)")
        self.ax00.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax00.ticklabel_format(useOffset=False)
        self.ax00.set_xlim([min(vb), max(vb)])
        for idx, val in enumerate(vg):
            self.ax00.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax10 = self.fig.add_subplot(self.grid[1, 0], sharex=self.ax00)
        self.ax10.set_xlabel("DC bias (V)")
        self.ax10.set_ylabel(r"$i_{gate}$ (A)")
        self.ax10.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vg):
            self.ax10.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax01 = self.fig.add_subplot(self.grid[0, 1], sharey=self.ax00)
        self.ax01.set_title(r"$i_{gate}$ vs Gate")
        self.ax01.set_xlabel("Gate voltage (V)")
        self.ax01.set_ylabel(r"$i_{gate}$ (A)")
        self.ax01.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax01.set_xlim([min(vg), max(vg)])
        for idx, val in enumerate(vb):
            self.ax01.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax11 = self.fig.add_subplot(self.grid[1, 1], sharex=self.ax01, sharey=self.ax10)
        self.ax11.set_xlabel("Gate voltage (V)")
        self.ax11.set_ylabel(r"$i_{gate}$ (A)")
        self.ax11.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vb):
            self.ax11.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax02 = self.fig.add_subplot(self.grid[0, 2:])
        self.ax02.set_title(r"$i_{gate}$ vs DC bias vs Gate")
        self.ax02.set_xlabel("Gate voltage (V)")
        self.ax02.set_ylabel("DC bias (V)")
        self.ax02.set_xlim([min(vg), max(vg)])
        self.ax02.set_ylim([min(vb), max(vb)])
        self.im02 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb02 = self.fig.colorbar(self.im02, ax=self.ax02)

        self.ax12 = self.fig.add_subplot(self.grid[1, 2:])
        self.ax12.set_xlabel("Gate voltage (V)")
        self.ax12.set_ylabel("DC bias (V)")
        self.ax12.set_xlim([min(vg), max(vg)])
        self.ax12.set_ylim([min(vb), max(vb)])
        self.im12 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb12 = self.fig.colorbar(self.im12, ax=self.ax12)
# now in measurement object
class PlotTEStabilityDiagramI:

    def __init__(self, vg, vb):

        temp = empty((len(vb), len(vg)))
        temp[:] = nan

        self.fig = plt.figure(figsize=(45 / 2.54, 22.5 / 2.54))
        self.fig.set_animated(True)
        # If True, the artist is excluded from regular drawing of the figure. You have to call Figure.draw_artist / Axes.draw_artist
        # explicitly on the artist. This approach is used to speed up animations using blitting.
        self.grid = GridSpec(nrows=2, ncols=4)
        self.fig.subplots_adjust(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0.19, wspace=0.315)
        self.norm_vg = Normalize(vmin=min(vg), vmax=max(vg))
        self.norm_vb = Normalize(vmin=min(vb), vmax=max(vb))
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
        self.cm2 = matplotlib.cm.get_cmap("inferno")

        self.ax00 = self.fig.add_subplot(self.grid[0, 0])
        self.ax00.set_title(r"$i_{2\omega_{\alpha},\pi/2}$ vs DC bias")
        self.ax00.set_xlabel("DC bias (V)")
        self.ax00.set_ylabel(r"$i_{2\omega_{\alpha},\pi/2}$ (A)")
        self.ax00.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax00.ticklabel_format(useOffset=False)
        self.ax00.set_xlim([min(vb), max(vb)])
        for idx, val in enumerate(vg):
            self.ax00.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax10 = self.fig.add_subplot(self.grid[1, 0], sharex=self.ax00)
        self.ax10.set_xlabel("DC bias (V)")
        self.ax10.set_ylabel(r"$i_{2\omega_{\alpha},\pi/2}$ (A)")
        self.ax10.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vg):
            self.ax10.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax01 = self.fig.add_subplot(self.grid[0, 1], sharey=self.ax00)
        self.ax01.set_xlabel("Gate voltage (V)")
        self.ax01.set_ylabel(r"$i_{2\omega_{\alpha},\pi/2}$ (A)")
        self.ax01.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax01.set_xlim([min(vg), max(vg)])
        self.ax01.set_title(r"$i_{2\omega_{\alpha},\pi/2}$ vs Gate")
        for idx, val in enumerate(vb):
            self.ax01.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax11 = self.fig.add_subplot(self.grid[1, 1], sharex=self.ax01, sharey=self.ax10)
        self.ax11.set_xlabel("Gate voltage (V)")
        self.ax11.set_ylabel(r"$i_{2\omega_{\alpha},\pi/2}$ (A)")
        self.ax11.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vb):
            self.ax11.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax02 = self.fig.add_subplot(self.grid[0, 2:])
        self.ax02.set_xlabel("Gate voltage (V)")
        self.ax02.set_ylabel("DC bias (V)")
        self.ax02.set_title(r"$i_{2\omega_{\alpha},\pi/2}$ vs DC bias vs Gate")
        self.ax02.set_xlim([min(vg), max(vg)])
        self.ax02.set_ylim([min(vb), max(vb)])
        self.im02 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb02 = self.fig.colorbar(self.im02, ax=self.ax02)

        self.ax12 = self.fig.add_subplot(self.grid[1, 2:])
        self.ax12.set_xlabel("Gate voltage (V)")
        self.ax12.set_ylabel("DC bias (V)")
        self.ax12.set_xlim([min(vg), max(vg)])
        self.ax12.set_ylim([min(vb), max(vb)])
        self.im12 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb12 = self.fig.colorbar(self.im12, ax=self.ax12)
# now in measurement object
class PlotTEStabilityDiagramV:

    def __init__(self, vg, vb):

        temp = empty((len(vb), len(vg)))
        temp[:] = nan

        self.fig = plt.figure(figsize=(45 / 2.54, 22.5 / 2.54))
        #self.fig.set_animated(True)
        # If True, the artist is excluded from regular drawing of the figure. You have to call Figure.draw_artist / Axes.draw_artist
        # explicitly on the artist. This approach is used to speed up animations using blitting.
        self.grid = GridSpec(nrows=2, ncols=4)
        self.fig.subplots_adjust(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0.19, wspace=0.315)
        self.norm_vg = Normalize(vmin=min(vg), vmax=max(vg))
        self.norm_vb = Normalize(vmin=min(vb), vmax=max(vb))
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
        self.cm2 = matplotlib.cm.get_cmap("inferno")

        self.ax00 = self.fig.add_subplot(self.grid[0, 0])
        self.ax00.set_title(r"$v_{2\omega_{\alpha},\pi/2}$ vs DC bias")
        self.ax00.set_xlabel("DC bias (V)")
        self.ax00.set_ylabel(r"$v_{2\omega_{\alpha},\pi/2}$ (A)")
        self.ax00.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax00.ticklabel_format(useOffset=False)
        self.ax00.set_xlim([min(vb), max(vb)])
        for idx, val in enumerate(vg):
            self.ax00.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax10 = self.fig.add_subplot(self.grid[1, 0], sharex=self.ax00)
        self.ax10.set_xlabel("DC bias (V)")
        self.ax10.set_ylabel(r"$v_{2\omega_{\alpha},\pi/2}$ (A)")
        self.ax10.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vg):
            self.ax10.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax01 = self.fig.add_subplot(self.grid[0, 1], sharey=self.ax00)
        self.ax01.set_xlabel("Gate voltage (V)")
        self.ax01.set_ylabel(r"$v_{2\omega_{\alpha},\pi/2}$ (A)")
        self.ax01.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax01.set_xlim([min(vg), max(vg)])
        self.ax01.set_title(r"$v_{2\omega_{\alpha},\pi/2}$ vs Gate")
        for idx, val in enumerate(vb):
            self.ax01.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax11 = self.fig.add_subplot(self.grid[1, 1], sharex=self.ax01, sharey=self.ax10)
        self.ax11.set_xlabel("Gate voltage (V)")
        self.ax11.set_ylabel(r"$v_{2\omega_{\alpha},\pi/2}$ (A)")
        self.ax11.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vb):
            self.ax11.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax02 = self.fig.add_subplot(self.grid[0, 2:])
        self.ax02.set_xlabel("Gate voltage (V)")
        self.ax02.set_ylabel("DC bias (V)")
        self.ax02.set_title(r"$v_{2\omega_{\alpha},\pi/2}$ vs DC bias vs Gate")
        self.ax02.set_xlim([min(vg), max(vg)])
        self.ax02.set_ylim([min(vb), max(vb)])
        self.im02 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb02 = self.fig.colorbar(self.im02, ax=self.ax02)

        self.ax12 = self.fig.add_subplot(self.grid[1, 2:])
        self.ax12.set_xlabel("Gate voltage (V)")
        self.ax12.set_ylabel("DC bias (V)")
        self.ax12.set_xlim([min(vg), max(vg)])
        self.ax12.set_ylim([min(vb), max(vb)])
        self.im12 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb12 = self.fig.colorbar(self.im12, ax=self.ax12)


class PlotDUTFrequencySweep:

    def __init__(self, t, f, i_h, vg, vb, nrows=1, ncols=3, wait=0.001):

        self.wait = wait
        self.grid = GridSpec(nrows, ncols)
        self.fig = plt.figure(figsize=(40 / 2.54, 15 / 2.54))
        self.grid.update(wspace=0.4, hspace=0.4)
        self.xlim = [f.min(), f.max()]
        self.norm = Normalize(min(i_h), max(i_h))
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")

        self.ax1 = self.fig.add_subplot(self.grid[0])
        self.ax1.set_xlabel("Frequency (Hz)")
        self.ax1.set_ylabel(r"$i_{\omega_2}$ (A)")
        self.ax1.set_xscale("log")
        self.ax1.set_xlim(self.xlim)
        self.ax1.add_line(Line2D(xdata=[None], ydata=[None], linewidth=0, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.ax2 = self.fig.add_subplot(self.grid[1])
        self.ax2.set_xlabel("Frequency (Hz)")
        self.ax2.set_ylabel(r"$i_{2\omega_1}$ (A)")
        self.ax2.set_xscale("log")
        self.ax2.set_xlim(self.xlim)
        self.ax2.add_line(Line2D(xdata=[None], ydata=[None], linewidth=0, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

        self.ax3 = self.fig.add_subplot(self.grid[2])
        self.ax3.set_xlabel("Frequency (Hz)")
        self.ax3.set_ylabel(r"$v_{2\omega_1}$ (V)")
        self.ax3.set_xscale("log")
        self.ax3.set_xlim(self.xlim)
        self.ax3.add_line(Line2D(xdata=[None], ydata=[None], linewidth=0, marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

# now in measurement object
class PlotFET:

    """A class to plot FET measurements, including Vds sweep and Vgs sweep. """

    def __init__(self, sweep, vgs, vds):

        """
        :param vgs:
        :param vds:
        :param sweep: [int] select between "FET Vgs sweep" (0), "FET Vds sweep" (1), and "IV Vds Sweep" (2)
        """

        if not (sweep == 0 or sweep == 1 or sweep == 2):
            exit("PlotFET 'sweep' value must be either 0 (vgs) or 1 (vds) or 2 (iv). Execution terminates.")

        self.grid = GridSpec(2, 1)
        self.fig = plt.figure(figsize=(20 / 2.54, 20 / 2.54))
        self.grid.update(wspace=0.2, hspace=0.2)
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
        self.lookIds = {"linewidth": 0, "marker": "o", "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.4}
        self.lookIgs = {"linewidth": 0, "marker": "D", "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.4}
        self.ax0 = self.fig.add_subplot(self.grid[0])
        self.ax1 = self.fig.add_subplot(self.grid[1])
        self.ax0.set_ylabel("$I$ (A)")
        self.ax1.set_ylabel("$Log_{10}(I)$")
        if sweep == 0:
            self.norm = Normalize(0, len(vds)-1)
            self.ax0.set_title("$V_{gs}$ sweep", fontsize=10, fontstyle="italic")
            self.ax0.set_xlabel("$V_{gs}$ (V)")
            self.ax1.set_xlabel("$V_{gs}$ (V)")
            self.ax0.set_xlim([min(vgs), max(vgs)])
            self.ax1.set_xlim([min(vgs), max(vgs)])
            # add lines to axes
            for i, val in enumerate(vds):
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIgs))
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIds))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIgs))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIds))
            # make legend
            custom_lines = [Line2D([0], [0], color=self.cm(self.norm(x)), lw=4) for x in range(len(vds))]
            custom_legend = self.ax0.legend(custom_lines, [x for x in vds], title="Vds", fancybox=True, framealpha=0.5)
            self.ax0.add_artist(custom_legend)
        elif sweep == 1 or sweep == 2:
            self.norm = Normalize(0, len(vgs)-1)
            self.ax0.set_title("$V_{ds}$ sweep", fontsize=10, fontstyle="italic")
            self.ax0.set_xlabel("$V_{ds}$ (V)")
            self.ax1.set_xlabel("$V_{ds}$ (V)")
            self.ax0.set_xlim([min(vds), max(vds)])
            self.ax1.set_xlim([min(vds), max(vds)])
            # add lines to axes
            for i, val in enumerate(vgs):
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIgs))
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIds))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIgs))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIds))
            # make legend
            custom_lines = [Line2D([0], [0], color=self.cm(self.norm(x)), lw=4) for x in range(len(vgs))]
            custom_legend = self.ax0.legend(custom_lines, [x for x in vgs], title="Vds", fancybox=True, framealpha=0.5)
            self.ax0.add_artist(custom_legend)
# now in measurement object
class PlotFETvsT:

    """A class to plot FET measurements, including Vds sweep and Vgs sweep. """

    def __init__(self, t, n, x="vds"):

        # n is the number of vds or vgs steps

        if x not in ["vds", "vgs"]:
            exit("PlotFET 'x' value is not accepted. Execution terminates.")

        self.grid = GridSpec(2, 1)
        self.fig = plt.figure(figsize=(30 / 2.54, 15 / 2.54))
        self.grid.update(wspace=0.2, hspace=0.2)
        self.norm = Normalize(min(t), max(t))
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
        self.lookIds = {"linewidth": 0, "marker": "o", "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.4}
        self.lookIgs = {"linewidth": 0, "marker": "D", "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.4}

        self.ax0 = self.fig.add_subplot(self.grid[0, 1])
        self.ax1 = self.fig.add_subplot(self.grid[1, 1])
        self.ax0.set_ylabel("$I$ (A)")
        self.ax1.set_ylabel("$Log_{10}(I)$")
        if x == "vds":
            self.ax0.set_title("$V_{ds}$ sweep", fontsize=10, fontstyle="italic")
            self.ax0.set_xlabel("$V_{ds}$ (V)")
            self.ax1.set_xlabel("$V_{ds}$ (V)")
        elif x == "vgs":
            self.ax0.set_title("$V_{gs}$ sweep", fontsize=10, fontstyle="italic")
            self.ax0.set_xlabel("$V_{gs}$ (V)")
            self.ax1.set_xlabel("$V_{gs}$ (V)")

        for i, val in enumerate(t):
            for j, val in enumerate(n):
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), **self.lookIgs))
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), **self.lookIds))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), **self.lookIgs))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), **self.lookIds))
# now in measurement object
class PlotTEStabilityDiagramAlpha:

    def __init__(self, vg, vb):

        temp = empty((len(vb), len(vg)))
        temp[:] = nan

        self.fig = plt.figure(figsize=(45 / 2.54, 22.5 / 2.54))
        self.fig.set_animated(True)
        # If True, the artist is excluded from regular drawing of the figure. You have to call Figure.draw_artist / Axes.draw_artist
        # explicitly on the artist. This approach is used to speed up animations using blitting.
        self.grid = GridSpec(nrows=2, ncols=4)
        self.fig.subplots_adjust(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0.19, wspace=0.315)
        self.norm_vg = Normalize(vmin=min(vg), vmax=max(vg))
        self.norm_vb = Normalize(vmin=min(vb), vmax=max(vb))
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
        self.cm2 = matplotlib.cm.get_cmap("inferno")

        self.ax00 = self.fig.add_subplot(self.grid[0, 0])
        self.ax00.set_title(r"$\alpha_y$ vs DC bias")
        self.ax00.set_xlabel("DC bias (V)")
        self.ax00.set_ylabel(r"$\alpha_y$ ($\mu V /K$)")
        self.ax00.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax00.ticklabel_format(useOffset=False)
        self.ax00.set_xlim([min(vb), max(vb)])
        for idx, val in enumerate(vg):
            self.ax00.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax10 = self.fig.add_subplot(self.grid[1, 0], sharex=self.ax00)
        self.ax10.set_xlabel("DC bias (V)")
        self.ax10.set_ylabel(r"$\alpha_y$ ($\mu V /K$)")
        self.ax10.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vg):
            self.ax10.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax01 = self.fig.add_subplot(self.grid[0, 1], sharey=self.ax00)
        self.ax01.set_xlabel("Gate voltage (V)")
        self.ax01.set_ylabel(r"$\alpha_y$ ($\mu V /K$)")
        self.ax01.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax01.set_xlim([min(vg), max(vg)])
        self.ax01.set_title(r"$\alpha_y$ vs Gate")
        for idx, val in enumerate(vb):
            self.ax01.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax11 = self.fig.add_subplot(self.grid[1, 1], sharex=self.ax01, sharey=self.ax10)
        self.ax11.set_xlabel("Gate voltage (V)")
        self.ax11.set_ylabel(r"$\alpha_y$ ($\mu V /K$)")
        self.ax11.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vb):
            self.ax11.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax02 = self.fig.add_subplot(self.grid[0, 2:])
        self.ax02.set_xlabel("Gate voltage (V)")
        self.ax02.set_ylabel("DC bias (V)")
        self.ax02.set_title(r"$\alpha_y$ vs DC bias vs Gate")
        self.ax02.set_xlim([min(vg), max(vg)])
        self.ax02.set_ylim([min(vb), max(vb)])
        self.im02 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb02 = self.fig.colorbar(self.im02, ax=self.ax02)

        self.ax12 = self.fig.add_subplot(self.grid[1, 2:])
        self.ax12.set_xlabel("Gate voltage (V)")
        self.ax12.set_ylabel("DC bias (V)")
        self.ax12.set_xlim([min(vg), max(vg)])
        self.ax12.set_ylim([min(vb), max(vb)])
        self.im12 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb12 = self.fig.colorbar(self.im12, ax=self.ax12)
# now in measurement object
class PlotTEStabilityDiagramG:

    def __init__(self, vg, vb):

        temp = empty((len(vb), len(vg)))
        temp[:] = nan

        self.fig = plt.figure(figsize=(45 / 2.54, 22.5 / 2.54))
        self.fig.set_animated(True)
        # If True, the artist is excluded from regular drawing of the figure. You have to call Figure.draw_artist / Axes.draw_artist
        # explicitly on the artist. This approach is used to speed up animations using blitting.
        self.grid = GridSpec(nrows=2, ncols=4)
        self.fig.subplots_adjust(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0.19, wspace=0.315)
        self.norm_vg = Normalize(vmin=min(vg), vmax=max(vg))
        self.norm_vb = Normalize(vmin=min(vb), vmax=max(vb))
        self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
        self.cm2 = matplotlib.cm.get_cmap("inferno")

        self.ax00 = self.fig.add_subplot(self.grid[0, 0])
        self.ax00.set_title(r"G vs DC bias")
        self.ax00.set_xlabel("DC bias (V)")
        self.ax00.set_ylabel(r"G (S)")
        self.ax00.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax00.ticklabel_format(useOffset=False)
        self.ax00.set_xlim([min(vb), max(vb)])
        for idx, val in enumerate(vg):
            self.ax00.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax10 = self.fig.add_subplot(self.grid[1, 0], sharex=self.ax00)
        self.ax10.set_xlabel("DC bias (V)")
        self.ax10.set_ylabel(r"G (S)")
        self.ax10.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vg):
            self.ax10.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

        self.ax01 = self.fig.add_subplot(self.grid[0, 1], sharey=self.ax00)
        self.ax01.set_xlabel("Gate voltage (V)")
        self.ax01.set_ylabel(r"G (S)")
        self.ax01.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        self.ax01.set_xlim([min(vg), max(vg)])
        self.ax01.set_title(r"G vs Gate")
        for idx, val in enumerate(vb):
            self.ax01.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax11 = self.fig.add_subplot(self.grid[1, 1], sharex=self.ax01, sharey=self.ax10)
        self.ax11.set_xlabel("Gate voltage (V)")
        self.ax11.set_ylabel(r"G (S)")
        self.ax11.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
        for idx, val in enumerate(vb):
            self.ax11.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

        self.ax02 = self.fig.add_subplot(self.grid[0, 2:])
        self.ax02.set_xlabel("Gate voltage (V)")
        self.ax02.set_ylabel("DC bias (V)")
        self.ax02.set_title(r"G vs DC bias vs Gate")
        self.ax02.set_xlim([min(vg), max(vg)])
        self.ax02.set_ylim([min(vb), max(vb)])
        self.im02 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb02 = self.fig.colorbar(self.im02, ax=self.ax02)

        self.ax12 = self.fig.add_subplot(self.grid[1, 2:])
        self.ax12.set_xlabel("Gate voltage (V)")
        self.ax12.set_ylabel("DC bias (V)")
        self.ax12.set_xlim([min(vg), max(vg)])
        self.ax12.set_ylim([min(vb), max(vb)])
        self.im12 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
        self.cb12 = self.fig.colorbar(self.im12, ax=self.ax12)
