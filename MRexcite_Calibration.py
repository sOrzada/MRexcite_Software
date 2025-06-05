'''GUIs for calibration of MRexcite System.'''
from tkinter import *

import scipy.interpolate
import MRexcite_Control
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import os
import math
import scipy
from PIL import Image, ImageTk
from time import sleep
import numpy as np

U_0dBm = math.sqrt(0.05) #RMS voltage at 0 dBm on 50 Ohms.

class CalibrateZeroObj:
    '''This class is used to calibrate the modulators LO-feedthrough/zero offset.\n
    It contains a GUI which can be started by using the "openGUI()" method.'''
    def __init__(self) -> None:
        self.number_of_channels = MRexcite_Control.MRexcite_System.Modulator.number_of_channels
        self.active_channel = 1
        self.IQoffset = MRexcite_Control.MRexcite_System.Modulator.IQoffset
        self.IQoffset_hybrid = MRexcite_Control.MRexcite_System.Modulator.IQoffset_hybrid

        #Initiate Amplitudes, Phases and States(for the purpose of this Calibration step, the letter is unimportant, but needs to be set anyway)
        self.amplitudes = list([0])*self.number_of_channels
        self.phases = [0]*self.number_of_channels
        self.states = [0]*self.number_of_channels

        self.RFprepState = IntVar()
    
    def openGUI(self):
        '''Prepares and Opens the GUI or this Class Object.'''
        self.WindowMain = Toplevel()
        self.WindowMain.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.WindowMain.title('Zero Point Calibration of Modulators')
        self.WindowMain.config(width=1200, height=550)
        self.WindowMain.protocol('WM_DELETE_WINDOW', lambda: self.saveClose())
        
        #Initialize Controls
        self.__controlButtonsInit__(x_center=150, y_center=250) #Initialize control buttons
        self.__channelSelectInit__(x_center=150,y_center=100) #Initialize Listbox for channel selection

        self.ButtonSaveClose = Button(self.WindowMain, width=10, height=2, text='Save & Close', command=self.saveClose)
        self.ButtonSaveClose.place(x=150, y=400, anchor='center')

        #Selection of gain:
        if MRexcite_Control.MRexcite_System.RFprepModule.Status=='Full':
            self.RFprepState.set(0)
        else:
            self.RFprepState.set(1)
        
        self.checkBoxGain = Checkbutton(self.WindowMain,text='Hybrid Mode', variable=self.RFprepState, onvalue=1, offvalue=0,command=self.update)
        self.checkBoxGain.place(x=150,y=60,anchor=CENTER)



        #Load explanatory image and show in GUI
        self.image_path=os.path.dirname(__file__) + r'\Images\Zero_Point_Cal.jpg'
        self.ph=Image.open(self.image_path)
        self.ph_resize=self.ph.resize((450,300), resample=1)
        self.ph_image=ImageTk.PhotoImage(self.ph_resize)
        self.label_image = Label(self.WindowMain, image=self.ph_image)
        self.label_image.config(image=self.ph_image)
        self.label_image.place(x=950,y=250, anchor='center')

        #Initialize Figure for Offset indication
        self.figureOffset = Figure(figsize=(5,5), dpi=80)
        self.plotFigureOffset = self.figureOffset.add_subplot(111)
        self.canvasFigureOffset = FigureCanvasTkAgg(self.figureOffset, master=self.WindowMain)
        self.canvasFigureOffset.get_tk_widget().place(x=500, y=250, anchor='center')
        
        #Update to show user the current offset
        self.update()

    def mainloop(self):
        '''Calls the mainloop() method for the GUI window.'''
        self.WindowMain.mainloop()

    def changeIQ(self,I_change,Q_change):
        '''Changes the IQ offset for the active channel by the numbers specified in I_change and Q_change'''
        if self.RFprepState.get()==0:
            self.IQoffset[self.active_channel-1][0] = self.IQoffset[self.active_channel-1][0] + I_change
            self.IQoffset[self.active_channel-1][1] = self.IQoffset[self.active_channel-1][1] + Q_change
        else:
            self.IQoffset_hybrid[self.active_channel-1][0] = self.IQoffset_hybrid[self.active_channel-1][0] + I_change
            self.IQoffset_hybrid[self.active_channel-1][1] = self.IQoffset_hybrid[self.active_channel-1][1] + Q_change
        
        self.update()

    def saveClose(self):
        '''Function for closing the calibration Window. Also calls the "write_IQ_offset" method of the Modulator-Object.'''
        
        MRexcite_Control.MRexcite_System.Modulator.IQoffset = self.IQoffset
        MRexcite_Control.MRexcite_System.Modulator.write_IQ_offset()
        self.WindowMain.destroy()
        pass

    def __controlButtonsInit__(self,x_center,y_center): #Initialize Control Panel for I/Q correction
        '''Initializes the control Buttons and places them as a group at the location specified in x_center and y_center'''
        
        #This frame is only for looks:
        self.frame_buttons = Frame(self.WindowMain, width=180, height=180, borderwidth=3, relief='ridge')
        
        #Buttons for up/down
        self.frame_buttons.place(x=x_center,y=y_center, anchor='center')
        self.Button_up1 = Button(self.WindowMain, width=3, height=1, text='+1', command=lambda: self.changeIQ(1,0))
        self.Button_up10 = Button(self.WindowMain, width=3, height=1, text='+10', command=lambda: self.changeIQ(10,0))
        self.Button_down1 = Button(self.WindowMain, width=3, height=1, text='-1', command=lambda: self.changeIQ(-1,0))
        self.Button_down10 = Button(self.WindowMain, width=3, height=1, text='-10', command=lambda: self.changeIQ(-10,0))
        self.Button_up1.place(x=x_center, y=y_center-30, anchor='center')
        self.Button_up10.place(x=x_center, y=y_center-60, anchor='center')
        self.Button_down1.place(x=x_center, y=y_center+30, anchor='center')
        self.Button_down10.place(x=x_center, y=y_center+60, anchor='center')

        #Buttons for left/right
        self.Button_right1 = Button(self.WindowMain, width=3, height=1, text='+1', command=lambda: self.changeIQ(0,1))
        self.Button_right10 = Button(self.WindowMain, width=3, height=1, text='+10', command=lambda: self.changeIQ(0,10))
        self.Button_left1 = Button(self.WindowMain, width=3, height=1, text='-1', command=lambda: self.changeIQ(0,-1))
        self.Button_left10 = Button(self.WindowMain, width=3, height=1, text='-10', command=lambda: self.changeIQ(0,-10))
        self.Button_right1.place(x=x_center+30, y=y_center, anchor='center')
        self.Button_right10.place(x=x_center+65, y=y_center, anchor='center')
        self.Button_left1.place(x=x_center-30, y=y_center, anchor='center')
        self.Button_left10.place(x=x_center-65, y=y_center, anchor='center')
    
    def __channelSelectInit__(self, x_center, y_center): #Initialize Buttons and Label for Channel selection
        '''Initializes the channel selection interface at the coordinates specified by x_center and y_center.'''
        Button_prev = Button(self.WindowMain, width=3,height=1, text='<', command=lambda: self.channelselect(-1))
        Button_next = Button(self.WindowMain, width=3,height=1, text='>', command=lambda: self.channelselect(+1))
        self.label_channel = Label(self.WindowMain, height=1, width=6, text='Ch ' + str(self.active_channel), relief='sunken', bg='white')
        Button_prev.place(x=x_center-50,y=y_center,anchor='center')
        self.label_channel.place(x=x_center,y=y_center, anchor='center')
        Button_next.place(x=x_center+50,y=y_center, anchor='center')
    
    def channelselect(self,a): #Select channel with buttons and stay within actual channel count
        '''Selects a channel and makes sure you stay within actual channel count.'''
        self.active_channel = self.active_channel + a
        if self.active_channel<1:
            self.active_channel=1
        elif self.active_channel>self.number_of_channels:
            self.active_channel=self.number_of_channels
        self.label_channel.config(text='Ch ' + str(self.active_channel))
        self.update()

    def plotFigure(self):
        '''Plots the figure for modulator offset from center.'''
        a=self.active_channel
        self.plotFigureOffset.clear()
        self.plotFigureOffset.scatter(0,0, marker='o')
        if self.RFprepState.get()==0:
            self.plotFigureOffset.scatter(self.IQoffset[a-1][1],self.IQoffset[a-1][0], marker='x')
        else:
            self.plotFigureOffset.scatter(self.IQoffset_hybrid[a-1][1],self.IQoffset_hybrid[a-1][0], marker='x')

        self.plotFigureOffset.axis([-128,128,-128,128])
        self.plotFigureOffset.set_xlabel('I offset')
        self.plotFigureOffset.set_ylabel('Q offset')
        self.plotFigureOffset.set_title('Channel ' + str(self.active_channel))
        self.figureOffset.tight_layout()
        self.canvasFigureOffset.draw()

    def update(self):
        '''Calls functions for updating the figure and setting the Modulators. (self.plotFigure() and self.set_Modulators)'''
        if self.RFprepState.get()==0:
            MRexcite_Control.MRexcite_System.RFprepModule.set_gain_high()
        else:
            MRexcite_Control.MRexcite_System.RFprepModule.set_gain_low()

        self.plotFigure()
        self.set_Modulators()
    
    def set_Modulators(self):
        '''Sets the modulators by transmitting through SPI-Interface. Uses the SPI-object from the STASIS System.'''
        CB=MRexcite_Control.ControlByteObj 
        MRexcite_Control.MRexcite_System.Modulator.IQoffset = self.IQoffset
        MRexcite_Control.MRexcite_System.Modulator.set_amplitudes_phases_state(self.amplitudes,self.phases,self.states)
        bitstream=MRexcite_Control.MRexcite_System.Modulator.return_byte_stream()
        bitstream_RFprep = MRexcite_Control.MRexcite_System.RFprepModule.return_byte_stream() #Set RFprep Module to correct state.
        start_adress = MRexcite_Control.MRexcite_System.Modulator.start_address
        bitstream_adress = bytes([0 , start_adress-1+self.active_channel,0,0]) #sending this word as final word lets the active channels LED light up. Unblank is disabled.
        bitstream_enable_mod = bytes([CB.clock,0,0,0]) #Send clock bit.
        bitstream = bitstream_RFprep+bitstream +bitstream_enable_mod+ bitstream_adress
        try:
            MRexcite_Control.MRexcite_System.SPI.send_bitstream(bitstream)
            sleep(0.05)
            MRexcite_Control.MRexcite_System.SPI.send_bitstream(bitstream_enable_mod+bitstream_enable_mod+bitstream_adress)
            sleep(0.05)
        except:
            print('Error! Could not transmit via SPI.')
            sleep(0.05)

