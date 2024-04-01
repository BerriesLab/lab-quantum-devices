'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 2
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
'Gt_18b: ramps voltage on AO1, recording voltage on AI 1-4

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
'PAR_36 = stop flag

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
'#INCLUDE C:\Users\lab405\Desktop\Lakeshore-ADwin-GoldII\Matlab\ADwin_script\Additional_functions.Inc

DIM DATA_1[2000000] as float  'averaged AI1 bin array
DIM DATA_2[2000000] as float  'averaged AI2 bin array
DIM DATA_3[2000000] as float  'averaged AI3 bin array
DIM DATA_4[2000000] as float
DIM DATA_5[2000000] as float
DIM DATA_6[2000000] as float
DIM DATA_7[2000000] as float
DIM DATA_8[2000000] as float
DIM DATA_9[2000000] as float  'time array

DIM sum1, sum2, sum3, sum4, sum5, sum6, sum7, sum8 as float
DIM idx_scan, idx_avg as long
Dim time_, time As Long

INIT:
  idx_avg = 0
  idx_scan = 1
  sum1 = 0
  sum2 = 0
  sum3 = 0
  sum4 = 0
  sum5 = 0
  sum6 = 0
  sum7 = 0
  sum8 = 0
  time_ = Read_Timer()
             
EVENT:
  
  'set multiplexer to read AI1 and AI2
  Set_Mux1(00000b) 'set MUX1
  Set_Mux2(00000b) 'set MUX1
  IO_Sleep(200)
  'read data
  START_CONV(11b)
  WAIT_EOC(11b)
  sum1 = sum1 + READ_ADC24(1)/64
  sum2 = sum2 + READ_ADC24(2)/64
      
  'set multiplexer to read AI3 and AI4
  Set_Mux1(00001b) 'set MUX1
  Set_Mux2(00001b) 'set MUX2
  IO_Sleep(200)
  'read data
  START_CONV(11b)
  WAIT_EOC(11b)
  sum3 = sum3 + READ_ADC24(1)/64
  sum4 = sum4 + READ_ADC24(2)/64
     
  'set multiplexer to read AI5 and AI6
  Set_Mux1(00010b) 'set MUX1
  Set_Mux2(00010b) 'set MUX2
  IO_Sleep(200)
  'read data
  START_CONV(11b)
  WAIT_EOC(11b)
  sum5 = sum5 + READ_ADC24(1)/64
  sum6 = sum6 + READ_ADC24(2)/64
      
  'set multiplexer to read AI7 and AI8
  Set_Mux1(00011b) 'set MUX1
  Set_Mux2(00011b) 'set MUX2
  IO_Sleep(200)
  'read data
  START_CONV(11b)
  WAIT_EOC(11b)
  sum7 = sum7 + READ_ADC24(1)/64
  sum8 = sum8 + READ_ADC24(2)/64
        
  ' update index average
  inc(idx_avg)
      
  'If summed PAR_33 samples, get average values
  IF(idx_avg = PAR_33) THEN
    
    'update time
    time = Read_Timer()  ''Process time in clock pulses
    DATA_9[idx_scan] = (time - time_) * 25 * 1E-9  
    time_ = time
    
    'average data1 and data2
    DATA_1[idx_scan]= sum1 / PAR_33
    DATA_2[idx_scan]= sum2 / PAR_33
    sum1 = 0
    sum2 = 0
       
    'average data3 and data4 
    DATA_3[idx_scan]= sum3 / PAR_33
    DATA_4[idx_scan]= sum4 / PAR_33
    sum3 = 0
    sum4 = 0
        
    'average data5 and data6
    DATA_5[idx_scan]= sum5 / PAR_33
    DATA_6[idx_scan]= sum6 / PAR_33
    sum5 = 0
    sum6 = 0
        
    'average data7 and data8
    DATA_7[idx_scan]= sum7 / PAR_33
    DATA_8[idx_scan]= sum8 / PAR_33
    sum7 = 0
    sum8 = 0
        
    'increment index scan and relative parameter         
    inc(idx_scan)
    PAR_35 = idx_scan
        
    'reset index average
    idx_avg = 0
    
    IF (idx_scan = PAR_71 + 1) THEN end
            
  ENDIF
