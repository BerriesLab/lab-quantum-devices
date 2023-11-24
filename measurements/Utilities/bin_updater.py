#######################################################################
#   Author:         Davide Beretta
#   Date:           31.03.2021
#   Description:    load bin(s) file and add a parameter
#######################################################################

import os
import pickle

# region ----- USER inputs -----
main = r"R:\Scratch\405\dabe"    # [string] Main folder directory
data2load = [("tetra fet au p3ht", ["4wire d-20um"])]
# endregion

for chip_devices in data2load:  # run over the (chip, [devices]) tuples to load

    chip = chip_devices[0]
    devices = chip_devices[1]

    for device in devices:  # run over the devices to load

        experiments = os.listdir(rf"{main}\{chip}\{device}\fet\iv")
        experiments = [x for x in experiments if x.endswith(".data")]

        for experiment in experiments:  # run over the experiments to load

            # region ----- Load file -----
            path = rf"{main}\{chip}\{device}\fet\iv\{experiment}"
            with open(path, "rb") as file:
                data = pickle.load(file)
            print("Adding/modifying parameter... ", end="")
            data.data.channel_length = 20e-6
            print("Done.")
            print("Saving bin to disc... ", end="")
            with open(path, "wb") as f:
                pickle.dump(data, f)
            print("Done.")
# endregion
