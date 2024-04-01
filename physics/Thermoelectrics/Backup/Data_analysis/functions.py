# region ----- Import packages -----
import numpy as np
from scipy.stats import linregress
from Objects.Backup.measurement_objects import *
from scipy.special import kv
# endregion


def get_resistance(data=Calibration, thermoresistance=int):

    """Return the slope of the thermoresistance (1 or 2)"""

    if not isinstance(data, Calibration):
        exit("The passed object is not Calibration type.")

    t = np.zeros(len(data.t))
    r = np.zeros(len(data.t))
    r_err = np.zeros(len(data.t))

    for idx in range(len(data.t)):

        t[idx] = data.t[idx]["t"]
        r[idx] = data.t[idx][f"iv{thermoresistance}"].r
        r_err[idx] = data.t[idx][f"iv{thermoresistance}"].r_stderr

    return t, r, r_err, linregress(t, r)


def get_heater_sweep(data=Calibration, heater=int, thermoresistance=int):

    """Return the heater sweep data"""

    if not isinstance(data, Calibration):
        exit("The passed object is not Calibration type.")

    for n in range(len(data.t)):
        if data.t[n]["dr"] is not None: #data.t[n]["t"] == temperature and
            idx = n

    temperature = data.t[idx]["t"]
    i = array([k["i_h"] for k in data.t[idx]["dr"][f"h{heater}"]])
    drdc = array([k[f"iv{thermoresistance}"].r for k in data.t[idx]["dr"][f"h{heater}"]])
    drdc_err = array([k[f"iv{thermoresistance}"].r_stderr for k in data.t[idx]["dr"][f"h{heater}"]])
    drx = array([k[f"drt{thermoresistance}"].x_avg for k in data.t[idx]["dr"][f"h{heater}"]])
    drx_err = array([k[f"drt{thermoresistance}"].x_stddev for k in data.t[idx]["dr"][f"h{heater}"]])
    dry = array([k[f"drt{thermoresistance}"].y_avg for k in data.t[idx]["dr"][f"h{heater}"]])
    dry_err = array([k[f"drt{thermoresistance}"].y_stddev for k in data.t[idx]["dr"][f"h{heater}"]])

    return temperature, i, drdc, drdc_err, drx, drx_err, dry, dry_err


def calculate_temperatures(drdc, drdc_err, drx, drx_err, dry, dry_err, fit):

    dtx = drx / fit[0]
    dtx_err = sqrt((drx_err / fit[0]) ** 2 + (-drx / fit[0] ** 2 * fit[4]) ** 2)
    dty = dry / fit[0]
    dty_err = sqrt((dry_err / fit[0]) ** 2 + (-dry / fit[0] ** 2 * fit[4]) ** 2)
    dtdc = (drdc - drdc[0]) / fit[0]
    dtdc_err = sqrt((drdc_err / fit[0]) ** 2 + (drdc_err / fit[0]) ** 2 + ((drdc - drdc_err) / fit[0] * fit[4]) ** 2)

    return dtdc, dtdc_err, dtx, dtx_err, dty, dty_err


def sinfunc(x, a, b, c, r, dr):
    # x: frequency
    # a: effective thermal diffusivity
    # b: power dissipated per unit length
    # c: effective thermal conductivity = K * m * cv
    return b / (4 * np.pi * c) * (np.imag(kv(0, np.sqrt(1j * 2 * (2 * np.pi * x) / a) * r) -
                                          kv(0, np.sqrt(1j * 2 * (2 * np.pi * x) / a) * (r + dr))))


def cosfunc(x, a, b, c, r, dr):
    # x: frequency
    # a: effective thermal diffusivity
    # b: power dissipated per unit length
    # c: effective thermal conductivity = K * m * cv
    return - b / (4 * np.pi * c) * (np.real(kv(0, np.sqrt(1j * 2 * (2 * np.pi * x) / a) * r) -
                                            kv(0, np.sqrt(1j * 2 * (2 * np.pi * x) / a) * (r + dr))))

