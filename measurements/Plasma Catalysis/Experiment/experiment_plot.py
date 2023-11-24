import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

folder_main = "C:/Users/Berri/Google Drive/Projects/Plasma Catalysis/Experimental/CCP/" #Main directory
folder_catalyst = "SS 316L/" #Folder of the catalyst
folder_experiment = "Experiment 02/" #Folder of the experiment
file_dir = folder_main + folder_catalyst + folder_experiment #Current folder
df = pd.read_csv(file_dir + "experiment_" + folder_experiment[-3:-1] + ".csv")

#Choose type of plot and y_limits
# 1: eta_vs_power
# 2: eta_vs_position
plot_type = 1
y_limits = [-0.5, 10]

# Create figure
length = 18 #cm
height = 18/2.5 #cm
figsize = (length/2.54, height/2.54) #px, py = w*dpi, h*dpi  # pixels 300*16/2.54
fig = plt.figure(figsize=figsize, dpi=100) #My screen is 120 dpi
fig.subplots_adjust(left=0.1, right=0.84,top=0.9,bottom=0.18,wspace=0.25)
plt.rc("font", size=8, family="Arial")
plt.rc("axes", titlesize=8)
plt.rc("axes", labelsize=8)
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
plt.rc('legend', fontsize=8)
symbols = ["o","v","s","^","<",">","D"]

#Define figure properties depending on the plot type
if plot_type == 1:
    a = "Power"
    b = "Position"
    x_label = "Power (W)"
    y_label = "$\eta_{N_2} (\%)$"
    legend_title = "Position (in)"
    figure_file_name = "eta vs power"
    x_limits = [-5, 80]
elif plot_type == 2:
    a = "Position"
    b = "Power"
    x_label = "Position (in)"
    y_label = "$\eta_{N_2} (\%)$"
    legend_title = "Power (W)"
    figure_file_name = "eta vs position"
    x_limits = [-7, 7]

ax1 = fig.add_subplot(1,3,1)
ax1.set_title("0.5 Torr")
ax1.set_xlim(x_limits)
ax1.set_xlabel(x_label)
ax1.set_ylim(y_limits)
ax1.set_ylabel(y_label)
ax1.tick_params(axis="both", which="both",direction="in",length=3)
ax2 = fig.add_subplot(1,3,2)
ax2.set_title("1 Torr")
ax2.set_xlim(x_limits)
ax2.set_xlabel(x_label)
ax2.set_ylim(y_limits)
#ax2.set_ylabel(y_label)
ax2.tick_params(axis="both", which="both",direction="in",length=3)
ax3 = fig.add_subplot(1,3,3)
ax3.set_title("2 Torr")
ax3.set_xlim(x_limits)
ax3.set_xlabel(x_label)
ax3.set_ylim(y_limits)
#ax3.set_ylabel(y_label)
ax3.tick_params(axis="both", which="both",direction="in",length=3)

for n,val in enumerate(np.sort(df[b].unique())):
    x=df[(df["Pressure"]==0.5)&(df[b]==val)][a].values
    y=df[(df["Pressure"]==0.5)&(df[b]==val)]["eta_N2 mean"].values
    yerr=df[(df["Pressure"]==0.5)&(df[b]==val)]["eta_N2 std"].values
    xerr = 0.2
    ax1.errorbar(x=x, y=y, yerr=yerr, xerr=xerr, linewidth=1, elinewidth=1, capsize=5, marker=symbols[n],markersize=8, alpha=0.5)

for n,val in enumerate(np.sort(df[b].unique())):
    x = df[(df["Pressure"] == 1.0) & (df[b] == val)][a].values
    y = df[(df["Pressure"] == 1.0) & (df[b] == val)]["eta_N2 mean"].values
    yerr = df[(df["Pressure"] == 1.0) & (df[b] == val)]["eta_N2 std"].values
    xerr = 0.2
    ax2.errorbar(x=x, y=y, yerr=yerr, xerr=xerr,linewidth=1, elinewidth=1, capsize=5, marker=symbols[n],markersize=8, alpha=0.5)

for n, val in enumerate(np.sort(df[b].unique())):
    x = df[(df["Pressure"] == 2.0) & (df[b] == val)][a].values
    y = df[(df["Pressure"] == 2.0) & (df[b] == val)]["eta_N2 mean"].values
    yerr = df[(df["Pressure"] == 2.0) & (df[b] == val)]["eta_N2 std"].values
    xerr = 0.2
    ax3.errorbar(x=x, y=y, yerr=yerr, xerr=xerr,linewidth=1, elinewidth=1, capsize=5, marker=symbols[n],markersize=8, alpha=0.5)

ax3.legend([str(x) for x in np.sort(df[b].unique())], title=legend_title, bbox_to_anchor=(1.05, 1.05), loc=2, ncol=1, frameon=False)#, mode="expand")

plt.savefig(file_dir + figure_file_name + ".png", format='png', dpi=300)

plt.show()