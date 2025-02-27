'''
Classes for Hardware Modules of MRexcite system are defined and initialized here.
-------------------------------------------------------------------------------'''
import math
import numpy as np
import scipy
import ft4222
from ft4222.SPI import Cpha, Cpol
from ft4222.SPIMaster import Mode, Clock, SlaveSelect
import os
import configparser
import csv

import scipy.interpolate

### Main Class ###
class MRexcite_SystemObj: #This Object will contain all other hardware specific objects.
    '''Here we combine all classes to have a single object for the MRexcite System.'''
    def __init__(self,config):

        if config['DEFAULT']['Modulator_Module'] == 'true':
            self.Modulator = ModulatorObj(config)
        
        if config['DEFAULT']['Enable_Module'] == 'true':
            self.EnableModule = EnableObj(config)

        if config['DEFAULT']['Optical_Module'] == 'true':
            self.OpticalModule = OpticalObj(config)

        if config['DEFAULT']['RF_prep_Module'] == 'true':
            self.RFprepModule = RFprepObj(config)
        
        if config['DEFAULT']['Trigger_Module'] == 'true':
            self.TriggerModule = TriggerObj(config)

 
        try:
            if config['DEFAULT']['USB2SPI_Module'] == 'true':
                try:
                    self.SPI = USB2SPIObj(config)
                    print('FT4222 connected.')
                except:
                    print('<p>Error accessing FT4222! Make sure to connect to USB.</p>')
                    quit()
        except:
            pass
    def enable_system(self):
        self.SPI.send_bitstream(bytes([128,0,0,0]))
    def setup_system(self):
        self.TimingControl.trigger_off() #Trigger needs to be switched off before programming Modulators, because trigger is used to select adress.
        bytestream = self.TimingControl.return_byte_stream()
        self.TimingControl.trigger_on() #Trigger can be switched on again after programming Modulators.
        bytestream = bytestream + self.SignalSource.return_byte_stream() + self.Modulator.return_byte_stream() + self.TimingControl.return_byte_stream() + bytes([0,0,0,0])
        self.SPI.send_bitstream(bytestream)    
    def disable_system(self):
        try:
            self.SPI.send_bitstream(bytes([0,0,0,0]))
        except:
            print('Error: Could not transmit via SPI!')

### Helper Classes ###
class PulseObj:
    '''This is a Pulse Object for saving/loading pulses to/from files.'''
    Amplitudes=[]
    Phases=[]
    States=[]

class ControlByteObj: #Contains the control bits. Select the state and add for complete control byte. I introduced this for better readability of code.
    '''This class contains some constants that make the code in this module more readable.'''
    chip0=0 #Important: Use only one chip at a time!
    chip1=1
    chip2=2
    chip3=3
    prog=4 #Set System to programming mode
    reset=8 #Reset Modulator Counters
    clock=16 #Trigger Modulator Counters
    we=32 #Write to Latch/SRAM
    #64 (7th bit) is reserved for future use
    enable=128 #Enable system. This enables the Unblank Signal for the Amplifiers. If this is not set, no signal can come from the amplifiers
    def __init__(self):
        pass
    def chip(self,c): #Another option to define chip. 0-3
        '''chip(c) simply returns c.'''
        return int(c)

