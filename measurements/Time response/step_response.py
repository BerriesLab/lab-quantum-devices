import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import time
import pickle
import os
from datetime import datetime
import matplotlib.gridspec as gs
import matplotlib.colors

# I/V amplifier
iv_gain = 1e5 #

# oscilloscope
sec_div = 1e-6 # 500e-9
ch1_volt_div = 1   # 100 mV/div
ch2_volt_div = 2  # 100 mV/div

# wave generator
frequency = 1  # Hz
v_step = 2 # pp
v_offset = 1 # v_step/2
trigger_level = v_offset/2

# File saving settings
chip_id = "210127_Au(50)_Pentacene(120)_Al(50)"
device_id = "C8"
path = "C:/python/osja/experimental/Measurements/210127_Au(50)_Pentacene(120)_Al(50)/Time_response"       # saving directory
os.chdir( path )                                    # Change the directory
print("Current working directory " + os.getcwd())   # Check current working directory.

rm = visa.ResourceManager()
print(rm.list_resources())

wfg = rm.open_resource('GPIB1::10::INSTR')
osc = rm.open_resource('GPIB1::1::INSTR')
osc.timeout = None

# Get all the points from oscilloscope
Datastart = 1
Datastop = 2500

wfg.write("*RST")
wfg.write("APPLy:SQUare {}, {}, {}".format(frequency, v_step, v_offset))
wfg.write(":OUTP1:LOAD MAX")    # Load impedance
wfg.write(":OUTP1 ON")
wfg.write("*WAI")
time.sleep(3)

timeaxis = np.linspace(start=Datastart,stop=Datastop,num=Datastop,endpoint=True)

#osc.write("*RST")
osc.write("AUTOSet")

osc.write("TRIGger:MAIn:EDGE:SOUrce CH1") # trigger on ch1
osc.write("TRIGger:MAIn:EDGE:COUPling DC")
osc.write("TRIGger:MAIn:EDGE:SLOpe RISE")  # rise or fall
osc.write("TRIGger:MAIn:MODe AUTO") # NORMal or AUTO
osc.write("TRIGger:MAIn:TYPe EDGE")
osc.write("TRIGger:MAIn:LEVel {}".format(trigger_level))  # trigger to 50% of max min

osc.write("CH1:BANdwidth OFF")     # OFF 60 MHz, ON 20 MHz
osc.write("CH1:COUPling DC")
osc.write("CH1:INVert OFF")
osc.write("CH1:POSition 0")
osc.write("CH1:SCAle {}".format(ch1_volt_div))
#osc.write("CH1:PRObe 1")            # attenuation factor$
#osc.write("CH1:VOLts 1")  # gain

osc.write("CH2:BANdwidth OFF")     # OFF 60 MHz, ON 20 MHz
osc.write("CH2:COUPling DC")
osc.write("CH2:INVert OFF")
osc.write("CH2:POSition 0")
osc.write("CH2:SCAle {}".format(ch2_volt_div))
#osc.write("CH2:PRObe 1")            # attenuation factor$
#osc.write("CH2:VOLts 1")  # gain

osc.write("HORizontal:MAIn:SECdiv {}".format(sec_div))
osc.write("HORizontal:MAIn:POSition 0")

osc.write("*WAI")

osc.write("ACQuire:MODE SAMPLE")

#osc.write("ACQuire:MODE Average")
#osc.write("ACQuire:NUMAVg 64")   # 4 16 64 128
#osc.write("ACQuire:STOPAfter SEQuence")

#osc.write("DATa:WIDth 2")
osc.write("DATa:START {}".format(Datastart))
osc.write("DATa:STOP {}".format(Datastop))

osc.write("*WAI")

# osc.write("MEASUrement:MEAS1:SOUrce CH1")
# osc.write("MEASUrement:MEAS2:SOUrce CH2")
# osc.write("MEASUrement:MEAS1:TYPe RISe")
# osc.write("MEASUrement:MEAS2:TYPe RISe")

print(osc.query("*OPC?"))

while int(osc.query("*OPC?")) == 0:
    print(osc.query("*OPC?"))

