import pickle
import os
import lmfit
from Objects.measurement import FitDoubleSchottkyBarrier
from numpy import where
import matplotlib.pyplot as plt


main = r"C:\Samples"
data2load = [("tetra fet au p3ht", ["4wire h-20um"])]  # list of tuples [(chip1, [device1, device2, ...]), (chip2, [device1, device2, ...]), ...]
confidence_band = False
temperature = False
cycle_n = None  # filter measurement cycle number (0 is first cycle...)
sweep_direction = "-"  # filter forward ("+") or backward ("-") or both (None) traces
t_bounds = [290, 350]
d = 100 * 1e-9  # organic semiconductor thickness (for Poole Frenkel model)
fit_double_schottky_barrier = True
fit_poole_frenkel = False
# design = design.lille
phi1 = "Au/C60"
phi2 = "Gr/C60"

if temperature:
    plot0 = FitDoubleSchottkyBarrier.PlotDoubleSchottkyBarrierVsT()
elif not temperature:
    plot0 = FitDoubleSchottkyBarrier.PlotDoubleSchottkyBarrier()

T = []
fit_report = []
for x in data2load:

    for y in x[1]:

        path = rf"{main}\{x[0]}\{y}\iv"
        files = [x for x in os.listdir(path) if x.endswith(".data")]

        for z in files:

            # region ----- LOAD FILE AND EXTRACT DATA -----
            print(rf"Loading {path}\{z}... ", end="")
            path = rf"{main}\{x[0]}\{y}\iv\{z}"
            with open(path, "rb") as file:
                sweep = pickle.load(file)
                print("Done")
            # endregion

            # region ----- FILTER DATA -----
            print("Filtering data... ", end="")
            # collect only data corresponding to the n-th cycle
            sweep.data = sweep.filter_vgs_cycle()
            sweep.data = sweep.filter_vds_cycle()
            # keep only data corresponding to the forward (+) or backward (-) sweep
            sweep.data = sweep.filter_vds_fwd_sweep()
            print("Done.")  # endregion

            # region ----- EXTRACT TEMPERATURE -----
            if temperature:
                T.append(sweep.temperature)

            # T.append(float(data["temperature"] + 273.15))
            # endregion

            xdata = sweep.data[0, :, 2]
            ydata = sweep.data[0, :, 3]
            # region ----- FIT DOUBLE SCHOTTKY BARRIER MODEL -----
            if fit_double_schottky_barrier:
                print("Fitting curve with double Schottky barrier model... ", end="") #design["S1"][name], design["S2"][name]
                dsb = FitDoubleSchottkyBarrier(V=xdata, I=ydata, T=T[-1], S1=1e-3*50e-9, S2=1e-3*50e-9, ideal=False)  # create schottky object
                dsb.v1_vary = False
                dsb.v2_vary = False
                dsb.S1_vary =True
                dsb.S2_vary =True
                weights = where(abs(xdata) >= 0, ydata, 0)  # define weights
                result = dsb.iv_fit(weights)  # run fit
                print(result.fit_report())
                fit_report.append(result)

                # plot fit
                plot0.ax00.plot(xdata, ydata, **plot0.lookIds, label=f"{T[-1]} K")
                #plot0.ax00.plot(xdata, ydata, **plot0.lookIds, c=plot0.cm(plot0.norm_T(T[-1])), label=f"{T[-1]} K", alpha=0.4)
                fit = dsb.func(xdata, result.params["phi01"], result.params["phi02"], dsb.T_ini, dsb.S1_ini, dsb.S2_ini, result.params["n1"], result.params["n2"], result.params["v1"], result.params["v2"])
                plot0.ax00.plot(xdata, fit, '--', dashes=(3, 5))
                plot0.ax01.plot(xdata, (ydata - fit), **plot0.lookIds, label=f"{T[-1]} K")
                plot0.ax01.fill_between(xdata, (ydata - fit), alpha=0.4)
                # plot0.ax00.plot(xdata, fit, '--', c=plot0.cm(plot0.norm_T(T[-1])), dashes=(3, 15))

                if confidence_band is True:
                    ci = result.conf_interval(sigmas=[3])
                    print(lmfit.report_ci(ci))
                    fit_ci_dn = dsb.func(xdata, ci["phi01"][0][1], ci["phi02"][0][1], dsb.T_ini, dsb.S1_ini, dsb.S2_ini, ci["n1"][0][1], ci["n2"][0][1], result.params["v1"].value, result.params["v2"].value)
                    fit_ci_up = dsb.func(xdata, ci["phi01"][2][1], ci["phi02"][2][1], dsb.T_ini, dsb.S1_ini, dsb.S2_ini, ci["n1"][2][1], ci["n2"][2][1], result.params["v1"].value, result.params["v2"].value)
                    plot0.ax00.plot(xdata, fit_ci_up, "black", "-.")
                    plot0.ax00.plot(xdata, fit_ci_dn, "red", "-.")
                    plot0.ax00.fill_between(x=xdata, y1=fit_ci_up, y2=fit_ci_dn)
                print("Done.\n")
            # endregion

            # # region ----- FIT POOLE-FRENKEL MODEL -----
            # if fit_poole_frenkel:
            #     print("Fitting curve with Poole-Frenkel model... ", end="")
            #     pf = poole_frenkel(V=xdata_fit, I=ydata_fit, T=T[-1], d=d, epsilon_r=3.83)  # create poole frenkel object
            #     pf.S_ini = mean([pi * (diameter[data["device"][1]] * 1e-6 / 2) ** 2, pi * ((diameter[data["device"][1]] + 2) * 1e-6 / 2) ** 2])
            #     pf.S_min = pf.S_ini * 0.1
            #     pf.S_max = pf.S_ini * 10
            #     result = pf.iv_fit()  # run fit
            #     print(result.fit_report())
            #     fit_report.append(result)
            #
            #     ax00.plot(xdata_fit, ydata_fit, 'o', markeredgecolor="black", markeredgewidth=0.2, c=cm(norm_T(T[-1])), label=f"{x[0]} - {y} - {T[-1]} K", alpha=0.4)
            #     fit = pf.func(xdata_fit, result.params["phi"], pf.T_ini, pf.d_ini, pf.sigma0_ini, pf.S_ini, pf.epsilon_r_ini)
            #     ax00.plot(xdata_fit, fit, '--', c=cm(norm_T(T[-1])), dashes=(3, 15))
            #
            #     # if confidence_band is True:
            #     #     ci = result.conf_interval(sigmas=[3])
            #     #     print(lmfit.report_ci(ci))
            #     #     fit_ci_dn = dsb.func(xdata_fit, ci["phi01"][0][1], ci["phi02"][0][1], dsb.T_ini, dsb.S1_ini, dsb.S2_ini, ci["n1"][0][1], ci["n2"][0][1], result.params["v1"].value, result.params["v2"].value)
            #     #     fit_ci_up = dsb.func(xdata_fit, ci["phi01"][2][1], ci["phi02"][2][1], dsb.T_ini, dsb.S1_ini, dsb.S2_ini, ci["n1"][2][1], ci["n2"][2][1], result.params["v1"].value, result.params["v2"].value)
            #     #     ax00.plot(xdata_fit, fit_ci_up, "black", "-.")
            #     #     ax00.plot(xdata_fit, fit_ci_dn, "red", "-.")
            #     #     ax00.fill_between(x=xdata_fit, y1=fit_ci_up, y2=fit_ci_dn)
            #     print("Done.\n")
            # # endregion

