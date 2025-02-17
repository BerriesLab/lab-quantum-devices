import os
from Objects.Backup.measurement_objects import FitSimmons
from numpy import loadtxt, logspace, sqrt, inf, linspace, array, log10, mean, std, argmin
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.cm import get_cmap
from pandas import DataFrame

plot_represenative = False
device = ("anl", r"C:\EB_Data_Sorted\anl\tep_01_g1\AfterEB\IV\dat\2019-12-03_run12_F5_IVs.dat")
main = "C:\EB_Data_Sorted"
chips = [("anl", ["tep_01_g1", "tep_01_g16"]),
         ("graphenea", ["a1"]),
         ("empa", ["tep06a10", "tep06e10", "tep07", "tep12a1", "tep12e1"])]
all_files = []
for x in chips:
    for y in x[1]:
        for z in os.listdir(rf"{main}\{x[0]}\{y}\AfterEB\IV\dat"):
            path = rf"{main}\{x[0]}\{y}\AfterEB\IV\dat"
            if z.endswith(".dat"):
                all_files.append((rf"{path}\{z}", x[0]))
sweep_direction = "-"

# region ----- Init figure -----
fig = plt.figure(figsize=(45 / 2.54, 22.5 / 2.54))
grid = GridSpec(nrows=2, ncols=4)
fig.subplots_adjust(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0.19, wspace=0.315)
#norm_T = Normalize(vmin=T_min, vmax=T_max)
cm = get_cmap("RdYlBu_r")
ax00 = fig.add_subplot(grid[0:2, 0:2])
ax00.set_xlabel("Voltage (V)")
ax00.set_ylabel(r"Current (I)")
ax01 = fig.add_subplot(grid[0, 2])
ax01.set_xlabel("A (nm$^2$)")
ax01.set_ylabel("Counts")
ax11 = fig.add_subplot(grid[0, 3])
ax11.set_xlabel("$\phi$ (eV)")
ax11.set_ylabel("Counts")
ax02 = fig.add_subplot(grid[1, 2])
ax02.set_xlabel("d (nm)")
ax02.set_ylabel("Counts")
ax12 = fig.add_subplot(grid[1, 3])
ax12.set_xlabel("Error")
ax12.set_ylabel("Counts")  # endregion

As_fit = []
phis_fit = []
ds_fit = []
error_fit = []
gr_fit = []
n_anl, n_empa, n_graphenea = 0, 0, 0

# region ----- Clean the list of files to process -----
files = []
for file in all_files:
    data = loadtxt(file[0], dtype=float, skiprows=5)

    x = data[:, 0]
    y = data[:, 1]

    if file[1] == "anl":
        n_anl += 1
    elif file[1] == "empa":
        n_empa += 1
    elif file[1] == "graphenea":
        n_graphenea += 1

    if max(x) <= 0.1 and max(x) != 3:
        continue

    if max(y) >= 9e-9:
        continue

    # if max(x) >= 0.2 and max(x) < 0.4:
    #    x = x * 10

    files.append(file)
    # print(file)
print(n_anl+n_graphenea+n_empa)
# endregion

