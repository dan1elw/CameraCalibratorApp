# IMPORTS
import time
import tkinter
from camera_calibrator import *

#####################################################################################################################
# Main Loop
#####################################################################################################################

if __name__ == '__main__':
    print('\nCamera Calibrator App\nStart: {}'.format(time.strftime('%H:%M:%S Uhr')))
    root = tkinter.Tk()
    app = App(root)
    root.mainloop()
    if app.Art == 'Single' and app.CalibrationCompleted == True:
        Params = app.CameraParams
    elif app.Art == 'Stereo' and app.CalibrationCompleted == True:
        Params = app.StereoParams
    print('End:  {}'.format(time.strftime('%H:%M:%S Uhr')))
