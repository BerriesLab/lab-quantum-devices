import matplotlib.colors
import pandas as pd
import matplotlib.pyplot as plt
from Objects.measurement import Figure
from numpy import gradient, floor, linspace
from scipy.signal import savgol_filter
from scipy.constants import epsilon_0
from scipy.stats import norm
import matplotlib.cm


main = r"C:\Data\automated probestation\osja_gfet04_gr_p5"
overwrite = True
architecture = "gfet06"

w = 5e-6
bias = 50e-3
sweep_dir = 1  # "bkw"
smooth_window = 20/100  # [float] windon to smooth (in % of array lenght)
smooth_order = 3        # [int] order of the polynomial used to smooth
epsilon_r = 3.9
oxide_thickness = 285e-9  # 330e-9

linestyle = {"markersize": 0, "linewidth": 1, "alpha": 0.6}
matplotlib.rcParams.update({'font.size': 8})
cmap = matplotlib.cm.get_cmap("coolwarm")
cmap_label = "$L_{CH}$ (m)"
normbar = matplotlib.colors.LogNorm(1e-6, 100e-6)
sizex = 9.5/2.54
sizey = 7/2.54
plot_dirac = Figure.PlotLine("$V_{DIRAC}$ (V)", "Count", title="$Dirac$")
plot_dirac.fig.tight_layout()
plot_mu_e = Figure.PlotLine("$\mu_e$ ($cm^{2}V{^-1}s{-1}$)", "Count", title="$\mu_e$")
plot_mu_e.fig.tight_layout()
plot_mu_h = Figure.PlotLine("$\mu_h$ ($cm^{2}V{^-1}s{-1}$)", "Count", title="$\mu_h$")
plot_mu_h.fig.tight_layout()
plt.show(block=False)
plt.pause(0.25)

def capacitance(e0, er, t):
    return e0 * er / t

def mu(l, w, c, bias, di_dv_max):
    return l / (w * c * bias) * di_dv_max

df = pd.read_pickle(f"{main}\data.pkl")
data = pd.DataFrame(data=None, columns=["chip", "device", "material", "date", "l", "dirac", "mu_e", "mu_h"])


for key, item in df.groupby(["chip", "device", "material", "date", "l", "w"]):
    print(f"{key}... ", end="")

    dirac = item["vgs"][item["ids"] == min(item["ids"])].values[0]
    l = key[4]
    w = key[5]
    c = capacitance(epsilon_0, epsilon_r, oxide_thickness)
    y = savgol_filter(item["ids"], int(2 * floor(smooth_window * len(item["vgs"]) / 2) + 1), smooth_order)
    dy_dvgs = abs(gradient(y, item["vgs"]))
    mu_e = mu(key[4], key[5], c, bias, max(dy_dvgs[item["vgs"]>dirac]))
    mu_h = mu(key[4], key[5], c, bias, max(dy_dvgs[item["vgs"]<dirac]))
    data = data.append({"chip": key[0],
                        "device": key[1],
                        "material": key[2],
                        "date": key[3],
                        "l": key[4],
                        "w": key[5],
                        "dirac": dirac,
                        "mu_e": mu_e,
                        "mu_h": mu_h}, ignore_index=True)
    print("Done.")

for key, item in data.groupby(["chip", "material", "date"]):
    print(f"{key}... ", end="")
    hist = plot_dirac.ax.hist(item["dirac"].values, edgecolor='black', linewidth=0.5, range=(-50, 50), bins=51, alpha=0.6, label=key)
    mu, std = norm.fit(item["dirac"].values)
    x = linspace(-50, 50, 100)
    p = norm.pdf(x, mu, std)
    plot_dirac.ax.plot(x, max(hist[0])/max(p)*p, linewidth=1.5)
    plot_dirac.ax.relim()
    plot_dirac.ax.autoscale_view()
    plot_dirac.fig.canvas.draw()
    hist = plot_mu_e.ax.hist(1e4*item["mu_e"].values, edgecolor='black', linewidth=0.5, bins=51, alpha=0.6, label=key)
    mu, std = norm.fit(item["mu_e"].values)
    x = linspace(plot_mu_e.ax.get_xlim()[0], plot_mu_e.ax.get_xlim()[1], 100)
    p = norm.pdf(x, 1e4*mu, 1e4*std)
    plot_mu_e.ax.plot(x, max(hist[0])/max(p)*p, linewidth=1.5)
    plot_mu_e.ax.relim()
    plot_mu_e.ax.autoscale_view()
    plot_mu_e.fig.canvas.draw()
    hist = plot_mu_h.ax.hist(1e4*item["mu_h"].values, edgecolor='black', linewidth=0.5, bins=51, alpha=0.6, label=key)
    mu, std = norm.fit(item["mu_h"].values)
    x = linspace(plot_mu_h.ax.get_xlim()[0], plot_mu_h.ax.get_xlim()[1], 100)
    p = norm.pdf(x, 1e4*mu, 1e4*std)
    plot_mu_h.ax.plot(x, max(hist[0])/max(p)*p, linewidth=1.5)
    plot_mu_h.ax.relim()
    plot_mu_h.ax.autoscale_view()
    plot_mu_h.fig.canvas.draw()
print(data)

data.to_csv(f"{main}\data stats.csv", index=False)
plot_dirac.fig.tight_layout()
plot_dirac.fig.savefig(f"{main}\hist dirac.tiff")
plot_mu_e.fig.savefig(f"{main}\hist mu_e.tiff")
plot_mu_h.fig.savefig(f"{main}\hist mu_h.tiff")

plt.show()
