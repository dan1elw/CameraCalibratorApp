# IMPORTS
#import tkinter
#import tkinter.filedialog
#from tkinter.scrolledtext import ScrolledText
#from tkinter import ttk, HORIZONTAL, VERTICAL
#import time
#import os
#import cv2
#import numpy as np

# VARIABLES
LEFT_PATH = './example/example_left_30mm/'
RIGHT_PATH = './example/example_right_30mm/'
SQUARE_SIZE = 30.0  # in mm

# INTERNAL IMPORTS
from .graphics import App
from .image import Images
from .camera import Camera, Stereo
from .cal import SingleCamera, StereoCamera