#random_list = random.choices(files, k=10)
for file in files:
    #print(f"Fitting {file}")
    data = loadtxt(file[0], dtype=float, skiprows=5)
    x = data[:, 0]
    y = data[:, 1]
    if max(x) <= 0.3:
        x = x * 10

    # region keep only data corresponding to the forward (+) or backward (-) sweep
    if sweep_direction == "-":
        xtemp = []
        ytemp = []
        for idx, val in enumerate(x):
            if idx == 0:
                continue
            else:
                if x[idx] - x[idx - 1] < 0:
                    if len(xtemp) == 0:
                        xtemp.append(x[idx - 1])
                        xtemp.append(x[idx])
                        ytemp.append(y[idx - 1])
                        ytemp.append(y[idx])
                    else:
                        xtemp.append(x[idx - 1])
                        ytemp.append(y[idx - 1])
        x = array(xtemp)
        y = array(ytemp)
    elif sweep_direction == "+":
        xtemp = []
        ytemp = []
        for idx, val in enumerate(x):
            if idx == 0:
                continue
            else:
                if x[idx] - x[idx - 1] > 0:
                    if len(xtemp) == 0:
                        xtemp.append(x[idx - 1])
                        xtemp.append(x[idx])
                        ytemp.append(y[idx - 1])
                        ytemp.append(y[idx])
                    else:
                        xtemp.append(x[idx - 1])
                        ytemp.append(y[idx - 1])
        x = array(xtemp)
        y = array(ytemp)
    elif sweep_direction == "":
        pass
    else:
        exit("Sweep direction value not accepted. Please select among forward ('+'), backward ('-') or both ('').")
    # endregion

    index = argmin(abs(x))
    offset = y[index]
    y = y - offset

    simmons = FitSimmons(x, y)
    simmons.A_vary = True
    simmons.d_vary = True
    simmons.phi_vary = True
    simmons.A_max = 40
    simmons.A_ini = 0.1
    As = logspace(log10(simmons.A_min), log10(simmons.A_max), 4001)
    phis = linspace(simmons.phi_min, simmons.phi_max, 11)

    if simmons.A_vary is True and simmons.phi_vary is True:
        optimal = simmons.simmons_for_intermediate_voltage_range()
        params = optimal.params
        eval = simmons.simmons_eval(optimal.model, optimal.params)
        error = sqrt(sum(simmons.I - eval) ** 2)

    if simmons.A_vary is False and simmons.phi_vary is True:
        temp = inf
        for A in As:
            simmons.A_vary = True
            simmons.A_ini = A
            result = simmons.simmons_lmfit()
            params = result.params
            eval = simmons.simmons_eval(result.model, result.params)
            error = sqrt(sum(simmons.I - eval) ** 2)
            if error < temp:
                temp = error
                optimal = result

    if simmons.A_vary is False and simmons.phi_vary is False:
        temp = inf
        for A in As:
            simmons.A_ini = A
            for phi in phis:
                simmons.phi_ini = phi
                result = simmons.simmons_lmfit()
                params = result.params
                # calculate error
                eval = simmons.simmons_eval(result.model, result.params)
                error = sqrt(sum(simmons.I - eval) ** 2)
                if error < temp:
                    temp = error
                    optimal = result

    if log10(error) > -1 or optimal.params["phi"].value < 2.5 or optimal.params["d"].value > 5.0:
        print("Discarded.")
        continue
    eval = simmons.simmons_eval(optimal.model, optimal.params)

    #print(optimal.params)

    ax00.plot(simmons.V, simmons.I)
    ax00.plot(simmons.V, eval, "--", )
    gr_fit.append(file[1])
    As_fit.append(optimal.params["A"].value)
    phis_fit.append(optimal.params["phi"].value)
    ds_fit.append(optimal.params["d"].value)
    error_fit.append(error)

    print(file[1], file[0])
    if plot_represenative is True and file[1] == device[0] and file[0] == device[1]:
        print("here")
        fig2 = plt.figure(figsize=(6 / 2.54, 9 / 2.54))
        grid2 = GridSpec(nrows=2, ncols=1)
        fig2.subplots_adjust(top=0.94, bottom=0.085, left=0.065, right=0.955, hspace=0.19, wspace=0.315)
        cm2 = get_cmap("RdYlBu_r")
        axa = fig2.add_subplot(grid2[0])
        axa.set_xlabel("Voltage (V)")
        axa.set_ylabel(r"Current (I)")
        axb = fig2.add_subplot(grid2[1])
        axb.set_xlabel("A (nm$^2$)")
        axb.set_ylabel("Counts")
        #axa.plot()
        out0 = x
        out1 = simmons.simmons_eval(optimal.model, optimal.params)
        out2 = y
        DataFrame({"V": x, "y_exp": out2, "y_fit": out1}).to_csv(f"{main}\data_fit_single.csv", index=False)
        axa.plot(simmons.V, simmons.simmons_eval(optimal.model, optimal.params), "--")
        print(optimal.params)
        #ci = optimal.conf_interval(sigmas=[3])
        #fit_ci_dn = simmons.simmons(simmons.V, ci["A"][0][1], ci["phi"][0][1], ci["d"][0][1])
        #fit_ci_up = simmons.simmons(simmons.V, ci["A"][2][1], ci["phi"][2][1], ci["d"][2][1])
        axa.plot(x, y, 'o')
        #axb.plot(simmons.V, fit_ci_up, "black", "-.")
        #axb.plot(simmons.V, fit_ci_dn, "red", "-.")
        plt.show()

