import matplotlib.pyplot as plt
import os
import numpy as np

# region ----- User input -----
os.chdir(r"D:\My Drive\Work\Projects\2020 - TeTra\Experimental\Reference spectra")
ref_files = ["emimi2", "toluene2", "hexane2", "methanol2", "oleic_acid2"]   # list of compounds
spectrum_type = "raman"             # type of spectrum to plot: raman, ir_atr, ir_trans
xlims = [1000, 3500]
# endregion


for ref_file in ref_files:
    filename = ref_file + "_" + spectrum_type + ".csv"
    if os.path.isfile(filename):
        print("Loading: {}".format(filename))
        data = np.loadtxt(filename, delimiter=",")
        # lower_bound = np.min(data[:, 1])
        plt.plot(data[:, 0], data[:, 1], label=ref_file)
        plt.fill_between(data[:, 0], data[:, 1], 0, alpha=0.1)
    else:
        print("Cannot find: {}".format(filename))

plt.xlabel("Raman stokes ($cm^{-1}$)")
plt.ylabel("Intensity (a.u.)")
# plt.axvline(1252, c="black", linestyle="--")
plt.axvline(3132, c="black", linestyle="--")
plt.legend()
plt.xlim(xlims)
plt.show()
