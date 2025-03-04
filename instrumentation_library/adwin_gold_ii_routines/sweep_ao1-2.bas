'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 7
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.3.1
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = DDM05677  EMPA\dabe
'<Header End>
' AO1_read_AI_18b.bas: ramps voltage on AO1, recording voltage on AI 1-4


'General input-output parameters (1-29):
'PAR_1 = active analog input (0000000000000010b -> 2 for input 2 ON and all the others OFF)
'PAR_2 = active analog output (00000011b -> 3 for inputs 1 and 2 ON)

'ADC-DAC parameters (31-40):
'PAR_31 = ADC resolution
'PAR_32 = DAC resolution
'PAR_33 = number of points to average in-hardware
'PAR_34 = number of loops to wait after setting analog output
'PAR_35 = scan index (current scan, the number of acquisitions completed is PAR_35-1)

'process parameters (41-80):
'PAR_41 = length of analog output arrays (all arrays must be the same length)

'PAR_51 = current analog output 1 value
'PAR_52 = current analog output 2 value


#INCLUDE ADwinGoldII.inc

'AI arrays: 1-16
DIM DATA_1[50000] as float  'AI1 data arrays - (bin values)
DIM DATA_2[50000] as float  'AI2 data arrays - (bin values)
DIM DATA_3[50000] as float  'AI3 data arrays - (bin values)
DIM DATA_4[50000] as float  'AI4 data arrays - (bin values)
DIM DATA_5[50000] as float  'AI5 data arrays - (bin values)
DIM DATA_6[50000] as float  'AI6 data arrays - (bin values)
DIM DATA_7[50000] as float  'AI7 data arrays - (bin values)
DIM DATA_8[50000] as float  'AI8 data arrays - (bin values)
DIM DATA_9[50000] as float  'AI9 data arrays - (bin values)
DIM DATA_10[50000] as float  'AI0 data arrays - (bin values)
DIM DATA_11[50000] as float  'AI11 data arrays - (bin values)
DIM DATA_12[50000] as float  'AI12 data arrays - (bin values)
DIM DATA_13[50000] as float  'AI13 data arrays - (bin values)
DIM DATA_14[50000] as float  'AI14 data arrays - (bin values)
DIM DATA_15[50000] as float  'AI15 data arrays - (bin values)
DIM DATA_16[50000] as float  'AI16 data arrays - (bin values)
'AO arrays: 21-28
DIM DATA_21[50000] as long   'AO1 data arrays - (bin values)
DIM DATA_22[50000] as long   'AO2 data arrays - (bin values)
DIM DATA_23[50000] as long   'AO3 data arrays - (bin values)
DIM DATA_24[50000] as long   'AO4 data arrays - (bin values)
DIM DATA_25[50000] as long   'AO5 data arrays - (bin values)
DIM DATA_26[50000] as long   'AO6 data arrays - (bin values)
DIM DATA_27[50000] as long   'AO7 data arrays - (bin values)
DIM DATA_28[50000] as long   'AO8 data arrays - (bin values)
'other arrays
DIM DATA_31[50000] as long   'time array

DIM flag1, flag2, flag as long
DIM sum1, sum2 as float
DIM idx_avg, idx_wait as long
DIM idx_scan as long  'index of current scan
DIM v1, v2 as long
DIM bin as long

INIT:
  flag = 0 'to start measurement directly after start voltage is reached, then increase output 
  flag1 = 0
  flag2 = 0
  idx_avg = 0
  idx_wait = 0
  idx_scan = 1
  sum1 = 0
  sum2 = 0
  
  Set_Mux1(00000b) 'set MUX1
  Set_Mux2(00000b) 'set MUX2
  IO_Sleep(200)  'wait 2us (200 * 10ns)
  
  PAR_35 = idx_scan 
  
  v1 = DATA_21[1]
  v2 = DATA_22[1]
  DAC(1, v1)  'set AO1 to first value
  DAC(2, v2)  'set AO2 to first value
  PAR_51 = v1
  PAR_52 = v2
  
     
EVENT:

  SELECTCASE flag '0 = ramp to next voltage point ; 1 = wait
  
    CASE 0 'set analog output --------------------------------
      
      'increment/decrement ao1 bin value
      IF (idx_scan <= PAR_41) THEN
        
        IF (v1 < DATA_21[idx_scan]) THEN INC(v1)      
        IF (v1 > DATA_21[idx_scan]) THEN  DEC(v1)
        IF (v1 = (DATA_21[idx_scan])) THEN flag1 = 1
        PAR_51 = v1
        DAC(1, v1)
        
        IF (v2 < DATA_22[idx_scan]) THEN INC(v2)      
        IF (v2 > DATA_22[idx_scan]) THEN  DEC(v2)
        IF (v2 = (DATA_22[idx_scan])) THEN flag2 = 1
        PAR_52 = v2
        DAC(2, v2)
        
        IF (flag1 * flag2 = 1) THEN 
          flag1 = 0
          flag2 = 0
          flag = 1
        ENDIF   
      ENDIF     
      
    CASE 1 'wait --------------------------------
        
      IF(idx_wait = PAR_34) THEN
        flag = 0
        idx_wait = 0
        idx_avg = 0
      ELSE
        idx_wait = idx_wait + 1
      ENDIF
              
  ENDSELECT
  
FINISH:
  'set analog output if analog output is active
  DAC(1, DATA_21[PAR_41])
  DAC(2, DATA_22[PAR_41])
