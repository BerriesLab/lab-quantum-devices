import numpy
import pandas
import os
import matplotlib.pyplot as plt
import platform

print("\nPython version: {}".format(platform.python_version()))

#Set folders
folder_main = "C:/Users/Berri/Google Drive/Projects/P18. - Plasma Catalysis/Experimental/Data/"
folder_current = "2019.03.14 - Afterglow 00/"
file_dir = folder_main + folder_current

#Define averaging window (seconds)
window = 60

#Retrieve the list of files in folder and print the list to screen
file_list = os.listdir(file_dir)
print("\n************ FILE LIST ************")
for idx in file_list:
    print(idx)
print("************************\n")

#Select RGA and Note files and import data into dfs
file_name = "data.txt" #input("Select RGA file from list\n")
RGA_file = file_dir + file_name
if os.path.isfile(RGA_file) == True:
    RGA_header = ["Time", "N_2", "H_2", "a.m.u. 17",
                  "a.m.u. 18", "a.m.u. 16", "O_2"]
    RGA_data = pandas.read_csv(RGA_file, engine="c", sep=",", header=None,
                           names=RGA_header, skiprows=29, index_col=False)

file_name = "notes2.csv"#input("Select Note file from list\n")
note_file = file_dir + file_name
if os.path.isfile(note_file) == True:
    note_header = ["Time init", "Temperature init",
                   "Time fin", "Temperature fin",
                   "Power","N2 flow","H2 flow","Total flow","Th. RGA flow ratio","Reactor pressure",
                   "Pulse duration","Duty cycle","Period","ON duration per second","OFF duration per second"]
    note_data = pandas.read_csv(note_file, engine="c", sep=",", header=None,
                           names=note_header, skiprows=3, index_col=False)
    #Convert timedelta to seconds elapsed
    note_data["Time init"] = pandas.to_timedelta(note_data["Time init"]).dt.total_seconds()
    note_data["Time fin"] = pandas.to_timedelta(note_data["Time fin"]).dt.total_seconds()

#Calculate NH3, N2:H2 ratio and efficiency and append to RGA-df as new columns
k1 = 0.524934 #fragments of NH3 at 17 amu
k2 = 0.20109 #fragments of H2O at 17 amu
k3 = 0.744048 #fragments of H2O at 18 amu
k4 = 0.925926 #fragments of N2 at 28amu

N2H2 = (RGA_data["N_2"]/k4)/RGA_data["H_2"]
RGA_data["N2:H2"] = N2H2
NH_3 = 1/k1*(RGA_data["a.m.u. 17"]-k2/k3*RGA_data["a.m.u. 18"])
RGA_data["NH_3"] = NH_3
eta = 100*RGA_data["NH_3"]/(RGA_data["NH_3"]+2*RGA_data["N_2"]/k4)
RGA_data["Efficiency"] = eta

#Elaborate dataframes
RGA_data["key"]=0
note_data["key"]=0
data = pandas.merge(RGA_data, note_data, how="outer")
data = data.loc[(data["Time"]<data["Time fin"])&(data["Time"]>data["Time init"])]

#To calculate efficiency, check first if pulsing is active
def pulse(df):
    if pandas.isnull(df["Duty cycle"]):
        return df["Efficiency"]
    else:
        return 100 * df["Efficiency"] / df["Duty cycle"]
data["Efficiency"] = data.apply(pulse, axis=1)


#Extract list of intervals and take averages
data_avg = data.loc[(data["Time"]<data["Time fin"])&(data["Time"]>(data["Time fin"]-window))]
data_avg = data_avg.groupby(["Power","Temperature fin","Time fin"], as_index=False).mean()

print(data_avg)
#Select columns, rename, and build final dataframe
data_avg = data_avg[["Time","Power","Total flow","N2:H2",
                     "Temperature fin","Reactor pressure",
                     "Pulse duration", "Duty cycle",
                     "Efficiency"]].sort_values("Time")#,

