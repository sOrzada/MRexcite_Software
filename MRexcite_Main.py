import MRexcite_Control #Contains definition of Hardware and Initializes Hardware.
import pathlib
import scipy

# Constants
COLOR_SAR_EXCEEDED = '#FF0000'
COLOR_SAR_OK = '#00FF00'
import numpy as np
from time import sleep
import os
from tkinter import *
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter.messagebox import askyesno
import MRexcite_Calibration
from PIL import Image, ImageTk
from threading import Thread
from random import randint
import webbrowser
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

### Define GUI ###
class MainGUIObj:
    def start_main_GUI(self): #Main GUI
        '''This function starts the main GUI for the MRexcite System.'''
        self.MainWindow = Tk()
        self.MainWindow.title('MRexcite Control')
        self.MainWindow.config(width=1200, height=600)
        self.MainWindow.resizable(False,False)
        self.MainWindow.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.MainWindow.protocol('WM_DELETE_WINDOW', self.end_Software) #This is important: If the software is ended, we need to call a function that resets to a safe state (Siemens)
        self.menu_bar()
        self.place_buttons()
        
        self.status_text_box = scrolledtext.ScrolledText(self.MainWindow, width = 55, height =30)
        self.status_text_box.place(x=700,y=50)

        #The following could be used to display SAR. There is no connection to the SAR supervision System yet.
        #self.SARDisplay=SARSupervisionDisplyObj(self.MainWindow)
        #self.SARDisplay.place_SAR_info(400,150)
        #self.SARthread=Thread(target=self.SARDisplay.getSAR,args=[],daemon=TRUE)
        #self.SARthread.start()

        self.AddressTestGUI=AddressTestObj()
        self.AdvancedUser=AdvancedUserObj()
        self.GeneralSettingsGUI=GeneralSettingsObj()
        self.CalibrateZero=MRexcite_Calibration.CalibrateZeroObj()
        self.CalibrateMod = MRexcite_Calibration.ModulatorCalibrationObj()
        self.CalibrateLin = MRexcite_Calibration.CalibrateLinearity1DObj()
        self.PulseInfoGUI = pulseInfoWindowObj()
        self.update_status()

    def menu_bar(self): #Menu Bar for main window.
        '''Menu Bar for main window.'''
        MenuBar=Menu(self.MainWindow)
        self.MainWindow.config(menu=MenuBar)
    
        FileMenu = Menu(MenuBar, tearoff = 0)
        MenuBar.add_cascade(label='File', menu=FileMenu)
        FileMenu.add_command(label= 'Load System State...', command=self.openFile)
        FileMenu.add_command(label= 'Save System State...', command=self.saveFile)
        FileMenu.add_separator()
        FileMenu.add_command(label = 'Quit', command = self.end_Software)
        
        PulseMenu=Menu(MenuBar, tearoff = 0)
        MenuBar.add_cascade(label='Shim', menu=PulseMenu)
        PulseMenu.add_command(label='Load Shim...', command=self.loadShim)
        PulseMenu.add_separator()
        PulseMenu.add_command(label='Set CP+ Mode', command=self.setCPplus)
        PulseMenu.add_command(label='Set simple TIAMO', command=self.setTIAMO)
        PulseMenu.add_separator()
        PulseMenu.add_command(label='Channelwise B1 Map', command=self.setCHB1)
        PulseMenu.add_command(label='Channelwise MRF', command=self.setMRF)
        PulseMenu.add_separator()
        PulseMenu.add_command(label='Pulse Info', command=self.PulseInfo)

        TriggerMenu=Menu(MenuBar, tearoff=0)
        MenuBar.add_cascade(label='Trigger', menu=TriggerMenu)
        TriggerMenu.add_command(label='Reset Trigger', command=self.TriggerReset)
        TriggerMenu.add_command(label='Send Trigger', command=self.TriggerSend)
        TriggerMenu.add_command(label='Go to Position...', command=self.TriggerGoTo)

        
        ConfigurationMenu=Menu(MenuBar, tearoff = 0)
        MenuBar.add_cascade(label='Configuration', menu=ConfigurationMenu)
        ConfigurationMenu.add_command(label='Advanced User', command=self.enableAdvancedUser)
        ConfigurationMenu.add_separator()
        ConfigurationMenu.add_command(label='Address Test',command=self.AddressTest)
        ConfigurationMenu.add_command(label='General Settings', command=self.settingsGeneral)
        ConfigurationMenu.add_separator()
        ConfigurationMenu.add_command(label = 'Zero Offset Calibration', command = self.calibrateSystemZero)
        ConfigurationMenu.add_command(label = 'Linearity Calibration', command = self.calibrateSystemLin1D)
        ConfigurationMenu.add_command(label = 'Modulator Calibration', command = self.calibrateModulators)
        
        HelpMenu=Menu(MenuBar, tearoff = 0)
        MenuBar.add_cascade(label='Help', menu=HelpMenu)
        HelpMenu.add_command(label='Help', command=self.callHelp)
        HelpMenu.add_separator()
        HelpMenu.add_command(label='Info', command=self.showInfo)
    
    def place_buttons(self):
        self.Image_Button_On = PhotoImage(file=r'.\Images\MRx_On.png')
        self.Image_Button_Off = PhotoImage(file=r'.\Images\MRx_Off.png')
        self.Image_Button_Toggle_Right = PhotoImage(file=r'.\Images\Toggle_right.png')
        self.Image_Button_Toggle_Left = PhotoImage(file=r'.\Images\Toggle_left.png')
        
        self.ButtonSystemOn = Button(self.MainWindow,image=self.Image_Button_Off,bd=0,command=self.switch_system)
        self.ButtonSystemOn.place(x=200,y=100,anchor=CENTER)
        self.LabelSiemens = Label(self.MainWindow,text='Siemens')
        self.LabelSiemens.place(x=100,y=100,anchor=CENTER)
        self.LabelMRexcite = Label(self.MainWindow,text='MRexcite')
        self.LabelMRexcite.place(x=300,y=100,anchor=CENTER)

        self.ButtonRxSelect = Button(self.MainWindow,image=self.Image_Button_Toggle_Left,bd=0,command=self.switch_Rx)
        self.ButtonRxSelect.place(x=200,y=175,anchor=CENTER)
        self.LabelLocalCoils = Label(self.MainWindow,text='Local Coils')
        self.LabelLocalCoils.place(x=100,y=175,anchor=CENTER)
        self.LabelBodyCoil = Label(self.MainWindow,text='Body Coil')
        self.LabelBodyCoil.place(x=300,y=175,anchor=CENTER)

        self.ButtonOSCSelect = Button(self.MainWindow,image=self.Image_Button_Toggle_Left,bd=0,command=self.switch_OSC)
        self.ButtonOSCSelect.place(x=200,y=250,anchor=CENTER)
        self.LabelOSC0 = Label(self.MainWindow,text='OSCbit 0')
        self.LabelOSC0.place(x=100,y=250,anchor=CENTER)
        self.LabelOSC1 = Label(self.MainWindow,text='OSCbit 1')
        self.LabelOSC1.place(x=300,y=250,anchor=CENTER)

        self.ButtonArmUnblank = Button(self.MainWindow,width=10, height=2, fg='red', bg='#dddddd', text='Unblank', relief='raised', command=self.UnblankClick)
        self.ButtonArmUnblank.place(x=200,y=350,anchor=CENTER)

        self.ButtonLoadShim = Button(self.MainWindow, width=10,height= 2, text='Load Shim...', command=self.loadShim)
        self.ButtonLoadShim.place(x=100, y=475, anchor=CENTER)
        self.displayShim=StringVar()
        self.LabelShim = Label(self.MainWindow, textvariable=self.displayShim)
        self.LabelShim.place (x=150,y=475, anchor = 'w')
    
    def switch_system(self):
        '''This function allows for switching between Siemens and MRexcite'''
        if MRexcite_Control.MRexcite_System.EnableModule.RF_Switch==0:
            MRexcite_Control.MRexcite_System.EnableModule.RF_Switch=1
        else:
            MRexcite_Control.MRexcite_System.EnableModule.RF_Switch=0
        self.update_status()

    def UnblankClick(self):
        if MRexcite_Control.MRexcite_System.EnableModule.RF_Switch==1: #Enabling Unblank is only allowed if system is switched to MRexcite.
            if MRexcite_Control.MRexcite_System.Unblank_Status==0:
                MRexcite_Control.MRexcite_System.Unblank_Status=1
            else:
                MRexcite_Control.MRexcite_System.Unblank_Status=0
        self.update_status()

    def switch_OSC(self):
        if MRexcite_Control.MRexcite_System.TriggerModule.osc_select==0:
            MRexcite_Control.MRexcite_System.TriggerModule.osc_select=1
        else:
            MRexcite_Control.MRexcite_System.TriggerModule.osc_select=0
        self.update_status()

    def switch_Rx(self):
        if MRexcite_Control.MRexcite_System.EnableModule.RF_Switch==1:
            if MRexcite_Control.MRexcite_System.OpticalModule.select_Rx==0:
                MRexcite_Control.MRexcite_System.OpticalModule.select_Rx=1
                MRexcite_Control.MRexcite_System.OpticalModule.pre_amp_on=1
            else:
                MRexcite_Control.MRexcite_System.OpticalModule.select_Rx=0
                MRexcite_Control.MRexcite_System.OpticalModule.pre_amp_on=0
        self.update_status()

    def update_status(self):
        '''This function updates the text and the appearance of the switches. We do this here to make loading a system state easy.'''
        
        
        #Prepare Text Box
        # Set the text box state to NORMAL to allow modifications to its content.
        self.status_text_box.config(state=NORMAL)
        self.status_text_box.delete('1.0',END)
        status_text='Current status of system:\n\n'
        if self.AdvancedUser.advancedUseEnabled==TRUE:
            status_text=status_text + 'Advanced User Enabled. BE CAREFUL!\n\n'

        #System State. This MUST come first, otherwise the status of ButtonRxSelect and ButtonArmUnblank will be wrong!
        if MRexcite_Control.MRexcite_System.EnableModule.RF_Switch==1:
            MRexcite_Control.MRexcite_System.EnableModule.enable_Amps1()
            MRexcite_Control.MRexcite_System.EnableModule.enable_All()
            self.ButtonSystemOn.config(image=self.Image_Button_On)
            status_text=status_text + '*MRexcite* System is currently enabled.\n\n'
        else:
            MRexcite_Control.MRexcite_System.EnableModule.disable_All()
            self.ButtonSystemOn.config(image=self.Image_Button_Off)
            MRexcite_Control.MRexcite_System.OpticalModule.select_Rx=0
            MRexcite_Control.MRexcite_System.Unblank_Status=0
            status_text=status_text + '*Siemens* System is currently enabled.\n\n'
        

        #Rx State
        if MRexcite_Control.MRexcite_System.OpticalModule.select_Rx==0:
            status_text = status_text + 'Receiving with *LOCAL* coils.\n\n'
            self.ButtonRxSelect.config(image=self.Image_Button_Toggle_Left)
        else:
            self.ButtonRxSelect.config(image=self.Image_Button_Toggle_Right)
            status_text = status_text + 'Receiving with *BODY* coil.\n\n'
        
        #Amplifier Status
        if MRexcite_Control.MRexcite_System.EnableModule.Amps1==1 & MRexcite_Control.MRexcite_System.EnableModule.Amps2==1:
            status_text = status_text + 'Amplifier Rack 1 and Rack 2 are switched *ON*.\n\n'
        elif MRexcite_Control.MRexcite_System.EnableModule.Amps1==0 & MRexcite_Control.MRexcite_System.EnableModule.Amps2==0:
            status_text = status_text + 'Amplifier Rack 1 and Rack 2 are switched *OFF*.\n\n'
        elif MRexcite_Control.MRexcite_System.EnableModule.Amps1==1 & MRexcite_Control.MRexcite_System.EnableModule.Amps2==0:
            status_text = status_text + 'Amplifier Rack 1 is switched *ON* and Rack 2 is switched *OFF*.\n\n'
        elif MRexcite_Control.MRexcite_System.EnableModule.Amps1==0 & MRexcite_Control.MRexcite_System.EnableModule.Amps2==1:
            status_text = status_text + 'Amplifier Rack 1 is switched *OFF* and Rack 2 is switched *ON*.\n\n'
        
        #Trigger Status
        status_text=status_text + 'Using OSCbit ' + str(MRexcite_Control.MRexcite_System.TriggerModule.osc_select) + '\n'
        if MRexcite_Control.MRexcite_System.TriggerModule.osc_select==1:
            self.ButtonOSCSelect.config(image=self.Image_Button_Toggle_Right)
        else:
            self.ButtonOSCSelect.config(image=self.Image_Button_Toggle_Left)

        if MRexcite_Control.MRexcite_System.TriggerModule.gen_select==1:
            status_text = status_text + 'Single Trigger Mode.\n'
        else:
            MRexcite_Control.MRexcite_System.TriggerModule.calculate_sampling_rate()
            sampling_in_kHz=MRexcite_Control.MRexcite_System.TriggerModule.sampling_rate/1000
            number_of_samples = MRexcite_Control.MRexcite_System.TriggerModule.clock_counter
            # Calculate the length of the pulse in milliseconds.
            # Formula: number_of_samples * (1 / sampling_rate_in_kHz)
            # This converts the number of samples into time duration based on the sampling rate.
            length_of_pulse_in_ms = number_of_samples*1/sampling_in_kHz
            status_text = status_text   + 'Trigger is generated with following paramters:\n'\
                                        + '\tSampling rate: ' + str(sampling_in_kHz) + ' kHz\n'\
                                        + '\tNumber of samples: ' + str(number_of_samples) +'\n'\
                                        + '\tPulse duration: ' + str(length_of_pulse_in_ms) + ' ms\n\n'
        
        #Modulation Type
        status_text = status_text + 'Using ' + MRexcite_Control.MRexcite_System.RFprepModule.Status + ' modulation mode. \n\n'

        #Modulator Status
        max_number_samples = max(MRexcite_Control.MRexcite_System.Modulator.counter_max)
        ID_max = MRexcite_Control.MRexcite_System.Modulator.counter_max.index(max_number_samples)

        status_text = status_text + 'Maximum number of samples in pulse: ' + str(max_number_samples) + ' (ch: ' + str(ID_max+1) +')\n\n'

        #Unblank Status
        if MRexcite_Control.MRexcite_System.Unblank_Status==0:
            status_text = status_text + 'Unblank is disabled. No RF can be transmitted!'
            self.ButtonArmUnblank.config(relief='raised', fg='red', bg='#dddddd')
        else:
            self.ButtonArmUnblank.config(relief='sunken', fg='black', bg='#00ff00')
            status_text = status_text + 'Unblank is ENABLED! Ready to transmit!'

        
        #Write everything but RF-Pulse to hardware. (We do not write the RF pulse here, as this can take long and the user shouldn't wait 3s after clicking "unblank")
        checkSPI=MRexcite_Control.MRexcite_System.SetSystemState()
        if checkSPI==0:
            print('Could not send via SPI!')
            status_text= status_text + '\n\n\n\t***!!!Could not connect to SPI!!!***'

                
        if MRexcite_Control.MRexcite_System.Unblank_Status==1:
            try:
                MRexcite_Control.MRexcite_System.enable_system()
            except Exception as e:
                print(f"Error enabling system: {e}")
                    

        self.status_text_box.insert('1.0',status_text)
        self.status_text_box.config(state=DISABLED)    

    def openFile(self): #Open a file that contains all settings and pulses from a previous session.
        pass

    def saveFile(self): #Save current settings and pulses for a later session.
        pass

    def loadShim(self, **kwargs): #Load a shim file
        '''Loads a shim file, either Matlab (.mat) or Numpy (.npy) based.\n
        Matlab: Needs to contain variables with one being "shim".\n
        Numpy: Pack variables in a dictionary. One variable needs to be "shim".'''
        f_name = kwargs.get('fname',[])
        start_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'shims'))
        if f_name==[]:
            f_name=filedialog.askopenfile(mode='rb', initialdir=start_dir, filetypes=(('Matlab File','*.mat'),('Numpy Files','*.npz')), defaultextension=(('Matlab File','*.mat'),))
        if f_name is not None:
            self.displayShim.set(str(f_name.name))
            try:
                if f_name.name.endswith('.mat'):
                    data = scipy.io.loadmat(f_name.name)
                elif f_name.name.endswith('.npz'):
                    data = np.load(f_name.name)
                else:
                    print('Unsupported file format.')
            except Exception as e:
                print(f"Error loading shim file: {e}")
        else:
            print('No file selected. Non loaded.')
            return
        
        # Check if the loaded data is a dictionary
        if not isinstance(data, dict) and not isinstance(data, np.lib.npyio.NpzFile):
            print('Loaded data is not a valid dictionary.')
            return
        # Check if the dictionary contains 'shim'
        if 'shim' in data:
            shim_data = data['shim']
            if isinstance(shim_data, np.ndarray):
                if shim_data.ndim == 3:
                    MRexcite_Control.MRexcite_System.Modulator.set_amplitudes_phases_state(shim_data[:,0,:].tolist(),shim_data[:,1,:].tolist(),(shim_data[:,2,:].astype(int)).tolist())
                elif shim_data.ndim == 2:
                    MRexcite_Control.MRexcite_System.Modulator.set_amplitudes_phases_state(shim_data[:,0].tolist(),shim_data[:,1].tolist(),(shim_data[:,2].astype(int)).tolist())
                else:
                    print('Shim has the wrong number of dimensions.')
                    return
            else:
                print('Loaded shim data is not a valid numpy array.')
                return
        else:
            print('Loaded data does not contain "shim" key.')
            return
        
        #Check for desired gain.
        if 'gain' in data:
            gain=data['gain']
            if isinstance(gain, np.ndarray) and gain.size == 1: #Since "and" in python is short circuit, this should not throw an error if gain is not an ndarray.
                if gain == 'high':
                    MRexcite_Control.MRexcite_System.RFprepModule.set_gain_high()
                elif gain=='low':
                    MRexcite_Control.MRexcite_System.RFprepModule.set_gain_low()
                else:
                    try:
                        gain=int(gain) #This is only reached if gain is size 1. We can therefore ignore the warning.
                        MRexcite_Control.MRexcite_System.RFprepModule.set_gain(gain)
                    except:
                        print('Error in "gain". Wrong format. Reverting to Hybrid shimming.')
                        MRexcite_Control.MRexcite_System.RFprepModule.set_gain_low()
            else:
                print('Error in "gain". Wrong format. Reverting to Hybrid shimming.')
                MRexcite_Control.MRexcite_System.RFprepModule.set_gain_low()
        else: #If no gain is given, revert to hybrid shimming.
            MRexcite_Control.MRexcite_System.RFprepModule.set_gain_low()
        
        #Check for trigger settings.
        if 'OSCbit' in data: #Check which OSCbit to use. Revert to OSC0
            OSCbit=data['OSCbit']
            if OSCbit == 1:
                MRexcite_Control.MRexcite_System.TriggerModule.set_OSC1()
            else:
                MRexcite_Control.MRexcite_System.TriggerModule.set_OSC0()
        else: #If no settings for trigger are provided, set to feedthrough and OSC0
            MRexcite_Control.MRexcite_System.TriggerModule.set_OSC0()

        if 'trigger' in data: #Check for Trigger settings. If no trigger settings, revert to feedthrough.
            Trigger = data['trigger']
            Trigger = Trigger.squeeze() #Squeeze to get the right number of dimensions.
            if Trigger.size==2:
                MRexcite_Control.MRexcite_System.TriggerModule.set_clock(Trigger[0])
                MRexcite_Control.MRexcite_System.TriggerModule.clock_counter = Trigger[1]
                MRexcite_Control.MRexcite_System.TriggerModule.set_Generate_Sampling()
            else:
                print('Wrong number of entries in "trigger". Reverting to OSC feedthrough.')
        else:
            MRexcite_Control.MRexcite_System.TriggerModule.set_OSC_feedthrough()
        
        #Check whether there are settings for reception. If so, apply.
        if 'rx' in data:
            rx=data['rx']
            if isinstance(rx,int):
                MRexcite_Control.MRexcite_System.OpticalModule.select_Rx=rx
            else:
                pass
        
        #Update Status.
        self.update_status()
        MRexcite_Control.MRexcite_System.SetAll()

    def setCPplus(self): #Applies the CP+ mode for the Body coil.
        try:
            filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'shims', 'default', 'CP_plus.mat'))
            fname = open(filename)
        except:
            print('Error. Could not open CP-plus definition.')
            return
        self.loadShim(fname=fname)

    def setTIAMO(self): #Loads a simple predefined TIAMO shim set.
        try:
            filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'shims', 'default', 'simple_TIAMO.mat'))
            fname = open(filename)
        except:
            print('Error. Could not open CP-plus definition.')
            return
        self.loadShim(fname=fname)
    def setCHB1(self):
        try:
            filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'shims', 'B1_mapping', 'chwise_b1mapping.mat'))
            fname = open(filename)
        except:
            print('Error. Could not open Channelwise B1 Mapping dataset.')
            return
        self.loadShim(fname=fname)

    def setMRF(self):
        try:
            filename = os.path.abspath(os.path.join(os.path.dirname(__file__), 'shims', 'B1_mapping', 'MRF_chwise_b1mapping.mat'))
            fname = open(filename)
        except:
            print('Error. Could not open Channelwise MRF B1 Mapping dataset.')
            return
        self.loadShim(fname=fname)
    def PulseInfo(self): #Provides Information on loaded pulse.
        self.PulseInfoGUI.openGUI()

    def TriggerReset(self):
        MRexcite_Control.MRexcite_System.TriggerReset()
    
    def TriggerSend(self):
        MRexcite_Control.MRexcite_System.TriggerSend()
    
    def TriggerGoTo(self):
        triggerSelectWindow=TriggerSelectObj()
        triggerSelectWindow.WindowMain.grab_set()
        triggerSelectWindow.WindowMain.wait_window(triggerSelectWindow.WindowMain)
    
    def AddressTest(self):
        if self.AdvancedUser.check()==TRUE:
            self.AddressTestGUI.openGUI()
            self.AddressTestGUI.WindowAddress.focus()
            self.AddressTestGUI.WindowAddress.grab_set()
            self.AddressTestGUI.WindowAddress.wait_window(self.AddressTestGUI.WindowAddress)
    
    def settingsGeneral(self): #General settings for the System.
        if self.AdvancedUser.check()==TRUE:
            self.GeneralSettingsGUI.openGUI()
            self.GeneralSettingsGUI.WindowMain.focus()
            self.GeneralSettingsGUI.WindowMain.grab_set()
            self.GeneralSettingsGUI.WindowMain.wait_window(self.GeneralSettingsGUI.WindowMain)
            self.update_status()
        else:
            pass

    def calibrateSystemZero(self): #Calibration of the Zero point of the Modulators
        if self.AdvancedUser.check()==TRUE:
            self.CalibrateZero.openGUI()
            self.CalibrateZero.WindowMain.focus()
            self.CalibrateZero.WindowMain.wait_window(self.CalibrateZero.WindowMain)
            self.update_status()
        else:
            pass

    def calibrateSystemLin1D(self): #Calibration for full modulation including amplifiers
        if self.AdvancedUser.check()==TRUE:
            self.CalibrateLin.openGUI()
            self.CalibrateLin.WindowCalLin.focus()
            self.CalibrateLin.WindowCalLin.wait_window(self.CalibrateLin.WindowCalLin)
            self.update_status()
        

    def calibrateModulators(self): #Calibration for hybrid modulation. (Modulators not run in saturation)
        if self.AdvancedUser.check()==TRUE:
            self.CalibrateMod.openGUI()
            self.CalibrateMod.WindowCalMod.focus()
            self.CalibrateMod.WindowCalMod.wait_window(self.CalibrateMod.WindowCalMod)
            self.update_status()
        else:
            pass

    def callHelp(self):
        url = "https://github.com/sOrzada/MRexcite_Software/wiki"
        webbrowser.open(url, new=0, autoraise=True)

    def showInfo(self):
        infoWindow=InfoWindowObj()
        infoWindow.WindowMain.grab_set()
        infoWindow.WindowMain.wait_window(infoWindow.WindowMain)

    def enableAdvancedUser(self):
        self.AdvancedUser.openGUI()
        self.AdvancedUser.WindowPassword.grab_set()
        
        self.AdvancedUser.WindowPassword.wait_window(self.AdvancedUser.WindowPassword)
        self.update_status()

    def end_Software(self): # This is important to ensure that we switch back to Siemens Mode when we end this software.
        '''This function safely resets the MRexcite System to Siemens mode and ends the software.'''
        MRexcite_Control.MRexcite_System.EnableModule.RF_Switch=0
        self.update_status()
        self.MainWindow.update() #This is necessary. Otherwise the user does not see the changes before the window closes.
        sleep(0.5) #This wait time is used to give the users time to realize, that everything is set back to Siemens.
        self.MainWindow.destroy()

