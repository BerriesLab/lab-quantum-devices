import os, scipy.stats as stats, numpy as np, matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import scipy.constants as c


# USER inputs ------------------------------------------------------------------------
sample = "24DdevP"
path = "C:\\Users\\dabe\\Google Drive\\Work\Projects\\2020 - MOF\\Data\\" + sample + "\\"
Tmax, Tmin = 300, 250   # define max, min temperature of fitting
alpha = 1.0               # define alpha


# Read GT data ------------------------------------------------------------------------
data = np.loadtxt(fname=path + "data.txt", dtype=float, delimiter=",", skiprows=1)  # Read file


fig = plt.figure(constrained_layout=False, figsize=(15/2.54, 18/2.54))
grid = gridspec.GridSpec(2, 1)
axGT = fig.add_subplot(grid[0, 0])
axGT.set_xlabel("1000 / T")
axGT.set_ylabel("lnG")
axr = fig.add_subplot(grid[1, 0])
axr.set_xlabel("1000 / T")
axr.set_ylabel("Residuals")

# Select temperature interval and number of files to avoid back-scan measurements ----------------------------------------------------------

# Initialize Temperature and arrays
# slope = np.zeros(len(alphas))
# intercept = np.zeros(len(alphas))
# rvalue = np.zeros(len(alphas))
# pvalue = np.zeros(len(alphas))
# stderr = np.zeros(len(alphas))

data_fit = data[(data[:, 1] >= Tmin) & (data[:, 1] <= Tmax)]    # select subset of data where Tmin <= T <= Tman

T_fit = np.power(data_fit[:, 1], -alpha)                 # FIT data: (1 / T) ^alpha
lnG_fit = np.log(data_fit[:, 2])                                # FIT data: logarithm of G
slope, intercept, rvalue, pvalue, stderr = stats.linregress(T_fit, lnG_fit)
W = - slope * c.Boltzmann / c.e   # in eV
print(W)

T = np.power(data[:, 1], -alpha)                         # data: (1 / T) ^alpha
lnG = np.log(data[:, 2])                                        # data: logarithm of G



# Plot fit
axGT.plot(1000*T, lnG, 'o', color="black", alpha=0.4)
axGT.plot(1000*T, intercept + slope * T, '--', color="red", alpha=0.4)
axGT.axvline(x=1000/Tmin, color="black", linestyle="--", alpha=0.4)
axr.fill_between(1000*T, (intercept + slope * T) - lnG, 0, facecolor="red", alpha=0.4)
axr.plot(1000*T, (intercept + slope * T) - lnG, color="black", marker="o", alpha=0.4, linewidth=0)
axr.axhline(y=0, color="black", linestyle="--", alpha=0.4)
axr.axvline(x=1000/Tmin, color="black", linestyle="--", alpha=0.4)

plt.show()