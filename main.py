# IMPORTS
import time
import tkinter
from optic import *

########################################################
# Main Loop
########################################################

if __name__ == '__main__':

    print('\nWelcome to the OPTIC Camera Calibrator!\n')
    
    print(r'   ___  ____ _____ ___ ____ ')
    print(r'  / _ \|  _ \_   _|_ _/ ___| ')
    print(r' | | | | |_) || |  | | |     ')
    print(r' | |_| |  __/ | |  | | |___  ')
    print(r'  \___/|_|    |_| |___\____| ')

    print('\nStart:  {}'.format(time.strftime('%H:%M:%S Uhr')))

    app = App(tkinter.Tk())
    app.master.mainloop()

    if app.Art == 'Single' and app.CalibrationCompleted == True:
        Params = app.CameraParams
    elif app.Art == 'Stereo' and app.CalibrationCompleted == True:
        Params = app.StereoParams

    print('End:  {}\n'.format(time.strftime('%H:%M:%S Uhr')))