class SARSupervisionDisplyObj:
    '''Possible solution for showing SAR overview within the MRexcite control GUI.'''
    def __init__(self,MainWindow):
        self.MainWindow=MainWindow
    
    def place_SAR_info(self,x_in,y_in):
        '''Defines the Box and labels for SAR Supervision display.\nx_in and y_in are the coordinates of the upper left corner.'''
        frameWidth=250

        self.FrameSAR = Frame(self.MainWindow,width=frameWidth,height=230,bd=5, relief=RIDGE)
        self.FrameSAR.place(x=x_in,y=y_in)

        self.LabelSARTitle = Label(self.MainWindow,width=20,height=1,text='SAR Supervision',font=('Helvetica',14))
        self.LabelSARTitle.place(x=x_in+frameWidth/2,y=y_in+30,anchor=CENTER)

        # 10s Average:
        self.LabelSAR10s = Label(self.MainWindow, width=8,height=1,text='0 %',relief='sunken',font=('Helvetica',14),background='#00FF00')
        labelSAR10sText = Label(self.MainWindow,width=8,height=1,text='SAR 10s:',font=('Helvetica',14))
        labelSAR10sText.place(x=x_in+frameWidth/2-5,y=y_in+60,anchor=NE)
        self.LabelSAR10s.place(x=x_in+frameWidth/2+5,y=y_in+60,anchor=NW)

        # 6min Average
        self.LabelSAR6min = Label(self.MainWindow, width=8,height=1,text='0 %',relief='sunken',font=('Helvetica',14),background='#00FF00')
        labelSAR6minText = Label(self.MainWindow,width=8,height=1,text='SAR 6min:',font=('Helvetica',14))
        labelSAR6minText.place(x=x_in+frameWidth/2-5,y=y_in+110,anchor=NE)
        self.LabelSAR6min.place(x=x_in+frameWidth/2+5,y=y_in+110,anchor=NW)

        #Power
        self.LabelSARPower = Label(self.MainWindow,width=8,height=1,text='0 W',relief='sunken',font=('Helvetica',14))
        labelSARPowerText=Label(self.MainWindow,width=8,height=1,text='Power:',font=('Helvetica',14))
        labelSARPowerText.place(x=x_in+frameWidth/2-5,y=y_in+160,anchor=NE)
        self.LabelSARPower.place(x=x_in+frameWidth/2+5,y=y_in+160,anchor=NW)
    
    def update_SAR(self,SAR10s,SAR6min,power):
        self.LabelSAR10s.config(text=str(round(SAR10s))+' %')
        self.LabelSAR6min.config(text=str(round(SAR6min))+' %')
        self.LabelSARPower.config(text=str(power)+' W')
        if SAR10s>100:
            self.LabelSAR10s.config(background=COLOR_SAR_EXCEEDED)
        else:
            self.LabelSAR10s.config(background=COLOR_SAR_OK)

        if SAR6min>100:
            self.LabelSAR6min.config(background=COLOR_SAR_EXCEEDED)
        else:
            self.LabelSAR6min.config(background=COLOR_SAR_OK)
    
    def getSAR(self):
        while TRUE:
            #The following lines are a placeholder until we implement TCP/IP communication with the SAR supervision.
            SAR10s=randint(0,150)
            SAR6min=randint(0,150)
            SARpower=randint(0,1000)
            self.update_SAR(SAR10s,SAR6min,SARpower)
            sleep(0.5)

