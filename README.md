# CameraCalibratorApp

An app for calibration of a camera or stereo-camera with OpenCV.

## Start of the Application

## Reusing the saved Parameters

After a successful calibration you can save the calculated parameters with a command in the menu.
The parametes will be saved in a npz file. To use the stored data you have to run following code in your file.

'''python
import numpy as np
params = dict(np.load('filename.npz'))
'''
