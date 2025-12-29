# CameraCalibratorApp

An app for calibration of a camera or stereo-camera with OpenCV.

## Setup

Install the Python dependencies and (optionally) system GUI packages.

Run via pip:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

Or run the bundled installer script (make it executable first if needed):

```bash
chmod +x setup.sh
./setup.sh
```

If the GUI fails to start because of missing tkinter on Debian/Ubuntu, run:

```bash
sudo apt update && sudo apt install python3-tk
```

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
