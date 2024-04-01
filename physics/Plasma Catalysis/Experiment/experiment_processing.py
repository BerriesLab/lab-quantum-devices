#THIS CODE IS DESIGNED TO PROCESS A SINGLE EXPERIMENT
#Reads: 'log.csv' and 'data.txt' files
#Returns: 'experiment.csv' file

import sys
import os
import platform
import pandas as pd
import re

#Set folders
folder_main = "C:/Users/Berri/Google Drive/Projects/Plasma Catalysis/Experimental/CCP/" #Main directory
folder_catalyst = "Ti/" #Folder of the ctalyst
folder_experiment = "Experiment 01/" #Folder of the experiment
file_dir = folder_main + folder_catalyst + folder_experiment #Current folder

print("PYTHON VERSION: {}".format(platform.python_version()))
print("PYTHON DIRECTORY: {}".format(sys.executable))
print("CURRENT DIRECTORY: {}".format(file_dir))
print("FILE IN CURRENT DIRECTORY: {}".format(os.listdir(file_dir)))

#Define constants and functions
window = 30 #averaging window, in seconds
groups = ["Catalyst","Temperature","N2 flow","H2 flow","Total flow","Position","Pressure","Power"] #Grouping keys
columns_log = ["ID", "Acquisition time", "Temperature", "N2 flow", "H2 flow", "Total flow", "Position", "Pressure", "Power", "Catalyst"] #Header of log files
columns_data = ["Time", "p(amu 28)", "p(amu 2)", "p(amu 17)", "p(amu 18)", "p(amu 16)", "p(amu 32)"] #Header of data files
columns_data_bg = ["Time", "p(amu 28) bg", "p(amu 2) bg", "p(amu 17) bg", "p(amu 18) bg", "p(amu 16) bg", "p(amu 32) bg"] #Header of background files
k1 = 0.524934  # fragments of NH3 at amu 17
k2 = 0.20109  # fragments of H2O at amu 17
k3 = 0.744048  # fragments of H2O at amu 18
k4 = 0.925926  # fragments of N2 at amu 28
k5 = 0.952381 # fragmenents of H2 at amu 2
log_list = list(filter(lambda x: ("log" in x) & ("csv" in x),os.listdir(file_dir))) #List of 'log.csv' files of the experiment
data_list = list(filter(lambda x: ("data" in x) & ("txt" in x),os.listdir(file_dir))) #List of 'data.txt' files of the experiment
log_list.sort() #Sort the log_list from 01 to 0x
data_list.sort() #Sort the data_list from 01 to 0x

#Import files and create a comprehensive DataFrame
DF = pd.DataFrame(data=None, index=None, columns=[""]) #Define the structure of the dataframe where to save the analysis of the experiment
print("Log files: " + str(log_list)) #Display the list of log files
print("Data files: " + str(data_list)) #Display the list of data files
for n in range(0,len(log_list)): #Check that log files and data files match
    if log_list[n][6:-3] != data_list[n][7:-3]:
        print("Log File and Data File mismatch. Aborting")
        exit()
