import scipy.stats
import scipy.integrate as integrate
from numpy import array, where, zeros, sqrt, linspace, sinh, exp, concatenate, flip, ceil, nan, zeros_like, empty, unique, log10, sin, sinc
from scipy.constants import Boltzmann as k_b, elementary_charge as e, pi, electron_mass as m_e, h, epsilon_0, hbar
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
from matplotlib.lines import Line2D
import matplotlib.cm
from lmfit import Model
import itertools

class EmptyClass:

    """ An empty class """

    def __init__(self):
        pass

class Experiment:

    """ A class designed to collect experimental data and instrumentation settings in a single object.
    The self.data can be any experiment data class. Further attributes can be added without limitations. """

    def __init__(self):

        self.main = None
        self.filename = None
        self.backupname = None
        self.experiment = None
        self.chip = None
        self.device = None
        self.date = None
        self.settings = None
        self.data = None

class Thermoelectrics:

    class Calibration:
        """ Experiment data class for field-effect thermoelectric device calibration. """
        def __init__(self, h, th, t, i_h, t_h, i_th, i_th_ex, settings):
            self.heater = h
            self.thermometer = th
            self.t_h = t_h
            self.i_h = i_h
            self.t = [{"t": x,
                       "tt": ObsT(["stage", "shield"]),
                       "iv1": IV() if th == 0 or th == 1 else None,
                       "iv2": IV() if th == 0 or th == 2 else None,
                       "dr": {"h1": [{"i_h": y1,
                                      "drt1": Lockin() if th == 0 or th == 1 else None,
                                      "drt2": Lockin() if th == 0 or th == 2 else None,
                                      "iv1": IV() if th == 0 or th == 1 else None,
                                      "iv2": IV() if th == 0 or th == 2 else None}
                                     for y1 in i_h] if h == 1 else None,
                              "h2": [{"i_h": y2,
                                      "drt1": Lockin() if th == 0 or th == 1 else None,
                                      "drt2": Lockin() if th == 0 or th == 2 else None,
                                      "iv1": IV() if th == 0 or th == 2 else None,
                                      "iv2": IV() if th == 0 or th == 2 else None}
                                     for y2 in i_h] if h == 2 else None} if x in t_h else None}
                      for x in t]

            vt_samples = int(ceil((settings.adc.vt_settling_time + settings.adc.vt_measurement_time) / (settings.adc.nplc / settings.adc.line_freq)))

            for idx_x, x in enumerate(self.t):
                if settings.tc.address is not None:
                    if idx_x == 0:
                        x["tt"].time = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                        x["tt"].stage = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                        x["tt"].shield = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                    if idx_x != 0:
                        x["tt"].time = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))
                        x["tt"].stage = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))
                        x["tt"].shield = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))
                if x["iv1"] is not None:
                    x["iv1"].i = i_th
                    x["iv1"].v = zeros(len(i_th))
                if x["iv2"] is not None:
                    x["iv2"].i = i_th
                    x["iv2"].v = zeros(len(i_th))
                if x["dr"] is not None:
                    if x["dr"]["h1"] is not None:
                        for y in x["dr"]["h1"]:
                            if y["drt1"] is not None:
                                y["drt1"].__setattr__("i_th_ex", i_th_ex)
                                y["drt1"].time = zeros(vt_samples)
                                y["drt1"].x = zeros(vt_samples)
                                y["drt1"].y = zeros(vt_samples)
                                y["drt1"].raw = zeros(vt_samples)
                            if y["drt2"] is not None:
                                y["drt2"].__setattr__("i_th_ex", i_th_ex)
                                y["drt2"].time = zeros(vt_samples)
                                y["drt2"].x = zeros(vt_samples)
                                y["drt2"].y = zeros(vt_samples)
                                y["drt2"].raw = zeros(vt_samples)
                            if y["iv1"] is not None:
                                y["iv1"].i = i_th
                                y["iv1"].v = zeros(len(i_th))
                            if y["iv2"] is not None:
                                y["iv2"].i = i_th
                                y["iv2"].v = zeros(len(i_th))
                    if x["dr"]["h2"] is not None:
                        for y in x["dr"]["h2"]:
                            if y["drt1"] is not None:
                                y["drt1"].__setattr__("i_th_ex", i_th_ex)
                                y["drt1"].time = zeros(vt_samples)
                                y["drt1"].x = zeros(vt_samples)
                                y["drt1"].y = zeros(vt_samples)
                                y["drt1"].raw = zeros(vt_samples)
                            if y["drt2"] is not None:
                                y["drt2"].__setattr__("i_th_ex", i_th_ex)
                                y["drt2"].time = zeros(vt_samples)
                                y["drt2"].x = zeros(vt_samples)
                                y["drt2"].y = zeros(vt_samples)
                                y["drt2"].raw = zeros(vt_samples)
                            if y["iv1"] is not None:
                                y["iv1"].i = i_th
                                y["iv1"].v = zeros(len(i_th))
                            if y["iv2"] is not None:
                                y["iv2"].i = i_th
                                y["iv2"].v = zeros(len(i_th))

        def get_resistance(self, th):
            """ Fit all V vs I data """
            t = zeros(len(self.t))
            r = zeros_like(t)
            r_err = zeros_like(t)
            for idx, val in enumerate(self.t):
                t[idx] = val["t"]
                r[idx] = val[f"iv{th}"].r
                r_err[idx] = val[f"iv{th}"].r_stderr
            fit = scipy.stats.linregress(t, r)
            return t, r, r_err, fit

        def get_heater_sweep(self, h, th):
            """ Get heater sweep data """
            for idx1, val1 in enumerate(self.t):
                if val1["dr"] is not None:
                    t = val1["t"]
                    i = zeros(len(val1["dr"][f"h{h}"]))
                    drdc = zeros_like(i)
                    drdc_err = zeros_like(i)
                    drx = zeros_like(i)
                    drx_err = zeros_like(i)
                    dry = zeros_like(i)
                    dry_err = zeros_like(i)
                    for idx2, val2 in enumerate(val1["dr"][f"h{h}"]):
                        i[idx2] = val2["i_h"]
                        drdc[idx2] = val2[f"iv{th}"].r
                        drdc_err[idx2] = val2[f"iv{th}"].r_stderr
                        drx[idx2] = val2[f"drt{th}"].x_avg
                        drx_err[idx2] = val2[f"drt{th}"].x_stddev
                        dry[idx2] = val2[f"drt{th}"].y_avg
                        dry_err[idx2] = val2[f"drt{th}"].y_stddev
            return t, i, drdc, drdc_err, drx, drx_err, dry, dry_err

        def calculate_temperatures(drdc, drdc_err, drx, drx_err, dry, dry_err, fit):
            """ Calculate temperature from resistance and slope data """
            dtdc = (drdc - fit[1])/ fit[0]
            dtdc_err = drdc_err / fit[0]
            dtx = drx / fit[0]
            dtx_err = drx_err / fit[0]
            dty = dry / fit[0]
            dty_err = dry_err / fit[0]
            return dtdc, dtdc_err, dtx, dtx_err, dty, dty_err

    class StabilityDiagram:

        def __init__(self, mode, h, t, i_h, vg, vb, v_ex, settings):

            self.heater = h
            self.t = t
            self.i_h = i_h
            self.vg = vg
            self.vb = vb
            self.v_ex = v_ex
            self.mode = mode

            self.t = [{"t": x,
                       "tt": ObsT(["stage", "shield"]),
                       "sd": {"h1": [{"i_h": y1,
                                      "i_w2": {"x": zeros((len(vg), len(vb), 2)),
                                               "y": zeros((len(vg), len(vb), 2))},
                                      "i_2w1": {"x": zeros((len(vg), len(vb), 2)),
                                                "y": zeros((len(vg), len(vb), 2))},
                                      "v_w2": {"x": zeros((len(vg), len(vb), 2)),
                                               "y": zeros((len(vg), len(vb), 2))},
                                      "i_dc": zeros((len(vg), len(vb), 2)),
                                      "v_dc": zeros((len(vg), len(vb), 2)),
                                      "i_gs": zeros((len(vg), len(vb), 2))}
                                     for y1 in i_h] if h == 1 else None,
                              "h2": [{"i_h": y2,
                                      "i_w2": {"x": zeros((len(vg), len(vb), 2)),
                                               "y": zeros((len(vg), len(vb), 2))},
                                      "i_2w1": {"x": zeros((len(vg), len(vb), 2)),
                                                "y": zeros((len(vg), len(vb), 2))},
                                      "v_w2": {"x": zeros((len(vg), len(vb), 2)),
                                               "y": zeros((len(vg), len(vb), 2))},
                                      "i_dc": zeros((len(vg), len(vb), 2)),
                                      "v_dc": zeros((len(vg), len(vb), 2)),
                                      "i_gs": zeros((len(vg), len(vb), 2))}
                                     for y2 in i_h] if h == 2 else None}}
                      for x in t]

            for idx_x, x in enumerate(self.t):
                if settings.tc.address is not None:
                    if idx_x == 0:
                        x["tt"].time = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                        x["tt"].stage = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                        x["tt"].shield = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                    if idx_x != 0:
                        x["tt"].time = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))
                        x["tt"].stage = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))
                        x["tt"].shield = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))

    class TemperatureVsFrequency:
        """ Experiment data class for frequency-dependent lock-in measurements. """
        def __init__(self, h, th, t, i_h, f, settings):

            self.t = [{"t": x,
                       "tt": ObsT(["stage", "shield"]),
                       "dr": {"h1": [[{"i_h": y1,
                                       "f": y2,
                                       "drt1": Lockin() if th == 0 or th == 1 else None,
                                       "drt2": Lockin() if th == 0 or th == 2 else None}
                                      for y2 in f] for y1 in i_h] if h == 1 else None,
                              "h2": [[{"i_h": y1,
                                       "f": y2,
                                       "drt1": Lockin() if th == 0 or th == 1 else None,
                                       "drt2": Lockin() if th == 0 or th == 2 else None}
                                      for y2 in f] for y1 in i_h] if h == 2 else None}}
                      for x in t]

            for idx_x, x in enumerate(self.t):
                if settings.tc.address is not None:
                    if idx_x == 0:
                        x["tt"].time = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                        x["tt"].stage = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                        x["tt"].shield = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                    if idx_x != 0:
                        x["tt"].time = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))
                        x["tt"].stage = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))
                        x["tt"].shield = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))

    class DUTVsFrequency:
        """ Experiment data class for frequency-dependent lock-in measurements. """
        def __init__(self, mode, h, t, i_h, vg, vb, f, v_ex, settings):

            self.heater = h
            self.t = t
            self.i_h = i_h
            self.vg = vg
            self.vb = vb
            self.v_ex = v_ex
            self.mode = mode
            self.f = f

            self.t = [{"t": x,
                       "tt": ObsT(["stage", "shield"]),
                       "sd": {"h1": [[{"i_h": y1,
                                       "f": y2,
                                       "i_w2": {"x": zeros((len(vg), len(vb), 2)),
                                                "y": zeros((len(vg), len(vb), 2))},
                                       "i_2w1": {"x": zeros((len(vg), len(vb), 2)),
                                                 "y": zeros((len(vg), len(vb), 2))},
                                       "v_w2": {"x": zeros((len(vg), len(vb), 2)),
                                                 "y": zeros((len(vg), len(vb), 2))},
                                       "i_dc": zeros((len(vg), len(vb), 2)),
                                       "v_dc": zeros((len(vg), len(vb), 2)),
                                       "i_gs": zeros((len(vg), len(vb), 2))}
                                      for y2 in f] for y1 in i_h] if h == 1 else None,
                              "h2": [[{"i_h": y1,
                                       "f": y2,
                                       "i_w2": {"x": zeros((len(vg), len(vb), 2)),
                                                "y": zeros((len(vg), len(vb), 2))},
                                       "i_2w1": {"x": zeros((len(vg), len(vb), 2)),
                                                 "y": zeros((len(vg), len(vb), 2))},
                                       "v_w2": {"x": zeros((len(vg), len(vb), 2)),
                                                 "y": zeros((len(vg), len(vb), 2))},
                                       "i_dc": zeros((len(vg), len(vb), 2)),
                                       "v_dc": zeros((len(vg), len(vb), 2)),
                                       "i_gs": zeros((len(vg), len(vb), 2))}
                                      for y2 in f] for y1 in i_h] if h == 1 else None}}
                      for x in t]

            for idx_x, x in enumerate(self.t):
                if settings.tc.address is not None:
                    if idx_x == 0:
                        x["tt"].time = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                        x["tt"].stage = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                        x["tt"].shield = zeros(int(ceil(settings.tc.settling_time_init * settings.tc.sampling_freq)))
                    if idx_x != 0:
                        x["tt"].time = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))
                        x["tt"].stage = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))
                        x["tt"].shield = zeros(int(ceil(settings.tc.settling_time * settings.tc.sampling_freq)))

    class PlotCalibration:
        """A class to plot calibration data. Based on Line2D objects. """
        def __init__(self, t, t_h, i_th, i_h, nrows=30, ncols=4, wait=0.001):

            self.wait = wait
            self.grid = GridSpec(nrows, ncols)
            self.fig = plt.figure(figsize=(45 / 2.54, 25 / 2.54))
            self.fig.subplots_adjust(top=0.96, bottom=0.06, left=0.05, right=0.98, hspace=1.0, wspace=0.3)
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
            # self.iv1.ticklabel_format(axis="y", style="scientific", scilimits=(0, 0))
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
            # self.iv2.ticklabel_format(axis="y", style="scientific", scilimits=(0, 0))
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

    class PlotStabilityDiagram:
        """A class to plot the stability diagram of any observable"""
        def __init__(self, vg, vb, x, y, z):
            """
            :param vg: VG vector (in V)
            :param vb: VB vector (in V)
            :param x: [string] x-axis with units, typically "$V_{GS}$ (V)"
            :param y: [string] y-axis with units, typically "$V_{DS}$ (V)"
            :param z: [string] z-axis with units, typically "$G$ (S)"
            """
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
            self.ax00.set_title(rf"{z} vs {y}", fontsize=10, fontstyle="italic")
            self.ax00.set_xlabel(rf"{y}")
            self.ax00.set_ylabel(rf"{z}")
            self.ax00.ticklabel_format(useOffset=False)
            self.ax00.set_xlim([min(vb), max(vb)])
            self.ax00.ticklabel_format(axis="y", style="scientific", scilimits=(0, 0))
            for idx, val in enumerate(vg):
                self.ax00.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

            self.ax10 = self.fig.add_subplot(self.grid[1, 0], sharex=self.ax00)
            self.ax10.set_xlabel(rf"{y}")
            self.ax10.set_ylabel(rf"{z}")
            self.ax10.ticklabel_format(axis="y", style="plain", scilimits=(0, 0))
            for idx, val in enumerate(vg):
                self.ax10.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vg(val)), linewidth=2, label=val, alpha=0.4))

            self.ax01 = self.fig.add_subplot(self.grid[0, 1], sharey=self.ax00)
            self.ax01.set_title(rf"{z} vs {x}", fontsize=10, fontstyle="italic")
            self.ax01.set_xlabel(rf"{x}")
            self.ax01.set_ylabel(rf"{z}")
            self.ax01.set_xlim([min(vg), max(vg)])
            self.ax01.ticklabel_format(axis="y", style="scientific", scilimits=(0, 0))
            for idx, val in enumerate(vb):
                self.ax01.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

            self.ax11 = self.fig.add_subplot(self.grid[1, 1], sharex=self.ax01, sharey=self.ax10)
            self.ax11.set_xlabel(rf"{x}")
            self.ax11.set_ylabel(rf"{z}")
            self.ax11.ticklabel_format(axis="y", style="plain", scilimits=(0, 0))
            for idx, val in enumerate(vb):
                self.ax11.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm2(self.norm_vb(val)), linewidth=2, label=val, alpha=0.4))

            self.ax02 = self.fig.add_subplot(self.grid[0, 2:])
            self.ax02.set_title(rf"{z} vs {x} vs {y}", fontsize=10, fontstyle="italic")
            self.ax02.set_xlabel(rf"{x}")
            self.ax02.set_ylabel(rf"{y}")
            self.ax02.set_xlim([min(vg), max(vg)])
            self.ax02.set_ylim([min(vb), max(vb)])
            self.ax02.ticklabel_format(axis="y", style="scientific", scilimits=(0, 0))
            self.im02 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
            self.cb02 = self.fig.colorbar(self.im02, ax=self.ax02)

            self.ax12 = self.fig.add_subplot(self.grid[1, 2:])
            self.ax12.set_xlabel(rf"{x}")
            self.ax12.set_ylabel(rf"{y}")
            self.ax12.set_xlim([min(vg), max(vg)])
            self.ax12.set_ylim([min(vb), max(vb)])
            self.ax12.ticklabel_format(axis="y", style="scientific", scilimits=(0, 0))
            self.im12 = plt.imshow(temp, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(vg), max(vg), min(vb), max(vb)))
            self.cb12 = self.fig.colorbar(self.im12, ax=self.ax12)

    class PlotTemperatureVsFrequency:

        def __init__(self, t, f, i_h, nrows=2, ncols=2, wait=0.001):

            self.wait = wait
            self.grid = GridSpec(nrows, ncols)
            self.fig = plt.figure(figsize=(30 / 2.54, 20 / 2.54))
            self.grid.update(wspace=0.2, hspace=0.2)
            self.xlim = [f.min(), f.max()]
            self.norm = Normalize(min(i_h), max(i_h))
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.axlg = [Line2D(xdata=[0], ydata=[0], color="grey", marker="o", markersize=6, markeredgecolor='black', markeredgewidth=0.2, linewidth=0, label="Th1"),
                         Line2D(xdata=[0], ydata=[0], color="grey", marker="D", markersize=6, markeredgecolor='black', markeredgewidth=0.2, linewidth=0, label="Th2")]

            self.axx = self.fig.add_subplot(self.grid[0, 0])
            self.axx.set_title("X-Y", fontsize=10, fontstyle="italic")
            self.axx.set_xlabel("Frequency (Hz)")
            self.axx.set_ylabel(r"$dR_X$ ($\Omega$)")
            self.axx.set_xscale("log")
            self.axx.set_xlim(self.xlim)
            for idx, val in enumerate(i_h):
                self.axx.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th1 {val}", marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))
                self.axx.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th2 {val}", marker="D", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))
            self.axx.legend(self.axlg, ["Th1", "Th2"])

            self.axy = self.fig.add_subplot(self.grid[1, 0])
            self.axy.set_xlabel("Frequency (Hz)")
            self.axy.set_ylabel(r"$dR_Y$ ($\Omega$)")
            self.axy.set_xscale("log")
            self.axy.set_xlim(self.xlim)
            for idx, val in enumerate(i_h):
                self.axy.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th1 {val}", marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))
                self.axy.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th2 {val}", marker="D", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

            self.axr = self.fig.add_subplot(self.grid[0, 1])
            self.axr.set_xlabel("Frequency (Hz)")
            self.axr.set_ylabel(r"$|R|$ ($\Omega$)")
            self.axr.set_title("R-$\phi$", fontsize=10, fontstyle="italic")
            self.axr.set_xscale("log")
            self.axr.set_yscale("log")
            self.axr.set_xlim(self.xlim)
            for idx, val in enumerate(i_h):
                self.axr.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th1 {val}", marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))
                self.axr.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th2 {val}", marker="D", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

            self.axp = self.fig.add_subplot(self.grid[1, 1])
            self.axp.set_xlabel("Frequency (Hz)")
            self.axp.set_ylabel(r"$\phi$ (°)")
            self.axp.set_xscale("log")
            self.axp.set_xlim(self.xlim)
            for idx, val in enumerate(i_h):
                self.axp.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th1 {val}", marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))
                self.axp.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), linewidth=0, label=f"th2 {val}", marker="D", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))

    class PlotDUTVsFrequency:

        def __init__(self, mode, t, f, i_h, vgs, vds, nrows=1, ncols=2, wait=0.001):

            self.wait = wait
            self.grid = GridSpec(nrows, ncols)
            self.fig = plt.figure(figsize=(30 / 2.54, 15 / 2.54))
            self.grid.update(wspace=0.4, hspace=0.4)
            self.xlim = [f.min(), f.max()]
            self.norm = Normalize(min(i_h), max(i_h))
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")

            self.ax1 = self.fig.add_subplot(self.grid[0])
            self.ax1.set_xlabel("Frequency (Hz)")
            if mode == 0:
                self.ax1.set_title(r"$I_{\omega_G}$ vs Frequency", fontsize=10, fontstyle="italic")
                self.ax1.set_ylabel(r"$I_{\omega_G}$ (A)")
            elif mode == 1:
                self.ax1.set_title(r"$V_{\omega_G}$ vs Frequency", fontsize=10, fontstyle="italic")
                self.ax1.set_ylabel(r"$V_{\omega_G}$ (A)")
            self.ax1.set_xscale("log")
            self.ax1.set_xlim(self.xlim)

            self.ax2 = self.fig.add_subplot(self.grid[1])
            self.ax2.set_title(r"$I_{2\omega_\alpha}$ vs Frequency", fontsize=10, fontstyle="italic")
            self.ax2.set_xlabel("Frequency (Hz)")
            self.ax2.set_ylabel(r"$I_{2\omega_\alpha}$ (A)")
            self.ax2.set_xscale("log")
            self.ax2.set_xlim(self.xlim)

            for i in range(len(i_h)):
                for j in range(len(vgs)):
                    for k in range(len(vds)):
                        self.ax1.add_line(Line2D(xdata=[None], ydata=[None], linewidth=0, marker="o", markeredgecolor='black', markeredgewidth=0.2, color=self.cm(self.norm(i_h[i])), alpha=0.4))
                        self.ax2.add_line(Line2D(xdata=[None], ydata=[None], linewidth=0, marker="o", markeredgecolor='black', markeredgewidth=0.2, color=self.cm(self.norm(i_h[i])), alpha=0.4))

