# region ----- Import packages -----
import matplotlib.pyplot as plt
import matplotlib.colors
import matplotlib.gridspec
import matplotlib.cm
from matplotlib.lines import Line2D
import pickle
import os
import numpy as np
# endregion

# region ----- USER inputs -----
main = "C:\\Users\\dabe\\Google Drive\\Work\\Projects\\2019 - QuIET\\Experimental\\Data"    # [string] Main folder directory
chip = ["tepb02"]  # [list of strings] pass an empty list to load all chips
device = ["h5"]  # [list of strings] pass an empty list to load all devices
experiment = 1  # [int] select experiment between "3 terminal vds sweep" (0) and "3 terminal vgs sweep" (1)
# experiment = "3 terminal vgs sweep"  # "3 terminal fet vgs sweep"
what_to_plot = ["ids", "igs"]  # [string] "ids" and/or "igs"
what_to_colorcode = "vds"  # select between "vds", "vgs", "environment", "time", "device", "channel", "illumination"
filter_material = []
filter_vgs = []
filter_vds = [1]
filter_environment = ["vacuum"]
filter_illumination = ["dark"]
filter_vds_delay = []  # [float] select only measurement with vgs delay (in ms)
filter_vgs_delay = []  # [float] select only measurement with vgs delay (in ms)
filter_channel = []  # [string] select only devices with channel length (in um)
vds_lims = [-10, 10]
vgs_lims = [-100, 100]

