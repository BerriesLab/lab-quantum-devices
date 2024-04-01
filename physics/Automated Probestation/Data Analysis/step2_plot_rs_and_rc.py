from scipy.stats import linregress
from matplotlib.lines import Line2D
import matplotlib.colors
import pandas as pd
import matplotlib.pyplot as plt
from Objects.measurement import Figure


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
norm = matplotlib.colors.LogNorm(1e-6, 100e-6)
normbar = matplotlib.colors.LogNorm(1e-6, 100e-6)
sizex = 9.5/2.54
sizey = 7/2.54
plot_rs_vs_vgs = Figure.PlotLine("$V_{GS}$ (V)", "$R_{S}$ (k$\Omega$)", title="$R_S$")
plot_rs_vs_vgs.fig.tight_layout()
plot_rc_vs_vgs = Figure.PlotLine("$V_{GS}$ (V)", "$R_{C}$ (k$\Omega$)", title="$R_C$")
plot_rc_vs_vgs.fig.tight_layout()
plot_rc_rs_vs_vgs = Figure.PlotLine("$V_{GS}$ (V)", "$R_{C}/R_{S}$ (%)", title="$R_C/R_S$")
plot_rc_rs_vs_vgs.fig.tight_layout()
plt.show(block=False)
plt.pause(0.25)


df = pd.read_pickle(f"{main}\data.pkl")
data = pd.DataFrame(data=None, columns=["chip", "material", "date", "vgs", "r_s", "r_s_stderr", "r_c", "r_c_stderr"])

for key, item in df.groupby(["chip", "material", "date", "vgs"]):
    print(f"Fitting {key}... ", end="")
    fit = linregress(item["l"], bias / item["ids"])
    data = data.append({"chip": key[0],
                        "material": key[1],
                        "date": key[2],
                        "vgs": key[3],
                        "r_s": fit.slope*item["w"].unique()[0],
                        "r_s_stderr": fit.stderr*item["w"].unique()[0],
                        "r_c":fit.intercept/2,
                        "r_c_stderr": fit.intercept_stderr/2}, ignore_index=True)
    print("Done.")

for key, item in data.groupby(["chip", "material", "date"]):
    plot_rs_vs_vgs.ax.add_line(Line2D(xdata=item["vgs"], ydata=item["r_s"]/1e3))
    plot_rs_vs_vgs.ax.fill_between(x=item["vgs"], y1=(item["r_s"]-item["r_s_stderr"])/1e3, y2=(item["r_s"]+item["r_s_stderr"])/1e3, alpha=0.3)
    plot_rs_vs_vgs.ax.relim()
    plot_rs_vs_vgs.ax.autoscale_view()
    plot_rs_vs_vgs.fig.tight_layout()
    plt.pause(0.1)
    plot_rc_vs_vgs.ax.add_line(Line2D(xdata=item["vgs"], ydata=item["r_c"]/1e3))
    plot_rc_vs_vgs.ax.fill_between(x=item["vgs"], y1=(item["r_c"]-item["r_c_stderr"])/1e3, y2=(item["r_c"]+item["r_c_stderr"])/1e3, alpha=0.3)
    plot_rc_vs_vgs.ax.relim()
    plot_rc_vs_vgs.ax.autoscale_view()
    plot_rc_vs_vgs.fig.tight_layout()
    plt.pause(0.1)
    plot_rc_rs_vs_vgs.ax.add_line(Line2D(xdata=item["vgs"], ydata=100*item["r_c"]/item["r_s"]))
    plot_rc_rs_vs_vgs.ax.relim()
    plot_rc_rs_vs_vgs.ax.autoscale_view()
    plot_rc_rs_vs_vgs.fig.tight_layout()
    plt.pause(0.1)

data.to_csv(f"{main}\data resistance.csv", index=False)
plot_rs_vs_vgs.fig.tight_layout()
plot_rs_vs_vgs.fig.savefig(rf"{main}\r_s.tiff")
plot_rc_vs_vgs.fig.tight_layout()
plot_rc_vs_vgs.fig.savefig(rf"{main}\r_c.tiff")
plot_rc_rs_vs_vgs.fig.tight_layout()
plot_rc_rs_vs_vgs.fig.savefig(rf"{main}\r_c_r_s.tiff")
plt.show()