osc.write("DATa:SOUrce CH1")
channel1_yrescale = float(osc.query("WFMPre:YMUl?"))
channel1_yoff = float(osc.query("WFMPre:YOFf?"))
channel1_yzero = float(osc.query("WFMPre:YZEro?"))
channel1_xrescale = float(osc.query("WFMPre?").split(";")[8])
channel1_xzero = float(osc.query("WFMPre:CH1:XZEro?"))
channel1_xincr = float(osc.query("WFMPre:CH1:XINcr?"))
channel1_xptoff = float(osc.query("WFMPre:CH1:PT_Off?"))
channel1_data = osc.query("curve?")
channel1_data = channel1_data.split(",")
channel1_data = [float(x) for x in channel1_data]
channel1_data = np.array(channel1_data)

osc.write("DATa:SOUrce CH2")
channel2_yrescale = float(osc.query("WFMPre:YMUl?"))
channel2_yoff = float(osc.query("WFMPre:YOFf?"))
channel2_yzero = float(osc.query("WFMPre:YZEro?"))
channel2_xrescale = float(osc.query("WFMPre?").split(";")[8])
channel2_xzero = float(osc.query("WFMPre:CH2:XZEro?"))
channel2_xincr = float(osc.query("WFMPre:CH2:XINcr?"))
channel2_xptoff = float(osc.query("WFMPre:CH2:PT_Off?"))
# channel2_xrescale = float(osc.query("WFMPre:CH1:XMUlt?"))
channel2_data = osc.query("curve?")
channel2_data = channel2_data.split(",")
channel2_data = [float(x) for x in channel2_data]
channel2_data = np.array(channel2_data)

channel1_data = channel1_data * channel1_yrescale
#channel1_data = (channel1_data - channel1_yoff) * channel1_yrescale + channel1_yzero
channel2_data = channel2_data * channel2_yrescale
#channel1_data = (channel1_data - channel1_yoff) * channel1_yrescale + channel1_yzero

#channel1_time = channel1_xrescale * timeaxis
channel1_time = channel1_xincr * (timeaxis - channel1_xptoff) + channel1_xzero
#channel2_time = channel2_xrescale * timeaxis
channel2_time = channel2_xincr * (timeaxis - channel2_xptoff) + channel2_xzero
#
# channel1_risetime = float(osc.query("MEASUrement:MEAS1:VALue?"))
# channel2_risetime = float(osc.query("MEASUrement:MEAS2:VALue?"))
# print("Rise time ch1: {}".format(channel1_risetime))
# print("Rise time ch2: {}".format(channel2_risetime))

time.sleep(1)
wfg.write(":OUTP1 OFF")

now = datetime.now()
filename = "{}_chip_{}_device_{}".format(now.strftime("%Y-%m-%d_%Hh%Mh%Ss"), chip_id, device_id)
with open(filename + str(".bin"), "wb") as file:
    pickle.dump({"chip": chip_id,
                 "device": device_id,
                 "datetime": now,
                 "data": {"ch1_time": channel1_time, "ch2_time": channel2_time, "ch1_data": channel1_data, "ch2_data": channel2_data},
                 "settings": ""}, file)


fig = plt.figure(figsize=[12.8, 9.6], dpi=100, facecolor=None, edgecolor=None, linewidth=0.0, frameon=None, subplotpars=None, tight_layout=None, constrained_layout=None)
gs = gs.GridSpec(2, 1)
ax1 = fig.add_subplot(gs[0,0])
ax1.set_xlabel('t [s]')
ax1.set_ylabel('V [A]')
ax2 = fig.add_subplot(gs[1,0])
ax2.set_xlabel('t [s]')
ax2.set_ylabel('I [A]')
c = matplotlib.cm.get_cmap("RdYlBu_r")

ax1.plot(channel1_time, channel1_data, label="CH1", marker='o', alpha=0.3)
ax2.plot(channel2_time, channel2_data / iv_gain, label="CH2", marker='o', alpha=0.3)
ax1.legend()
ax2.legend()
plt.savefig(fname=filename + str(".png"), format="png")

plt.show()