for n, file in enumerate(log_list): #Run through list of file
    p = re.search("log_(.*)_Torr", log_list[n]).groups()[0] #Read the pressure from the file name
    df_log = pd.read_csv(file_dir+log_list[n], engine="c", sep=",", header=None, names=columns_log, skiprows=2, index_col=False, keep_default_na=False) #Load log file
    if (len(df_log["Pressure"].unique())==1) & (p == df_log["Pressure"].unique()[0]): #Check that the pressure saved in the log file is unique and equal to the one reported in the file name
        print("The pressure in " + file + " does not match the pressure reported in the file name.\nAborting.")
        exit()
    df_log["Acquisition time"] = pd.to_timedelta(df_log["Acquisition time"]).dt.total_seconds() #Convert HH:mm.ss into seconds
    df_data = pd.read_csv(file_dir+data_list[n], engine="c", sep=",", header=None, names=columns_data, skiprows=29, index_col=False) #Load data file
    df_alphas = pd.read_csv(folder_main[0:-4] + "Calibration/gammas.csv", engine="c", sep=",", header=0, names=None, skiprows=0, index_col=False)  # Load alphas file
    df_betas = pd.read_csv(folder_main[0:-4] +"Calibration/betas.csv",engine="c",sep=",",header=0, names=None, skiprows=0, index_col=False) #Load betas file
    #df_bg = pd.read_csv(folder main + "Background/bg_"+p+"_Torr.txt", engine="c", sep=",", header=None, names=columns_data_bg, skiprows=29, index_col=False) #Load background file

    #Process background #This is commented as the background subtraction is not significantly changing the results of the analysis
    #df_bg = df_bg.loc[(df["Time"] < np.max(df["Time"])) & (df["Time"] > (np.max(df["Time"]) - window))]  # Select data window
    #df_bg = df_bg.drop(columns=["Time"]) #Drop Time
    #df_bg = df_bg.agg["mean", "std"] #Average last minute of data
    #df_bg.columns = [" ".join(col) if (("mean" in col) | ("std" in col)) else "".join(col) for col in df_bg.columns] #Remove multi-index

    #Process data and log
    df_data["key"]=0 #Define key column
    df_log["key"]=0 #Define key column
    df = pd.merge(df_data, df_log, on="key", how="outer") #Merge data and log on key to return all the possible combination
    df = df[(df["Time"] < df["Acquisition time"]) & (df["Time"] > (df["Acquisition time"] - window))] #Select time windows to process
    df = df.drop(columns=["key", "Time", "Acquisition time"]) #Get rid of useless columns
    df = df.groupby(groups, as_index=False).agg({"p(amu 2)": ["mean", "std"], #Aggregate columns
                                                 "p(amu 16)": ["mean", "std"],
                                                 "p(amu 17)": ["mean", "std"],
                                                 "p(amu 18)": ["mean", "std"],
                                                 "p(amu 28)": ["mean", "std"],
                                                 "p(amu 32)": ["mean", "std"]})
    df.columns = [" ".join(col) if (("mean" in col) | ("std" in col)) else "".join(col) for col in df.columns] #Remove multi-index

    #Process alphas and betas
    df_alphas = df_alphas[df_alphas["Pressure"] == float(p)] #Filter on pressure p
    df_betas = df_betas[df_betas["Pressure"] == float(p)] #Filter on pressure p
    df_thetas = pd.merge(df_alphas, df_betas, on="Pressure", suffixes=("_alpha", "_beta")) #Create new dataframe that contains all the thetas

    #Create DataFrame
    df = pd.merge(df, df_thetas, how="outer") #Create dataframe
    #df = pd.merge(df, df_bg, how="outer")

    #Subtract the background #This is commented as the background subtraction is not significantly changing the results of the analysis
    #gas_list = ["p(amu 2)", "p(amu 16)", "p(amu 17)", "p(amu 18)", "p(amu 28)", "p(amu 32)"]
    #for gas in gas_list:
    #    df[gas + " mean"] = df[gas + " mean"] - df[gas + " bg mean"]
    #    df[gas + " std"] = ( df[gas + " std"]**2 + df[gas + " bg std"]**2 )**0.5

    #Drop useless columns
    #for col in df.columns:
    #    if "bg" in col:
    #        df = df.drop(columns=col)

    print("DataFrame " + file[0:-4] + " created")

    DF = DF.append(df, ignore_index=True) #Append current DataFrame to the comprehensive one

print("DataFrames appended")

