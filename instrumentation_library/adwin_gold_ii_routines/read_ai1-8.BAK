'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 4
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
'Gt_18b: ramps voltage on AO1, recording voltage on AI 1-4

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
'PAR_41 = length of AI and AO arrays (all arrays must be the same length)

'PAR_51 = current analog output 1 value
'PAR_52 = current analog output 2 value

'read ai parameters (71-80):
'PAR_71 = length of time array


#INCLUDE ADwinGoldII.inc
'#INCLUDE C:\Users\lab405\Desktop\Lakeshore-ADwin-GoldII\Matlab\ADwin_script\Additional_functions.Inc

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
    DATA_31[idx_scan] = (time - time_) * 25 * 1E-9  
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
    
    IF (idx_scan = PAR_41 + 1) THEN end
            
  ENDIF