class GeneralSettingsObj:
    '''Class for Window for general settings.'''
    def __init__(self):
        pass
    
    def openGUI(self):
        '''Function defines and opens window for GUI.'''
        #Input Window for general settings
        self.WindowMain = Toplevel()
        self.WindowMain.title('General Settings')
        self.WindowMain.config(width=600, height=500)
        self.WindowMain.resizable(False,False)
        self.WindowMain.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.WindowMain.protocol('WM_DELETE_WINDOW', self.closeWindow)

        #RF switch state:
        self.SwitchState=IntVar()
        self.SwitchState.set(MRexcite_Control.MRexcite_System.EnableModule.RF_Switch) #Get System State and apply to variable
        checkbox_SwitchState = Checkbutton(self.WindowMain, text='RF to MRexcite',variable=self.SwitchState,onvalue=1,offvalue=0)
        checkbox_SwitchState.place(x=30,y=25,anchor=W)
        
        #Amplifier States:
        self.AmpState1=IntVar()
        self.AmpState2=IntVar()
        self.AmpState1.set(MRexcite_Control.MRexcite_System.EnableModule.Amps1) #Get System State and apply to variable
        self.AmpState2.set(MRexcite_Control.MRexcite_System.EnableModule.Amps2) #Get System State and apply to variable
        checkbox_AmpState1 = Checkbutton(self.WindowMain,text='Amplifiers 1-16',variable=self.AmpState1,onvalue=1,offvalue=0)
        checkbox_AmpState2 = Checkbutton(self.WindowMain,text='Amplifiers 17-32',variable=self.AmpState2,onvalue=1,offvalue=0)
        checkbox_AmpState1.place(x=30,y=75,anchor=W)
        checkbox_AmpState2.place(x=30,y=100,anchor=W)

        #RF Preparation State:
        self.Gain = IntVar()
        self.Gain.set(MRexcite_Control.MRexcite_System.RFprepModule.gain) #Get gain from system and apply to variable
        self.Entry_Gain = Entry(self.WindowMain, textvariable=self.Gain,width=6)
        self.Entry_Gain.place(x=30, y=150, anchor=W)
        self.Label_Gain = Label(self.WindowMain,text='RF Preparation Gain')
        self.Label_Gain.place(x=80,y=150, anchor=W)

        #Trigger Module State:
        xpos=280
        ypos=50
        self.triggerMode=IntVar()
        self.clockDivider=IntVar()
        self.triggerCount=IntVar()
        
        LabelFrame_Trigger = LabelFrame(self.WindowMain,text='TriggerModule',width=200,height=120)
        LabelFrame_Trigger.place(x=xpos-20,y=ypos-35,anchor=NW)

        self.triggerMode.set(abs(MRexcite_Control.MRexcite_System.TriggerModule.gen_select-1))
        self.clockDivider.set(MRexcite_Control.MRexcite_System.TriggerModule.clock_divider)
        self.triggerCount.set(MRexcite_Control.MRexcite_System.TriggerModule.clock_counter)
        
        checkbox_TriggerMode=Checkbutton(self.WindowMain, text='Generate Trigger Train',variable=self.triggerMode,onvalue=1,offvalue=0)
        Entry_clockDividerTrigger = Entry(self.WindowMain,textvariable=self.clockDivider,width=6)
        Entry_triggerCount = Entry(self.WindowMain,textvariable=self.triggerCount,width=6)
        Label_clockDividerTrigger = Label(self.WindowMain,text='Clock Divider')
        Label_triggerCount = Label(self.WindowMain,text='Trigger Count')

        checkbox_TriggerMode.place(x=xpos,y=ypos,anchor=W)
        Entry_clockDividerTrigger.place(x=xpos,y=ypos+25, anchor=W)
        Label_clockDividerTrigger.place(x=xpos+50,y=ypos+25,anchor=W)
        Entry_triggerCount.place(x=xpos,y=ypos+50,anchor=W)
        Label_triggerCount.place(x=xpos+50,y=ypos+50,anchor=W)

        #Optical Module:
        self.pre_amp_on = IntVar() #if this is 1, Pre-amps are switched on during Rx
        self.pre_amp_on_always = IntVar() #if this in 1, Pre-amps are always on
        self.Tx_always_on = IntVar() #if this is 1, the MRexcite System's T/R switches are always in Tx mode
        self.det_always = IntVar() #If this is 1, detuning is always on
        self.det_never = IntVar() #if this is 1, MRexcite is never detuned (!Is Overwritten by det_always!)
        self.select_Rx = IntVar() #If 0, local coil reception is enabled. If 1, Body coil reception is enabled.

        self.pre_amp_on.set(MRexcite_Control.MRexcite_System.OpticalModule.pre_amp_on)
        self.pre_amp_on_always.set(MRexcite_Control.MRexcite_System.OpticalModule.pre_amp_on_always)
        self.Tx_always_on.set(MRexcite_Control.MRexcite_System.OpticalModule.Tx_always_on)
        self.det_always.set(MRexcite_Control.MRexcite_System.OpticalModule.det_always)
        self.det_never.set(MRexcite_Control.MRexcite_System.OpticalModule.det_never)
        self.select_Rx.set(MRexcite_Control.MRexcite_System.OpticalModule.select_Rx)

        xpos=65
        ypos=230
        LabelFrame_Optical = LabelFrame(self.WindowMain,text='Optical Module', width=400,height=115)
        LabelFrame_Optical.place(x=xpos-20,y=ypos-35)

        checkbox_pre_amp_on=Checkbutton(self.WindowMain,text='Pre Amp On', variable=self.pre_amp_on,onvalue=1,offvalue=0)
        checkbox_pre_amp_on_always=Checkbutton(self.WindowMain,text='Pre Amp On Always', variable=self.pre_amp_on_always,onvalue=1,offvalue=0)
        checkbox_Tx_always_on=Checkbutton(self.WindowMain,text='Tx always on', variable=self.Tx_always_on,onvalue=1,offvalue=0)
        checkbox_det_always=Checkbutton(self.WindowMain,text='Detuning always on (master)', variable=self.det_always,onvalue=1,offvalue=0)
        checkbox_det_never=Checkbutton(self.WindowMain,text='Detuning never on', variable=self.det_never,onvalue=1,offvalue=0)
        checkbox_select_Rx=Checkbutton(self.WindowMain,text='Body Coil reception', variable=self.select_Rx,onvalue=1,offvalue=0)

        checkbox_pre_amp_on.place(x=xpos,y=ypos,anchor=W)
        checkbox_pre_amp_on_always.place(x=xpos+200,y=ypos,anchor=W)
        checkbox_det_always.place(x=xpos,y=ypos+25,anchor=W)
        checkbox_det_never.place(x=xpos+200,y=ypos+25,anchor=W)
        checkbox_Tx_always_on.place(x=xpos,y=ypos+50,anchor=W)
        checkbox_select_Rx.place(x=xpos+200,y=ypos+50,anchor=W)

        #Command Buttons
        xpos=150
        ypos=350

        Button_Apply = Button(self.WindowMain, text='Apply', width=10, command=self.updateConfig)
        Button_Apply.place(x=xpos,y=ypos,anchor=CENTER)

        Button_Close = Button(self.WindowMain, text='Close', width=10, command=self.closeWindow)
        Button_Close.place(x=xpos+150,y=ypos,anchor=CENTER)

    def updateConfig(self):
        '''This function applies all changes to system.'''
        if self.SwitchState.get()==1:
            MRexcite_Control.MRexcite_System.EnableModule.set_RF_MRexcite()
        else:
            MRexcite_Control.MRexcite_System.EnableModule.set_RF_Siemens()
        
        if self.AmpState1.get()==1:
            MRexcite_Control.MRexcite_System.EnableModule.enable_Amps1()
        else:
            MRexcite_Control.MRexcite_System.EnableModule.disable_Amps1()
        
        if self.AmpState2.get()==1:
            MRexcite_Control.MRexcite_System.EnableModule.enable_Amps2()
        else:
            MRexcite_Control.MRexcite_System.EnableModule.disable_Amps2()
        
        MRexcite_Control.MRexcite_System.RFprepModule.set_gain(self.Gain.get())

        MRexcite_Control.MRexcite_System.TriggerModule.gen_select=abs(self.triggerMode.get()-1)
        MRexcite_Control.MRexcite_System.TriggerModule.clock_counter=self.triggerCount.get()
        MRexcite_Control.MRexcite_System.TriggerModule.clock_divider=self.clockDivider.get()

        MRexcite_Control.MRexcite_System.OpticalModule.det_always=self.det_always.get()
        MRexcite_Control.MRexcite_System.OpticalModule.det_never=self.det_never.get()
        MRexcite_Control.MRexcite_System.OpticalModule.pre_amp_on=self.pre_amp_on.get()
        MRexcite_Control.MRexcite_System.OpticalModule.pre_amp_on_always=self.pre_amp_on_always.get()
        MRexcite_Control.MRexcite_System.OpticalModule.select_Rx=self.select_Rx.get()
        MRexcite_Control.MRexcite_System.OpticalModule.Tx_always_on=self.Tx_always_on.get()

        MRexcite_Control.MRexcite_System.SetSystemState()

    def closeWindow(self):
        self.updateConfig()
        self.WindowMain.destroy()

