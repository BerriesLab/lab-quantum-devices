from numpy import pi, loadtxt, where
from Objects.measurement import FitDoubleSchottkyBarrier
from Objects.measurement import Figure
import matplotlib.pyplot as plt


confidence_band = False
sweep_direction = "-"  # filter forward ("+") or backward ("-") or both (None) traces
phi1 = "Au/C60"
phi2 = "Gr/C60"

data = loadtxt(r"C:\Users\dabe\Desktop\pe\2022-10-27_run23_PE-CC_Stability_up_285.00K_channel_1.dat", skiprows=5)
fig = Figure.PlotLineLinAndLog(xlabel="V (V)", ylabel="I (A)", xlim=(-10, 10))
xdata = data[:, 0]
ydata = data[:, 1]
T = 285
d1 = 50e-6
d2 = 52e-6

# region ----- FILTER DATA -----
print("Filtering data... ", end="")

# keep only data corresponding to the forward (+) or backward (-) sweep
print("Done.")  # endregion

# region ----- FIT DOUBLE SCHOTTKY BARRIER MODEL -----
print("Fitting curve with double Schottky barrier model... ", end="") #design["S1"][name], design["S2"][name]
dsb = FitDoubleSchottkyBarrier(V=xdata, I=ydata, T=T, S1=pi*(d1/2)**2, S2=pi*(d2/2)**2, ideal=False)  # create schottky object
dsb.v1_ini = 1
dsb.v2_ini = 1
dsb.v1_vary = False
dsb.v2_vary = False
dsb.S1_vary = False
dsb.S2_vary = False
weights = where(abs(xdata) >= 8, 1, 0)  # define weights
result = dsb.iv_fit()  # run fit
print(result.fit_report())

look = {"marker":"o", "markersize":5, "markeredgewidth":0.1, "markeredgecolor":"black", "markerfacecolor":"None", "linewidth":0}
fit = dsb.func(xdata, result.params["phi01"], result.params["phi02"], dsb.T_ini, dsb.S1_ini, dsb.S2_ini, result.params["n1"], result.params["n2"], result.params["v1"], result.params["v2"])
fig.fig_lin.ax.plot(xdata, ydata, **look, label="Experimental")
fig.fig_log.ax.plot(xdata, abs(ydata), **look, label="Experimental")
fig.fig_lin.ax.plot(xdata, fit, linestyle="--", color="red", label="Fit")
fig.fig_log.ax.plot(xdata, abs(fit), linestyle="--", color="red", label="Fit")
plt.legend()
plt.show()
