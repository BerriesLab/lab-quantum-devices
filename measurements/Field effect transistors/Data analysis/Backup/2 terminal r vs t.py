# region ----- Import packages -----
import matplotlib.pyplot as plt
import matplotlib.gridspec
import matplotlib.cm
import pickle
import os
# endregion

# region ----- USER inputs -----
main = "C:\\Users\\dabe\\Google Drive\\Work\\Projects\\2020 - TeTra\\Experimental\\Data"    # [string] Main folder directory
chip = ["f003"]                 # [list of strings] pass an empty list to load all chips
device = ["g-2um"]                     # [list of strings] pass an empty list to load all devices
what_to_select = ["air"]
ms = 6                          # [float] markersize
# endregion

# region ----- Look for cwd -----
try:
    os.chdir(main)
    print("{} ... found.".format(main))
except OSError:  # if path does not exists
    exit("{} ... not found. Terminating program.".format(main))
print("Current working directory set to: {}".format(os.getcwd()))
# endregion

# region ----- Load bin files in memory -----
data = []
if not chip:
    temp1 = [item for item in os.listdir(main) if os.path.isdir(main)]
else:
    temp1 = chip
for x in temp1:
    path = main + "\\" + x
    os.chdir(path)
    if not device:
        temp2 = [item for item in os.listdir(main + "\\" + x)]
    else:
        temp2 = device
    for y in temp2:
        path = main + "\\" + x + "\\" + y + "\\2 terminal r vs t"
        if os.path.exists(path):
            os.chdir(path)
            files = [item for item in os.listdir() if item.endswith(".bin")]
            for file in files:
                with open(file, "rb") as f:
                    temp = pickle.load(f)
                if (temp["experiment"] == "2 terminal r vs t") and (temp["environment"] in what_to_select):
                    print("Loading file: {}... ".format(file), end="")
                    data.append(temp)
                    print("Done.")
print("{} experiments loaded.".format(len(data)))
# endregion

# region ----- Initialize figure -----
# ------------------------------------
plt.ion()
fig = plt.figure(figsize=(30 / 2.54, 15 / 2.54))
grid = matplotlib.gridspec.GridSpec(nrows=1, ncols=2)
fig.suptitle("Chip: {}. Device: {}.".format("all" if not chip else chip, "[all]" if not device else device), fontsize=12)
grid.update(wspace=0.4, hspace=2)
# ------------------------------------
ax1_lin = fig.add_subplot(grid[0, 0])
ax1_lin.set_xlabel("Time (min)")
ax1_lin.set_ylabel("R ($\Omega$)")
# ------------------------------------
ax3_log = fig.add_subplot(grid[0, 1])
ax3_log.set_xlabel("Time (min)")
ax3_log.set_ylabel("R ($\Omega$)")
# ------------------------------------
# endregion

for x in data:

    ax1_lin.plot(x["data"][:, 0]/60, x["data"][:, 1], linewidth=0, marker="o", markerfacecolor="grey", markeredgecolor="black", alpha=0.5)
    ax3_log.semilogy(x["data"][:, 0]/60, abs(x["data"][:, 1]), linewidth=0, marker="o", markerfacecolor="grey", markeredgecolor="black", alpha=0.5)

plt.ioff()
plt.show()