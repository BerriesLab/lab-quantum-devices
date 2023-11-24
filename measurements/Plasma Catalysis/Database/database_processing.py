import sys
import os
import platform
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from functools import reduce

#Set folders
folder_main = "C:/Users/Berri/Google Drive/Projects/Plasma Catalysis/Experimental/CCP/"

print("PYTHON DIRECTORY: {}".format(sys.executable))
print("PYTHON VERSION: {}".format(platform.python_version()))
print("CURRENT DIRECTORY: {}".format(folder_main))
print("FILE IN CURRENT DIRECTORY: {}".format(os.listdir(folder_main)))
groups = ["Catalyst","Temperature","N2 flow","H2 flow","Total flow","Position","Pressure","Power"]
columns = ["Catalyst","Temperature","N2 flow","H2 flow","Total flow","Position","Pressure","Power","eta mean","eta_N2 mean","eta_H2 mean","eta std","eta_N2 std","eta_H2 std"]
catalysts = ["None", "SS 316L", "Pt", "Cu", "Co", "Al2O3", "Ti"]

def STD(col):
    return reduce(lambda x, y: (x**2 + y**2)**0.5,col)

#IMPORT FILES and return DataFrame
df = pd.DataFrame(data=None, index=None, columns=columns)
for folder_catalyst in os.listdir(folder_main):
    if folder_catalyst in catalysts:
        for file in os.listdir(folder_main + folder_catalyst):
            if ("catalyst" in file) & (".csv" in file):
                print("Loading " + folder_catalyst + file)
                df = df.append(pd.read_csv(folder_main + folder_catalyst + "/" + file, engine="c", sep=",", header=0,index_col=False, keep_default_na=False))

print(df)
df.to_csv(folder_main+"/database.csv", index=False)