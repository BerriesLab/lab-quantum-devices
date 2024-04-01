import os, math, csv, pandas, numpy as np, scipy.stats as stats
import matplotlib.pyplot as plt
import scipy.constants as c


# USER inputs ------------------------------------------------------------------------
sample = "24DdevP"
path = "C:\\Users\\dabe\\Google Drive\\Work\Projects\\2020 - MOF\\Data\\" + sample + "\\"
Tmax, Tmin = 300, 250   # Define the max, min temperature
alphas = np.array([1/4, 1/3, 1/2, 1])    # Define the alpha-s


# Read GT data
data = np.loadtxt(fname=path + "data.txt", dtype=float, delimiter=",", skiprows=1)  # Read file


# Select temperature interval and number of files to avoid back-scan measurements
data = data[(data[:, 1] >= Tmin) & (data[:, 1] <= Tmax)]  # select subset of data where Tmin <= T <= Tman
lnG = np.log(data[:, 2])    # Take the logarithm of G


# Initialize Temperature and arrays
slope = np.zeros(len(alphas))
intercept = np.zeros(len(alphas))
rvalue = np.zeros(len(alphas))
pvalue = np.zeros(len(alphas))
stderr = np.zeros(len(alphas))

index = 0
df = []
for idx, alpha in enumerate(alphas):
    T_alpha = np.power(data[:, 1], -alpha)    # make x axis array
    slope[idx], intercept[idx], rvalue[idx], pvalue[idx], stderr[idx] = stats.linregress(T_alpha, lnG)
    W = - slope[idx] * c.Boltzmann / c.e  # in eV
    print(W)

    # Plot fit
    plt.subplot(3, 4, index+1)
    plt.plot(T_alpha, lnG, 'o')
    plt.plot(T_alpha, intercept[idx] + slope[idx] * T_alpha, '-')
    plt.title(r"T$^{-%s}$" %alpha)
    plt.ylabel("lnG")
    plt.xlabel(r"T$^{-%s}$" %alpha)

    # Plot residuals
    plt.subplot(3, 4, idx+4+1)
    plt.plot(T_alpha, (intercept[idx] + slope[idx] * T_alpha) - lnG, 'x')
    plt.axhline(0)
    plt.ylabel("Residuals")

    # Plot distribution
    plt.subplot(3, 4, idx + 8 + 1)
    qq = stats.probplot((intercept[idx] + slope[idx] * T_alpha) - lnG, dist="norm", plot=plt)
    qq_fit = [qq[1][0]*x + qq[1][1] for x in qq[0][0]]

    index += 1

# np.savetxt(fname=path + "fits.txt", X=np.c_[alpha, slope, rvalue, pvalue, stderr],
#                header="ID, Temperature (K), Conductance (S), rvalue, pvalue, stderr",
#                delimiter=",", comments="")

    #                               "Residuals": residuals,
    #                               "qq_x theoretical": qq[0][0],
    #                               "qq_y experimental": qq[0][1],
    #                               "qq_y Fit": qq_fit})
    # df_output.to_csv(path_output+"alpha_%s.csv"%alpha, index=False, header=True)

plt.show()