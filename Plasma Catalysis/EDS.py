import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

folder_main = "C:/Users/Berri/Google Drive/Projects/P18. - Plasma Catalysis/Experimental/CCP/" #Main directory
folder_catalyst = "Pt/" #Folder of the experiment
folder_experiment = "01/"
file_dir = folder_main + folder_catalyst + folder_experiment + "SEM and EDS/" #Current folder
df = pd.read_csv(file_dir + "Pt_pristine.csv", engine="python", delimiter=";", skiprows=0, skipfooter=1, index_col="Spectrum Label")

df = df.transpose()
print(df)
