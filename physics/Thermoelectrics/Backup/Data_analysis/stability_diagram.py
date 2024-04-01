import os
from Objects.Backup.plot_objects import *
from numpy import linspace, loadtxt, nanmin, nanmax, log10
import pickle

main = r"C:/samples"
chip = "teps02"
device = "d2"
experiments = os.listdir(rf"{main}\{chip}\{device}\te stability diagram")
nano = False
heater_current = [3e-3]
bath_temperature = [100]


for experiment in experiments:
    path = rf"{main}\{chip}\{device}\te stability diagram\{experiment}\{chip} - {device} - te stability diagram.data"
    print(f"Loading experiment {path}... ", end="")
    with open(path, "rb") as f:
        data = pickle.load(f)
    # if data.data.t not in bath_temperature:
    #     print("Skipped.")
    #     continue
    print("Done.")

    path = rf"{main}\{chip}\{device}\calibration\calibration.csv"
    print(f"Loading calibration data {path}... ", end="")
    cal = loadtxt(path, delimiter=",", skiprows=1)
    print("Done.")

    v_ex = 100e-6  # data.data.v_ex
    vb = linspace(-5e-3, 5e-3, 11)  # data.data.vb
    vg = linspace(-100, 100, 101)  # data.data.vg
    for x in range(len(data.data.t[0]["sd"]["h1"])):
        if data.data.t[0]["sd"]["h1"][x]["i_h"] in heater_current:
            i_h = data.data.t[0]["sd"]["h1"][0]["i_h"]
            iw2x = data.data.t[0]["sd"]["h1"][0]["i_w2"]["x"][:, :, 0]
            iw2y = data.data.t[0]["sd"]["h1"][0]["i_w2"]["y"][:, :, 0]
            i2w1x = data.data.t[0]["sd"]["h1"][0]["i_2w1"]["x"][:, :, 0]
            i2w1y = data.data.t[0]["sd"]["h1"][0]["i_2w1"]["y"][:, :, 0]
            if True:  # data.data.mode == 1:
                vw2x = data.data.t[0]["sd"]["h1"][0]["v_2w1"]["x"][:, :, 0]  # = data.data.t[0]["sd"]["h1"][0]["v_w2"]["x"][:, :, 0]
                vw2y = data.data.t[0]["sd"]["h1"][0]["v_2w1"]["y"][:, :, 0]  # = data.data.t[0]["sd"]["h1"][0]["v_w2"]["y"][:, :, 0]
                vdc = data.data.t[0]["sd"]["h1"][0]["v_dc"][:, :, 0]
            idc = data.data.t[0]["sd"]["h1"][0]["i_dc"][:, :, 0]

            if True:  # data.data.mode == 1:
                rdut = vw2x / iw2x
                rtot = v_ex / iw2x
            else:
                rtot = v_ex / iw2x
                rdut = rtot

            gdut = 1 / rdut
            dtx = cal[(cal[:, 1] == heater_current) & (cal[:, 0] == bath_temperature), 2]
            dty = cal[(cal[:, 1] == heater_current) & (cal[:, 0] == bath_temperature), 4]
            tbath = cal[cal[:, 0] == bath_temperature, 0][0]
            alpha_th = (- 8.2302 - 0.011056 * tbath + 2212 / tbath - 84652 / tbath**2) * 1e-6
            if nano is False:
                alpha = i2w1y * rtot / dty - alpha_th

            # region ----- Initialize figure -----
            plot1 = PlotTEStabilityDiagramAlpha(vg, vb)
            plot1.im02.set_data(alpha.T*1e6)
            plot1.im02.set_clim(vmin=nanmin((1e6*alpha).flatten()), vmax=nanmax((1e6*alpha).flatten()))
            plot1.im12.set_data(log10(abs(alpha.T*1e6)))
            plot1.im12.set_clim(vmin=nanmin(log10(abs((1e6*alpha).flatten()))), vmax=nanmax(log10(abs((1e6*alpha).flatten()))))

            plot2 = PlotTEStabilityDiagramG(vg, vb)
            plot2.im02.set_data(gdut.T)
            plot2.im02.set_clim(vmin=nanmin(gdut.flatten()), vmax=nanmax(gdut.flatten()))
            plot2.im12.set_data(log10(abs(gdut.T)))
            plot2.im12.set_clim(vmin=nanmin(log10(abs(gdut.flatten()))), vmax=nanmax(log10(abs(gdut.flatten()))))

            for idx_vg in range(len(vg)):
                plot1.ax00.lines[idx_vg].set_data(vb, 1e6 * alpha[idx_vg, :])
                plot1.ax00.relim()
                plot1.ax00.autoscale_view(scalex=False, scaley=True)
                plot1.ax10.lines[idx_vg].set_data(vb, log10(abs(1e6*alpha[idx_vg, :])))
                plot1.ax10.relim()
                plot1.ax10.autoscale_view(scalex=False, scaley=True)

                plot2.ax00.lines[idx_vg].set_data(vb, gdut[idx_vg, :])
                plot2.ax00.relim()
                plot2.ax00.autoscale_view(scalex=False, scaley=True)
                plot2.ax10.lines[idx_vg].set_data(vb, log10(abs(gdut[idx_vg, :])))
                plot2.ax10.relim()
                plot2.ax10.autoscale_view(scalex=False, scaley=True)

            for idx_vb in range(len(vb)):
                plot1.ax01.lines[idx_vb].set_data(vg, 1e6 * alpha[:, idx_vb])
                plot1.ax01.relim()
                plot1.ax01.autoscale_view(scalex=False, scaley=True)
                plot1.ax11.lines[idx_vb].set_data(vg, log10(abs(1e6 * alpha[:, idx_vb])))
                plot1.ax11.relim()
                plot1.ax11.autoscale_view(scalex=False, scaley=True)

                plot2.ax01.lines[idx_vb].set_data(vg, gdut[:, idx_vb])
                plot2.ax01.relim()
                plot2.ax01.autoscale_view(scalex=False, scaley=True)
                plot2.ax11.lines[idx_vb].set_data(vg, log10(abs(gdut[:, idx_vb])))
                plot2.ax11.relim()
                plot2.ax11.autoscale_view(scalex=False, scaley=True)

            plt.show()
            # endregion


# region ----- Plot -----
# endregion