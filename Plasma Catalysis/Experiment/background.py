import sys
import os
import platform
import pandas
import numpy as np

#Set folders
folder_main = "C:/Users/Berri/Google Drive/Projects/P18. - Plasma Catalysis/Experimental/Data/"
folder_current = "Background/"
file_name = "background_0.5_Torr.csv"
file = folder_main + folder_current + file_name

print("PYTHON DIRECTORY: {}".format(sys.executable))
print("PYTHON VERSION: {}".format(platform.python_version()))
print("CURRENT DIRECTORY: {}".format(file_dir))
print("FILE IN CURRENT DIRECTORY: {}".format(os.listdir(file_dir)))

df_bg = pandas.read_csv(file,engine="c",sep=",",header=None,
                        names=["Time","p(amu 28)","p(amu 2)","p(amu 17)","p(amu 18)","p(amu 16)","p(amu 32)"],
                        skiprows=29,index_col=False)

df_bg = df_bg.loc[(df["Time"]<np.max(df["Time"]))&(df["Time"]>(np.max(df["Acquisition time"])-window))] #Load background and select last minute of data
df_bg = df_bg.agg["mean","std"] #Average last minute of data

df_bg.to_csv(file[-4]+"processed.csv", index=False, columns=[])
print("File saved")