class CalibrateLinearity1DObj:
    '''This class is used for calibrating for non-linearities of the Modulator/Amplifier system in full calibration mode.'''
    def __init__(self) -> None:
        self.number_of_channels = MRexcite_Control.MRexcite_System.Modulator.number_of_channels
        self.active_channel = 1
        self.IQoffset = MRexcite_Control.MRexcite_System.Modulator.IQoffset #Load IQoffset from Modulators.
        self.Cal1D = MRexcite_Control.MRexcite_System.Modulator.Cal1D       #Load 1D Calibration from Modulators.
        self.dig_index = 0  #Always start with the first digital value (which is 0, so no danger to components or people)
        self.max_dig_value = MRexcite_Control.MRexcite_System.Modulator.number_of_1D_samples #Maximum number of 1D samples.

    def openGUI(self):
        '''Prepares and Opens the GUI or this Class Object.'''
        #Preparations for safety:
        self.active_channel = 1 #Always start with first channel when user activates GUI.
        self.dig_index = 0  #Always start with the first digital value (which is 0, so no danger to components or people)
        
        #Open Main Window
        self.WindowCalLin = Toplevel()
        self.WindowCalLin.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.WindowCalLin.title('Linearity Calibration of Amplifiers')
        self.WindowCalLin.config(width=1300, height=550)
        self.WindowCalLin.protocol('WM_DELETE_WINDOW', lambda: self.saveClose())

        #Load explanatory image and show in GUI
        self.image_path=os.path.dirname(__file__) + r'\Images\Cal_Lin1D.jpg'
        self.ph=Image.open(self.image_path)
        self.ph_resize=self.ph.resize((550,375), resample=1)
        self.ph_image=ImageTk.PhotoImage(self.ph_resize)
        self.label_image = Label(self.WindowCalLin, image=self.ph_image)
        self.label_image.config(image=self.ph_image)
        self.label_image.place(x=1000,y=250, anchor='center')

        #Save & Close Button
        self.ButtonSaveClose = Button(self.WindowCalLin, width=10, height=2, text='Save & Close', command=self.saveClose)
        self.ButtonSaveClose.place(x=150, y=400, anchor='center')
        
        #Channel Select
        self.channelSelectInit(x_center=150,y_center=100) #Initialize Listbox for channel selection
        
        #Radio Buttons for Amplifier Mode
        self.init_radiobuttons(x_start=80,y_start=130)

        #Digital Value Selector
        self.init_dig_value_select(x_center=150,y_center=210)

        #Initialize Entry Boxes
        self.init_entry_boxes(x_center=130, y_center=250)

        #Initialize Figure for linearity results
        self.Figurelin = Figure(figsize=(5,5), dpi=80)
        self.plotFigurelin = self.Figurelin.add_subplot(111) #Axes for Amplitude
        self.plotFigureAngle= self.plotFigurelin.twinx() #Axes for Phase
        self.canvasFigurelin = FigureCanvasTkAgg(self.Figurelin, master=self.WindowCalLin)
        self.canvasFigurelin.get_tk_widget().place(x=500, y=250, anchor='center')

        #Set System state
        MRexcite_Control.MRexcite_System.RFprepModule.set_gain_high() #We can only calibrate for linearity in high power mode, so set it.
        

        #Update
        self.update()
    
    def init_radiobuttons(self, x_start, y_start):
        '''Initializes the radio buttons for selecting amplifier state.'''
        self.Amp_Mode=IntVar()
        R1= Radiobutton(self.WindowCalLin, text='Low Power Mode', variable=self.Amp_Mode, value=0, command=self.sel)
        R1.place(x=x_start,y=y_start,anchor=W)
        R2= Radiobutton(self.WindowCalLin, text='High Power Mode', variable=self.Amp_Mode, value=1, command=self.sel)
        R2.place(x=x_start,y=y_start+20,anchor=W)
    
    def init_dig_value_select(self, x_center, y_center): #Initialize Buttons and Label for Digital Value Selection
        '''Initializes the channel selection interface at the coordinates specified by x_center and y_center.'''
        Caption1 = Label(self.WindowCalLin, height=1, width=20, text='Digital Value Selector')
        Caption1.place(x=x_center,y=y_center-30, anchor=CENTER)
        Button_prev = Button(self.WindowCalLin, width=3,height=1, text='<', command=lambda: self.dig_value_select(-1))
        Button_next = Button(self.WindowCalLin, width=3,height=1, text='>', command=lambda: self.dig_value_select(+1))
        self.label_dig_value = Label(self.WindowCalLin, height=1, width=6, text=str(0), relief='sunken', bg='white')
        Button_prev.place(x=x_center-50,y=y_center,anchor='center')
        self.label_dig_value.place(x=x_center,y=y_center, anchor='center')
        Button_next.place(x=x_center+50,y=y_center, anchor='center')

    def init_entry_boxes(self,x_center,y_center):
        '''Initializes the entry boxes for amplitude and phase inputs'''
        # Initialize StringVar variables for storing amplitude (dB) and phase (degrees) values
        self.dB_value = StringVar()
        self.deg_value = StringVar()
        
        self.entry_db = Entry(self.WindowCalLin, width=12, textvariable=self.dB_value)
        self.entry_db.place(x=x_center,y=y_center-10, anchor=W)
        label_dB = Label(self.WindowCalLin, height=1, width=6, text='dB')
        label_dB.place(x=x_center-60,y=y_center-10, anchor=W)
        self.entry_degree = Entry(self.WindowCalLin, width=12, textvariable=self.deg_value)
        self.entry_degree.place(x=x_center,y=y_center+10, anchor=W)
        label_deg = Label(self.WindowCalLin, height=1, width=6, text='°')
        label_deg.place(x=x_center-60,y=y_center+10,anchor=W)
        Button_entry= Button(self.WindowCalLin, width=5,height=2, text='Apply', command=lambda: self.apply_entry())
        Button_entry.place(x=x_center+110, y=y_center, anchor=CENTER)

    def channelSelectInit(self, x_center, y_center): #Initialize Buttons and Label for Channel selection
        '''Initializes the channel selection interface at the coordinates specified by x_center and y_center.'''
        Button_prev = Button(self.WindowCalLin, width=3,height=1, text='<', command=lambda: self.channelselect(-1))
        Button_next = Button(self.WindowCalLin, width=3,height=1, text='>', command=lambda: self.channelselect(+1))
        self.label_channel = Label(self.WindowCalLin, height=1, width=6, text='Ch ' + str(self.active_channel), relief='sunken', bg='white')
        Button_prev.place(x=x_center-50,y=y_center,anchor='center')
        self.label_channel.place(x=x_center,y=y_center, anchor='center')
        Button_next.place(x=x_center+50,y=y_center, anchor='center')

    def apply_entry(self):
        '''Applies the entry from the entry boxes and writes them into the Cal1D variable.'''
        if self.dig_index>0: #Only allow changes for digital values other than 0
            voltage=pow(10,float(self.dB_value.get())/20)*U_0dBm
            angle=float(self.deg_value.get())
            self.Cal1D[self.active_channel-1,self.Amp_Mode.get(),self.dig_index,1]=voltage
            self.Cal1D[self.active_channel-1,self.Amp_Mode.get(),self.dig_index,2]=angle
            self.Cal1D[self.active_channel-1,self.Amp_Mode.get(),0,2]=self.Cal1D[self.active_channel-1,self.Amp_Mode.get(),1,2] #We need to make sure that there is no change in angle between 0V and the smallest measured voltage.
        self.update()


    def dig_value_select(self,a):
        '''Selects a digital value from a pre-defined set. These are the digital values added on top of the zero point calibration.'''
        self.dig_index=self.dig_index+a
        if self.dig_index<0:
            self.dig_index=0
        if self.dig_index>self.max_dig_value-1:
            self.dig_index=self.max_dig_value-1
        
        self.label_dig_value.config(text=str(int(self.Cal1D[self.active_channel-1,self.Amp_Mode.get(),self.dig_index,0])))
        self.update()

    def sel(self):
        
        self.update()

    def channelselect(self,a): #Select channel with buttons and stay within actual channel count
        '''Selects a channel and makes sure you stay within actual channel count.'''
        self.dig_value_select(-10000) #Reset to 0 output for safety. User might forget to plug cable!
        self.active_channel = self.active_channel + a
        if self.active_channel<1:
            self.active_channel=1
        elif self.active_channel>self.number_of_channels:
            self.active_channel=self.number_of_channels
        self.label_channel.config(text='Ch ' + str(self.active_channel))
        self.update()

    def plotFigure(self):
        '''Plots the figure for System linearity'''

        color_highlight='0'  #Color for highlighting current point of measurement
        color_amp = 'tab:blue' #Color for amplitude plot
        color_angle = 'tab:red' #Color for phase plot

        ch=self.active_channel-1
        mode=self.Amp_Mode.get()
        dig_index=self.dig_index
        self.plotFigurelin.clear()
        self.plotFigureAngle.clear()

        #For convenience of reader, change y axis of plot:
        if mode==0:
            U_max=100
        else:
            U_max=270
        
        if mode==0:
            x_ax_max=900
        else:
            x_ax_max=4500

        x=range(0,x_ax_max,20) #Range for possible digital values (<2^13-1)

        #Plot interpolated values of Amplitude
        xi=self.Cal1D[ch,mode,:,0]
        yi=self.Cal1D[ch,mode,:,1]
        y=scipy.interpolate.pchip_interpolate(xi,yi,x)
        self.plotFigurelin.plot(x,y,color=color_amp)
        #Plot interpolated values of Phase
        xi=self.Cal1D[ch,mode,:,0]
        yi=self.Cal1D[ch,mode,:,2]
        y=scipy.interpolate.pchip_interpolate(xi,yi,x)
        self.plotFigureAngle.plot(x,y,color=color_angle)

        self.plotFigurelin.scatter(self.Cal1D[ch,mode,:,0],self.Cal1D[ch,mode,:,1], color=color_amp, marker='x')
        self.plotFigurelin.scatter(self.Cal1D[ch,mode,dig_index,0],self.Cal1D[ch,mode,dig_index,1],color=color_highlight, marker='o')
        self.plotFigureAngle.scatter(self.Cal1D[ch,mode,:,0],self.Cal1D[ch,mode,:,2],color=color_angle,marker='*' )
        self.plotFigureAngle.scatter(self.Cal1D[ch,mode,dig_index,0],self.Cal1D[ch,mode,dig_index,2],color=color_highlight, marker='o')
        self.plotFigureAngle.set_ylim(-180,180)
        
        self.plotFigurelin.axis([0,x_ax_max*1.1,0,U_max])
        self.plotFigurelin.set_xlabel('Digital Value')
        self.plotFigurelin.set_ylabel('Output in V',color='tab:blue')
        self.plotFigureAngle.set_ylabel('Phase in °',color='tab:red')
        self.plotFigureAngle.yaxis.set_label_position('right')
        self.plotFigurelin.set_title('Channel ' + str(ch+1) + ', Mode: ' +str(mode))
        self.Figurelin.tight_layout()
        self.Figurelin.canvas.draw()

    def set_Modulators(self):
        '''Updates the modulators.'''
        CB=MRexcite_Control.ControlByteObj 
        bitstream=MRexcite_Control.MRexcite_System.Modulator.return_byte_stream()
        start_adress = MRexcite_Control.MRexcite_System.Modulator.start_address
        bitstream_adress = bytes([CB.enable, start_adress-1+self.active_channel,0,0]) #sending this word as final word lets the active channels LED light up and sets the system transmit.
        bitstream_enable_mod = bytes([CB.clock,0,0,0])
        bitstream = bitstream +bitstream_enable_mod+ bitstream_adress
        try:
            MRexcite_Control.MRexcite_System.SPI.send_bitstream(bitstream)
            sleep(0.05)
            MRexcite_Control.MRexcite_System.SPI.send_bitstream(bitstream_enable_mod+bitstream_enable_mod+bitstream_adress)
            sleep(0.05)
        except:
            print('Error! Could not transmit via SPI.')
            sleep(0.005)
    
    def update(self):
        '''Calls functions for updating the figure and setting the Modulators. (self.plotFigure() and self.set_Modulators)'''
        I_values=[0]*self.number_of_channels
        Q_values=[0]*self.number_of_channels
        
        for a in range(self.number_of_channels): #Set all values for I and Q to calibrated zero, to make sure no transmit happens.
            I_values[a]=pow(2,13)-1 + self.IQoffset[a][0]
            Q_values[a]=pow(2,13)-1 + self.IQoffset[a][1]
        

        ch=self.active_channel-1
        mode=self.Amp_Mode.get()
        dig_index=self.dig_index
        self.plotFigurelin.clear()
        self.entry_degree.delete('0',END)
        self.entry_db.delete('0',END)

        I_values[ch]=int(I_values[ch]+self.Cal1D[ch,mode,dig_index,0]) #For measurement, add the current digital value to zero point.

        MRexcite_Control.MRexcite_System.Modulator.I_values=I_values
        MRexcite_Control.MRexcite_System.Modulator.Q_values=Q_values
        MRexcite_Control.MRexcite_System.Modulator.counter_max=[1]*self.number_of_channels
        MRexcite_Control.MRexcite_System.Modulator.Amp_state=[mode]*self.number_of_channels
        self.set_Modulators() #Set the Modulators to the values just provided.

        if dig_index==0:
            self.entry_db.insert('0','-inf')
            self.entry_degree.insert('0','n.a.')
            self.entry_db.config(state='readonly')
            self.entry_degree.config(state='readonly')
        else:
            self.entry_db.config(state='normal')
            self.entry_degree.config(state='normal')
            self.entry_degree.delete('0',END)
            self.entry_db.delete('0',END)

        current_dB = 20*math.log10((self.Cal1D[ch,mode,dig_index,1]+0.000001)/U_0dBm)
        current_deg = self.Cal1D[ch,mode,dig_index,2]

        
        self.entry_db.insert('0',str(current_dB))
        self.entry_degree.insert('0',str(current_deg))

        self.plotFigure()

    def saveClose(self):
        '''Function for closing the calibration Window. Also calls the "write_1D_Cal" method of the Modulator-Object and disables the system.'''
        try:
            MRexcite_Control.MRexcite_System.disable_system()
        except:
            print('Error! Could not transmit via SPI.')
        MRexcite_Control.MRexcite_System.Modulator.Cal1D=self.Cal1D #Write the new calibration data into the Modulator.
        MRexcite_Control.MRexcite_System.Modulator.write_1D_Cal()
        self.WindowCalLin.destroy()
            
