# CameraCalibratorApp

An app for calibration of a camera or stereo-camera with OpenCV.

## Reusing the saved Parameters

After a successful calibration you can save the calculated parameters with a command in the menu.
The parametes will be saved in a npz file. 
To use the stored data you have to run following code in your file.
All the values are stored as a numpy array and can be used for further calculations.

```python
import numpy as np
params = dict(np.load('filename.npz'))
```

## Undistort an image with the Parameters

As an example for the application of the calculated parameters you can undistort an image.
To realy see the difference between before and after I prefer to use a fisheye camera.

```python
import cv2
import numpy as np
params = dict(np.load('filename.npz'))

path = 'exampleimage.jpg'
img = cv2.imread(path,0)
dst = cv2.undistort(img, params['Intrinsic'], params['Distortion'])
```