class AdvancedUserObj:
    '''Class for enabling Advanced User'''
    password = 'meduser1' #This is not a real password. It is just a low key way to keep users away from stuff they normally should not use. (Ask Siemens about that *lol*) 
    advancedUseEnabled=FALSE
    
    def __init__(self):
        pass
    
    def openGUI(self):
        '''This is the GUI for password entry. Is called by the check() function'''
        #Password Entry for advanced usage
        self.WindowPassword = Toplevel()
        self.WindowPassword.title('Enter Password')
        self.WindowPassword.config(width=200, height=100)
        self.WindowPassword.resizable(False,False)
        self.WindowPassword.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.WindowPassword.protocol('WM_DELETE_WINDOW', self.closeWindow)
        self.VarInputPassword = StringVar()
        self.EntryPassword = Entry(self.WindowPassword,show='*', textvariable=self.VarInputPassword,width=10)
        self.EntryPassword.place(x=100,y=30,anchor=CENTER)
        self.EntryPassword.bind('<Return>', lambda event: self.closeWindow()) #Here I use the lambda so that the event object is not passed to the close window function.
        self.ButtonPassword = Button(self.WindowPassword,text='Enter', command=self.closeWindow)
        self.ButtonPassword.place(x=100,y=60,anchor=CENTER)
        self.EntryPassword.focus()
    
    def check(self):
        '''This function checks whether advanced usage is enabled. If not, it will open an input window for password entry.'''
        if self.advancedUseEnabled==TRUE:
            return_value=TRUE
        else:
            return_value=FALSE
            self.openGUI()
            if self.advancedUseEnabled==TRUE:
                return_value=TRUE
        return return_value

    def closeWindow(self):
        passwordEntered=self.VarInputPassword.get()
        if passwordEntered == self.password:
            self.advancedUseEnabled=TRUE
            print('Password correct. Enble Advanced User.')
        else:
            self.advancedUseEnabled=FALSE
            print('Wrong password.')
        
        self.WindowPassword.destroy()