class IV:

    """ Experiment data class for iv measurements. """

    def __init__(self):

        self.i = None
        self.v = None
        self.r = None
        self.r_stderr = None

class Lockin:

    """ Experiment data class for (time-dependent) lock-in measurements. """

    def __init__(self):

        # use time, raw, x and y to store time-dependent data for plotting purposes
        self.time = None
        self.x = None
        self.y = None
        self.rho = None
        self.phi = None
        self.raw = None

        # use raw_avg and raw_stddev to store averaged data information (time dependence is lost)
        self.raw_avg = float
        self.raw_stddev = float

        # use x_avg and x_stddev to store averaged x-component data information (time dependence is lost)
        self.x_avg = float
        self.x_stddev = float

        # use y_avg and y_stddev to store averaged y-component data information (time dependence is lost)
        self.y_avg = float
        self.y_stddev = float

        # use rho_avg and rho_stddev to store averaged module data information (time dependence is lost)
        self.rho_avg = float
        self.rho_stddev = float

        # use phi_avg and phi_stddev to store averaged phase data information (time dependence is lost)
        self.phi_avg = float
        self.phi_stddev = float

class ObsT:

    """ Experiment data class for time-dependent measurements. """

    def __init__(self, obs):

        """ obs is a list of observables """

        self.time = None
        for idx, val in enumerate(obs):
            self.__setattr__(val, None)

