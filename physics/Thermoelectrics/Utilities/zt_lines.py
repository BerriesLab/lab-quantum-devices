import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import *
from matplotlib import ticker, cm
import matplotlib.colors
from matplotlib.lines import Line2D
import matplotlib.ticker as mtick


# collect iso lines
with open(r"C:\Users\dabe\Google Drive\Work\Projects\2021 - Review - Charge Transport in Doped Systems\data_dorothea.csv", "r") as file:
    lines = file.readlines()
    doro_zt = np.array([1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1e0, 1e1])
    doro_iso = []
    doro_sigma = np.zeros(len(lines[1:]))
    doro_alpha = np.zeros((len(lines[1:]), 7))
    for idx, line in enumerate(lines[1:]):
        data = np.array([float(x) for x in line.split(",")])
        doro_sigma[idx] = data[0]
        doro_alpha[idx, :] = data[1:]
    for idx in range(len(doro_zt)):
        doro_iso.append(np.c_[doro_sigma, doro_alpha[:, idx]])

data_doro = np.zeros(shape=(len(doro_sigma), len(doro_alpha[:, 0])))
for i in range(len(doro_sigma)):
    for k in range(len(doro_alpha[0, :])):
        for j in range(len(doro_alpha[:, k])):
            data_doro[i, j] = doro_zt[k]

T = 300  # K
Lambda1 = 0.5 * e
Lambda2 = 0.05 * e
kappa_ph = 0.2  # W / m K
sigma = np.logspace(0, 6, 100)  # S / m
alpha = np.logspace(-6, -2, 100)  # V / K
ss, aa = np.meshgrid(sigma, alpha)


def wf(sigma, T):
    L = (pi ** 2 / 3) * (Boltzmann / e) ** 2
    kappa_el = sigma * L * T
    return kappa_el


def mwf(sigma, Lambda):
    kappa_el = sigma * (Boltzmann / e) ** 2 * (Lambda / Boltzmann)
    return kappa_el


kappa_wf = wf(ss, T) + kappa_ph
zt_wf = aa ** 2 * ss * T / kappa_wf

kappa_mwf1 = mwf(ss, Lambda1) + kappa_ph
zt_mwf1 = aa ** 2 * ss * T / kappa_mwf1

kappa_mwf2 = mwf(ss, Lambda2) + kappa_ph
zt_mwf2 = aa ** 2 * ss * T / kappa_mwf2

cmap = cm.afmhot
norm = matplotlib.colors.LogNorm(vmin=doro_zt.min(), vmax=doro_zt.max()*1000000)
coll1 = plt.contour(ss, aa, zt_wf, locator=ticker.LogLocator(), levels=doro_zt).collections
coll2 = plt.contour(ss, aa, zt_mwf1, locator=ticker.LogLocator(), levels=doro_zt).collections
coll3 = plt.contour(ss, aa, zt_mwf2, locator=ticker.LogLocator(), levels=doro_zt).collections

fig = plt.figure(figsize=(18 / 2.54, 12 / 2.54))
grid = matplotlib.gridspec.GridSpec(nrows=1, ncols=10)
ax = fig.add_subplot(grid[:, 0:7])
axbar = fig.add_subplot(grid[:, 9:10])
axbar.xaxis.set_visible(False)
axbar.yaxis.set_visible(False)
axbar.axis("off")
grid.update(wspace=1, hspace=0)

for idx in range(len(coll1)):
    p = coll1[idx].get_paths()[0].vertices
    x = p[:, 0]
    y = p[:, 1]
    ax.plot(x, y, linestyle="-", c=cmap(norm(doro_zt[idx])), linewidth=2, alpha=0.5, label=f"Wiedamann-Franz, zT = {doro_zt[idx]}")

for idx in range(len(coll2)):
    p = coll2[idx].get_paths()[0].vertices
    x2 = p[:, 0]
    y2 = p[:, 1]
    ax.plot(x2, y2, linestyle="--", c=cmap(norm(doro_zt[idx])), alpha=0.5, label=f"Crave et al., lambda = 0.5 eV, zT = {doro_zt[idx]}")

for idx in range(len(coll3)):
    p = coll3[idx].get_paths()[0].vertices
    x3 = p[:, 0]
    y3 = p[:, 1]
    ax.plot(x3, y3, linestyle="-.", c=cmap(norm(doro_zt[idx])), alpha=0.5, label=f"Crave et al., lambda=0.05 eV, zT = {doro_zt[idx]}")

for idx, iso in enumerate(doro_iso):
    x = iso[:, 0]
    y = iso[:, 1]
    ax.plot(x, y, linestyle=":", c=cmap(norm(doro_zt[idx])), alpha=0.5, label=f"Scheunemann et al., zT = {doro_zt[idx]}")

idx2 = np.where(x2>100)
x2 = x2[idx2]
y2 = y2[idx2]

ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlabel("$\sigma$ (S / m)", fontsize=12)
ax.set_ylabel(r"$|\alpha|$ ($V / K$)", fontsize=12)
ax.set_xlim([1e1, 1e6])
ax.set_ylim([1e-6, 1e-2])
ax.tick_params(axis="both", labelsize=12)


custom_lines = [Line2D([0], [0], color="grey", lw=2, linestyle="-"),
                Line2D([0], [0], color="grey", lw=2, linestyle="--"),
                Line2D([0], [0], color="grey", lw=2, linestyle="-."),
                Line2D([0], [0], color="grey", lw=2, linestyle=":")]
ax.legend(custom_lines, ["Wiedemann-Franz", "Crave et al., $\lambda=0.5$ eV", "Crave et al., $\lambda=0.05$ eV", "Scheunemann et al."], loc="lower left", fontsize=10)

custom_levels = [Line2D([0], [0], color=cmap(norm(1e1)), lw=4),
                 Line2D([0], [0], color=cmap(norm(1e0)), lw=4),
                 Line2D([0], [0], color=cmap(norm(1e-1)), lw=4),
                 Line2D([0], [0], color=cmap(norm(1e-2)), lw=4),
                 Line2D([0], [0], color=cmap(norm(1e-3)), lw=4),
                 Line2D([0], [0], color=cmap(norm(1e-4)), lw=4),
                 Line2D([0], [0], color=cmap(norm(1e-5)), lw=4)]
# axbar.legend(custom_levels, reversed(doro_zt), loc="right", title="iso-zT lines", fontsize=12)
f = mtick.ScalarFormatter(useOffset=False, useMathText=True)
text = ["${}$".format(f._formatSciNotation("%e" % x)) for x in reversed(doro_zt)]
#func = ["{}".format(f._formatSciNotation('%1.10e' % x) for x in reversed(doro_zt))]
axbar.legend(custom_levels, text, loc="right", title="iso-zT lines", fontsize=12)
plt.show()

data = [] #np.zeros([28, 2, 200])
# print(len(ax.lines[0].get_data()[0]))
dir = r"C:\Users\dabe\Google Drive\Work\Projects\2021 - Review - Charge Transport in Doped Systems\export\\"
for idx, line in enumerate(ax.lines):
    temp = np.transpose(line.get_data())
    print(ax.lines[idx].get_label())
    np.savetxt(fname=f"{dir}{ax.lines[idx].get_label()}.csv", X=temp, delimiter=",", header="sigma (S/m), alpha (V/K)")
    # print(data)