class AddressTestObj:
    '''Class for lighting up the address LED on any card in the System. For Test puproses.'''
    def __init__(self):
        self.Address_Selected = IntVar()
        self.Address_Selected.set(0)
        #Prepare List for running through all VALID addresses:
        number_of_channels = MRexcite_Control.MRexcite_System.Modulator.number_of_channels
        start_address_modulators= MRexcite_Control.MRexcite_System.Modulator.start_address
        add_trig_module = MRexcite_Control.MRexcite_System.TriggerModule.address
        add_enable_module = MRexcite_Control.MRexcite_System.EnableModule.address
        add_RFprep_module = MRexcite_Control.MRexcite_System.RFprepModule.address
        add_optical_module = MRexcite_Control.MRexcite_System.OpticalModule.address
        self.addressList = [0]*(number_of_channels+4)

        for a in range(number_of_channels):
            self.addressList[a]=a+start_address_modulators
        
        self.addressList[number_of_channels]=add_trig_module
        self.addressList[number_of_channels+1]=add_RFprep_module
        self.addressList[number_of_channels+2]=add_optical_module
        self.addressList[number_of_channels+3]=add_enable_module
        
    def openGUI(self):    
        #Input Window for AddressTest
        self.WindowAddress = Toplevel()
        self.WindowAddress.title('Address Check')
        self.WindowAddress.config(width=300, height=200)
        self.WindowAddress.resizable(False,False)
        self.WindowAddress.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.WindowAddress.protocol('WM_DELETE_WINDOW', self.closeWindow)
        
        #Input for specific address
        Entry_Address = Entry(self.WindowAddress, textvariable=self.Address_Selected, width = 5 )
        Entry_Address.place(x=100, y=50, anchor=W)
        self.Button_SendAdress= Button(self.WindowAddress,text='Send',command=self.__sendAddress__)
        self.Button_SendAdress.place(x=140,y=50, anchor=W)
        self.Button_RunAddresses = Button(self.WindowAddress,text='Run All Addresses',command=self.__runAddresses__)
        self.Button_RunAddresses.place(x=100,y=100)

    def __sendAddress__(self):
        '''Light a specific address LED'''
        MRexcite_Control.MRexcite_System.LightAddress(self.Address_Selected.get())
    
    def __runAddresses__(self):
        '''Runs through all valid adresses and lights the indicator LEDs'''
        self.Button_RunAddresses["state"]="disabled"
        self.Button_SendAdress["state"]="disabled"
        for a in self.addressList:
            MRexcite_Control.MRexcite_System.LightAddress(a)
            self.Address_Selected.set(a)
            self.WindowAddress.update()
            sleep(1)
        self.Button_RunAddresses["state"]="normal"
        self.Button_SendAdress["state"]="normal"
    
    def closeWindow(self):
        self.WindowAddress.destroy()        