# region ----- PLOT PARAMETERS vs TEMPERATURE -----
if temperature:
    if fit_double_schottky_barrier:
        plot0.ax01.scatter([x.params["T"].value for x in fit_report], [x.params["phi01"].value for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="o", linewidth=0.2, edgecolor="black", label=phi1)
        plot0.ax01.scatter([x.params["T"].value for x in fit_report], [x.params["phi02"].value for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="D", linewidth=0.2, edgecolor="black", label=phi2)
        plot0.ax02.scatter([x.params["T"].value for x in fit_report], [x.params["n1"].value for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="o", linewidth=0.2, edgecolor="black", label="n1")
        plot0.ax02.scatter([x.params["T"].value for x in fit_report], [x.params["n2"].value for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="D", linewidth=0.2, edgecolor="black", label="n2")
        plot0.ax11.scatter([x.params["T"].value for x in fit_report], [x.params["phi01"].stderr for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="o", linewidth=0.2, edgecolor="black", label=phi1)
        plot0.ax11.scatter([x.params["T"].value for x in fit_report], [x.params["phi02"].stderr for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="D", linewidth=0.2, edgecolor="black", label=phi2)
        plot0.ax12.scatter([x.params["T"].value for x in fit_report], [x.params["n1"].stderr for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="o", linewidth=0.2, edgecolor="black", label="n1")
        plot0.ax12.scatter([x.params["T"].value for x in fit_report], [x.params["n2"].stderr for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="D", linewidth=0.2, edgecolor="black", label="n2")
        plot0.ax00.legend()
        plot0.ax01.legend()
        plot0.ax02.legend()
    if fit_poole_frenkel:
        plot0.ax01.scatter([x.params["T"].value for x in fit_report], [x.params["phi"].value for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="o", linewidth=0.2, edgecolor="black", label=phi1)
        plot0.ax11.scatter([x.params["T"].value for x in fit_report], [x.params["phi"].stderr for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="D", linewidth=0.2, edgecolor="black", label=phi2)
        plot0.ax02.scatter([x.params["T"].value for x in fit_report], [x.params["sigma0"].value for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="o", linewidth=0.2, edgecolor="black", label="n1")
        plot0.ax12.scatter([x.params["T"].value for x in fit_report], [x.params["sigma0"].stderr for x in fit_report], c=plot0.cm(plot0.norm_T(T)), marker="D", linewidth=0.2, edgecolor="black", label="n2")
# endregion

plt.show()
