import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.gridspec as gs
import numpy as np
import pickle
from impedance.models.circuits import CustomCircuit


open_circuit = r"C:\samples\osja\test pcbs\open\impedance analysis\2021.11.18 09.34.55 - frequency sweep - bias 0.0V - air - light - 21C.bin"
short_circuit = r"C:\samples\osja\test pcbs\\0R\impedance analysis\2021.11.18 09.30.46 - frequency sweep - bias 0.0V - air - light - 21C.bin"
#measured = r"C:\samples\osja\test pcbs\100mhz\impedance analysis\2021.11.18 10.39.30 - frequency sweep - bias 0.0V - air - light - 21C.bin"
measured = r"C:\samples\osja\test pcbs\100khz\impedance analysis\2021.11.18 10.15.41 - frequency sweep - bias 0.0V - air - light - 21C.bin"

def make_complex(r, p):
    x = r * np.cos(p * np.pi / 180)
    y = r * np.sin(p * np.pi / 180)
    return x + 1j * y

with open(open_circuit, "rb") as f:
    temp = pickle.load(f)
    z_o = make_complex(temp["data"]["impedance_modulus"], temp["data"]["impedance_phase"])

with open(short_circuit, "rb") as f:
    temp = pickle.load(f)
    z_s = make_complex(temp["data"]["impedance_modulus"], temp["data"]["impedance_phase"])

with open(measured, "rb") as f:
    temp = pickle.load(f)
    z_xm = make_complex(temp["data"]["impedance_modulus"], temp["data"]["impedance_phase"])
    frequency = np.array(temp["data"]["frequency"])

z_dut = (z_xm - z_s) / (1 - (z_xm - z_s) * 1/z_o)

#r_0 = np.mean(abs(z_dut[frequency <= 1000]))
r_0 = abs(z_dut[0])
print(r_0)

# fitting
#customCircuit = CustomCircuit(initial_guess=[None, 1e-13], constants={'R_0' : r_0}, circuit='p(R_0,C_0)')
#customCircuit = CustomCircuit(initial_guess=[1e12, 1e-13], circuit='p(R_0,C_0)')
#z_fit = customCircuit.fit(frequency, z_dut, weight_by_modulus=True, bounds=([1e12, 1e-14],[1e15, 1e-11]))
#z_eval = customCircuit.predict(use_initial=False, frequencies=frequency)

customCircuit = CustomCircuit(initial_guess=[None, 1e-13], constants={'R_0' : 10e12}, circuit='p(R_0,C_0)')
z_fit = customCircuit.fit(frequency, z_dut, weight_by_modulus=True, bounds=([1e-14],[1e-11]))
z_eval = customCircuit.predict(use_initial=False, frequencies=frequency)


print(z_fit)
print(8.854e-12*np.pi*(25e-6)**2/100e-9 )

# create figures
fig = plt.figure(figsize=(40 / 2.54, 20 / 2.54))
gs = gs.GridSpec(2, 1)
ax1 = fig.add_subplot(gs[0, :])
ax2 = fig.add_subplot(gs[1, :])

ax1.set_xlabel('Frequency [Hz]')
ax1.set_ylabel('Impedance modulus [Ohm]')

ax2.set_xlabel('Frequency [Hz]')
ax2.set_ylabel('Impedance phase [°]')  # we already handled the x-label with ax1

# plot data
ax1.loglog(frequency, abs(z_dut),  alpha=0.4, linewidth=0, marker='o', label="corrected")
ax1.loglog(frequency, abs(z_xm),  alpha=0.4, linewidth=0, marker='o', label="meaured")
#ax1.loglog(frequency, abs(z_eval),  alpha=1, linewidth=2, linestyle='--', label="fit")
ax2.semilogx(frequency, np.angle(z_dut, deg=True), alpha=0.4, linewidth=0, marker='o', label="corrected")
ax2.semilogx(frequency, np.angle(z_xm, deg=True), alpha=0.4, linewidth=0, marker='o', label="measured")
#ax2.semilogx(frequency, np.angle(z_eval, deg=True),  alpha=1, linewidth=2, linestyle='--', label="fit")
plt.legend()
plt.show()