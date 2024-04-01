'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
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

'General input-output parameters (1-16):
'PAR_1 = active analog inputs (0000000000000010b -> 2 for input 2 ON and all the others OFF)
'PAR_2 = active analog outputs (00000011b -> 3 for inputs 1 and 2 ON)

'ADC-DAC parameters (31-40):
'PAR_31 = ADC resolution
'PAR_32 = DAC resolution
'PAR_33 = number of points to average in-hardware
'PAR_34 = number of loops to wait after setting analog output
'PAR_35 = scan index (the number of acquisitions completed is PAR_35-1)

'iv process parameters (41-80):
'PAR_41 = length of analog output 1 array
'PAR_42 = length of analog output 2 array
'PAR_43 = length of analog output 3 array
'PAR_44 = length of analog output 4 array
'PAR_45 = length of analog output 5 array
'PAR_46 = length of analog output 6 array
'PAR_47 = length of analog output 7 array
'PAR_48 = length of analog output 8 array

'PAR_51 = current analog output 1
'PAR_52 = current analog output 2

'read ai parameters (71-80):
'PAR_71 = length of time array

#INCLUDE ADwinGoldII.inc

'AI data arrays (1-16)
DIM DATA_11[50000] as float    'AI1
DIM DATA_12[50000] as float    'AI2

'AO data arrays (21-28)
DIM DATA_21[50000] as long    'AO1 - bin values
DIM DATA_22[50000] as long    'AO2 - bin values

DIM flag as long
DIM sum1, sum2 as float
DIM idx_avg, idx_wait as long
DIM idx_scan as long  'index of current scan
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
  v1 = DATA_21[1]
  v2 = DATA_22[1]
  IF (PAR_2 = 1 OR PAR_2 = 3) THEN 
    DAC(1, v1)
    PAR_51 = v1
  ENDIF
  IF (PAR_2 = 2 OR PAR_2 = 3) THEN 
    DAC(2, v2)
    PAR_52 = v2
  ENDIF
  
  'set multiplexer to read AI 1-2
  Set_Mux1(00000b) 'set MUX1
  Set_Mux2(00000b) 'set MUX2
  IO_Sleep(200)

     
EVENT:

  SELECTCASE flag '0 = ramp to next voltage point ; 1 = wait ; 2 = measure 
  
    CASE 0 'set analog output --------------------------------
      
      'increment/decrement ao1 bin value
      IF (PAR_2 = 1 OR PAR_2 = 3) THEN
        IF (idx_scan <= PAR_41) THEN
          IF (v1 < DATA_21[idx_scan]) THEN INC(v1)      
          IF (v1 > DATA_21[idx_scan]) THEN  DEC(v1)
          IF (v1 = (DATA_21[idx_scan])) THEN flag = 1
          PAR_51 = v1
          DAC(1, v1)
        ENDIF
      ENDIF
      
      'increment/decrement ao2 bin value
      IF (PAR_2 = 2 OR PAR_2 = 3) THEN
        IF (idx_scan <= PAR_42) THEN
          IF (v2 < DATA_22[idx_scan]) THEN INC(v2)
          IF (v2 > DATA_22[idx_scan]) THEN  DEC(v2)
          IF (v2 = (DATA_22[idx_scan])) THEN flag = 1
          PAR_52 = v2
          DAC(2, v2)        
        ENDIF
      ENDIF              
      
    CASE 1 'wait --------------------------------
      
      IF(idx_wait = PAR_34) THEN
        flag = 2
        idx_wait = 0
        idx_avg = 0
      ELSE
        idx_wait = idx_wait + 1
      ENDIF
      
      
    CASE 2 'measure --------------------------------
        
      'read data
      START_CONV(11b)
      WAIT_EOC(11b)
        
      sum1 = sum1 + READ_ADC24(1)/64
      sum2 = sum2 + READ_ADC24(2)/64
  
      idx_avg = idx_avg + 1
      
      'if reached number of samples to average      
      IF(idx_avg = PAR_33) THEN 
        'get average values
        IF (idx_scan <= PAR_41) THEN 
          DATA_11[idx_scan] = sum1 / PAR_33 
          sum1 = 0
        ENDIF       
        IF (idx_scan <= PAR_42) THEN 
          DATA_12[idx_scan] = sum2 / PAR_33
          sum2 = 0
        ENDIF        
                
        flag = 0                  'set flag to 0
        idx_scan = idx_scan + 1 'update scan index
        PAR_35 = idx_scan       'update PAR_35: scan index
        
        'stop when reached end of vector
        IF (idx_scan = max_long(PAR_41 + 1, PAR_42 + 1)) THEN end 
        
      ENDIF
    
  ENDSELECT
  
FINISH:
  'set analog output if analog output is active
  IF (PAR_2 = 1 OR PAR_2 = 3) THEN DAC(1, DATA_21[PAR_41])
  IF (PAR_2 = 2 OR PAR_2 = 3) THEN DAC(2, DATA_22[PAR_42])
