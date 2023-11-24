import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
from Objects.measurement import Figure
import pickle

main = r"C:/Data"
chip = "tep_ch5_10"
device = "a3"
sd_raw = "2022-05-19 18.28.09 - tep_ch5_10 - a3 - te stability diagram.data"
sd_raw = "2022-05-22 10.07.15 - tep_ch5_10 - a3 - te stability diagram.data"
sd_raw = "2022-05-23 17.37.47 - tep_ch5_10 - a3 - te stability diagram.data"
cal = "calibration.csv"

heater = 1
mode = 1
t_bath = 293
i_h = 1e-3

# Load stability diagram
path = rf"{main}\{chip}\{device}\te stability diagram\{sd_raw}"
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
for idx, val in enumerate(data.t[0]["sd"][f"h{heater}"]):
    if val["i_h"] == i_h:
        i_w2 = val["i_w2"]
        i_2w1 = val["i_2w1"]
        v_w2 = val["v_w2"]
        i_dc = val["i_dc"]
        v_dc = val["v_dc"]
        i_gs = val["i_gs"]
# Compue device resistance
G = i_w2["x"] / v_w2["x"]
# Compute Seebeck
alpha_pt = (- 8.2302 - 0.011056 * t_bath + 2212 / t_bath - 84652 / t_bath**2) * 1e-6
alpha = i_2w1["y"] / G / cal[(cal["tbath"] == t_bath) & (cal["i"] == i_h)]["dty"].values - alpha_pt

# Plot
dp = vgs[np.argmin(abs(alpha[:, 1, 0]))]
dp = vgs[np.argmax(abs(1/G[:, 1, 0]))]
matplotlib.rcParams.update({'font.size': 7})
Figure.Plot2D(vgs-dp, vds*1e3, 1/G[:, :, 0].T/1e3, "R (k$\Omega$)", "$\Delta V_{GS}$ (V)", "$V_{DS}$ (mV)")
Figure.Plot2D(vgs-dp, vds*1e3, 1/G[:, :, 0].T/1e3, "R (k$\Omega$)", "$\Delta V_{GS}$ (V)", "$V_{DS}$ (mV)", "bilinear")
Figure.Plot2D(vgs-dp, vds*1e3, np.log10(abs(1/G[:, :, 0].T)), "$Log_{10}(R)$", "$\Delta V_{GS}$ (V)", "$V_{DS}$ (mV)", "bilinear")
Figure.Plot2D(vgs-dp, vds*1e3, -alpha[:, :, 0].T/1e-6, r"$\alpha$ ($\mu$V/K)", "$\Delta V_{GS}$ (V)", "$V_{DS}$ (mV)", "bilinear")
Figure.Plot2D(vgs-dp, vds*1e3, np.log10(abs(alpha[:, :, 0].T)), r"$Log_{10}(\alpha$)", "$\Delta V_{GS}$ (V)", "$V_{DS}$ (mV)", "bilinear")
Figure.PlotXY([(vgs-dp, -1e6*alpha[:, k, 0], f"{vds[k]*1e3:0.1f} mV") for k in range(alpha.shape[1])], "", "$\Delta V_{GS}$", r"$\alpha$ ($\mu$V/K)")
Figure.PlotXY([(vgs-dp, 1/G[:, k, 0]/1e3, f"{vds[k]*1e3:0.1f} mV") for k in range(alpha.shape[1])], "", "$\Delta V_{GS}$", r"R (k$\Omega$)")

np.savetxt(f"{main}/G.csv", G[:, :, 0], delimiter=",")
np.savetxt(f"{main}/alpha.csv", alpha[:, :, 0], delimiter=",")

plt.show()
