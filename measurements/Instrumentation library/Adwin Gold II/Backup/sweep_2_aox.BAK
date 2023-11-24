'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 6.3.0
' Optimize                       = Yes
' Optimize_Level                 = 1
' Stacksize                      = 1000
' Info_Last_Save                 = DDM06513  EMPA\Lab405
'<Header End>
' AO1_read_AI_18b.bas: ramps voltage on AO1, recording voltage on AI 1-4

'General input parameters (1-16):
'PAR_1 =  analog input 1 status (0: off, 1: on)
'PAR_2 =  analog input 2 status (0: off, 1: on)
'PAR_3 =  analog input 3 status (0: off, 1: on)
'PAR_4 =  analog input 4 status (0: off, 1: on)
'PAR_5 =  analog input 5 status (0: off, 1: on)
'PAR_6 =  analog input 6 status (0: off, 1: on)
'PAR_7 =  analog input 7 status (0: off, 1: on)
'PAR_8 =  analog input 8 status (0: off, 1: on)
'PAR_9 =  analog input 9 status (0: off, 1: on)
'PAR_10 = analog input 10 status (0: off, 1: on)
'PAR_11 = analog input 11 status (0: off, 1: on)
'PAR_12 = analog input 12 status (0: off, 1: on)
'PAR_13 = analog input 13 status (0: off, 1: on)
'PAR_14 = analog input 14 status (0: off, 1: on)
'PAR_15 = analog input 15 status (0: off, 1: on)
'PAR_16 = analog input 16 status (0: off, 1: on)

'General output parameters (21-28):
'PAR_21 = analog output 1 status (0: off, 1: on)
'PAR_22 = analog output 2 status (0: off, 1: on)
'PAR_23 = analog output 3 status (0: off, 1: on)
'PAR_24 = analog output 4 status (0: off, 1: on)
'PAR_25 = analog output 5 status (0: off, 1: on)
'PAR_26 = analog output 6 status (0: off, 1: on)
'PAR_27 = analog output 6 status (0: off, 1: on)
'PAR_28 = analog output 6 status (0: off, 1: on)

'ADC-DAC parameters (31-40):
'PAR_31 = ADC resolution
'PAR_32 = DAC resolution
'PAR_33 = number of points to average in-hardware
'PAR_34 = number of loops to wait after setting analog output
'PAR_35 = loop (scan) index

'iv and sweep ao process parameters (41-80):
'PAR_41 = length of analog output 1 array
'PAR_42 = length of analog output 2 array
'PAR_43 = length of analog output 3 array
'PAR_44 = length of analog output 4 array
'PAR_45 = length of analog output 5 array
'PAR_46 = length of analog output 6 array
'PAR_47 = length of analog output 7 array
'PAR_48 = length of analog output 8 array

'fixed ao parameters:
'PAR_51 = analog output 1 current value (in bins)
'PAR_52 = analog output 2 current value (in bins)

'read ai parameters (71-80):
'PAR_71 = length of time array

#INCLUDE ADwinGoldII.inc
'#INCLUDE C:\Users\lab405\Desktop\Lakeshore-ADwin-GoldII\Matlab\ADwin_script\Additional_functions.Inc

'AO data arrays (21-28)
DIM DATA_21[50000] as long    'AO1 - bin values
DIM DATA_22[50000] as long    'AO2 - bin values

DIM flag as long
DIM sum1, sum2 as float
DIM idx_avg, idx_wait, idx_scan as long
DIM v1, v2 as long
DIM bin1, bin2 as long

INIT:
  flag = 0 'to start measurement directly after start voltage is reached, then increase output 
  idx_avg = 0
  idx_wait = 0
  idx_scan = 1
  sum1 = 0
  sum2 = 0
  
  PAR_35 = idx_scan
  
  'set output to first value
  IF (PAR_21 = 1) THEN 
    PAR_51 = DATA_21[1]
    DAC(1, PAR_51)
  ENDIF
  
  IF (PAR_22 = 1) THEN 
    PAR_52 = DATA_22[1]    
    DAC(2, PAR_52)
  ENDIF
 
     
EVENT:

  SELECTCASE flag 'measurement: 0 = ramp to next voltage point ; 1 = wait
  
    CASE 0 'set analog output --------------------------------
      
      PAR_35 = idx_scan       'update PAR_35: scan index
      
      'increment/decrement ao1 bin value
      IF (PAR_21 = 1) THEN
        IF (idx_scan <= PAR_41) THEN
          IF (PAR_51 < DATA_21[idx_scan]) THEN INC(PAR_51)      
          IF (PAR_51 > DATA_21[idx_scan]) THEN  DEC(PAR_51)
          IF (PAR_51 = (DATA_21[idx_scan])) THEN flag = 1
          DAC(1, PAR_51)
        ENDIF
      ENDIF
      
      'increment/decrement ao2 bin value
      IF (PAR_22 = 1) THEN
        IF (idx_scan <= PAR_42) THEN
          IF (PAR_52 < DATA_22[idx_scan]) THEN INC(PAR_52)
          IF (PAR_52 > DATA_22[idx_scan]) THEN  DEC(PAR_52)
          IF (PAR_52 = (DATA_22[idx_scan])) THEN flag = 1
          DAC(2, PAR_52)
        ENDIF
      ENDIF              
      
      IF (idx_scan = max_long(PAR_41 + 1, PAR_42 + 1)) THEN 
        end
      ELSE
        idx_scan = idx_scan + 1
        flag = 1
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
  IF (PAR_21 = 1) THEN DAC(1, PAR_51)
  IF (PAR_22 = 1) THEN DAC(2, PAR_52)
