import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

folder_main = "C:/Users/Berri/Google Drive/Projects/Plasma Catalysis/Experimental/CCP/" #Main directory
df = pd.read_csv(folder_main + "database.csv", engine="c", sep=",", header=0, index_col=False, keep_default_na=False) #Load log file)

# Create figure
length = 18 #cm
height = 18/2.5#1.61 #cm
figsize = (length/2.54, height/2.54) #px, py = w*dpi, h*dpi  # pixels 300*16/2.54
fig = plt.figure(figsize=figsize, dpi=100) #My screen is 120 dpi
fig.subplots_adjust(left=0.1, right=0.82,top=0.9,bottom=0.18,wspace=0.25)
plt.rc("font", size=8, family="Arial")
plt.rc("axes", titlesize=8)
plt.rc("axes", labelsize=8)
plt.rc('xtick', labelsize=8)
plt.rc('ytick', labelsize=8)
plt.rc('legend', fontsize=8)
symbols = ["o","v","s","^","<",">","D"]

ax1 = fig.add_subplot(1,3,1)
ax1.set_title("0.5 Torr, +2 in")
ax1.set_xlabel("Power (W)")
ax1.set_ylabel("$\eta_{N_2} (\%)$")
ax1.set_ylim(bottom=-1, top=6)
ax2 = fig.add_subplot(1,3,2)
ax2.set_title("1 Torr, +2 in")
ax2.set_xlabel("Power (W)")
#ax2.set_ylabel("$\eta_{N_2} (\%)$", {'fontname':'Arial', 'size':'10'})
ax2.set_ylim(bottom=-1, top=6)
ax3 = fig.add_subplot(1,3,3)
ax3.set_title("2 Torr, +2 in")
ax3.set_xlabel("Power (W)")
#ax3.set_ylabel("$\eta_{N_2} (\%)$", {'fontname':'Arial', 'size':'10'})
ax3.set_ylim(bottom=-1, top=6)

pressures = np.sort(df["Pressure"].unique())
powers = np.sort(df["Power"].unique())
positions = np.sort(df["Position"].unique())
catalysts = np.sort(df["Catalyst"].unique())

for n,catalyst in enumerate(catalysts):
    x = df[(df["Position"]==2)&(df["Pressure"]==0.5)&(df["Catalyst"]==catalyst)]["Power"].values
    y = df[(df["Position"]==2)&(df["Pressure"]==0.5)&(df["Catalyst"]==catalyst)]["eta_N2 mean"].values
    xerr = 2
    yerr = df[(df["Position"]==2)&(df["Pressure"]==0.5)&(df["Catalyst"]==catalyst)]["eta_N2 std"].values
    ax1.errorbar(x=x, y=y, yerr=yerr, xerr=xerr, linewidth=0.5, elinewidth=0.5, capsize=3, marker=symbols[n],markersize=4, alpha=0.5)

for n,catalyst in enumerate(catalysts):
    x = df[(df["Position"]==2)&(df["Pressure"]==1.0)&(df["Catalyst"]==catalyst)]["Power"].values
    y = df[(df["Position"]==2)&(df["Pressure"]==1.0)&(df["Catalyst"]==catalyst)]["eta_N2 mean"].values
    xerr = 2
    yerr = df[(df["Position"]==2)&(df["Pressure"]==1.0)&(df["Catalyst"]==catalyst)]["eta_N2 std"].values
    ax2.errorbar(x=x, y=y, yerr=yerr, xerr=xerr, linewidth=0.5, elinewidth=0.5, capsize=3, marker=symbols[n],markersize=4, alpha=0.5)

for n,catalyst in enumerate(catalysts):
    x = df[(df["Position"]==2)&(df["Pressure"]==2.0)&(df["Catalyst"]==catalyst)]["Power"].values
    y = df[(df["Position"]==2)&(df["Pressure"]==2.0)&(df["Catalyst"]==catalyst)]["eta_N2 mean"].values
    xerr = 2
    yerr = df[(df["Position"]==2)&(df["Pressure"]==2.0)&(df["Catalyst"]==catalyst)]["eta_N2 std"].values
    ax3.errorbar(x=x, y=y, yerr=yerr, xerr=xerr, linewidth=0.5, elinewidth=0.5, capsize=3, marker=symbols[n],markersize=4, alpha=0.5)

ax3.legend([str(x) for x in catalysts], title="Catalyst", bbox_to_anchor=(1.05, 1.05), loc=2, ncol=1, frameon=False)#, mode="expand")

plt.savefig(folder_main + "database.png", format='png', dpi=300)
plt.show()