from Objects.measurement import FET
from numpy import loadtxt, linspace, concatenate, shape

def convert_gate_sweep_to_fet(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        flag = False

        for line in lines:  # extract gate parameters
            if line == "<Gate Parameters>\n":
                flag = True
            elif line == "</Gate Parameters>\n":
                flag = False
                break
            if flag is True and "U Start [V]" in line:
                vgs_start = float(line.split()[-1])
            if flag is True and "U End [V]" in line:
                vgs_end = float(line.split()[-1])
            if flag is True and "U Max [V]" in line:
                vgs_max = float(line.split()[-1])
            if flag is True and "U Min [V]" in line:
                vgs_min = float(line.split()[-1])
            if flag is True and "dU [V]" in line:
                vgs_dv = float(line.split()[-1])

        for line in lines:  # extract bias parameters
            if line == "<Bias parameters>\n":
                flag = True
            elif line == "</Bias parameters>\n":
                flag = False
                break
            if flag is True and "U Start [V]" in line:
                vds_start = float(line.split()[-1])
            if flag is True and "U End [V]" in line:
                vds_end = float(line.split()[-1])
            if flag is True and "U Max [V]" in line:
                vds_max = float(line.split()[-1])
            if flag is True and "U Min [V]" in line:
                vds_min = float(line.split()[-1])
            if flag is True and "dU [V]" in line:
                vds_dv = float(line.split()[-1])

        for line in lines:  # extract IV parameters
            if line == "<IV Parameters>\n":
                flag = True
            elif line == "</IV Parameters>\n":
                flag = False
                break
            if flag is True and "U Start [V]" in line:
                iv_start = float(line.split()[-1])
            if flag is True and "U Min [V]" in line:
                iv_min = float(line.split()[-1])
            if flag is True and "U Max [V]" in line:
                iv_max = float(line.split()[-1])
            if flag is True and "Nr. Points" in line:
                iv_n = float(line.split()[-1])

    if vgs_max == vgs_min:
        vgs = [vgs_start, vgs_max, 1, 0, 0, 1]
    else:
        vgs = [vgs_start, vgs_max, int(abs((vgs_start - vgs_max) / vgs_dv) + 1), 0, 2, 1]

    if vds_max == vds_min:
        vds = [vds_max, vds_max, 1, 0, 0, 1]
    else:
        vds = [vds_start, vds_max, int(abs((vds_start - vds_max) / vds_dv) + 1), 0, 2, 1]

    data = loadtxt(filename, skiprows=77)

    fet = FET.Sweep(vgs, vds)
    for j in range(shape(fet.data)[1]):
        for i in range(shape(fet.data)[0]):
            fet.data[i, j, 0] = fet.vgs[i]
            fet.data[i, j, 2] = fet.vds[0]
            fet.data[i, j, 3] = data[i, 1]
    return fet

#data = convert_gate_sweep_to_fet("C:\Data\osja_gfet_00\GateSweep_Data\GateSweepData_C01_R01_P01.dat")