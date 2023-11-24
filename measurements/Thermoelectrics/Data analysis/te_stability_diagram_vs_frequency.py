import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
from Objects.measurement import Figure
import pickle

main = r"C:/Data"
chip = "tep_ch5_10"
device = "a3"
sd_raw= "2022-05-20 19.22.31 - tep_ch5_10 - a3 - frequency response.data"
cal = "calibration.csv"

heater = 1
mode = 1
sds = [()]
t_bath = 293
i_h = [1e-3]

# Load stability diagram
path = rf"{main}\{chip}\{device}\frequency response\{sd_raw}"
print(f"Loading stability diagram... ", end="")
with open(path, "rb") as f:
    data = pickle.load(f).data
print("Done.")
# Load calibration data
print(f"Loading calibration data... ", end="")
cal = pd.read_csv(rf"{main}\{chip}\{device}\calibration\{cal}")
print("Done")

# Extract data from bin file
vgs = data.vg
vds = data.vb
f = data.f
i = data.i_h
idx_vgs = 0
idx_vds = 0
for idx_i, val_i in enumerate(i):
    if val_i in i_h:
        i_w2 = np.zeros_like(f)
        i_2w1 = np.zeros_like(f)
        v_w2 = np.zeros_like(f)
        i_dc = np.zeros_like(f)
        v_dc = np.zeros_like(f)
        i_gs = np.zeros_like(f)
        for idx2, val2 in enumerate(data.t[0]["sd"][f"h{heater}"][idx_i]):
            i_w2[idx2] = val2["i_w2"]["x"][idx_vgs, idx_vds, 0]
            i_2w1[idx2] = val2["i_2w1"]["y"][idx_vgs, idx_vds, 0]
            v_w2[idx2] = val2["v_w2"]["x"][idx_vgs, idx_vds, 0]
            i_dc[idx2] = val2["i_dc"][idx_vgs, idx_vds, 0]
            v_dc[idx2] = val2["v_dc"][idx_vgs, idx_vds, 0]
            i_gs[idx2] = val2["i_gs"][idx_vgs, idx_vds, 0]
# Compue device resistance
G = i_w2 / v_w2
# Compute Seebeck
alpha_pt = (- 8.2302 - 0.011056 * t_bath + 2212 / t_bath - 84652 / t_bath**2) * 1e-6
alpha = i_2w1 / G / cal[(cal["tbath"] == t_bath) & (cal["i"] == val_i)]["dty"].values - alpha_pt

# Plot
dp = vgs[np.argmin(abs(alpha))]
matplotlib.rcParams.update({'font.size': 7})
Figure.PlotXY([(f, -1e6*alpha, "")], "", "$f (Hz)$", r"$\alpha$ ($\mu$V/K)", logx=True)

plt.show()