class TriggerSelectObj:
    '''Class for Window for selecting number of Triggers to be sent'''
    def __init__(self):
        
        #Main Anchor Position for Controls
        posX=120
        posY=100

        #Input Window
        self.WindowMain = Toplevel()
        self.WindowMain.title('Set Trigger')
        self.WindowMain.config(width=250, height=220)
        self.WindowMain.resizable(False,False)
        self.WindowMain.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.WindowMain.protocol('WM_DELETE_WINDOW', self.closeWindow)
        
        #Input Entry
        self.TriggerCountInputVar=IntVar()
        TriggerCountEntry=Entry(self.WindowMain, textvariable=self.TriggerCountInputVar,width=10)
        TriggerCountEntry.place(x=posX,y=posY,anchor=CENTER)

        #Label
        TriggerCountLabel=Label(self.WindowMain, text='Number of Triggers to send:')
        TriggerCountLabel.place(x=posX,y=posY-30,anchor=CENTER)
        
        #Push Button
        TriggerCountPushButton=Button(self.WindowMain, text='Apply',command=self.closeWindow)
        TriggerCountPushButton.config(width=10,height=2)
        TriggerCountPushButton.place(x=posX,y=posY+50,anchor=CENTER)

    def closeWindow(self):
        triggerInt=self.TriggerCountInputVar.get()
        MRexcite_Control.MRexcite_System.TriggerGoTo(triggerInt)
        self.WindowMain.destroy()