frame = DataFrame({"Graphene": gr_fit, "Area": As_fit, "Phi": phis_fit, "d": ds_fit, "error": error_fit})
frame.to_csv(f"{main}\data.csv", index=False)

print(f"ANL n: {len(frame[frame['Graphene'] == 'anl'])} out of {n_anl}, {len(frame[frame['Graphene'] == 'anl'])/n_anl*100:.1f} %")
print(f"Graphenea n: {len(frame[frame['Graphene'] == 'graphenea'])} out of {n_graphenea}, {len(frame[frame['Graphene'] == 'graphenea'])/n_graphenea*100:.1f} %")
print(f"Empa n: {len(frame[frame['Graphene'] == 'empa'])} out of {n_empa}, {len(frame[frame['Graphene'] == 'empa'])/n_empa*100:.1f} %")

print(f"Average Area ANL: {mean(frame['Area'].where(frame['Graphene'] == 'anl'))}, std: {std(frame['Area'].where(frame['Graphene'] == 'anl'))}")
print(f"Average Area Graphenea: {mean(frame['Area'].where(frame['Graphene'] == 'graphenea'))}, std: {std(frame['Area'].where(frame['Graphene'] == 'graphenea'))}")
print(f"Average Area Empa: {mean(frame['Area'].where(frame['Graphene'] == 'empa'))}, std: {std(frame['Area'].where(frame['Graphene'] == 'empa'))}")
print(f"Average Phi ANL: {mean(frame['Phi'].where(frame['Graphene'] == 'anl'))}, std: {std(frame['Phi'].where(frame['Graphene'] == 'anl'))}")
print(f"Average Phi Graphenea: {mean(frame['Phi'].where(frame['Graphene'] == 'graphenea'))}, std: {std(frame['Phi'].where(frame['Graphene'] == 'graphenea'))}")
print(f"Average Phi Empa: {mean(frame['Phi'].where(frame['Graphene'] == 'empa'))}, std: {std(frame['Phi'].where(frame['Graphene'] == 'empa'))}")
print(f"Average d ANL: {mean(frame['d'].where(frame['Graphene'] == 'anl'))}, std: {std(frame['d'].where(frame['Graphene'] == 'anl'))}")
print(f"Average d Graphenea: {mean(frame['d'].where(frame['Graphene'] == 'graphenea'))}, std: {std(frame['d'].where(frame['Graphene'] == 'graphenea'))}")
print(f"Average d Empa: {mean(frame['d'].where(frame['Graphene'] == 'empa'))}, std: {std(frame['d'].where(frame['Graphene'] == 'empa'))}")
alpha = 1
ax01.hist(x=[log10(frame['Area'].where(frame['Graphene'] == 'anl')),
             log10(frame['Area'].where(frame['Graphene'] == 'graphenea')),
             log10(frame['Area'].where(frame['Graphene'] == 'empa'))], rwidth=0.9, alpha=alpha, color=["#9BD19A", "#FECE94", "#C4B3D4"])
ax11.hist(x=[array(frame['Phi'].where(frame['Graphene'] == 'anl')),
             array(frame['Phi'].where(frame['Graphene'] == 'graphenea')),
             array(frame['Phi'].where(frame['Graphene'] == 'empa'))], rwidth=0.9, alpha=alpha, color=["#9BD19A", "#FECE94", "#C4B3D4"])
ax02.hist(x=[array(frame['d'].where(frame['Graphene'] == 'anl')),
             array(frame['d'].where(frame['Graphene'] == 'graphenea')),
             array(frame['d'].where(frame['Graphene'] == 'empa'))], rwidth=0.9, alpha=alpha, color=["#9BD19A", "#FECE94", "#C4B3D4"])
ax12.hist(x=[log10(frame['error'].where(frame['Graphene'] == 'anl')),
             log10(frame['error'].where(frame['Graphene'] == 'graphenea')),
             log10(frame['error'].where(frame['Graphene'] == 'empa'))], rwidth=0.9, alpha=alpha, color=["#9BD19A", "#FECE94", "#C4B3D4"])
plt.show()