keywargs_ds = {"linewidth": 2, "linestyle": "-", "markersize": 0, "marker": "o", "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.6}
keywargs_gs = {"linewidth": 2, "linestyle": "--", "markersize": 0, "marker": "D", "markeredgecolor": "black", "markeredgewidth": 0.2, "alpha": 0.6}
c = matplotlib.cm.get_cmap("Set1")
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
materials = []
illuminations = []
environments = []
channels = []
dates = []
iter_min, iter_max = +np.inf, -np.inf
vgs_min, vgs_max = +np.inf, -np.inf
vds_min, vds_max = +np.inf, -np.inf
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
        path = main + "\\" + x + "\\" + y + "\\3 terminal fet"
        if os.path.exists(path):
            os.chdir(path)
            files = [item for item in os.listdir() if item.endswith(".bin")]
            for file in files:
                with open(file, "rb") as f:
                    temp = pickle.load(f)
                if (temp["experiment"] == experiment) and \
                        (temp["environment"] in filter_environment if len(filter_environment) > 0 else True) and \
                        (temp["settings"]["smu vds delay"] in filter_vds_delay if len(filter_vds_delay) > 0 else True) and \
                        (temp["settings"]["smu vgs delay"] in filter_vds_delay if len(filter_vds_delay) > 0 else True) and \
                        (temp["illumination"] in filter_illumination if len(filter_illumination) > 0 else True) and \
                        (temp["material"] in filter_material if len(filter_material) > 0 else True) and \
                        (temp["channel length"] in filter_channel if len(filter_channel) > 0 else True):
                    print("Loading file: {}... ".format(file), end="")
                    data.append(temp)
                    if temp["material"] not in materials:
                        materials.append(temp["material"])
                    if temp["illumination"] not in illuminations:
                        illuminations.append(temp["illumination"])
                    if temp["environment"] not in environments:
                        environments.append(temp["environment"])
                    if temp["channel length"] not in channels:
                        channels.append(temp["channel length"])
                    if temp["date"] not in dates:
                        dates.append(temp["date"].timestamp())
                    if temp["data"][:, :, 2].max() > vgs_max:
                        vgs_max = temp["data"][:, :, 2].max()
                    if temp["data"][:, :, 2].min() < vgs_min:
                        vgs_min = temp["data"][:, :, 2].min()
                    if temp["data"][:, :, 0].max() > vds_max:
                        vds_max = temp["data"][:, :, 2].max()
                    if temp["data"][:, :, 0].min() < vds_min:
                        vds_min = temp["data"][:, :, 2].min()
                    if temp["data"].shape[2] > 4 and temp["data"][:, :, 4].max() > iter_max:
                        iter_max = temp["data"][:, :, 4].max()
                    if temp["data"].shape[2] > 4 and temp["data"][:, :, 4].min() < iter_min:
                        iter_min = temp["data"][:, :, 4].min()
                    print("Done.")
print("{} experiments loaded.".format(len(data)))
# endregion

# region ----- Initialize figure -----
fig = plt.figure(figsize=(30 / 2.54, 15 / 2.54))
grid = matplotlib.gridspec.GridSpec(nrows=1, ncols=15)
fig.suptitle(f"""Chip: {', '.join([x for x in chip])}
Device: {', '.join([x for x in device])}
Material: {', '.join([x for x in materials])}
$V_{{gs}}$ = {', '.join([str(x) + " V" for x in filter_vgs])}, $V_{{ds}}$ = {', '.join([str(x) + " V" for x in filter_vds])}
Environment: {', '.join([x for x in filter_environment])} 
Illumination: {', '.join([x for x in filter_illumination])}""", fontsize=10)
grid.update(top=0.78, wspace=1, hspace=0)
# ------------------------------------
ax1_lin = fig.add_subplot(grid[0, 0:6])
ax3_log = fig.add_subplot(grid[0, 7:13])
if experiment == 0 or experiment == "3 terminal vds sweep" or experiment == "3 terminal fet vds sweep":
    ax1_lin.set_xlabel("$V_{ds}$ (V)")
    ax1_lin.set_ylabel("$I$ (A)")
    ax1_lin.set_xlim(vds_lims)
    ax3_log.set_xlabel("$V_{ds}$ (V)")
    ax3_log.set_ylabel("$I$ (A)")
    ax3_log.set_xlim(vds_lims)
if experiment == 1 or experiment == "3 terminal vgs sweep" or experiment == "3 terminal fet vgs sweep":
    ax1_lin.set_xlabel("$V_{gs}$ (V)")
    ax1_lin.set_ylabel("$I$ (A)")
    ax1_lin.set_xlim(vgs_lims)
    ax3_log.set_xlabel("$V_{gs}$ (V)")
    ax3_log.set_ylabel("$I$ (A)")
    ax3_log.set_xlim(vgs_lims)
# ------------------------------------
norm_vgs = matplotlib.colors.Normalize(vmin=vgs_min, vmax=vgs_max)
norm_vds = matplotlib.colors.Normalize(vmin=vds_min, vmax=vds_max)
norm_time = matplotlib.colors.Normalize(vmin=min(dates), vmax=max(dates))
norm_chan = matplotlib.colors.Normalize(vmin=min(channels), vmax=max(channels))
norm_iter = matplotlib.colors.Normalize(vmin=iter_min, vmax=iter_max)
dict_env = dict(zip(environments, np.linspace(0, 1, len(environments))))
norm_env = matplotlib.colors.Normalize(vmin=0, vmax=len(environments))
dict_ill = dict(zip(illuminations, np.linspace(0, 1, len(illuminations))))
norm_ill = matplotlib.colors.Normalize(vmin=0, vmax=len(dict_ill))
dict_mat = dict(zip(materials, np.linspace(0, 1, len(materials))))
norm_mat = matplotlib.colors.Normalize(vmin=0, vmax=len(materials))
# endregion

# region ----- Plot -----
for x in data:

    if experiment == 0 or experiment == "3 terminal vds sweep" or experiment == "3 terminal fet vds sweep":

        for i in range(x["data"].shape[0]):

            if all(x["data"][i, k, 2] in filter_vgs for k in range(len(x["data"][i, :, 2]))) if len(filter_vgs) > 0 else True:

                if what_to_colorcode == "vgs":
                    keywargs_ds["color"] = c(norm_vgs(x["data"][i, 0, 0]))
                    keywargs_ds["markerfacecolor"] = c(norm_vgs(x["data"][i, 0, 0]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "vds":
                    keywargs_ds["color"] = c(norm_vds(x["data"][i, 0, 2]))
                    keywargs_ds["markerfacecolor"] = c(norm_vds(x["data"][i, 0, 2]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "environment":
                    keywargs_ds["color"] = c(norm_env(dict_env[x["environment"]]))
                    keywargs_ds["markerfacecolor"] = c(norm_env(dict_env[x["environment"]]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "illumination":
                    keywargs_ds["color"] = c(norm_ill(dict_ill[x["illumination"]]))
                    keywargs_ds["markerfacecolor"] = c(norm_ill(dict_ill[x["illumination"]]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "time":
                    keywargs_ds["color"] = c(norm_time(x["date"].timestamp()))
                    keywargs_ds["markerfacecolor"] = c(norm_time(x["date"].timestamp()))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "device":
                    exit("Not implemented yet.")
                if what_to_colorcode == "channel":
                    keywargs_ds["color"] = c(norm_chan(x["channel length"]))
                    keywargs_ds["markerfacecolor"] = c(norm_chan(x["channel length"]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "material":
                    keywargs_ds["color"] = c(norm_mat(dict_mat[x["material"]]))
                    keywargs_ds["markerfacecolor"] = c(norm_mat(dict_mat[x["material"]]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "material":
                    keywargs_ds["color"] = c(norm_mat(dict_mat[x["material"]]))
                    keywargs_ds["markerfacecolor"] = c(norm_mat(dict_mat[x["material"]]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]

                if "ids" in what_to_plot:
                    ax1_lin.plot(x["data"][i, :, 0], x["data"][i, :, 1], **keywargs_ds)
                    ax3_log.semilogy(x["data"][i, :, 0], abs(x["data"][i, :, 1]), **keywargs_ds)

                if "igs" in what_to_plot:
                    ax1_lin.plot(x["data"][i, :, 0], x["data"][i, :, 3], **keywargs_gs)
                    ax3_log.semilogy(x["data"][i, :, 0], abs(x["data"][i, :, 3]), **keywargs_gs)

    if experiment == 1 or experiment == "3 terminal vgs sweep" or experiment == "3 terminal fet vgs sweep":

        for i in range(x["data"].shape[1]):

            if all(x["data"][k, i, 0] in filter_vds for k in range(len(x["data"][:, i, 0]))) if len(filter_vds) > 0 else True:

                if what_to_colorcode == "vgs":
                    keywargs_ds["color"] = c(norm_vgs(x["data"][0, i, 0]))
                    keywargs_ds["markerfacecolor"] = c(norm_vgs(x["data"][0, i, 0]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "vds":
                    keywargs_ds["color"] = c(norm_vds(x["data"][0, i, 2]))
                    keywargs_ds["markerfacecolor"] = c(norm_vds(x["data"][0, i, 2]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "environment":
                    keywargs_ds["color"] = c(norm_env(dict_env[x["environment"]]))
                    keywargs_ds["markerfacecolor"] = c(norm_env(dict_env[x["environment"]]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "illumination":
                    keywargs_ds["color"] = c(norm_ill(dict_ill[x["illumination"]]))
                    keywargs_ds["markerfacecolor"] = c(norm_ill(dict_ill[x["illumination"]]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "time":
                    keywargs_ds["color"] = c(norm_time(x["date"].timestamp()))
                    keywargs_ds["markerfacecolor"] = c(norm_time(x["date"].timestamp()))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "device":
                    exit("Not implemented yet.")
                if what_to_colorcode == "channel":
                    keywargs_ds["color"] = c(norm_chan(x["channel length"]))
                    keywargs_ds["markerfacecolor"] = c(norm_chan(x["channel length"]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "material":
                    keywargs_ds["color"] = c(norm_mat(dict_mat[x["material"]]))
                    keywargs_ds["markerfacecolor"] = c(norm_mat(dict_mat[x["material"]]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]
                if what_to_colorcode == "material":
                    keywargs_ds["color"] = c(norm_mat(dict_mat[x["material"]]))
                    keywargs_ds["markerfacecolor"] = c(norm_mat(dict_mat[x["material"]]))
                    keywargs_gs["color"] = keywargs_ds["color"]
                    keywargs_gs["markerfacecolor"] = keywargs_ds["markerfacecolor"]

                if "ids" in what_to_plot:
                    ax1_lin.plot(x["data"][:, i, 2], x["data"][:, i, 1], **keywargs_ds)
                    ax3_log.semilogy(x["data"][:, i, 2], abs(x["data"][:, i, 1]), **keywargs_ds)

                if "igs" in what_to_plot:
                    ax1_lin.plot(x["data"][:, i, 2], x["data"][:, i, 3], **keywargs_gs)
                    ax3_log.semilogy(x["data"][:, i, 2], abs(x["data"][:, i, 3]), **keywargs_gs)
# endregion

# region ----- Add legends -----
custom_lines2 = [Line2D([0], [0], color="black", lw=2, linestyle="-"), Line2D([0], [0], color="black", lw=2, linestyle="--")]
legend2 = ax3_log.legend(custom_lines2, ["$I_{ds}$", "$I_{gs}$"], bbox_to_anchor=(1.05, 1), loc="upper left", title="Legend")
ax3_log.add_artist(legend2)
if what_to_colorcode == "channel":
    custom_lines1 = [Line2D([0], [0], color=c(norm_chan(x)), lw=4) for x in filter_channel]
    legend1 = ax3_log.legend(custom_lines1, [str(x) + " $\mu$m" for x in filter_channel], bbox_to_anchor=(1.05, 1), loc="upper left", title="Channel length")
    ax3_log.add_artist(legend1)
if what_to_colorcode == "environment":
    custom_lines1 = [Line2D([0], [0], color=c(norm_env(dict_env[x])), lw=4) for x in filter_environment]
    legend1 = ax3_log.legend(custom_lines1, [x for x in filter_environment], bbox_to_anchor=(1.05, 1), loc="upper left", title="Environment")
    ax3_log.add_artist(legend1)
if what_to_colorcode == "material":
    custom_lines1 = [Line2D([0], [0], color=c(norm_mat(dict_mat[x])), lw=4) for x in materials]
    legend1 = ax3_log.legend(custom_lines1, [x for x in materials], bbox_to_anchor=(1.05, 1), loc="upper left", title="Material")
    ax3_log.add_artist(legend1)
# endregion

plt.show()