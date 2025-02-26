import numpy as np
from time import sleep
from tkinter import *
from tkinter import scrolledtext
import re
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import MRexcite_Control

#Test Program to test whether all I and Q lines are correctly connected within the Modulator Boards. (Helps debugging hardware)

CB = MRexcite_Control.ControlByteObj
data_reset=bytes([CB.reset,0,0,0])
MRexcite_Control.MRexcite_System.SPI.send_bitstream(data_reset)

#Set each byte in I channel on all Modulators

for a in range(12):
    for b in range(360):
        MRexcite_Control.MRexcite_System.Modulator.I_values = [int(pow(2,13)-1+(pow(2,a)-1)*np.sin(np.pi/180*b))]*MRexcite_Control.MRexcite_System.Modulator.number_of_channels
        MRexcite_Control.MRexcite_System.Modulator.Q_values = [int(pow(2,13)-1+(pow(2,a)-1)*np.cos(np.pi/180*b))]*MRexcite_Control.MRexcite_System.Modulator.number_of_channels
        MRexcite_Control.MRexcite_System.Modulator.Amp_state =[0]*MRexcite_Control.MRexcite_System.Modulator.number_of_channels
        data=MRexcite_Control.MRexcite_System.Modulator.return_byte_stream()
        MRexcite_Control.MRexcite_System.SPI.send_bitstream(data)
        sleep(0.01)