class ModulatorCalibrationObj:
    '''Calibration for Modulators in Hybrid Mode (including gain and phase offset of amplifiers in linear operation).\n
    In Hybrid mode the I and Q channels can have different gain and they might not be 90° apart. To measure this, 
    we need to measure the amplitude and phase for a fixed I and Q value, respectively. Then we can set up a system of equations to
    calculate the I and Q value to achieve a certain amplitude and phase. We need to do this for low and high power modes of the system, respectively,
    to account for the ampltiude and phase errors of the amplifiers.\n
    '''
    def __init__(self) -> None:
        self.number_of_channels = MRexcite_Control.MRexcite_System.Modulator.number_of_channels
        self.active_channel = 1
        self.IQoffset = MRexcite_Control.MRexcite_System.Modulator.IQoffset_hybrid
        self.I_values = [pow(2,14)-1]*self.number_of_channels
        self.Q_values = [pow(2,14)-1]*self.number_of_channels

        self.selected_value = 0 #Selected value for Measurement. 0:I low, 1:Q low, 2: I high, 3: Q high
        self.CalMod = MRexcite_Control.MRexcite_System.Modulator.CalMod      #Load 1D Calibration from Modulators.
        self.test_value_digital = 1000 #Digital value used for test.

        

    def openGUI(self):
        #Preparations for safety:
        self.active_channel = 1 #Always start with first channel when user activates GUI.
        self.system_active = 0 #This variable indicates whether the system should be active or not.
        #Set System to correct state:
        MRexcite_Control.MRexcite_System.disable_system() #System needs to be disabled on start to avoid accidents.
        
        #Open Main Window
        self.WindowCalMod = Toplevel()
        self.WindowCalMod.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.WindowCalMod.title('Calibration of amplifiers')
        self.WindowCalMod.config(width=1300, height=550)
        self.WindowCalMod.protocol('WM_DELETE_WINDOW', lambda: self.saveClose())
        
        self.init_unblank_button(150,300)
        self.channelSelectInit(150,70)
        self.init_value_select(150,150)
        self.init_entry_boxes(x_center=110, y_center=200)


        #Initialize Figure for IQ visualization
        self.FigureModIQ = Figure(figsize=(5,5), dpi=80)
        self.plotFigureModIQ = self.FigureModIQ.add_subplot(111,projection='polar') #Axes for Amplitude
        self.canvasFigureModIQ = FigureCanvasTkAgg(self.FigureModIQ, master=self.WindowCalMod)
        self.canvasFigureModIQ.get_tk_widget().place(x=500, y=250, anchor='center')
        self.plotFigureModIQ.set_ylim([0,2])

        #Set System state
        MRexcite_Control.MRexcite_System.RFprepModule.set_gain_low() #This is the calibration for the low gain state, so set it.

        self.update()
        

    def channelSelectInit(self, x_center:int, y_center:int): #Initialize Buttons and Label for Channel selection
        '''Initializes the channel selection interface at the coordinates specified by x_center and y_center.'''
        Button_prev = Button(self.WindowCalMod, width=3,height=1, text='<', command=lambda: self.channelselect(-1))
        Button_next = Button(self.WindowCalMod, width=3,height=1, text='>', command=lambda: self.channelselect(+1))
        self.label_channel = Label(self.WindowCalMod, height=1, width=6, text='Ch ' + str(self.active_channel), relief='sunken', bg='white')
        Button_prev.place(x=x_center-50,y=y_center,anchor='center')
        self.label_channel.place(x=x_center,y=y_center, anchor='center')
        Button_next.place(x=x_center+50,y=y_center, anchor='center')
    
    def channelselect(self,a:int): #Select channel with buttons and stay within actual channel count
        '''Selects a channel and makes sure you stay within actual channel count.'''
        self.system_active = 0 #Set System to inactive to avoid accidents. User must re-enable system. (self.update() must be called to make this happen!)
        self.active_channel = self.active_channel + a
        if self.active_channel<1:
            self.active_channel=1
        elif self.active_channel>self.number_of_channels:
            self.active_channel=self.number_of_channels
        self.label_channel.config(text='Ch ' + str(self.active_channel))
        
        self.update()
    
    def init_unblank_button(self,x_center:int,y_center:int):
        self.Button_Unblank = Button(self.WindowCalMod,width=10, height=3, text='Unblank', command=lambda: self.toggle_unblank())
        self.Button_Unblank.place(x=x_center,y=y_center,anchor=CENTER)

    def init_value_select(self, x_center:int, y_center:int): #Initialize Buttons and Label for Digital Value Selection
        '''Initializes the channel selection interface at the coordinates specified by x_center and y_center.'''
        Caption1 = Label(self.WindowCalMod, height=1, width=20, text='Digital Value Selector')
        Caption1.place(x=x_center,y=y_center-30, anchor=CENTER)
        Button_prev = Button(self.WindowCalMod, width=3,height=1, text='<', command=lambda: self.value_select(-1))
        Button_next = Button(self.WindowCalMod, width=3,height=1, text='>', command=lambda: self.value_select(+1))
        self.label_dig_value = Label(self.WindowCalMod, height=1, width=10, text='I low', relief='sunken', bg='white')
        Button_prev.place(x=x_center-70,y=y_center,anchor='center')
        self.label_dig_value.place(x=x_center,y=y_center, anchor='center')
        Button_next.place(x=x_center+70,y=y_center, anchor='center')
    
    def value_select(self,change_in: int):
        '''Select which value should be played out'''
        self.selected_value = self.selected_value+change_in
        display_list = ['I low','Q low', 'I high', 'Q_high']
        #Make sure to stay in the range 0-3:
        if self.selected_value<0:
            self.selected_value=0
        if self.selected_value>3:
            self.selected_value = 3
        
        self.label_dig_value.config(text=display_list[self.selected_value]) #Set text
        self.update()

    def init_entry_boxes(self,x_center,y_center):
        '''Initializes the entry boxes for amplitude and phase inputs'''
        self.dB_value = StringVar()
        self.deg_value = StringVar()
        
        self.entry_db = Entry(self.WindowCalMod, width=12, textvariable=self.dB_value)
        self.entry_db.place(x=x_center,y=y_center-10, anchor=W)
        label_dB = Label(self.WindowCalMod, height=1, width=6, text='dB')
        label_dB.place(x=x_center-60,y=y_center-10, anchor=W)
        self.entry_degree = Entry(self.WindowCalMod, width=12, textvariable=self.deg_value)
        self.entry_degree.place(x=x_center,y=y_center+10, anchor=W)
        label_deg = Label(self.WindowCalMod, height=1, width=6, text='°')
        label_deg.place(x=x_center-60,y=y_center+10,anchor=W)
        Button_entry= Button(self.WindowCalMod, width=5,height=2, text='Apply', command=lambda: self.apply_entry())
        Button_entry.place(x=x_center+110, y=y_center, anchor=CENTER)
    
    def toggle_unblank(self):
        '''This function is called when the Unblank-Button is pressed. Toggles system states.'''
        if self.system_active==0:
            self.system_active=1
        else:
            self.system_active=0
        
        self.update()
    
    def update_figure(self):
        # Define colors for different measurement points
        color_I_low = '#0000EE'  # Color for low-gain I measurement
        color_Q_low = '#0000AA'  # Color for low-gain Q measurement
        color_I_high = '#EE0000'  # Color for high-gain I measurement
        color_Q_high = '#AA0000'  # Color for high-gain Q measurement

        # Clear the previous plot
        self.plotFigureModIQ.clear()
        ch = self.active_channel-1
        values = self.CalMod[ch,:,:,:]

        # Plot low-gain I measurement as a vector in polar coordinates
        cplx_value = (values[0,0,0]+1j*values[0,1,0])
        self.plotFigureModIQ.plot([0,np.angle(cplx_value)],[0,np.abs(cplx_value)], color = color_I_low)

        # Plot low-gain Q measurement as a vector in polar coordinates
        cplx_value = (values[0,0,1]+1j*values[0,1,1])
        self.plotFigureModIQ.plot([0,np.angle(cplx_value)],[0,np.abs(cplx_value)],color = color_Q_low)

        # Plot high-gain I measurement as a vector in polar coordinates
        cplx_value = (values[1,0,0]+1j*values[1,1,0])
        self.plotFigureModIQ.plot([0,np.angle(cplx_value)],[0,np.abs(cplx_value)], color = color_I_high)

        # Plot high-gain Q measurement as a vector in polar coordinates
        cplx_value = (values[1,0,1]+1j*values[1,1,1])
        self.plotFigureModIQ.plot([0,np.angle(cplx_value)],[0,np.abs(cplx_value)], color = color_Q_high)

        # Highlight the currently selected measurement point
        d=self.get_values()
        self.plotFigureModIQ.scatter(d['Phase_rad'],d['Amp_lin'], marker = 'x')
        self.plotFigureModIQ.scatter(d['Phase_rad'],d['Amp_lin'], marker = 'o')

        # Redraw the canvas to reflect the updates
        self.FigureModIQ.canvas.draw()


    def update(self):
        '''Central function to update entries, figures and system settings after changes.'''
        #Set Modulators ():
        self.set_modulators()

        #Set unblank status:
        if self.system_active==0:
            try:
                MRexcite_Control.MRexcite_System.disable_system()
            except:
                pass
            self.Button_Unblank.config(relief='raised')
        else:
            try:
                MRexcite_Control.MRexcite_System.enable_system(add = self.active_channel-1 + MRexcite_Control.MRexcite_System.Modulator.start_address) #Enable and light up channel
            except:
                pass
            self.Button_Unblank.config(relief='sunken')
        
       
        #Write current internal values into entry fields:
        d = self.get_values()
        self.dB_value.set(str(d['Amp']))
        self.deg_value.set(str(d['Phase']))

        #Update Figure:
        self.update_figure()



    def set_modulators(self):
        '''Set the modulators to the correct state and send data to hardware.'''
        I_values = self.I_values # Make a local copy which can then be changed.
        Q_values = self.Q_values # Make a local copy which can then be changed.

        #Add offset to the local I and Q values
        for ch in range(self.number_of_channels):
            I_values[ch]= I_values[ch] + MRexcite_Control.MRexcite_System.Modulator.IQoffset_hybrid[ch][0]
            Q_values[ch]= Q_values[ch] + MRexcite_Control.MRexcite_System.Modulator.IQoffset_hybrid[ch][1]
        
        #Decide which value has to be changed in local variable. (We want to change only one digital value away from 0)
        if self.selected_value<2:
            mode = 0
            dimension = self.selected_value
        else:
            mode = 1
            dimension = self.selected_value -2

        #Apply local values to variables stored in System
        MRexcite_Control.MRexcite_System.Modulator.Amp_state = [mode]*self.number_of_channels #Set the correct amplifier mode
        MRexcite_Control.MRexcite_System.Modulator.I_values = I_values 
        MRexcite_Control.MRexcite_System.Modulator.Q_values = Q_values

        #Add the test value to the correct variable in the MRexcite System
        ch=self.active_channel-1
        if dimension == 0:
            MRexcite_Control.MRexcite_System.Modulator.I_values[ch] = MRexcite_Control.MRexcite_System.Modulator.I_values[ch] + self.test_value_digital
        else:
            MRexcite_Control.MRexcite_System.Modulator.Q_values[ch] = MRexcite_Control.MRexcite_System.Modulator.Q_values[ch] + self.test_value_digital

        #Apply all data to hardware.
        MRexcite_Control.MRexcite_System.SetAll()


    def get_values(self):
        '''Returns a dictionary where 'Amp' is the Amplitude in dB and 'Phase' is the phase in degree, taken from the calibration data of the current point.'''
        ch = self.active_channel-1
        if self.selected_value<2:
            mode = 0
            dimension = self.selected_value
        else:
            mode = 1
            dimension = self.selected_value -2
        I_cal = self.CalMod[ch,mode,0,dimension]
        Q_cal = self.CalMod[ch,mode,1,dimension]
        value_cplx = I_cal + 1j * Q_cal
        d = dict()
        d['Amp_lin'] = np.abs(value_cplx)
        d['Phase_rad'] = np.angle(value_cplx)
        d['Cplx'] = value_cplx
        d['Amp'] = np.round(20*np.log10(np.abs(value_cplx)),3) #rounding is done to avoid numbers like "1.934343e-15" to be shown. More than 2 digits after comma for dB values are overkill anyway.
        d['Phase']=np.angle(value_cplx)/np.pi*180
        return d

    def apply_entry(self):
        '''Applies Entries to Calibration array when button is pressed.''' 
        ch=self.active_channel-1
        input_dB = float(self.entry_db.get())
        input_phase = float(self.entry_degree.get())
        amplitude = pow(10,input_dB/20)
        phase = input_phase/180 * np.pi
        IQ_meas_cplx = amplitude * np.exp(1j*phase)
        I_meas = np.real(IQ_meas_cplx)
        Q_meas = np.imag(IQ_meas_cplx)
        
        #Depending on "selected_values" decide where to write measured value in array
        if self.selected_value<2:
            mode = 0
            dimension = self.selected_value
        else:
            mode = 1
            dimension = self.selected_value -2

        self.CalMod[ch,mode,0,dimension]=I_meas
        self.CalMod[ch,mode,1,dimension]=Q_meas

        self.update()

    def saveClose(self): #TODO: Normalize values.
        '''Close Calibration GUI and save the calibration data to file.'''
        MRexcite_Control.MRexcite_System.Modulator.CalMod=self.CalMod #Send calibration data to system.
        MRexcite_Control.MRexcite_System.Modulator.write_Mod_Cal() #Write Calibration data to file.
        try:
            MRexcite_Control.MRexcite_System.disable_system() #Disable Unblank.
        except:
            print('Error! Could not transmit via SPI.')
        self.WindowCalMod.destroy() #Close window.
