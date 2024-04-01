#THIS CODE COLLECTS THE RESULTS OF THE EXPERIMENTS OF A GIVEN CATALYST,
#AND CREATEs A DATABASE
#Reads: 'experiments_xx.csv'
#Returns: 'catalyst.csv' file

import sys
import os
import platform
import pandas as pd
from functools import reduce

#Set folders
folder_main = "C:/Users/Berri/Google Drive/Projects/Plasma Catalysis/Experimental/CCP/"
folder_catalyst = "Ti/"

print("PYTHON DIRECTORY: {}".format(sys.executable))
print("PYTHON VERSION: {}".format(platform.python_version()))
print("CURRENT DIRECTORY: {}".format(folder_main))
print("FILE IN CURRENT DIRECTORY: {}".format(os.listdir(folder_main)))

#Define constants and functions
groups = ["Catalyst","Temperature","N2 flow","H2 flow","Total flow","Position","Pressure","Power"]
columns = ["Catalyst","Temperature","N2 flow","H2 flow","Total flow","Position","Pressure","Power","eta mean","eta_N2 mean","eta_H2 mean","eta std","eta_N2 std","eta_H2 std"]
catalysts = ["None", "SS 316L", "Pt", "Co", "Al2O3", "Ti"] #List of catalysts studied
def STD(col): #STD calculates the standard deviation of the average of a given population. A correction factor 1/sqrt(n) has to be applied to teh function
    return reduce(lambda x, y: (x**2 + y**2)**0.5,col)

#IMPORT FILES and return DataFrame
n = 0 #The number of experiments. Useful to calculate the std dev of the mean
df = pd.DataFrame(data=None, index=None, columns=columns) #Create dataframe
for folder in os.listdir(folder_main + folder_catalyst): #Run through the directory
    if os.path.isdir(folder_main + folder_catalyst+folder): #Check that folder is a sub-directory
        for file in os.listdir(folder_main + folder_catalyst + folder): #Run through the sub-directory
            if ("experiment" in file) & (".csv" in file): #If file is an experiment file append it to the dataframe
                print("Loading " + file)
                n += 1
                df = df.append(pd.read_csv(folder_main + folder_catalyst + folder + "/" + file, engine="c", sep=",", header=0,index_col=False, keep_default_na=False))
df = df.groupby(groups, as_index=False).agg({"eta mean":"mean", #Aggregate the dataframe
                                             "eta std": STD,
                                             "eta_N2 mean":"mean",
                                             "eta_N2 std":STD,
                                             "eta_H2 mean":"mean",
                                             "eta_H2 std":STD})
df[["eta std","eta_N2 std","eta_H2 std"]] = n**(-0.5)*df[["eta std","eta_N2 std","eta_H2 std"]] #Correct the std deviation with the number of samples

print(df.head())
#SAVE file
df.to_csv(folder_main+folder_catalyst+"catalyst.csv", index=False)