'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 3
' Initial_Processdelay           = 3000
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
' fixed_voltage.bas: ramps voltage

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

'iv process parameters (41-80):
'PAR_41 = length of analog output 1 array
'PAR_42 = length of analog output 2 array
'PAR_43 = length of analog output 3 array
'PAR_44 = length of analog output 4 array
'PAR_45 = length of analog output 5 array
'PAR_46 = length of analog output 6 array
'PAR_47 = length of analog output 7 array
'PAR_48 = length of analog output 8 array

'fixed ao parameters:
'PAR_51 = analog output 1 initial bin
'PAR_52 = analog output 1 setpoint bin
'PAR_53 = analog output 2 initial bin
'PAR_54 = analog output 2 setpoint bin
'PAR_55 = analog output 3 initial bin
'PAR_56 = analog output 3 setpoint bin
'PAR_57 = analog output 4 initial bin
'PAR_58 = analog output 4 setpoint bin
'PAR_59 = analog output 5 initial bin
'PAR_60 = analog output 5 setpoint bin
'PAR_61 = analog output 6 initial bin
'PAR_62 = analog output 6 setpoint bin
'PAR_63 = analog output 7 initial bin
'PAR_64 = analog output 7 setpoint bin
'PAR_65 = analog output 8 initial bin
'PAR_66 = analog output 8 setpoint bin

'read ai parameters (71-80):
'PAR_71 = length of time array
 

#INCLUDE ADwinGoldII.inc

DIM v1, v2, idx_wait, flag as long

INIT:
  
  flag = 0 
  idx_wait = 0 
  
  IF (PAR_1 = 1) THEN 
    v1 = PAR_51
    DAC(1, v1)
  ENDIF
  
  IF (PAR_2 = 1) THEN 
    v2 = PAR_53 
    DAC(2, v2)
  ENDIF
  
  
   
EVENT:
  
  SELECTCASE flag '0 = ramp to next voltage point ; 1 = wait 
    
    CASE 0
      
      IF (PAR_1 = 1) THEN
        IF (v1 < PAR_52) THEN INC(v1)      
        IF (v1 > PAR_52) THEN DEC(v1) 
        IF (v1 = PAR_52) THEN flag = 1
        DAC(1, v1)
      ENDIF
      
      IF (PAR_2 = 1) THEN
        IF (v2 < PAR_54) THEN INC(v2)      
        IF (v2 > PAR_54) THEN DEC(v2) 
        IF (v2 = PAR_54) THEN flag = 1
        DAC(2, v2)
      ENDIF
      
      flag = 1
      
    CASE 1
      
      IF(idx_wait = PAR_34) THEN
        idx_wait = 0
        flag = 0
        end
      ELSE
        idx_wait = idx_wait + 1
      ENDIF
  ENDSELECT
  
  
FINISH:
  IF (PAR_1 = 1) THEN DAC(1, PAR_52)  
  IF (PAR_2 = 1) THEN DAC(2, PAR_54)  
