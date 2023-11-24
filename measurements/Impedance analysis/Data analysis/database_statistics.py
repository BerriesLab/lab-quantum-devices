import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import Normalize
from matplotlib.cm import get_cmap
from impedance.models.circuits import CustomCircuit
from numpy import inf, pi, mean, std
import pandas as pd

main = r"T:"

df = pd.read_csv(rf"{main}\impedance_data_summary - Copy.csv")
grouped = df.groupby("area")

for key, grp in grouped:
    print(key)