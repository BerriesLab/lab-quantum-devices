from Objects.Backup.measurement_objects import *

vb = linspace(-1, 1, 21, endpoint=True)               # [1D array] array of dc bias voltage
vg = linspace(-100, 100, 101, endpoint=True)
f = logspace(0, 5, 10)
i_h = array([0, 1, 2])

fig = plt.figure(figsize=(40 / 2.54, 15 / 2.54))
xlim = [f.min(), f.max()]
cm = matplotlib.cm.get_cmap("RdYlBu_r")
norm = Normalize(min(i_h), max(i_h))

ax1 = fig.add_subplot()
ax1.set_xlabel("Frequency (Hz)")
ax1.set_ylabel(r"$i_{\omega_2}$ (A)")
ax1.set_xscale("log")
ax1.set_xlim(xlim)
lines = array((1, 2), dtype=Line2D)
for idx, val in enumerate(i_h):
    ax1.add_line(Line2D(xdata=[None], ydata=[None], color=cm(norm(val)), linewidth=0, label=f"th1 {val}", marker="o", markeredgecolor='black', markeredgewidth=0.2, alpha=0.4))