data_avg = data_avg.rename(index=str, columns={"Power":"Power (W)",
                                    "Temperature fin":"Temperature (°C)",
                                    "Total flow":"Total flow (sccm)",
                                    "Reactor pressure":"Reactor pressure (Torr)",
                                    "Efficiency":"Efficiency (%)"})
#Save to file
file_out = file_dir + "data_processed.csv"
data_avg.to_csv(file_out)

#PLOT PLOT PLOT


print(data_avg.head())
#Create figure
fig = plt.figure()

#Plot raw data
ax1 = fig.add_subplot(231)
RGA_data.plot(x="Time", y="a.m.u. 18", ax=ax1)
RGA_data.plot(x="Time", y="a.m.u. 17", ax=ax1)
RGA_data.plot(x="Time", y="a.m.u. 16", ax=ax1)
ax1.set_xlabel("Time")
ax1.set_ylabel("Partial pressure (Torr)")
ax1.set_title("Raw data")

#Plot efficiency versus temperature
ax2 = fig.add_subplot(232)
data_avg.where(data_avg["Duty cycle"].isnull()).plot(x="Time", y="Efficiency (%)", marker="o", linewidth=0, ax=ax2)
ax2.set_xlabel("Time")
ax2.set_ylabel("Efficiency (%)")
ax2.legend()

ax3 = fig.add_subplot(233)
data_avg.where(data_avg["Duty cycle"].isnull()).groupby("Reactor pressure (Torr)").plot(x="Temperature (°C)",y="Efficiency (%)", marker="o", linewidth=0, ax=ax3)
ax3.set_xlabel("Temperature")
ax3.set_ylabel("Efficiency (%)")
ax3.set_title("eta vs Temperature")
handles, labels = ax3.get_legend_handles_labels()


#for i, txt in enumerate(data_avg["Power (W)"]):
#    ax3.annotate(str(txt)+" W", (data_avg["Temperature (°C)"].iat[i], data_avg["Efficiency (%)"].iat[i]))

ax4 = fig.add_subplot(234)
data_avg.where(data_avg["Duty cycle"].isnull()).groupby("Reactor pressure (Torr)").plot(x="Power (W)", y="Efficiency (%)", marker="o", linewidth=0, ax=ax4)
ax4.set_xlabel("Power (W)")
ax4.set_ylabel("Efficiency (%)")
#for i, txt in enumerate(data_avg["Reactor pressure (Torr)"]):
#    ax4.annotate(str(txt)+" Torr", (data_avg["Power (W)"].iat[i], data_avg["Efficiency (%)"].iat[i]))

ax5 = fig.add_subplot(235)
data_avg.where(data_avg["Duty cycle"].notnull()).plot(x="Duty cycle", y="Efficiency (%)", marker="o", linewidth=0, ax=ax5)
ax5.set_xlabel("Duty cycle")
ax5.set_ylabel("Efficiency (%)")

fig2 = plt.plot()
df_pulsed = data_avg.where(data_avg["Duty cycle"].notnull())
min = data_avg.where((data_avg["Reactor pressure (Torr)"]==2)&(data_avg["Power (W)"]==200)&\
    (data_avg["Temperature (°C)"]==300))["Efficiency (%)"].min()
print(min)
#min = df_pulsed["Efficiency (%)"].min()
df_pulsed["Efficiency (%)"] /= min
df_pulsed.plot(x="Duty cycle", y="Efficiency (%)", marker="o", ms = 10, linewidth=0, color="red", alpha=0.8)
plt.xlabel("Duty cycle (%)")
plt.ylabel("$\eta$ pulsed / $\eta$ continuous")
plt.text(x=40, y=12, s="Pulse duration = 10 ms \nReactor pressure = 2 Torr \nPower = 200 W")
plt.legend().set_visible(False)
plt.axhline(1, linewidth=1, linestyle="dashed", color="black")
plt.yticks(list(plt.yticks()[0]) + [1])
plt.show()