class InfoWindowObj:
    '''Class for the info window'''
    def __init__(self):
        self.WindowMain = Toplevel()
        self.WindowMain.title('Info')
        self.WindowMain.config(width=250, height=220)
        self.WindowMain.resizable(False,False)
        self.WindowMain.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.WindowMain.protocol('WM_DELETE_WINDOW', self.closeWindow)
        InfoLabel = Label(self.WindowMain, text='MRexcite 3 Software by DKFZ. \nIn case of problems: Good Luck! \n(Or just ask Stephan)')
        InfoLabel.place(x=120,y=150,anchor=CENTER)
        # Add dkfz logo from images subfolder
        try:
            #from PIL import Image, ImageTk
            img_path = os.path.join(os.path.dirname(__file__), 'images', 'dkfz-logo2.png')
            if os.path.exists(img_path):
                ph = Image.open(img_path)
                ph_resize = ph.resize((200, 70), resample=Image.LANCZOS)
                self.dkfz_logo = ImageTk.PhotoImage(ph_resize)  # keep reference on self
                logo_label = Label(self.WindowMain, image=self.dkfz_logo, borderwidth=0)
                logo_label.place(x=120, y=70, anchor=CENTER)
            else:
                print('dkfz logo not found:', img_path)
        except Exception as e:
            print('Could not load dkfz logo:', e)

    def closeWindow(self):
        self.WindowMain.destroy()