### Hardware Representation Classes ###
class USB2SPIObj: #Contains all data and methods for USB2SPI hardware. (Communication between PC and MRexcite Hardware)
    '''This class contains all methods to send bit streams through a FT4222 in SPI mode.'''
    def __init__(self,config):
        
        #Open device with default Name
        self.devA = ft4222.openByDescription('FT4222 A')
        
        #Configure Device for SPI (We allow different clock speeds according to config file)
        if config['SPI_config']['clock_divider'] == '8':
            print('SPI Clock devider: 8')
            self.devA.spiMaster_Init(Mode.SINGLE, Clock.DIV_8, Cpha.CLK_LEADING, Cpol.IDLE_LOW, SlaveSelect.SS0)
        elif config['SPI_config']['clock_divider'] == '4':
            self.devA.spiMaster_Init(Mode.SINGLE, Clock.DIV_4, Cpha.CLK_LEADING, Cpol.IDLE_LOW, SlaveSelect.SS0)
        else:
            self.devA.spiMaster_Init(Mode.SINGLE, Clock.DIV_16, Cpha.CLK_LEADING, Cpol.IDLE_LOW, SlaveSelect.SS0)
    
    def send_bitstream(self, bitstream): #Write bit stream. Input variable is actually a row of 4*N bytes.
        '''This method sends a bitstream via the SPI interface.\n
        The input variable "bitstream" is a list of 4*N bytes.\n
        The order is: \n
            Control byte\n
            Address byte\n
            Data byte 2 (with most significant of 16 bits)\n
            Data byte 1 (with least significant of 16 bits)\n'''
        #In the following, the data in bitstream is sliced. This is necessary, as to long streams are cut by the FT4222's driver without notice.
        max_num_bytes=400
        stream_length=len(bitstream)
        number_of_steps=int(np.ceil(stream_length/max_num_bytes))
        for a in range(number_of_steps):
            if (a+1)*max_num_bytes<stream_length:
                bitstream_send=bitstream[a*max_num_bytes:(a+1)*max_num_bytes]
            else:
                bitstream_send=bitstream[a*max_num_bytes:stream_length]
            self.devA.spiMaster_SingleWrite(bitstream_send, True)


    '''Contains all data and methods for Timing Control Board'''
    
    ### Attributes ###
    con_mode = 0 #Continous Mode or intermittant mode (Tx/Rx)
    mod_res_sel = 0 #Select whether to reset modulators via Tx/Rx (1) or their own counters (0)
    ubl_enable = 1 #Enable unblank
    trig = 0 #Trigger from clock disabled/enabled
    clock_divider = 100 #Clock Divider for 10 MHz clock.
    counter_Rx = 255 #Rx will last this many clock cycles
    counter_Tx = 255 #Tx will last this many clock cycles
    
    ### Methods ###
    def __init__(self,config):
        self.address = int(config['DEFAULT']['timing_control_address']) #Physical Address for TimingControl
    
    def set_continous_mode(self):
        '''Set the variable for Continous Transmit Mode to enable.'''
        self.con_mode = 1
   
    def set_alternating_mode(self):
        '''Set the variable for Continous Transmit Mode to disable. System will be alternating between Tx and "Rx"'''
        self.con_mode = 0
    
    def switch_off(self):
        self.ubl_enable = 0
    
    def switch_on(self):
        self.ubl_enable = 1
    
    def trigger_on(self):
        self.trig = 1

    def trigger_off(self):
        self.trig = 0
    
    def return_byte_stream(self):
        '''Returns list of bytes to be transmitted via SPI interface. 
        The list of bytes provides the correct sequence to program the hardware to the settings in this object.'''
        CB = ControlByteObj() #For improved readability use the object CB to gerenate the control bits.
        byte_stream = [CB.prog, 0, 0, 0] #Initiate by setting system into write mode.
        for a in range(4): #Timing Control contains 4 registers.
            match a:
                case 0: #State Register
                    data1 = self.con_mode + 2* self.mod_res_sel + 4* self.ubl_enable + 8*self.trig #First four bits
                    data2 = 0 #Not used
                case 1: #Register for Clock Devider
                    data1=self.clock_divider%256
                    data2=math.floor(self.clock_divider/256)
                case 2: #Register for Tx Counter
                    data1=self.counter_Tx%256
                    data2=math.floor(self.counter_Tx/256)
                case 3: #Register for Rx Counter
                    data1=self.counter_Rx%256
                    data2=math.floor(self.counter_Rx/256)
            byte_stream_add = [CB.prog + CB.chip(a), self.address, data2, data1,
                               CB.prog + CB.we + CB.chip(a), self.address, data2, data1,
                               CB.prog + CB.chip(a), self.address, data2, data1]
            byte_stream = byte_stream + byte_stream_add
        byte_stream=byte_stream + [CB.prog, 0, 0, 0]
        data = bytes(byte_stream)
        return data
    
    def return_timings(self): #Calculate and return timings
        '''Calculates and prints timings Terminal'''
        clock_f=10e6/self.clock_divider
        t_Rx=self.counter_Rx/clock_f
        t_Tx=self.counter_Tx/clock_f
        duty_cycle = t_Tx/(t_Rx+t_Tx)*100
        print('Clock Frequency: ' + str(clock_f/1000) + 'kHz')
        print('Transmit Time: ' + str(t_Tx*1000) + 'ms')
        print('*Receive* Time: ' + str(t_Rx*1000) + 'ms')
        print('Duty Cycle: ' + str(duty_cycle) + '%')