#Calculate eta-s mean ans standard deviations #Refer to the manuscript for the equations.
DF["p(N2) mean"] = DF["p(amu 28) mean"] / k4
DF["p(N2) std"] = DF["p(amu 28) std"] / k4
DF["p(H2) mean"] = DF["p(amu 2) mean"] / k5
DF["p(H2) std"] = DF["p(amu 2) std"] / k5
DF["p(NH3) mean"] = 1 / k1 * (DF["p(amu 17) mean"] - k2 / k3 * DF["p(amu 18) mean"])
DF["p(NH3) std"] = ( ( DF["p(amu 17) std"] / k1 )**2 + (DF["p(amu 18) std"] * k2 / k1 / k3)**2 )**0.5
DF["p(NH3):p(N2) mean"] = DF["p(NH3) mean"] / DF["p(N2) mean"]
DF["p(NH3):p(N2) std"] = ( ( DF["p(NH3) std"]**2 / DF["p(N2) mean"] )**2 + ( DF["p(NH3) mean"] * DF["p(N2) std"] / DF["p(N2) mean"]**2 )**2 )**0.5
DF["p(NH3):p(H2) mean"] = DF["p(NH3) mean"] / DF["p(H2) mean"]
DF["p(NH3):p(H2) std"] = ( ( DF["p(NH3) std"]**2 / DF["p(H2) mean"] )**2 + ( DF["p(NH3) mean"] * DF["p(H2) std"] / DF["p(H2) mean"]**2 )**2 )**0.5
DF["delta_alpha mean"] = DF["theta_0_alpha"] + DF["theta_1_alpha"]*DF["p(NH3):p(N2) mean"] + DF["theta_2_alpha"]*DF["p(NH3):p(N2) mean"]**2
DF["delta_alpha std"] = DF["std_alpha"]
DF["delta_beta mean"] = DF["theta_0_beta"] + DF["theta_1_beta"]*DF["p(NH3):p(H2) mean"] + DF["theta_2_beta"]*DF["p(NH3):p(H2) mean"]**2
DF["delta_beta std"] = DF["std_beta"]
DF["eta mean"] = 100*2/(2+1/(DF["p(NH3):p(N2) mean"]+DF["delta_alpha mean"])+3/(DF["p(NH3):p(H2) mean"]+DF["delta_beta mean"]))
DF["eta std"] = 100*2/(2*(DF["p(NH3):p(N2) mean"]+DF["delta_alpha mean"])*(DF["p(NH3):p(H2) mean"]+DF["delta_beta mean"])+(DF["p(NH3):p(H2) mean"]+DF["delta_beta mean"])+3*(DF["p(NH3):p(N2) mean"]+DF["delta_alpha mean"]))**2*\
                ( (DF["p(NH3):p(H2) mean"]+DF["delta_beta mean"])**4*(DF["p(NH3):p(N2) std"]**2 + DF["delta_alpha std"]**2)+\
                  9*(DF["p(NH3):p(N2) mean"]+DF["delta_alpha mean"])**4*(DF["p(NH3):p(H2) std"]**2+DF["delta_beta std"]**2)\
                  )**0.5
DF["eta_N2 mean"] = 100*2/(2+1/(DF["p(NH3):p(N2) mean"]+DF["delta_alpha mean"]))
DF["eta_N2 std"] = 100*2/(2*(DF["p(NH3):p(N2) mean"]+DF["delta_alpha mean"])+1)**2*((DF["p(NH3):p(N2) std"]**2+DF["delta_alpha std"]**2))**0.5
DF["eta_H2 mean"] = 100*2/(2+3/(DF["p(NH3):p(H2) mean"]+DF["delta_beta mean"]))
DF["eta_H2 std"] = 100*6/(2*(DF["p(NH3):p(H2) mean"]+DF["delta_beta mean"])+3)**2*((DF["p(NH3):p(H2) std"]**2+DF["delta_beta std"]**2))**0.5
DF = DF[["Catalyst","Temperature","N2 flow","H2 flow","Total flow","Pressure","Position","Power", "eta mean","eta std","eta_N2 mean","eta_N2 std","eta_H2 mean","eta_H2 std"]]

#SAVE file
print(DF.head())
DF.to_csv(file_dir + "experiment_" + folder_experiment[-3:-1] + ".csv", index=False)
print(folder_experiment[0:-1] + ".csv saved to " + file_dir)