class pulseInfoWindowObj:
    def __init__(self):
        self.active_channel = 1
        self.number_of_channels = MRexcite_Control.MRexcite_System.Modulator.number_of_channels
        self.active_sample = 0
    def openGUI(self):
        '''Function defines and opens window for GUI.'''
        #Window for Pulse Info
        self.PulseWindow = Toplevel()
        self.PulseWindow.title('Pulse Info')
        self.PulseWindow.config(width=1200, height=500)
        self.PulseWindow.resizable(False,False)
        self.PulseWindow.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.PulseWindow.protocol('WM_DELETE_WINDOW', self.closeWindow)

        #Channel Select
        self.channelSelectInit(x_center=200,y_center=40) #Initialize Listbox for channel selection
        
        #Sample Select
        self.sampleSelectInit(x_center=200, y_center=90) #Initialize Listbox for sample selection

        #Initialize Figure for amplitude and phase
        self.FigurePulse = Figure(figsize=(9,5), dpi=80)
        self.plotFigureAmplitude = self.FigurePulse.add_subplot(111) #Axes for Amplitude
        self.plotFigureAngle= self.plotFigureAmplitude.twinx() #Axes for Phase
        self.pulseFigureCanvas = FigureCanvasTkAgg(self.FigurePulse, master=self.PulseWindow)
        self.pulseFigureCanvas.get_tk_widget().place(x=750, y=250, anchor='center')

        #Initialize Figure for Polar Plot for one sample
        self.PolarPlotFigure = Figure(figsize=(4,4), dpi=80)
        self.plotPolarPlot = self.PolarPlotFigure.add_subplot(111,projection='polar') #Axes for Amplitude
        self.canvasPolarPlot = FigureCanvasTkAgg(self.PolarPlotFigure, master=self.PulseWindow)
        self.canvasPolarPlot.get_tk_widget().place(x=200, y=290, anchor='center')

        #Initialize Pulse data
        self.pulseAmp = MRexcite_Control.MRexcite_System.Modulator.amplitudes
        self.pulsePhase = MRexcite_Control.MRexcite_System.Modulator.phases
        self.pulseMode = MRexcite_Control.MRexcite_System.Modulator.Amp_state
        self.pulseCounter = MRexcite_Control.MRexcite_System.Modulator.counter_max
        self.pulseMinCounter = min(self.pulseCounter) #Minimum of number of samples through all channels

        if MRexcite_Control.MRexcite_System.RFprepModule.Status == 'High':
            self.ylabel_text = 'Amplitude in V'
        else:
            self.ylabel_text = 'Relative Amplitude'

        self.update()

    def channelSelectInit(self,x_center,y_center):
        '''Initializes the channel selection interface at the coordinates specified by x_center and y_center.'''
        Button_prev = Button(self.PulseWindow, width=3,height=1, text='<', command=lambda: self.channelselect(-1))
        Button_next = Button(self.PulseWindow, width=3,height=1, text='>', command=lambda: self.channelselect(+1))
        self.label_channel = Label(self.PulseWindow, height=1, width=6, text='Ch ' + str(self.active_channel), relief='sunken', bg='white')
        Button_prev.place(x=x_center-50,y=y_center,anchor='center')
        self.label_channel.place(x=x_center,y=y_center, anchor='center')
        Button_next.place(x=x_center+50,y=y_center, anchor='center')
    
    def sampleSelectInit(self,x_center,y_center):
        '''Initializes the channel selection interface at the coordinates specified by x_center and y_center.'''
        Button_prev = Button(self.PulseWindow, width=3,height=1, text='<', command=lambda: self.sampleSelect(-1))
        Button_next = Button(self.PulseWindow, width=3,height=1, text='>', command=lambda: self.sampleSelect(+1))
        self.label_sample = Label(self.PulseWindow, height=1, width=6, text=str(self.active_sample), relief='sunken', bg='white')
        Button_prev.place(x=x_center-50,y=y_center,anchor='center')
        self.label_sample.place(x=x_center,y=y_center, anchor='center')
        Button_next.place(x=x_center+50,y=y_center, anchor='center')

    def channelselect(self,a):
        '''Function for selecting the active channel'''
        self.active_channel = self.active_channel + a
        if self.active_channel<1:
            self.active_channel=1
        elif self.active_channel>self.number_of_channels:
            self.active_channel=self.number_of_channels
        self.label_channel.config(text='Ch ' + str(self.active_channel))
        self.update()

    def sampleSelect(self,a):
        '''Function for selecting the active sample. Note: You can only choose a sample that EVERY channel has.'''
        self.active_sample = self.active_sample + a
        if self.active_sample<0:
            self.active_sample=0
        elif self.active_sample==self.pulseMinCounter:
            self.active_sample=self.pulseMinCounter-1
        self.label_sample.config(text= str(self.active_sample))
        self.update()

    def update(self):
        self.plotFigure()

    def plotFigure(self):
        '''Function to plot all figures.'''
        self.plotFigureAmplitude.clear()
        self.plotFigureAngle.clear()
        self.plotPolarPlot.clear()

        color_amp = 'tab:blue' #Color for amplitude plot
        color_angle = 'tab:red' #Color for phase plot

        isMultiSample = self.pulseCounter[self.active_channel-1] > 1 #I use this to distinguish between multi-sample and single sample pulses. This is important for referencing samples in the code.

        #Pulse plot for one channel
        x = range(self.pulseCounter[self.active_channel-1])
        y1 = self.pulseAmp[self.active_channel-1]
        y2 = self.pulsePhase[self.active_channel-1]
        self.plotFigureAmplitude.plot(x,y1,color_amp)
        self.plotFigureAngle.plot(x,y2,color_angle)

        self.plotFigureAmplitude.set_xlabel('Sample #')
        self.plotFigureAmplitude.set_ylabel(self.ylabel_text,color='tab:blue')
        self.plotFigureAngle.set_ylabel('Phase in °',color='tab:red')
        self.plotFigureAngle.yaxis.set_label_position('right')
        
        #Color Background according to amplifier mode. This is very slow. Need to use fewer boxes.
        if isMultiSample:
            switchPos,value = self._calcBackground(self.pulseMode[self.active_channel-1])
            numberOfAreas = len(value)
            
            if numberOfAreas ==1: #If there is only one mode thorughout the pulse
                if value[0] == 1:
                    backcolor = 'tab:red'
                else:
                    backcolor = 'tab:green'
                self.plotFigureAmplitude.axvspan(xmin=0,xmax=self.pulseCounter[self.active_channel-1]-1,color=backcolor,alpha=0.07)
            else: #If there are changes of the amplifier mode during the pulse
                for a in range(numberOfAreas):
                    if value[a] == 1:
                        backcolor = 'tab:red'
                    else:
                        backcolor = 'tab:green'
                    self.plotFigureAmplitude.axvspan(xmin=switchPos[a]-0.5,xmax=switchPos[a+1]+0.5,color=backcolor,alpha=0.07)
        else:
            if self.pulseMode[self.active_channel-1] == 1:
                backcolor = 'tab:red'
            else:
                backcolor = 'tab:green'
            self.plotFigureAmplitude.axvspan(xmin=-0.5,xmax=0.5,color=backcolor,alpha=0.07)


        
        #Polar plot for one sample
        for a in range(self.number_of_channels):
            if isMultiSample:
                self.plotPolarPlot.plot([0,self.pulsePhase[a][self.active_sample]/180*3.1415],[0,self.pulseAmp[a][self.active_sample]])
            else:
                self.plotPolarPlot.plot([0,self.pulsePhase[a]/180*3.1415],[0,self.pulseAmp[a]])
        if isMultiSample:
            self.plotPolarPlot.scatter(self.pulsePhase[self.active_channel-1][self.active_sample]/180*3.1415,self.pulseAmp[self.active_channel-1][self.active_sample],marker='o',c='tab:red',s=100)
        else:
            self.plotPolarPlot.scatter(self.pulsePhase[self.active_channel-1]/180*3.1415,self.pulseAmp[self.active_channel-1],marker='o',c='tab:red',s=100)
        

        self.FigurePulse.canvas.draw()
        self.PolarPlotFigure.canvas.draw()
    
    def _calcBackground(self,mode):
        '''Function to calculate the background color for amplifier mode'''
        numberOfSamples = len(mode)
        if numberOfSamples == 1:
            return 0, mode
        
        currentValue = -1
        switch_pos=[]
        value=[]
        for a in range(numberOfSamples):
            if mode[a] != currentValue:
                switch_pos.append(a)
                value.append(mode[a])
                currentValue = mode[a]
        switch_pos.append(numberOfSamples-1) #include maximum number of samples as end point for areas.
        return switch_pos,value
        
    def closeWindow(self):
        '''Function to close the Pulse Info window.'''
        self.PulseWindow.destroy()
MainGUI=MainGUIObj()
MainGUI.start_main_GUI()
MainGUI.MainWindow.mainloop()