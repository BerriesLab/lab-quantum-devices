import os, scipy.stats as stats, numpy as np, matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


# USER inputs ------------------------------------------------------------------------------------------------------------------------------
sample = "24DdevAbis"
path = "C:\\Users\\dabe\\Google Drive\\Work\Projects\\2020 - MOF\\Data\\" + sample + "\\"
i_filter = np.infty   # filter I-V values where current exceeds i_filter
n_filter = 20         # filter out measurements with IDs higher than n_filter


# Plot -------------------------------------------------------------------------------------------------------------------------------------
fig = plt.figure(constrained_layout=False, figsize=(30/2.54, 20/2.54))  # create figure for temperature plots
gs = gridspec.GridSpec(ncols=2, nrows=2, figure=fig)                    # define grid spacing object
c = cm.RdYlBu_r
norm = matplotlib.colors.Normalize(vmin=200, vmax=300)
axIV = fig.add_subplot(gs[0, 0])
axIV.set_xlabel("Current (A)")
axIV.set_ylabel("Voltage (V)")
axRes = fig.add_subplot(gs[1, 0])
axGT = fig.add_subplot(gs[:, 1])
axGT.set_xlabel(r"1000/T ($K^{-1}$)")
axGT.set_ylabel(r"ln(G)")


# Read list of files in folder -------------------------------------------------------------------------------------------------------------
file_list = os.listdir(path)  # returns list
file_list = [file for file in file_list if (file.endswith(".txt")) and ("data" not in file) and (int(file.split("_")[0]) <= n_filter)]


# Initialize Temperature and Conductance arrays --------------------------------------------------------------------------------------------
T = np.zeros(len(file_list))
G = np.zeros(len(file_list))
N = np.zeros(len(file_list))
slope = np.zeros(len(file_list))
intercept = np.zeros(len(file_list))
rvalue = np.zeros(len(file_list))
pvalue = np.zeros(len(file_list))
stderr = np.zeros(len(file_list))


# Process files (one file per time) --------------------------------------------------------------------------------------------------------
for idx, file in enumerate(file_list):
    N[idx] = int(file.split("_")[0])                        # Extract file number from file name
    T[idx] = float(file.split("_")[2][:-4])                 # Extract file temperature from file name
    data = np.loadtxt(fname=path + "/" + file, dtype=float, delimiter=",", skiprows=9)  # Read file
    I = data[:, 0]                                          # Extract current values
    V = data[:, 1]                                          # Extract voltage values
    index = np.where((I > -i_filter) & (I < i_filter))[0]   # filter out I-V values where I exceeds i_filter
    i = I[index]
    v = V[index]
    slope[idx], intercept[idx], rvalue[idx], pvalue[idx], stderr[idx] = stats.linregress(x=i, y=v)  # Fit I-V
    axIV.plot(i, v, linewidth=0, marker="o", alpha=0.2, color=c(norm(T[idx])))
    axIV.plot(i, intercept[idx] + slope[idx] * i, linestyle="--", alpha=0.5, color=c(norm(T[idx])))
    axRes.fill_between(i, 0, (intercept[idx] + slope[idx] * i) - v, color=c(norm(T[idx])), alpha=0.2)
    axGT.plot(1000/T[idx], np.log(1/slope[idx]), linewidth=0, marker="o", color=c(norm(T[idx])))

np.savetxt(fname=path + "data.txt", X=np.c_[N, T, 1/slope, rvalue, pvalue, stderr],
           header="ID, Temperature (K), Conductance (S), rvalue, pvalue, stderr",
           delimiter=",", comments="")

plt.show()
