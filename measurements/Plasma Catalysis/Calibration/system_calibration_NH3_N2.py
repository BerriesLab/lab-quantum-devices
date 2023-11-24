import sys
import os
import platform
import matplotlib.pyplot as plt
import pandas
import numpy
from scipy.stats import linregress

window = 30 #seconds

#Set folders
folder_main = "C:/Users/Berri/Google Drive/Projects/P18. - Plasma Catalysis/Experimental/Data/"
folder_current = "Calibration/"
file_dir = folder_main + folder_current

print("PYTHON DIRECTORY: {}".format(sys.executable))
print("PYTHON VERSION: {}".format(platform.python_version()))
print("CURRENT DIRECTORY: {}".format(file_dir))
print("FILE IN CURRENT DIRECTORY: {}".format(os.listdir(file_dir)))

#IMPORT FILES and return DataFrames
df_back = pandas.read_csv(file_dir+"background.txt",engine="c",sep=",",header=None,
                          names=["Time","p(amu 28)","p(amu 2)","p(amu 17)","p(amu 18)","p(amu 16)","p(amu 32)"],
                          skiprows=29,index_col=False)

df_RGA = pandas.read_csv(file_dir+"calibration.txt",engine="c",sep=",",header=None,
                         names=["Time","p(amu 28)","p(amu 2)","p(amu 17)","p(amu 18)","p(amu 16)","p(amu 32)"],
                         skiprows=29,index_col=False)
#df_RGA["amu 16/17"] = df_RGA["amu 16"]/df_RGA["amu 17"]*100

df_notes = pandas.read_csv(file_dir+"calibration.csv",engine="c",sep=",",header=None,
                           names=["Time notes","Pressure","Total flow rate in","N2 in",
                                  "H2 in","N2","H2","NH3","Total flow rate","NH3:N2","NH3:H2","eta"],
                           skiprows=3,index_col=False)
df_notes["Time notes"] = pandas.to_timedelta(df_notes["Time notes"]).dt.total_seconds()

df_RGA["key"]=0
df_notes["key"]=0
df = pandas.merge(df_RGA, df_notes, how="outer", on="key")
df = df.loc[(df["Time"]<df["Time notes"])&(df["Time"]>(df["Time notes"]-window))]

print("DataFrame created")

#Subtract background
max_time = df_back["Time"].max()
df_back = df_back[(df_back["Time"]<max_time)&(df_back["Time"]>max_time-60)].mean()

df["p(amu 28)"] -= df_back["p(amu 28)"]
df["p(amu 2)"] -= df_back["p(amu 2)"]
df["p(amu 17)"] -= df_back["p(amu 17)"]
df["p(amu 18)"] -= df_back["p(amu 18)"]
df["p(amu 16)"] -= df_back["p(amu 16)"]
df["p(amu 32)"] -= df_back["p(amu 32)"]

#Take into account for the fragmentation of the gases in the ion gauge, and calculate NH3:N2
k1 = 0.524934  # fragments of NH3 at 17 amu !!!!!!!!!
k2 = 0.20109  # fragments of H2O at 17 amu
k3 = 0.744048  # fragments of H2O at 18 amu
k4 = 0.925926  # fragments of N2 at 28amu
df["p(N2)"] = df["p(amu 28)"]/k4
df["p(NH3)"] = 1 / k1 * (df["p(amu 17)"] - k2 / k3 * df["p(amu 18)"])
df["p(NH3):p(N2)"] = df["p(NH3)"]/df["p(N2)"]

#Calculate averages
window = 30
df_avg = df.loc[(df["Time"]<df["Time notes"])&(df["Time"]>(df["Time notes"]-window))]
df_avg = df.groupby(["Pressure","N2","H2","NH3"], as_index=False).mean()
df_avg = df_avg[["Pressure","NH3:N2","p(NH3):p(N2)"]]
df_avg["delta_gamma"] = df_avg["NH3:N2"]-df_avg["p(NH3):p(N2)"]

#PLOTTING
fig, ax = plt.subplots()
df_avg.groupby("Pressure").plot(x="p(NH3):p(N2)",y="delta_gamma", ax=ax, marker="o", linewidth=0, logx=False)
legend = df_avg.groupby("Pressure").groups.keys()
plt.legend([str(x)+" Torr" for x in legend])
ax.set_xlabel("$\\alpha$")
ax.set_ylabel("$\Delta\\alpha = \u0391 - \\alpha$")
plt.title("$\Delta\\alpha(\\alpha, P)$")

df_fit = pandas.DataFrame(columns=["Pressure","theta_0","theta_1","theta_2","std"])
for index in df_avg["Pressure"].unique():
    x = [0]+df_avg[(df_avg["Pressure"]==index)]["p(NH3):p(N2)"].values
    y = [0]+df_avg[(df_avg["Pressure"]==index)]["delta_gamma"].values
    A = numpy.vstack([x**2, x]).T #Assume model y = ax + bx^2 because the curve must pass through zero
    p, resid = numpy.linalg.lstsq(A, y, rcond=None)[0:2]
    std = ( resid[0] / (len(x)**2) )**0.5
    plt.plot(x,p[1]*x+p[0]*x**2,linestyle="dashed", linewidth=2, color="black", alpha=0.5)
    df_fit = df_fit.append({"Pressure":index, "theta_0":0, "theta_1":p[1],"theta_2":p[0], "std":std}, ignore_index=True)

text = r"Model: $\Delta\alpha(\alpha,P) = \Theta_{0,P}^{(\alpha)} + \Theta_{1,P}^{(\alpha)}\alpha +\Theta_{2,P}^{(\alpha)}\alpha^2$"
ax.text(0.05, 0.1, text, transform=ax.transAxes, fontsize=10, verticalalignment='top')
plt.show()

print(df_fit)
#SAVE file
df_fit.to_csv(file_dir+"gammas.csv", index=False)