class ModulatorObj: #Contains all data and methods for Modulators
    '''Contains all data and methods for Modulator board. This also includes calibration data.'''
    
    def __init__(self,config):
        '''Initialize Modulator Object with standard values and values from config file.'''
        self.number_of_channels = int(config['DEFAULT']['number_of_channels']) #Number of modulators in system.
        self.start_address = int(config['DEFAULT']['start_channel']) #address of first modulator, others are counted upwards from here.
        self.counter_max = [1] * self.number_of_channels #Maximum of value of counter in modulator. On this number, it switches back to 0
        self.I_values = [0] * self.number_of_channels #In phase value for Modulator
        self.Amp_state = [0] * self.number_of_channels #Amplifier state (high(1) and low(0) voltage)
        self.Q_values = [0] * self.number_of_channels #Quadrature value for Modulator
        self.amplitudes = [10] *self.number_of_channels #Amplitudes of all channels
        self.phases = [0] * self.number_of_channels #Phases of all channels
        
        for a in range(self.number_of_channels):
            self.I_values[a] = [pow(2,14)-1]*self.counter_max[a]
            self.Q_values[a] = [pow(2,13)-1]*self.counter_max[a]
            self.Amp_state[a] = [0]*self.counter_max[a]
        
        #Initialize Variables for I/Q offset
        self.IQoffset = [0]*self.number_of_channels
        for a in range(self.number_of_channels):
            self.IQoffset[a]=[0]*2
        self.f_name_CalZP=os.path.dirname(__file__) + '/' + config['Calibration']['Calibration_File_Zero_Point'] #Get file name for Zero Calibration from Config file.
        try:
            self.read_IQ_offset() #Read the Offset values from thr IQ-Offset file.
        except:
            print('Could not open IQ offset calibration file. Using no offset.')
        
        #Initialize Variables for Linearity Calibration
        self.number_of_1D_samples=12
        Dig_Values = [0, 250, 500, 750, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500]
        for a in range(self.number_of_1D_samples):
            Dig_Values[a]=round(4500/self.number_of_1D_samples*a)

        self.Cal1D = np.zeros((self.number_of_channels,2,self.number_of_1D_samples,3)) #Number of Channels, Number of power modes (high/low), number of test samples, 3 (digital value, voltage, phase)
        self.voltageHigh=int(config['Amplifiers']['max_amplitude_high'])
        self.voltageLow=int(config['Amplifiers']['max_amplitude_low'])
        for a in range(self.number_of_1D_samples): #Define standard values for Calibration in case no calibration file is found.
            self.Cal1D[:,1,a,0] = Dig_Values[a] #Generic digital values
            self.Cal1D[:,0,a,0] = round(Dig_Values[a]/5) #Generic digital values
            self.Cal1D[:,0,a,1] = self.voltageLow /2500 * Dig_Values[a] #generic voltage values low power mode
            self.Cal1D[:,1,a,1] = self.voltageHigh/4500 * Dig_Values[a] #generic voltage values high power mode
            self.Cal1D[:,:,:,2] = 0 #No phase error

        self.f_name_Cal1D=os.path.dirname(__file__) + '/' + config['Calibration']['Calibration_File_1D'] #Get file name for Zero Calibration from Config file.
        try:
            self.read_1D_Cal() #Read the 1D linearity calibration data from file.
        except:
            print('Could not open 1D Linearity calibration file. Using generic data.')
    
    
    def read_IQ_offset(self):
        '''Reads the IQ offset from calibration file which is specified in the config file.'''
        with open(self.f_name_CalZP,'r') as f:
            reader = csv.reader(f, delimiter=',')
            a=0
            for row in reader:  #Read total file row by row. First value is I offset, second value is Q offset.
                self.IQoffset[a][0]=int(row[0])
                self.IQoffset[a][1]=int(row[1])
                a=a+1
    def read_1D_Cal(self):
        '''Reads the 1D calibration data file which is specified in the config file.'''
        self.Cal1D = np.load(self.f_name_Cal1D)

    def write_IQ_offset(self):
        '''Saves the current IQ offset to the calibration file which is specified in the config file.'''
        with open(self.f_name_CalZP, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerows(self.IQoffset)

    def write_1D_Cal(self):
        '''Saves the current 1D calibration data to file specified in config file.'''
        np.save(self.f_name_Cal1D,self.Cal1D)
    
    def prepare_1D_Cal(self):
        '''Prepares the Pchip-Interpolators for 1D Amplitude and Phase correction\n
        For each channel and each amplifier mode there is a fixed set of polynomials, which is prepared in this function, so that the polynomials do not have to be calculated again and again.'''
        
        self.pchip_objects_amplitude=[0]*self.number_of_channels #Prepare list of Pchip Objects
        self.pchip_objects_phase=[0]*self.number_of_channels #Prepare list of Pchip Objects

        for channel in range(self.number_of_channels):
            self.pchip_objects_amplitude[channel]=[]
            self.pchip_objects_phase[channel]=[]
            for amp_mode in range(2): #Toggle the two modes (low and high power)
            #Amplitude
                xi=self.Cal1D[channel,amp_mode,:,1]
                yi=self.Cal1D[channel,amp_mode,:,0]
                self.pchip_objects_amplitude[channel].append(scipy.interpolate.PchipInterpolator(xi,yi))
            #Phase
                xi=self.Cal1D[channel,amp_mode,:,0]
                yi=self.Cal1D[channel,amp_mode,:,2]
                self.pchip_objects_phase[channel].append(scipy.interpolate.PchipInterpolator(xi,yi))


    def set_amplitudes_phases_state(self,amplitudes_in,phases_in,state_in):
        '''Sets the digital I and Q values to achieve the amplitudes and phases specified in the input variables.\n
        This includes normalizing according to the calibration.'''
        self.prepare_1D_Cal() #Prepare Pchip Objects. This is to make sure that these are current.
        self.amplitudes=amplitudes_in
        self.phases=phases_in
        self.I_values=[0]*self.number_of_channels
        self.Q_values=[0]*self.number_of_channels
        for a in range(self.number_of_channels):
            if type(amplitudes_in[a]) is list: #Need to differentiate between cases with 1 and more elements.
                self.counter_max[a]=len(amplitudes_in[a])
                self.I_values[a]=[0]*self.counter_max[a]
                self.Q_values[a]=[0]*self.counter_max[a]
                self.Amp_state[a]=[0]*self.counter_max[a]
                for b in range(self.counter_max[a]):
                    cIQ=self.calcIQ(self.amplitudes[a][b],self.phases[a][b],a,state_in[a][b])
                    self.I_values[a][b]=int(np.real(cIQ))
                    self.Q_values[a][b]=int(np.imag(cIQ))
                    self.Amp_state[a][b]=state_in[a][b]
            else:
                self.counter_max[a]=1
                cIQ=self.calcIQ(self.amplitudes[a],self.phases[a],a,state_in[a])
                self.I_values[a]=int(np.real(cIQ))
                self.Q_values[a]=int(np.imag(cIQ))
                self.Amp_state[a]=state_in[a]

    def calcIQ(self,amp,ph,channel,mode): #Calculate digital values including calibration
        '''This function translates a value for amplitude and phase into a complex I/Q value including normalization according to the calibrations.\n
        "amp" is a single amplitude in Volts.\n
        "phase is a single phase in degrees.\n
        "channel" specifies for which channel this sample is. This is necessary to use the correct calibration values.\n
        "mode" specifies which state the amplifier is in.'''
        # Order of operation for correction:
        # 1. Calculate corrected amplitude (convert from Volts to digital value with pchip)
        # 2. Calculate correct angle in IQ-space
        # 3. Add offset

        #Calculate correct digital amplitude for required output voltage
        amp_digital = self.pchip_objects_amplitude[channel][mode].__call__(amp) #Corrected digital amplitude in arbitrary units
        
        #Calculate phase correction for digital amplitude
        phase_offset = self.pchip_objects_phase[channel][mode].__call__(amp_digital) #Correct phase for the selected digital amplitude
        ph=ph+phase_offset #This is the correct sign.

        IQ=(pow(2,13)-1 +self.IQoffset[channel][0])+ 1j*(pow(2,13)-1 +self.IQoffset[channel][1]) + amp_digital*np.exp(1j*np.pi/180*ph) #Only includes offset correction.
        return IQ
        
        

    def return_byte_stream(self):
        '''Returns a byte stream to be transmitted via SPI. This byte stream is suited to programm the modulators (hardware) to the state given in this object'''
        CB = ControlByteObj() #For improved readability use the object CB to gerenate the control bits.
        byte_stream = [CB.prog, 0 , 0, 0]*1000 #Make sure the switching to programming mode is finished.
        for a in range(self.number_of_channels): #Run through all channels
            data1=self.counter_max[a]%256
            data2=math.floor(self.counter_max[a]/256)
            byte_stream_add = [CB.prog + CB.chip0, a + self.start_address, data2, data1,
                               CB.prog + CB.we + CB.chip0, a + self.start_address, data2, data1,
                               CB.prog + CB.chip0, a + self.start_address, data2, data1]
            byte_stream = byte_stream + byte_stream_add
            for c in range(2): #Run through all SRAMs
                byte_stream_add = [CB.prog, a + self.start_address, 0, 0,
                                   CB.prog + CB.reset, a + self.start_address, 0, 0, #Reset counters before starting to fill SRAM.
                                   CB.prog, a + self.start_address, 0, 0]
                byte_stream = byte_stream + byte_stream_add
                for b in range(self.counter_max[a]): #Run through all samples
                    if c==0: #First SRAM Chip
                        if self.counter_max[a]>1:
                            data1=self.I_values[a][b]%256
                            data2=math.floor(self.I_values[a][b]/256)+self.Amp_state[a][b]*64 #Switch 15th bit (7th in byte 2) according to amplifier state.
                        else:
                            data1=self.I_values[a]%256
                            data2=math.floor(self.I_values[a]/256)+self.Amp_state[a]*64 #Switch 15th bit (7th in byte 2) according to amplifier state.
                    elif c==1: #Second SRAM Chip
                        if self.counter_max[a]>1:
                            data1=self.Q_values[a][b]%256
                            data2=math.floor(self.Q_values[a][b]/256)
                        else:
                            data1=self.Q_values[a]%256
                            data2=math.floor(self.Q_values[a]/256)

                    byte_stream_add = [CB.prog + CB.chip(c+1), a + self.start_address, data2, data1,
                                       CB.prog + CB.chip(c+1) + CB.we, a + self.start_address, data2, data1,
                                       CB.prog + CB.chip(c+1), a + self.start_address, data2, data1,
                                       CB.prog + CB.chip(c+1) + CB.clock, a + self.start_address, data2, data1]
                    byte_stream = byte_stream + byte_stream_add

        byte_stream = byte_stream + [CB.prog + CB.reset, 0, 0, 0] + [CB.prog, 0, 0, 0]
        data=bytes(byte_stream)    
        return data

class EnableObj: #Contains all data and methods for the Enable Board. (Enable Amplifiers, switch Exciter between systems)
    '''This Object represents the Enable Board. \n
    It enables the two amplifier racks (switches the power distribution on).\n
    It sets the RF switch either to the Siemens System or to MRexcite.'''
    #Note to self: Make sure all amplifiers are disabled and RF is switched back to Siemens when software is closed!
    RF_Switch=0
    Amps1=0
    Amps2=0

    def __init__(self,config):
        self.address = int(config['Enable_Module']['address'])
    def set_RF_Siemens(self):
        '''Set the RF-Switch to Siemens System. RF signals from the MRI-System's exciter go to the vendor amplifiers.'''
        self.RF_Switch=0
    def set_RF_MRexcite(self):
        '''Set the RF-Switch to MRexcite System. RF signals from the MRI-System's exciter go to MRexcite.'''
        self.RF_Switch=1
    def enable_Amps1(self):
        '''Enables the Amplifiers in the first RF Rack. (Switches the power distribution on)'''
        self.Amps1=1
    def disable_Amps1(self):
        '''Disables the Amplifiers in the first RF Rack. (Switches the power distribution off)'''
        self.Amps1=0
    def enable_Amps2(self):
        '''Enables the Amplifiers in the second RF Rack. (Switches the power distribution on)'''
        self.Amps2=1
    def disable_Amps2(self):
        '''Disables the Amplifiers in the second RF Rack. (Switches the power distribution off)'''
        self.Amps1=0
    def enable_All(self):
        '''Enables all Amplifiers. (Switches the Power Distributions on)'''
        self.Amps1=1
        self.Amps2=1
    def disable_All(self):
        '''Disables all Amplifiers. (Switches the Power Distributions off)'''
        self.Amps1=0
        self.Amps2=0
    def return_byte_stream(self):
        '''Returns a byte stream that can be used to programm the current state into the hardware.'''
        CB=ControlByteObj()
        data=self.Amps1+2*self.Amps2+4*self.RF_Switch
        byte_stream=[CB.prog,0,0,0]
        byte_stream_add = [CB.prog,self.address,0,data,
                           CB.prog + CB.we, self.address,0,data,
                           CB.prog,self.address,0,data]
        byte_stream=byte_stream+byte_stream_add + [CB.prog,0,0,0]
        return bytes(byte_stream)

class OpticalObj: #Contains all data and methods for the Optical Board (controls Pre-amps, T/R switches, Local/Bodycoil reception)
    '''This Object represents the Optical Board which controls Pre-Amp states, detuning, T/R switches and local/body coil reception.'''
    pre_amp_on=0 #if this is 1, Pre-amps are switched on during Rx
    pre_amp_on_always=0 #if this in 1, Pre-amps are always on
    Tx_always_on=0 #if this is 1, the MRexcite System's T/R switches are always in Tx mode
    det_always=1 #If this is 1, detuning is always on
    det_never=0 #if this is 1, MRexcite is never detuned (!Is Overwritten by det_always!)
    select_Rx=0 #If 0, local coil reception is enabled. If 1, Body coil reception is enabled.
    
    def __init__(self,config):
       self.address = int(config['Optical_Module']['address']) 
    
    def return_byte_stream(self):
        '''Returns a byte stream that can be used to programm the current state into the hardware.'''
        CB=ControlByteObj()
        data=2*self.pre_amp_on + 4*self.pre_amp_on_always + 8*self.Tx_always_on + 16*self.det_always + 32*self.det_never + 64*self.select_Rx
        byte_stream=[CB.prog,0,0,0,
                     CB.prog,self.address,0,data,
                     CB.prog+CB.we,self.address,0,data,
                     CB.prog,self.address,0,data,
                     CB.prog,0,0,0]
        return bytes(byte_stream)
    
class RFprepObj: #Contains all data and methods for the RF Preparation Board. (Prescales Exciter signal for Modulators)
    '''This Object represents the RF Preparation Board, which sets the gain of the exciter Signal.'''
    def __init__(self,config):
       self.address = int(config['RF_prep_Module']['address'])
       self.gain_high = int(config['RF_prep_Module']['gain_high'])
       self.gain_low = int(config['RF_prep_Module']['gain_low'])
       self.maxgain = int(config['RF_prep_Module']['maxgain'])
       self.gain_data=0

    def set_gain(self,gain_in:int):
        '''This function sets the gain for the exciter signal.\n
        Possible values: -31dB to + maxgain \n
        maxgain is set in MRexcite_config.ini'''
        gain_in=int(gain_in)
        #Make sure values are within range.
        if gain_in<-31:
            gain_in=-31
        elif gain_in>self.maxgain:
            gain_in=self.maxgain
        
        if gain_in <= 0:
            self.gain_data=gain_in
        else:
            self.gain_data=self.maxgain-gain_in + 128
        
    def set_gain_high(self):
        '''Sets gain for high signal mode (Full modulation by MRexcite).\n
        The gain value for high gain is set in the MRexcite_config.ini'''
        self.set_gain(self.gain_high)

    def set_gain_low(self):
        '''Sets gain for low signal mode (MRexcite modulation on top of modulated MR signal).\n
        The gain value for low gain is set in the MRexcite_config.ini'''
        self.set_gain(self.gain_low)

    def return_byte_stream(self):
        '''Returns a byte stream that can be used to programm the current state into the hardware.'''
        CB=ControlByteObj()
        data=self.gain_data
        byte_stream=[CB.prog,0,0,0,
                     CB.prog,self.address,0,data,
                     CB.prog+CB.we,self.address,0,data,
                     CB.prog,self.address,0,data,
                     CB.prog,0,0,0]
        return bytes(byte_stream)
    
class TriggerObj: #Contains all data and methods for the Trigger Board. (Sampling rates for Modulators).
    '''This Object represents the hardware of the Trigger Board.\n
    The Trigger Board detects OSCbits from the MRI system and either transmits them to the modulators, or starts a gated oscillator to produce a user defined number of trigger pulses at a user defined sampling rate.'''
    osc_select=0 #Selects one of two OSCbit inputs
    gen_select=0 #Selects whether OSCbit is fed through (0), or the Trigger generator is used (1).
    clock_divider=10 #Clock devider. The original clock (200MHz) is reduced to 10MHz and then devided by this number to provide the sampling frequency for the RF pulses in the modulators.
    clock_counter=100 #Number of clock ticks played out in a row after an OSCbit was detected.
    sampling_rate=10e6/clock_divider
    
    def __init__(self,config):
        self.address = int(config['Trigger_Module']['address'])

    def __setattr__(self, name, value):
        '''This function makes sure that sampling_rate is changed whenever clock_divider is changed.'''
        self.__dict__[name]=value
        if name == 'clock_divider':
            self.calculate_sampling_rate()

    def set_OSC0(self):
        '''Sets the input to OSCbit0 of the MRI System'''
        self.osc_select=0

    def set_OSC1(self):
        '''Sets the input to OSCbit1 of the MRI System'''
        self.osc_select=1

    def set_OSC_feedthrough(self):
        '''Sets the Trigger Board to "Feedthrough" mode, where the incoming OSCbit triggers a new modulator state.'''
        self.gen_select=0

    def set_Generate_Sampling(self):
        '''Sets the Trigger Board to "Generate Triggers" mode, where the incomming OSCbit starts a user defined stream of trigger pulses for the Modulators.'''
        self.gen_select=1

    def set_clock_1MHz(self):
        '''Sets the clock to 1MHz sampling rate'''
        self.clock_divider=10

    def set_clock_100kHz(self):
        '''Sets the clock to 100kHz sampling rate'''
        self.clock_divider=100

    def set_clock(self,freq_in):
        '''Sets the device to a user defined sampling rate.\n
        Automatically makes sure that the sampling rate is sensible:\n
        It sets the clock divider to the nearest feasible integer.'''
        self.clock_divider=int(np.round(10e6/freq_in))
        if self.clock_divider>255:
            self.clock_divider = 255
        elif self.clock_divider <1:
            self.clock_divider = 1

    def calculate_sampling_rate(self):
        self.sampling_rate = 10e6/self.clock_divider
        print('Sampling Rate: ' + str(self.sampling_rate/1000) + ' kHz')

    def return_byte_stream(self):
        CB=ControlByteObj()
        byte_stream = [CB.prog,0,0,0,
                       CB.prog+CB.chip0,self.address,self.osc_select+2*self.gen_select,self.clock_divider,
                       CB.prog+CB.chip0+CB.we,self.address,self.osc_select+2*self.gen_select,self.clock_divider, #Write clock divider and OSC/GEN select
                       CB.prog+CB.chip0,self.address,self.osc_select+2*self.gen_select,self.clock_divider,
                       CB.prog+CB.chip1,self.address,0,self.clock_counter,
                       CB.prog+CB.chip1+CB.we,self.address,0,self.clock_counter, #Write clock counter
                       CB.prog+CB.chip1,self.address,0,self.clock_counter,
                       CB.prog,0,0,0]
        return bytes(byte_stream)

### Load config file ###
config=configparser.ConfigParser()
config.read(os.path.dirname(__file__) + '/MRexcite_config.ini')

### Instance Hardware Objects ###
MRexcite_System = MRexcite_SystemObj(config)
print('Initialized System')