class PlotObsT:

    """A class to plot a set of observables vs time.
    Useful to monitor observables in real-time."""

    def __init__(self, labels, duration, ylabel="Signal (a.u.)", semilogy=False):

        self.grid = GridSpec(1, 1)
        self.fig = plt.figure(figsize=(20 / 2.54, 15 / 2.54))
        self.grid.update(wspace=0.4, hspace=2)

        self.ax = self.fig.add_subplot()
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel(ylabel)
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

class FET:

    class Sweep:
        def __init__(self, vgs, vds):
            """
            Class for Vds OR Vgs sweep measurement at constant temperature.
            :param sweep: [int] experiment, either 0 ("vgs") or 1 ("vds") or 2 ("iv")
            :param vgs: [list] [start (in V), stop (in V), no. steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles]
            :param vds: [list] [start (in V), stop (in V), no. steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles]
            Data matrix structure: [Vgs, Vds, [Vgs, Igs, Vds, Ids, cycle_Vgs, cycle_Vds, timestamp, dVds]]
            Data can be extended by adding further elements to the 3rd dimension.
            """
            self.temperature = float
            self.illumination = int
            self.environment = int
            self.annealing = int
            self.sweep_rate = float
            self.comment = str
            self.vgs = self.make_array_4_sweep(vgs)
            self.vds = self.make_array_4_sweep(vds)
            self.data = zeros((len(self.vgs), len(self.vds), 8))

        @staticmethod
        def make_array_4_sweep(x):
            """
            :param x: [list] In the order: start, stop, steps, lin-log, mode (0: FWD, 1: FWD-BWD, 2: LOOP), cycles
            :return: x
            """
            if isinstance(x, list) and len(x) == 6:
                if x[4] == 0:
                    y = linspace(x[0], x[1], x[2])
                elif x[4] == 1:
                    y = linspace(x[0], x[1], x[2])
                    y = concatenate((y[:-1], flip(y)))
                elif x[4] == 2:
                    y = linspace(x[0], x[1], x[2])
                    y = concatenate((y[:-1], flip(y), -y[1:-1], flip(-y)))
                if (x[4] == 1 or x[4] == 2) and (x[5] > 1):
                    y0 = y[1:]
                    for idx in range(x[5]-1):
                        y = concatenate((y, y0))
            else:
                exit("Cannot generate array from given input... Terminate.")
            return y

        def filter_vgs_cycle(self, n):
            newdata = zeros_like(self.data)
            k = 0
            for i in range(self.data.shape[0]):
                if all(self.data[i, :, 4] == n):
                    newdata[k, :, :] = self.data[i, :, :]
                    k = k + 1
            return newdata[0:k, :, :]

        def filter_vds_cycle(self, n):
            newdata = zeros_like(self.data)
            k = 0
            for j in range(self.data.shape[1]):
                # if all(self.data[:, j, 5] == n):
                if self.data[0, j, 5] == n:
                    newdata[:, k, :] = self.data[:, j, :]
                    k = k + 1
            return newdata[:, 0:k, :]

        def filter_vgs_fwd_sweep(self):
            newdata = zeros_like(self.data)
            k = 0
            for i in range(self.data.shape[0]):
                if i == 0:
                    continue
                else:
                    if all(self.data[i, :, 0] - self.data[i-1, :, 0] > 0):
                        if k == 0:
                            newdata[k, :, :] = self.data[i-1, :, :]
                            newdata[k+1, :, :] = self.data[i, :, :]
                            k = k + 2
                        else:
                            newdata[k, :, :] = self.data[i, :, :]
                            k = k + 1
            return newdata[0:k, :, :]

        def filter_vgs_bkw_sweep(self):
            newdata = zeros_like(self.data)
            k = 0
            for i in range(self.data.shape[0]):
                if i == 0:
                    continue
                else:
                    if all(self.data[i, :, 0] - self.data[i-1, :, 0] < 0):
                        if k == 0:
                            newdata[k, :, :] = self.data[i-1, :, :]
                            newdata[k+1, :, :] = self.data[i, :, :]
                            k = k + 2
                        else:
                            newdata[k, :, :] = self.data[i, :, :]
                            k = k + 1
            return newdata[0:k, :, :]

        def filter_vds_fwd_sweep(self):
            newdata = zeros_like(self.data)
            k = 0
            for j in range(self.data.shape[1]):
                if j == 0:
                    continue
                else:
                    if all(self.data[:, j, 2] - self.data[:, j-1, 2] > 0):
                        if k == 0:
                            newdata[:, k, :] = self.data[:, j, :]
                            newdata[:, k+1, :] = self.data[:, j-1, :]
                            k = k + 2
                        else:
                            newdata[:, k, :] = self.data[:, j, :]
                            k = k + 1
            return newdata[:, 0:k, :]

        def filter_vds_bkw_sweep(self):
            newdata = zeros_like(self.data)
            k = 0
            for j in range(self.data.shape[1]):
                if j == 0:
                    continue
                else:
                    #if all(self.data[:, j, 2] - self.data[:, j-1, 2] < 0):
                    if self.data[0, j, 2] - self.data[0, j-1, 2] < 0:
                        if k == 0:
                            newdata[:, k, :] = self.data[:, j, :]
                            newdata[:, k+1, :] = self.data[:, j-1, :]
                            k = k + 2
                        else:
                            newdata[:, k, :] = self.data[:, j, :]
                            k = k + 1
            return newdata[:, 0:k, :]

        def filter_vgs_values(self, values):
            if len(values) == 0 or values is None:
                return self.data
            else:
                newdata = zeros_like(self.data)
                k = 0
                for i in range(self.data.shape[0]):
                    if unique(self.data[i, :, 0])[0] in values:
                        newdata[k, :, :] = self.data[i, :, :]
                        k = k + 1
                return newdata[0:k, :, :]

        def filter_vds_values(self, values):
            if len(values) == 0 or values is None:
                return self.data
            else:
                newdata = zeros_like(self.data)
                k = 0
                for j in range(self.data.shape[1]):
                    if unique(self.data[:, j, 2])[0] in values:
                        newdata[:, k, :] = self.data[:, j, :]
                        k = k + 1
                return newdata[:, 0:k, :]

        def plot_output_characteristic(self):
            """Plot output characteristic"""
            plot0 = FET.PlotOutputCharacteristic(self.vgs, self.vds)
            for i in range(len(self.vgs)):
                plot0.ax0.set_data(self.data[i, :, 2], self.data[i, :, 1])
                plot0.ax0.set_data(self.data[i, :, 2], self.data[i, :, 3])
                plot0.ax1.set_data(self.data[i, :, 2], abs(self.data[i, :, 1]))
                plot0.ax1.set_data(self.data[i, :, 2], abs(self.data[i, :, 3]))
            plt.show()

        def plot_transfer_characteristic(self):
            """Plot transfer characteristic"""
            plot0 = FET.PlotTransferCharacteristic(self.vgs, self.vds)
            for i in range(len(self.vds)):
                plot0.ax0.set_data(self.data[i, :, 0], self.data[i, :, 1])
                plot0.ax0.set_data(self.data[i, :, 0], self.data[i, :, 3])
                plot0.ax1.set_data(self.data[i, :, 0], abs(self.data[i, :, 1]))
                plot0.ax1.set_data(self.data[i, :, 0], abs(self.data[i, :, 3]))
            plt.show()

        def plot_iv_2wire(self):
            """Plot IV - measured in 2 wire configuration"""
            plot0 = FET.PlotIV(self.vds)
            plot0.ax0.set_data(self.data[0, :, 2], self.data[0, :, 3])
            plot0.ax1.set_data(self.data[0, :, 2], abs(self.data[0, :, 3]))
            plt.show()

        # def plot_iv_4wire(self):
        #     """Plot IV - measured in 4 wire configuration"""
        #     plot0 = FET.PlotIV(self.vds)
        #     plot0.ax0.set_data(self.data[0, :, 7], self.data[0, :, 7])
        #     plot0.ax1.set_data(self.data[0, :, 7], abs(self.data[0, :, 7]))
        #     plt.show()

    class SweepVsT:
        def __init__(self, t, vgs, vds):
            """
            Class for Vds OR Vgs sweep measurement as a function of temperature.
            :param sweep: [int] experiment, either 0 ("vgs") or 1 ("vds")
            :param t: [array of float] temperature in K
            :param vgs: [array of float] Vgs in Volts, includes all cycles
            :param vds: [array of float] Vds in Volts, includes all cycles
            """
            self.data = []
            self.t = []
            for idx, val in enumerate(t):
                self.data.append(FET.Sweep(vgs, vds))
                self.data[idx].temperature = val
                self.t.append(ObsT(["stage", "shield"]))

    class PlotOutputCharacteristic:
        """A class to plot FET output characteristic."""
        def __init__(self, vgs, vds):
            """
            :param vgs: [array] Vgs (in V)
            :param vds: [array] Vds (in V)
            """
            self.grid = GridSpec(2, 1)
            self.fig = plt.figure(figsize=(20 / 2.54, 20 / 2.54))
            self.grid.update(wspace=0.2, hspace=0.2)
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.lookIds = {"linewidth": 0, "marker": "o", "markersize": 6, "markeredgecolor": "black",
                            "markeredgewidth": 0.2, "alpha": 0.4}
            self.lookIgs = {"linewidth": 0, "marker": "D", "markersize": 6, "markeredgecolor": "black",
                            "markeredgewidth": 0.2, "alpha": 0.4}
            self.ax0 = self.fig.add_subplot(self.grid[0])
            self.ax0.set_title("Output characteristic", fontsize=10, fontstyle="italic")
            self.ax0.set_ylabel("$I$ (A)")
            self.ax0.set_xlabel("$V_{ds}$ (V)")
            self.ax0.set_xlim([min(vds), max(vds)])
            self.ax1 = self.fig.add_subplot(self.grid[1])
            self.ax1.set_xlabel("$V_{ds}$ (V)")
            self.ax1.set_ylabel("$Log_{10}(I)$")
            self.ax1.set_xlim([min(vds), max(vds)])
            self.norm = Normalize(0, len(vgs) - 1)
            for i, val in enumerate(vgs):
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIgs))
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIds))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIgs))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIds))
            custom_lines = [Line2D([0], [0], color=self.cm(self.norm(x)), lw=4) for x in range(len(vgs))]
            custom_legend = self.ax0.legend(custom_lines, [x for x in vgs], title="Vgs", fancybox=True, framealpha=0.5)
            self.ax0.add_artist(custom_legend)

    class PlotTransferCharacteristic:

        """A class to plot FET transfer characteristic."""

        def __init__(self, vgs, vds):

            """
            :param vgs: [array] Vgs (in V)
            :param vds: [array] Vds (in V)
            """

            self.grid = GridSpec(2, 1)
            self.fig = plt.figure(figsize=(20 / 2.54, 20 / 2.54))
            self.grid.update(wspace=0.2, hspace=0.2)
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.lookIds = {"linewidth": 0, "marker": "o", "markersize": 6, "markeredgecolor": "black",
                            "markeredgewidth": 0.2, "alpha": 0.4}
            self.lookIgs = {"linewidth": 0, "marker": "D", "markersize": 6, "markeredgecolor": "black",
                            "markeredgewidth": 0.2, "alpha": 0.4}
            self.ax0 = self.fig.add_subplot(self.grid[0])
            self.ax0.set_title("Transfer characteristic", fontsize=10, fontstyle="italic")
            self.ax0.set_xlabel("$V_{gs}$ (V)")
            self.ax0.set_ylabel("$I$ (A)")
            self.ax0.set_xlim([min(vgs), max(vgs)])
            self.ax1 = self.fig.add_subplot(self.grid[1])
            self.ax1.set_ylabel("$Log_{10}(I)$")
            self.ax1.set_xlabel("$V_{gs}$ (V)")
            self.ax1.set_xlim([min(vgs), max(vgs)])
            self.norm = Normalize(0, len(vds) - 1)
            for i, val in enumerate(vds):
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIgs))
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIds))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIgs))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(i)), **self.lookIds))
            custom_lines = [Line2D([0], [0], color=self.cm(self.norm(x)), lw=4) for x in range(len(vds))]
            custom_legend = self.ax0.legend(custom_lines, [x for x in vds], title="Vds", fancybox=True,
                                            framealpha=0.5)
            self.ax0.add_artist(custom_legend)

        def plot_transfer_characteristic(self, sweep):
            for i in range(len(sweep.vds)):
                self.ax0.set_data(sweep.data[i, :, 0], sweep.data[i, :, 1])
                self.ax0.set_data(sweep.data[i, :, 0], sweep.data[i, :, 3])
                self.ax1.set_data(sweep.data[i, :, 0], abs(sweep.data[i, :, 1]))
                self.ax1.set_data(sweep.data[i, :, 0], abs(sweep.data[i, :, 3]))

    class PlotIV:

        """A class to plot IVs."""

        def __init__(self, vds=array([-1, 1]), xlabel="$V_{ds}$ (V)", ylabel="$I$ (A)", n=1):
            """
            :param vds: [array] Vds (in V)
            :param xlabel: [string] x-axis label
            :param ylabel: [string] y-axis label
            :param n: [int] number of lines. Pass n=0 if adding recursively in the main script
            """
            self.grid = GridSpec(2, 1)
            self.fig = plt.figure(figsize=(15 / 2.54, 20 / 2.54))
            self.grid.update(top=0.95, bottom=0.11, left=0.14, right=0.93, hspace=0.2, wspace=0.2)
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.lookIds = {"linewidth": 0, "marker": "o", "markersize": 6, "markeredgecolor": "black",
                            "markeredgewidth": 0.2, "alpha": 0.4}
            self.lookIgs = {"linewidth": 0, "marker": "D", "markersize": 6, "markeredgecolor": "black",
                            "markeredgewidth": 0.2, "alpha": 0.4}
            self.ax0 = self.fig.add_subplot(self.grid[0])
            self.ax0.set_title("IV", fontsize=10, fontstyle="italic")
            self.ax0.set_xlabel(xlabel)
            self.ax0.set_ylabel(ylabel)
            self.ax0.set_xlim([min(vds), max(vds)])
            self.ax1 = self.fig.add_subplot(self.grid[1])
            self.ax1.set_yscale("log")
            self.ax1.set_xlabel(xlabel)
            self.ax1.set_ylabel(ylabel)
            self.ax1.set_xlim([min(vds), max(vds)])
            # add lines to axes
            for i in range(n):
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color="black", **self.lookIds))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color="black", **self.lookIds))

    class PlotIVVsT:

        """A class to plot IVs."""

        def __init__(self, t, vds):
            """
            :param vds: [array] Vds (in V)
            """
            self.grid = GridSpec(2, 1)
            self.fig = plt.figure(figsize=(20 / 2.54, 20 / 2.54))
            self.grid.update(wspace=0.2, hspace=0.2)
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.norm = Normalize(min(t), max(t))
            self.lookIds = {"linewidth": 0, "marker": "o", "markersize": 6, "markeredgecolor": "black",
                            "markeredgewidth": 0.2, "alpha": 0.4}
            self.lookIgs = {"linewidth": 0, "marker": "D", "markersize": 6, "markeredgecolor": "black",
                            "markeredgewidth": 0.2, "alpha": 0.4}
            self.ax0 = self.fig.add_subplot(self.grid[0])
            self.ax0.set_title("IV", fontsize=10, fontstyle="italic")
            self.ax0.set_xlabel("$V_{ds}$ (V)")
            self.ax0.set_ylabel("$I$ (A)")
            self.ax0.set_xlim([min(vds), max(vds)])
            self.ax1 = self.fig.add_subplot(self.grid[1])
            self.ax1.set_xlabel("$V_{ds}$ (V)")
            self.ax1.set_ylabel("$Log_{10}(I)$")
            self.ax1.set_xlim([min(vds), max(vds)])
            # add lines to axes
            for val in t:
                self.ax0.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), **self.lookIds))
                self.ax1.add_line(Line2D(xdata=[None], ydata=[None], color=self.cm(self.norm(val)), **self.lookIds))

    class PlotStabilityDiagram:
        def __init__(self, vgs, vds, x, y, z):
            Thermoelectrics.PlotStabilityDiagram(vgs, vds, x, y, z)

    class PlotMobility:

        def __init__(self):

            """
            :param regime: [list of int]
            """

            self.grid = GridSpec(1, 2)
            self.fig = plt.figure(figsize=(25 / 2.54, 15 / 2.54))
            self.grid.update(top=0.91, bottom=0.12, left=0.075, right=0.945, hspace=0.2, wspace=0.245)
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.lookIds = {"linewidth": 0, "marker": "o", "markersize": 6, "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.6}
            self.lookIgs = {"linewidth": 0, "marker": "D", "markersize": 6, "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.6}
            self.lookSmooth = {"linewidth": 2, "linestyle": "--", "alpha": 0.6}
            self.ax0 = self.fig.add_subplot(self.grid[0])  # Ids vs Vgs
            self.ax0.set_xlabel("$V_{gs}$ (V)")
            self.ax0.set_ylabel("I (A)")
            self.ax1 = self.fig.add_subplot(self.grid[1])  # mobility in the linear region
            self.ax1.set_xlabel("$V_{gs}$ (V)")
            self.ax1.set_ylabel("$\mu$ ($cm^2/V\cdot s$)")

    class PlotContactResistance:

        def __init__(self):

            self.grid = GridSpec(1, 2)
            self.fig = plt.figure(figsize=(20 / 2.54, 12 / 2.54))
            self.grid.update(top=0.91,
                             bottom=0.14,
                             left=0.13,
                             right=0.9,
                             hspace=0.2,
                             wspace=0.4)
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.lookIds = {"linewidth": 0, "marker": "o", "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.4}
            self.lookIgs = {"linewidth": 0, "marker": "D", "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.4}

            self.ax0 = self.fig.add_subplot(self.grid[0])  # Ids vs Vds
            self.ax1 = self.fig.add_subplot(self.grid[1])  # R

            self.ax0.set_ylabel("$Ids$ (A)")
            self.ax0.set_xlabel("$Vds$ (V)")
            self.ax1.set_ylabel("R ($\Omega$m)")
            self.ax1.set_xlabel("Channel length ($\mu$m)")

class FitDoubleSchottkyBarrier:

    """ Object for Double Schottky barrier fitting """

    def __init__(self, V, I, T, S1, S2, ideal=True):

        self.V = V
        self.I = I

        # initial values, boundaries and vary
        self.T_vary = False
        self.T_ini = T
        self.T_min = 0
        self.T_max = 1000

        self.S1_vary = False
        self.S1_ini = S1
        self.S1_min = S1*0.1
        self.S1_max = S1*10

        self.S2_vary = False
        self.S2_ini = S2
        self.S2_min = S2*0.1
        self.S2_max = S2*10

        self.phi01_vary = True
        self.phi01_min = 0.0
        self.phi01_ini = 0.5
        self.phi01_max = 1

        self.phi02_vary = True
        self.phi02_min = 0.0
        self.phi02_ini = 0.5
        self.phi02_max = 1

        self.n1_vary = False if ideal is True else True
        self.n1_min = 0.999
        self.n1_ini = 1
        self.n1_max = 3

        self.n2_vary = False if ideal is True else True
        self.n2_min = 0.999
        self.n2_ini = 1
        self.n2_max = 3

        self.v1_vary = False if ideal is True else True
        self.v1_min = 0
        self.v1_ini = 0.5
        self.v1_max = 1

        self.v2_vary = False if ideal is True else True
        self.v2_min = 0
        self.v2_ini = 0.5
        self.v2_max = 1

        self.phiPF_vary = True
        self.phiPF_min = 0.0
        self.phiPF_ini = 0.5
        self.phiPF_max = 2

    @staticmethod
    def func(V, phi01, phi02, T, S1, S2, n1, n2, v1=0.5, v2=0.5):

        """We note that the semiconductor with SBs at both contacts can be modeled
        with two back-to-back Schottky diodes separated by a series resistance.
        When a sufficiently high external voltage is applied, whether positive
        or negative, one Schottky junction is forward-biased while the other one
        is reverse-biased. The reverse saturation current of the reverse-biased
        diode always limits the current."""

        # A = 4 * pi * q * m_e * k ** 2 / h ** 3
        A = 1.20173e6  # A / m2 K2
        beta = (k_b * T) / e  # in eV
        phi1 = phi01 + v1 * V * (1 - 1 / n1)
        phi2 = phi02 - v2 * V * (1 - 1 / n2)
        Is1 = S1 * A * T**2 * exp(-phi1 / beta)
        Is2 = S2 * A * T**2 * exp(-phi2 / beta)
        I = 2 * Is1 * Is2 * sinh(V / 2 / beta) / (Is1 * exp(V / 2 / beta) + Is2 * exp(- V / 2 / beta))
        return I

    def iv_fit(self, weights=1):
        model = Model(func=self.func, nan_policy="propagate")  # create model object
        # print(f"Parameters: {model.param_names}")
        # print(f"Independent variable: {model.independent_vars}")
        model.set_param_hint('phi01', value=self.phi01_ini, vary=self.phi01_vary, min=self.phi01_min, max=self.phi01_max)  # set parameter phi01 to passed argument
        model.set_param_hint('phi02', value=self.phi02_ini, vary=self.phi02_vary, min=self.phi02_min, max=self.phi02_max)  # set parameter phi02 to passed argument
        model.set_param_hint('T', value=self.T_ini, vary=self.T_vary, min=self.T_min, max=self.T_max)  # set parameter T to passed argument
        model.set_param_hint('S1', value=self.S1_ini, vary=self.S1_vary, min=self.S1_min, max=self.S1_max)  # set parameter S1 to passed argument
        model.set_param_hint('S2', value=self.S2_ini, vary=self.S2_vary, min=self.S2_min, max=self.S2_max)  # set parameter S2 to passed argument
        model.set_param_hint('n1', value=self.n1_ini, vary=self.n1_vary, min=self.n1_min, max=self.n1_max)
        model.set_param_hint('n2', value=self.n2_ini, vary=self.n2_vary, min=self.n2_min, max=self.n2_max)
        model.set_param_hint('v1', value=self.v1_ini, vary=self.v1_vary, min=self.v1_min, max=self.v1_max)
        model.set_param_hint('v2', value=self.v2_ini, vary=self.v2_vary, min=self.v2_min, max=self.v2_max)
        params = model.make_params()  # generate parameter objects
        result = model.fit(self.I, params, V=self.V, weights=weights)
        return result

    def recursive_fit(self, model, result):
        param_ini = {"phi01": self.phi01_ini, "phi02": self.phi02_ini, "n1": self.n1_ini, "n2": self.n2_ini, "v1": self.v1_ini, "v2": self.v2_ini}
        param_min = {"phi01": self.phi01_min, "phi02": self.phi02_min, "n1": self.n1_min, "n2": self.n2_min, "v1": self.v1_min, "v2": self.v2_min}
        param_max = {"phi01": self.phi01_max, "phi02": self.phi02_max, "n1": self.n1_max, "n2": self.n2_max, "v1": self.v1_max, "v2": self.v2_max}
        for p in result.params:
            if result.model.param_hints[p]["vary"] is True:
                if result.params[p].stderr == 0 or (result.params[p].stderr > 0 and result.params[p].stderr / result.params[p].value > 0.1) or result.params[p].stderr is None:
                    result.params[p].stderr = 0  # then set the error to zero
                    print(f"{p} error - re-initializing at {param_min[p] + (param_max[p] - param_min[p]) / self.sweep_steps}")
                    model.set_param_hint(p, value=param_min[p] + (param_max[p] - param_min[p]) / self.sweep_steps, vary=True, min=param_ini[p], max=param_max[p])
                    params = model.make_params()  # generate parameter objects
                    print(params["phi01"])
                    result = model.fit(self.I, params, V=self.V)
                    print(result.fit_report())
                    self.recursive_fit(model, result)
        return result

    class PlotDoubleSchottkyBarrier:

        def __init__(self):

            self.lookIds = {"linewidth": 0, "marker": "o", "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.4}
            self.lookFit = {"linestyle": '--', "dashes": (3, 15)}

            self.fig = plt.figure(figsize=(20 / 2.54, 22.5 / 2.54))
            self.grid = GridSpec(nrows=2, ncols=1)
            # self.grid.update(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0.19, wspace=0.315)
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.ax00 = self.fig.add_subplot(self.grid[0])
            self.ax00.set_title(r"Fit")
            self.ax00.set_xlabel("Voltage (V)")
            self.ax00.set_ylabel(r"Current (I)")
            self.ax01 = self.fig.add_subplot(self.grid[1])
            self.ax01.set_title(r"$\delta$")
            self.ax01.set_xlabel("Voltage (K)")
            self.ax01.set_ylabel(r"$\delta$ (A)")

    class PlotDoubleSchottkyBarrierVsT:

        def __init__(self, T):

            self.lookIds = {"linewidth": 0, "marker": "o", "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.4}
            self.lookFit = {"linestyle": '--', "dashes": (3, 15)}

            self.fig = plt.figure(figsize=(45 / 2.54, 22.5 / 2.54))
            self.grid = GridSpec(nrows=2, ncols=4)
            self.grid.update(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0.19, wspace=0.315)
            self.norm_T = matplotlib.colors.Normalize(vmin=min(T), vmax=max(T))
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.ax00 = self.fig.add_subplot(self.grid[:, 0:2])
            self.ax00.set_title(r"Fit")
            self.ax00.set_xlabel("Voltage (V)")
            self.ax00.set_ylabel(r"Current (I)")
            self.ax01 = self.fig.add_subplot(self.grid[0, 2])
            self.ax01.set_title(r"$\Phi$")
            self.ax01.set_xlabel("Temperature (K)")
            self.ax01.set_ylabel(r"$\Phi$ (eV)")
            self.ax11 = self.fig.add_subplot(self.grid[1, 2])
            self.ax11.set_xlabel("Temperature (K)")
            self.ax11.set_ylabel(r"$\Phi$ std. err. (eV)")
            self.ax02 = self.fig.add_subplot(self.grid[0, 3])
            self.ax02.set_title(r"n")
            self.ax02.set_xlabel("Temperature (K)")
            self.ax02.set_ylabel(r"n")
            self.ax12 = self.fig.add_subplot(self.grid[1, 3])
            self.ax12.set_xlabel("Temperature (K)")
            self.ax12.set_ylabel(r"n std. err.")

class FitPooleFrenkel:

    def __init__(self, V, I, T, d, S, epsilon_r=1):

        self.V = V
        self.I = I

        # initial values, boundaries and vary
        self.T_vary = False
        self.T_ini = T
        self.T_min = T-10
        self.T_max = T+10

        self.S_vary = False
        self.S_ini = S
        self.S_min = S*0.1
        self.S_max = S*10

        self.phi_vary = True
        self.phi_min = 0.01
        self.phi_ini = 0.1
        self.phi_max = 1

        self.d_vary = False
        self.d_ini = d
        self.d_min = d*0.5
        self.d_max = d*1.5

        self.epsilon_r_vary = False
        self.epsilon_r_ini = epsilon_r
        self.epsilon_r_min = epsilon_r * 0.1
        self.epsilon_r_max = epsilon_r * 10

        self.sigma0_vary = True
        self.sigma0_ini = 1e-6
        self.sigma0_min = 1e-7
        self.sigma0_max = 1e-5

    @staticmethod
    def func(self, V, phi, T, d, sigma0, S, epsilon_r):
        """ On theoretical grounds, the Poole–Frenkel effect is comparable to the Schottky effect,
        which is the lowering of the metal-insulator energy barrier due to the electrostatic interaction with
        the electric field at a metal-insulator interface. However, the conductivity arising from the
        Poole–Frenkel effect is detected in presence of bulk-limited conduction
        (when the limiting conduction process occurs in the bulk of a material),
        while the Schottky current is observed when the conductivity is contact-limited
        (when the limiting conduction mechanism occurs at the metal-insulator interface)."""
        # d is the dielectric/semiconductor thickness
        # phi_PF is the average barrier height that a charge must escape inside the insulator/semiconductor, with no externally applied field
        epsilon = epsilon_0 * epsilon_r  # is the high frequency dielectric constant of the material
        beta = (k_b * T) / e  # in eV
        A = sigma0 * V / d * S  # pre-factor
        I = A * exp(- 1 / beta * (phi - 2 * sqrt(abs(e * V) / (4 * pi * epsilon * d))))
        return I

    @staticmethod
    def func_linear(self, a, b, V):
        """ Linear fit of ln(I/V) vs sqrt(V). """
        return a + b * sqrt(V)

    def iv_fit(self, weights=1):
        model = Model(func=self.func, nan_policy="propagate")  # create model object
        # print(f"Parameters: {model.param_names}")
        # print(f"Independent variable: {model.independent_vars}")
        model.set_param_hint('phi', value=self.phi_ini, vary=self.phi_vary, min=self.phi_min, max=self.phi_max)  # set parameter phi01 to passed argument
        model.set_param_hint('T', value=self.T_ini, vary=self.T_vary, min=self.T_min, max=self.T_max)  # set parameter T to passed argument
        model.set_param_hint('S', value=self.S_ini, vary=self.S_vary, min=self.S_min, max=self.S_max)  # set parameter S to passed argument
        model.set_param_hint('d', value=self.d_ini, vary=self.d_vary, min=self.d_min, max=self.d_max)
        model.set_param_hint('epsilon_r', value=self.epsilon_r_ini, vary=self.epsilon_r_vary, min=self.epsilon_r_min, max=self.epsilon_r_max)
        model.set_param_hint('sigma0', value=self.sigma0_ini, vary=self.sigma0_vary, min=self.sigma0_min, max=self.sigma0_max)
        params = model.make_params()  # generate parameter objects
        result = model.fit(self.I, params, V=self.V, weights=weights)
        return result

class FitSimmons:
    """
    simmons fit sweep class
    """
    def __init__(self, V, I):

        self.V = V
        self.I = I

        # initial values
        self.A_ini = 0.1
        self.A_vary = False
        self.A_min = 0.01
        self.A_max = 40

        self.phi_ini = 4.2
        self.phi_vary = True
        self.phi_min = 1.5
        self.phi_max = 5.0  # graphite

        self.d_ini = 1.0
        self.d_vary = True
        self.d_min = 0.1
        self.d_max = 10.0

        self.rescale = 1

    def simmons_for_intermediate_voltage_range(self):
        """Valid for V > phi/2"""
        model = Model(func=self.simmons, nan_policy="propagate")  # create model object
        # print(f"Parameters: {model.param_names}")
        # print(f"Independent variable: {model.independent_vars}")
        model.set_param_hint("A", value=self.A_ini, vary=self.A_vary, min=self.A_min, max=self.A_max)
        model.set_param_hint("phi", value=self.phi_ini, vary=self.phi_vary, min=self.phi_min, max=self.phi_max)
        model.set_param_hint("d", value=self.d_ini, vary=self.d_vary, min=self.d_min, max=self.d_max)
        params = model.make_params()  # generate parameter objects
        weights = where((self.V <= 2) & (self.V >= 1.5), self.I * 10, self.I)
        result = model.fit(self.I[(abs(self.V) >= 1.5)], params, weights=1, V=self.V[(abs(self.V) >= 1.5)])
        return result

    def simmons_for_high_voltage_range(self):
        """Not implemented yet"""

    def simmons_eval(self, model, params):
        return model.eval(params, V=self.V)

    @staticmethod
    def u_sqrt(self, ua):
        try:
            uas = zeros_like(ua)
            for i in range(len(ua)):
                uas[i] = sqrt(ua[i])
            return uas
        except TypeError:
            return sqrt(ua)

    @staticmethod
    def u_exp(self, ua):
        try:
            uas = zeros_like(ua)
            for i in range(len(ua)):
                uas[i] = exp(ua[i])
            return uas
        except TypeError:
            return exp(ua)

    @staticmethod
    def simmons(self, V, A, phi, d):
        # simmons eq. 26, assume beta=1
        # is uncertainty compatible
        phi = e * phi
        d = d * 1e-9
        A = A * 1e-18
        prefactor = A * (e/(2 * pi * h * d**2))
        # term1 = (phi - e * V / 2) * self.u_exp(-4*pi*d/h*self.u_sqrt(2*m)*self.u_sqrt(phi-e*V/2))
        term1 = (phi - e * V / 2) * exp(-4 * pi * d / h * sqrt(2 * m_e) * sqrt(phi - e * V / 2))
        # term2 = (phi + e * V / 2) * self.u_exp(-4*pi*d/h*self.u_sqrt(2*m)*self.u_sqrt(phi+e*V/2))
        term2 = (phi + e * V / 2) * exp(-4 * pi * d / h * sqrt(2 * m_e) * sqrt(phi + e * V / 2))
        I = prefactor * (term1 - term2)
        return I

class Figure:

    class PlotLine:
        """A class to plot a set of observables vs x"""
        def __init__(self, xlabel, ylabel, title=None, obs=None, semilogy=False, sizex=8/2.54, sizey=7/2.54, cmap=None, norm=None, cmap_label=None, xlim=(-1, 1)):
            """
            :param xlabel: [string] x-axis label
            :param ylabel: [string] y-label axis
            :param title: [string] plot title
            :param obs: [list of string] name of the observables (used to build figure legend)
            :param semilogy: [bool] either the plot is semilogy (True) or not (False)
            :param sizex: [float] figure width (in inches)
            :param sizey: [float] figure heigth (in inches)
            :param cmap: [cmap] figure color map
            :param norm: [norm] normalization
            :param cmap_label: [string] color map bar title
            :param xlim: [tuple of float] x-axis limits
            """
            self.grid = GridSpec(1, 1)
            self.fig = plt.figure(figsize=(sizex, sizey), dpi=300)
            self.ax = self.fig.add_subplot()
            self.ax.set_xlabel(xlabel)
            self.ax.set_ylabel(ylabel)
            self.axlg = []
            self.ax.set_title(title)
            self.ax.set_yscale({0: "linear", 1: "log"}[semilogy])
            self.ax.set_xlim(xlim[0], xlim[1])
            self.cmap = cmap
            self.norm = norm

            if self.cmap is not None and self.norm is not None:
                self.fig.colorbar(mappable=matplotlib.cm.ScalarMappable(norm=self.norm, cmap=self.cmap), ax=self.ax, label=cmap_label)
            self.marker = itertools.cycle(("o", "D", "v", "^", "<", ">", "p", "H"))
            if obs is not None:
                for idx, val in enumerate(obs):
                    marker = next(self.marker)
                    color = matplotlib.cm.Paired(idx)
                    self.axlg.append(Line2D(xdata=[0], ydata=[0], color=color, marker=marker, markersize=6, markeredgecolor='black', markeredgewidth=0.2, linewidth=0, label=val))
                    self.ax.add_line(Line2D(xdata=[None], ydata=[None], color=color, marker=marker, markeredgecolor='black', markeredgewidth=0.2, linewidth=0, alpha=0.4, label=val))
                self.ax.legend(self.axlg, obs)

    class PlotLineLinAndLog:
        """A class to plot a set of observables vs x in linear and logarithmic scale"""
        def __init__(self, xlabel, ylabel, title=None, obs=None, sizex=8/2.54, sizey=7/2.54, cmap=None, norm=None, cmap_label=None, xlim=(-1, 1)):
            self.fig_lin = Figure.PlotLine(xlabel=xlabel, ylabel=ylabel, title=title, obs=obs, semilogy=False, sizex=sizex, sizey=sizey, cmap=cmap, norm=norm, cmap_label=cmap_label, xlim=xlim)
            self.fig_log = Figure.PlotLine(xlabel=xlabel, ylabel=ylabel, title=title, obs=obs, semilogy=True, sizex=sizex, sizey=sizey, cmap=cmap, norm=norm, cmap_label=cmap_label, xlim=xlim)

    class Plot2D:
        """A class to plot 2D data (x vs y vs z)"""
        def __init__(self, x=None, y=None, X=None, title="", xlabel="", ylabel="", interp=None):
            self.grid = GridSpec(1, 1)
            self.fig = plt.figure(figsize=(8.5 / 2.54, 6 / 2.54), dpi=300)
            self.grid.update(top=0.9, bottom=0.2, left=0.18, right=0.93)
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.ax = self.fig.add_subplot(self.grid[0])
            self.ax.set_title(title, fontstyle="italic")
            self.ax.set_xlabel(xlabel)
            self.ax.set_ylabel(ylabel)
            self.ax.ticklabel_format(axis="y", style="sci", scilimits=(0,0))
            self.im = plt.imshow(X, aspect="auto", origin="lower", cmap=self.cm, animated=True, extent=(min(x), max(x), min(y), max(y)), interpolation=interp)
            self.cb = self.fig.colorbar(self.im, ax=self.ax)

    class PlotXY:
        """A class to plot xy data"""
        def __init__(self, data, title="", xlabel="", ylabel="", colorcode="index", logx=False):
            self.grid = GridSpec(1, 1)
            self.fig = plt.figure(figsize=(8.5 / 2.54, 6 / 2.54), dpi=300)
            self.grid.update(top=0.9, bottom=0.2, left=0.18, right=0.93)
            self.cm = matplotlib.cm.get_cmap("RdYlBu_r")
            self.norm = Normalize(0, len(data))
            self.lookIds = {"linewidth": 0, "marker": "o", "markersize": 4, "markeredgecolor": "black",
                            "markeredgewidth": 0.2, "alpha": 0.4}
            self.ax = self.fig.add_subplot(self.grid[0])
            self.ax.set_title(title, fontstyle="italic")
            self.ax.set_xlabel(xlabel)
            self.ax.set_ylabel(ylabel)
            self.ax.ticklabel_format(axis="y", style="plain", scilimits=(0,0), useOffset=False)
            if logx is True:
                self.ax.set_xscale("log")
            for idx, val in enumerate(data):
                self.ax.add_line(Line2D(xdata=val[0], ydata=val[1], color=self.cm(self.norm(idx)), **self.lookIds, label=val[2]))
            self.ax.legend()
            self.ax.relim()
            self.ax.autoscale_view()

    class PlotHist:
        """A class to plot a set of observables vs x"""
        def __init__(self, xlabel, ylabel, obs=None):
            self.grid = GridSpec(1, 1)
            self.fig = plt.figure(figsize=(8 / 2.54, 7 / 2.54), dpi=300)
            self.ax = self.fig.add_subplot()
            self.ax.set_xlabel(xlabel)
            self.ax.set_ylabel(ylabel)
            self.axlg = []
            if obs is not None:
                for idx, val in enumerate(obs):
                    color = matplotlib.cm.Paired(idx)
                    self.axlg.append(Line2D(xdata=[0], ydata=[0], color=color, linewidth=2, label=val))
                    self.ax.hist(val, bins=1+3.322*log10(len(obs)))
                self.ax.legend(self.axlg, obs)


