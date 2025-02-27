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
        self.MainWindow.config(width=800, height=600)
        self.MainWindow.resizable(False,False)
        self.MainWindow.iconbitmap(os.path.dirname(__file__) + r'\images\MRexcite_logo.ico')
        self.MainWindow.protocol('WM_DELETE_WINDOW', self.end_Software) #This is important: If the software is ended, we need to call a function that resets to a safe state (Siemens)
        self.menu_bar()

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


    def openFile(self): #Open a file that contains all settings and pulses from a previous session.
        pass

    def saveFile(self): #Save current settings and pulses for a later session.
        pass

    def loadShim(self): #Load a shim file
        pass
    
    def setCPplus(self): #Applies the CP+ mode for the Body coil.
        pass

    def setTIAMO(self): #Loads a simple predefined TIAMO shim set.
        pass

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


MainGUI=MainGUIObj()
MainGUI.start_main_GUI()
MainGUI.MainWindow.mainloop()