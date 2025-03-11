import MRexcite_Control #Contains definition of Hardware and Initializes Hardware.
import pathlib
import scipy
import numpy as np
import configparser
from time import sleep
import os
from tkinter import *
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter.messagebox import askyesno
import re
import MRexcite_Calibration
import pickle
from PIL import Image, ImageTk

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
        self.status_text_box.place(x=700,y=60)

        



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
        PulseMenu.add_command(label='Pulse Info', command=self.PulseInfo)

        TriggerMenu=Menu(MenuBar, tearoff=0)
        MenuBar.add_cascade(label='Trigger', menu=TriggerMenu)
        TriggerMenu.add_command(label='Reset Trigger', command=self.TriggerReset)
        TriggerMenu.add_command(label='Send Trigger', command=self.TriggerSend)
        TriggerMenu.add_command(label='Go to Position...', command=self.TriggerGoTo)

        
        ConfigurationMenu=Menu(MenuBar, tearoff = 0)
        MenuBar.add_cascade(label='Configuration', menu=ConfigurationMenu)
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
            else:
                MRexcite_Control.MRexcite_System.OpticalModule.select_Rx=0
        self.update_status()

    def update_status(self):
        '''This function updates the text and the appearance of the switches. We do this here to make loading a system state easy.'''
        ### TODO: Update hardware when this funtion is called!
        
        #Prepare Text Box
        self.status_text_box.config(state=NORMAL)
        self.status_text_box.delete('1.0',END)
        status_text='Current status of system:\n\n'

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

        if MRexcite_Control.MRexcite_System.TriggerModule.gen_select==0:
            status_text = status_text + 'Single Trigger Mode.\n'
        else:
            sampling_in_kHz=10e6 / MRexcite_Control.MRexcite_System.TriggerModule.clock_divider / 1000
            number_of_samples = MRexcite_Control.MRexcite_System.TriggerModule.clock_counter
            length_of_pulse_in_ms = number_of_samples*1/sampling_in_kHz
            status_text = status_text   + 'Trigger is generated with following paramters:\n'\
                                        + '\tSampling rate: ' + str(sampling_in_kHz) + ' kHz\n'\
                                        + '\tNumber of samples: ' + str(number_of_samples) +'\n'\
                                        + '\tPulse duration: ' + str(length_of_pulse_in_ms) + ' ms\n\n'
        
        #Modulation Type
        status_text = status_text + 'Using ' + MRexcite_Control.MRexcite_System.RFprepModule.Status + ' modulation mode. \n\n'

        #Modulator Status
        max_number_samples = max(MRexcite_Control.MRexcite_System.Modulator.counter_max)
        ID_max = MRexcite_Control.MRexcite_System.Modulator.counter_max.index(max(MRexcite_Control.MRexcite_System.Modulator.counter_max))

        status_text = status_text + 'Maximum number of samples in pulse: ' + str(max_number_samples) + ' (ch: ' + str(ID_max+1) +')\n\n'

        #Unblank Status
        if MRexcite_Control.MRexcite_System.Unblank_Status==0:
            status_text = status_text + 'Unblank is disabled. No RF can be transmitted!'
            self.ButtonArmUnblank.config(relief='raised', fg='red', bg='#dddddd')
        else:
            self.ButtonArmUnblank.config(relief='sunken', fg='black', bg='#00ff00')
            status_text = status_text + 'Unblank is ENABLED! Ready to transmit!'

        
        #Write everything but RF-Pulse to hardware. (We do not write the RF pulse here, as this can take long and the user shouldn't wait 3s after clicking "unblank")
        bytestream_trigger = MRexcite_Control.MRexcite_System.TriggerModule.return_byte_stream()
        bytestream_optical = MRexcite_Control.MRexcite_System.OpticalModule.return_byte_stream()
        bytestream_RFprep = MRexcite_Control.MRexcite_System.RFprepModule.return_byte_stream()
        bytestream_enable = MRexcite_Control.MRexcite_System.EnableModule.return_byte_stream()
        bytestream=bytestream_trigger+bytestream_optical+bytestream_RFprep+bytestream_enable
        try:
            MRexcite_Control.MRexcite_System.SPI.send_bitstream(bytestream)
        except:
            print('Could not send via SPI!')
            status_text= status_text + '\n\n\n\t***!!!Could not connect to SPI!!!***'
        if MRexcite_Control.MRexcite_System.Unblank_Status==1:
            try:
                MRexcite_Control.MRexcite_System.enable_system()
            except:
                pass
                    

        self.status_text_box.insert('1.0',status_text)
        self.status_text_box.config(state=DISABLED)    

    def openFile(self): #Open a file that contains all settings and pulses from a previous session.
        pass

    def saveFile(self): #Save current settings and pulses for a later session.
        pass

    def loadShim(self): #Load a shim file
        f_name=filedialog.askopenfile(mode='rb', filetypes=(('Matlab File','*.mat'),), defaultextension=(('Matlab File','*.mat'),))
        self.displayShim.set(str(f_name.name))
    
    def setCPplus(self): #Applies the CP+ mode for the Body coil.
        pass

    def setTIAMO(self): #Loads a simple predefined TIAMO shim set.
        pass

    def PulseInfo(self): #Provides Information on loaded pulse.
        pass

    def TriggerReset(self):
        MRexcite_Control.MRexcite_System.TriggerReset()
    def TriggerSend(self):
        MRexcite_Control.MRexcite_System.TriggerSend()
    def TriggerGoTo(self):
        
        triggerSelectWindow=TriggerSelectObj()
        triggerSelectWindow.WindowMain.grab_set()
        triggerSelectWindow.WindowMain.wait_window(triggerSelectWindow.WindowMain)

    def settingsGeneral(self): #General settings for the System.
        pass

    def calibrateSystemZero(self): #Calibration of the Zero point of the Modulators
        pass

    def calibrateSystemLin1D(self): #Calibration for full modulation including amplifiers
        pass

    def calibrateModulators(self): #Calibration for hybrid modulation. (Modulators not run in saturation)
        pass

    def callHelp(self):
        pass

    def showInfo(self):
        pass

    def end_Software(self): # This is important to ensure that we switch back to Siemens Mode when we end this software.
        '''This function safely resets the MRexcite System to Siemens mode. (TODO!)'''
        print('We need to shut down the System!!!')
        self.MainWindow.destroy()

class TriggerSelectObj:
    def __init__(self):
        
        posX=120
        posY=100

        #Input Window
        self.WindowMain = Toplevel()
        self.WindowMain.title('MRexcite Control')
        self.WindowMain.config(width=300, height=300)
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


MainGUI=MainGUIObj()
MainGUI.start_main_GUI()
MainGUI.MainWindow.mainloop()