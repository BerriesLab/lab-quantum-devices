import os, math, csv, pandas, numpy as np, warnings, scipy.stats as stats
import matplotlib.pyplot as plt

# Ask user to input files path
sample = "24DdevP"
path = "C:\\Users\\dabe\\Google Drive\\Work\Projects\\2020 - MOF\\Data\\" + sample + "\\"

# Read list of files in folder
data = np.loadtxt(fname=path + "data.txt", dtype=float, delimiter=",", skiprows=1)  # Read file

# Select temperature interval and number of files to avoid back-scan measurements
T_mins = np.linspace(200, 280, 9)    # define the min temperature
T_max = 300                           # define the max temperature
alphas = np.linspace(1E-6, 1, 50)    # Define the alpha-s
r2 = np.zeros([len(alphas), len(T_mins)])    # Define matrix of residuals

# Fit data and calculate residuals for different T_max and alpha
i = 0
for T_min in T_mins:
    data = data[(data[:, 1] >= T_min) & (data[:, 1] <= T_max)]  # select subset of data where Tmin <= T <= Tman
    T = data[:, 1]
    G = data[:, 2]

    # Take the logarithm of G and normalize in the interval 0-1
    lnG = np.log(G)

    j = 0
    for alpha in alphas:
        T_alpha = np.power(T, -alpha)
        r2[j][i] = np.square(stats.linregress(T_alpha, lnG)[2])
        j += 1

    i += 1


plt.plot(alphas, r2, '-')
plt.legend(T_mins)
plt.ylabel("R^2")
plt.xlabel("alpha")
plt.show()

