#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Camera Calibrator App

Created by Daniel Weber. Copyright 2022
Version 1.2

This application provides a GUI for an easy calibration of a single or stereo camera.
Calibration takes place trough the functions of the OpenCV library, which is
based on the theoreticle priciples of the Zhang-Calibration process. 

The calculated Calibration-Parameters can be saved in a Numpy file to make 
further usage possible.

The application requires two independent folders with the Calibration-Images
as well as the square size of the checkerboard pattern. Further Information 
on correct use in the Help-Menu or in the Readme.
'''

#####################################################################################################################

import tkinter
import tkinter.filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, HORIZONTAL, VERTICAL
import time
import os
import cv2
import numpy as np
np.set_printoptions(suppress=True, precision=5)

####################################################################################################################
# Class App:
# in this class we create the graphical user interface
# handle the data input for the calibration
# plot the results live
#####################################################################################################################

LEFT_PATH = './example/example_left_30mm/'
RIGHT_PATH = './example/example_right_30mm/'
SQUARE_SIZE = 30.0  # in mm

class App():
    ''' Main Application '''
    
    def __init__(self, master):
        ''' Initialising the GUI '''
        self.master = master
        self.master.title('Camera Calibrator App')
        self.master.resizable(0,0)
        self.timestopper = 0
        self.timepause = 0.02
        self.VERSIONINDEX = '1.1' # Version-Index
        
        # DEFINE AREA's
        self.console = ttk.Frame(master)
        self.console.grid(column=0, row=0, sticky='nwes')
        
        self.vertical = ttk.PanedWindow(master, orient=VERTICAL)
        self.vertical.grid(column=0, row=0, sticky='nsew')
        self.horizontal = ttk.PanedWindow(self.vertical, orient=HORIZONTAL)
        self.vertical.add(self.horizontal)
        
        self.formframe = ttk.Labelframe(self.horizontal, text='')
        self.formframe.columnconfigure(1, weight=1)
        self.horizontal.add(self.formframe, weight=1)
        
        self.console = ttk.Labelframe(self.horizontal, text='')
        self.console.columnconfigure(0, weight=1)
        self.console.rowconfigure(0, weight=1)
        self.horizontal.add(self.console, weight=1)
        
        # INPUT
        ttk.Label(self.formframe, text=' ', font='Arial 2').grid(row=0, column=0, sticky='nw')
        ttk.Label(self.formframe, text='Directories:', font='TkDefaultFont 12 bold').grid(row=10, column=0, columnspan=3, sticky='nw')
        ttk.Label(self.formframe, text=' ', font='Arial 2').grid(row=11, column=0, sticky='nw')
        ttk.Label(self.formframe, text='left camera:                ').grid(row=15, column=0, sticky='w')
        self.InputButtonLeft = ttk.Button(self.formframe, text='Durchsuchen', command=self.InputLeft)
        self.InputButtonLeft.grid(row=15,column=1,sticky='nw')
        ttk.Label(self.formframe, text='right camera:').grid(row=16, column=0 ,sticky='w')
        self.InputButtonRight = ttk.Button(self.formframe, text='Durchsuchen', command=self.InputRight)
        self.InputButtonRight.grid(row=16,column=1,sticky='nw')
        
        ttk.Label(self.formframe, text=' ').grid(row=20, column=0 ,sticky='nw')
        ttk.Label(self.formframe, text='Checkerboard:', font='TkDefaultFont 12 bold').grid(row=21, column=0, columnspan=3, sticky='nw')
        ttk.Label(self.formframe, text=' ', font='Arial 2').grid(row=22, column=0, sticky='nw')
        ttk.Label(self.formframe, text='Square Size [mm]:').grid(row=25, column=0 ,sticky='nw')
        self.entry = tkinter.DoubleVar(); self.entry.set(SQUARE_SIZE)
        tkinter.Entry(self.formframe, textvariable=self.entry, justify='right', width=12).grid(row=25,column=1,sticky='nw',columnspan=8)
        
        ttk.Label(self.formframe, text=' ').grid(row=30, column=0 ,sticky='nw')
        ttk.Label(self.formframe, text='Calibration:', font='TkDefaultFont 12 bold').grid(row=31, column=0, sticky='w')
        self.InputButtonStart = ttk.Button(self.formframe, text=' Start ', command=self.StartButton)
        self.InputButtonStart.grid(row=31,column=1, sticky='nw')
        ttk.Label(self.formframe, text=' ').grid(row=31, column=2 ,sticky='nw')
        
        ttk.Label(self.formframe, text=' ').grid(row=40, column=2 ,sticky='nw')
        self.StatusLabelText = tkinter.StringVar()
        self.StatusLabelText.set(' ')
        self.StatusLabel = ttk.Label(self.formframe, textvariable=self.StatusLabelText)
        self.StatusLabel.grid(row=41, column=0, columnspan=3, sticky='nw')
        
        # CONSOLE
        self.scrollarea = ScrolledText(self.console, state='disabled', wrap=tkinter.WORD, height=25, width=70)
        self.scrollarea.grid(column=0)
        self.scrollarea.tag_config('normal', foreground='black')
        self.scrollarea.tag_config('error', foreground='red')
        self.scrollarea.tag_config('warn', foreground="#FF4D00")
        self.createMenu()
        self.ClearConsole()
        
        # VARIABLES
        self.LeftPath = LEFT_PATH
        self.RightPath = RIGHT_PATH
        self.Art = ''
        self.CalibrationCompleted = False
        self.CalBegonnen = False

    def Insert(self, text, pause=0, form='normal'):
        '''
        function to plot some text into the console.
        errors are red
        writing in the window is disabled.
        '''
        self.scrollarea.configure(state='normal')
        if text[:7] == '[ERROR]':
            self.scrollarea.insert(tkinter.END, text, 'error')
        else:
            self.scrollarea.insert(tkinter.END, text, form)
        self.scrollarea.insert(tkinter.END, '\n')
        self.scrollarea.configure(state='disabled')
        self.scrollarea.yview(tkinter.END)
        self.scrollarea.update()
        
        # waiting a little bit for smoother output
        if pause == 0:
            self.timestopper += 1
            time.sleep(self.timepause)
        
    def ClearConsole(self):
        ''' reset the console to default. '''
        self.scrollarea.configure(state='normal')
        self.scrollarea.delete('1.0', tkinter.END)
        self.Insert("--------------------------------------------------------------------",1)
        self.Insert("Camera Calibrator App\n\nCreated by dan1elw.\nhttps://github.com/dan1elw\nCopyright 2022. Version {}".format(self.VERSIONINDEX),1)
        self.Insert("--------------------------------------------------------------------\n",1)
        self.Insert("Time: {}\n".format(time.strftime('%d.%m.%Y , %H:%M Uhr')))
        self.scrollarea.configure(state='disabled')
        self.scrollarea.update()

    def createMenu(self):
        '''
        create the menu of the application
        with options for saving, new calibration and exit
        also a help and about function
        '''
        menu = tkinter.Menu(self.master, tearoff=False)
        self.master.config(menu=menu)

        # OPTIONS
        filemenu = tkinter.Menu(menu, tearoff=False)
        menu.add_cascade(label='Options', menu=filemenu)
        filemenu.add_command(label='Save Parameters', command=self.MENUSaveParams)
        filemenu.add_command(label='Save Log', command=self.MENUSaveConsole)
        filemenu.add_command(label='New Calibration', command=self.MENUNewCalibration)
        filemenu.add_separator()
        filemenu.add_command(label='Exit App', command=self.master.destroy)
        
        # HELP
        filemenu = tkinter.Menu(menu, tearoff=False)
        menu.add_cascade(label='Help', menu=filemenu)
        filemenu.add_command(label='About', command=self.MENUAbout)
        filemenu.add_command(label='Help', command=self.MENUHelp)
        
    def MENUSaveParams(self):
        '''
        save the calculated parameters in a npz-file
        reusable in an other python script
        '''
        # check if calibration is completed
        if self.CalibrationCompleted == True:
            ftypes = [('All files', '*'), ('Numpy Array Datei (.npz)', '.npz')]
            file = tkinter.filedialog.asksaveasfilename(initialfile='CalibrateParameters.npz', filetypes=ftypes, defaultextension='.npz')
            if file == '':
                return
            
            # save single camera parameters
            if self.Art == 'Single':
                d = self.CameraParams
                np.savez(file, **d)
                npz = dict(np.load(file))
                size = (npz['Imgpoints'].shape[0], npz['Imgpoints'].shape[1], npz['Imgpoints'].shape[3])
                npz['Imgpoints'] = np.resize(npz.pop('Imgpoints'), size)
                np.savez(file, **npz)
                
            # save stereo camera parameters
            elif self.Art == 'Stereo':
                d = self.StereoParams
                np.savez(file, **d)
                npz = dict(np.load(file))
                size = (npz['L_Imgpoints'].shape[0], npz['L_Imgpoints'].shape[1], npz['L_Imgpoints'].shape[3])
                npz['L_Imgpoints'] = np.resize(npz.pop('L_Imgpoints'), size)
                npz['R_Imgpoints'] = np.resize(npz.pop('R_Imgpoints'), size)
                np.savez(file, **npz)
                
            self.Insert('\n--------------------------------------------------------------------\n')
            self.Insert('Parameters saved under:\n{}'.format(file))
            self.Insert('\n--------------------------------------------------------------------\n')
        else:
            self.Insert('[ERROR] No Parameters. Calibrate first!')
        
    def MENUSaveConsole(self):
        ''' save the console content as a txt file '''
        ftypes = [('All files', '*'), ('Text Documents (.txt)', '.txt')]
        file = tkinter.filedialog.asksaveasfilename(initialfile='CalibrateLog.txt', filetypes=ftypes, defaultextension='.txt')
        txt = self.scrollarea.get('1.0', tkinter.END)
        if file=='':
            return
        f = open(file, 'w')
        f.write(txt)
        f.close()
        
        self.Insert('\n--------------------------------------------------------------------\n')
        self.Insert('Log saved under:\n{}'.format(file))
        self.Insert('\n--------------------------------------------------------------------\n')
        
    def MENUNewCalibration(self):
        ''' reset for a new calibration '''
        self.StatusLabelText.set(' ')
        self.SwitchButtonState('NORMAL')
        self.entry.set(30.0)
        self.formframe.update()
        self.ClearConsole()
        
        self.LeftPath = ''
        self.RightPath = ''
        self.Art = ''
        self.CalibrationCompleted = False
        self.CalBegonnen = False
        self.timestopper = 0
        
    def MENUAbout(self):
        ''' popup window with about text '''
        COPYRIGHT = 2022  # copyright year
        txt = 'Camera Calibrator App\nCreated by Daniel Weber. Copyright {}\nVersion {}'.format(COPYRIGHT,self.VERSIONINDEX)
        tkinter.messagebox.showinfo('Camera Calibrator App - About',txt)
        
    def MENUHelp(self):
        ''' help '''
        txt = 'HELP:\n\n'
        txt += 'for detailed help look at the README file.'
        
        self.Insert('--------------------------------------------------------------------\n')
        self.Insert(txt)
        self.Insert('\n--------------------------------------------------------------------\n')

    def InputLeft(self):
        ''' input directory of the left camera '''
        self.LeftPath = tkinter.filedialog.askdirectory()
        self.Insert('Path left camera:')
        self.Insert(self.LeftPath)
        self.Insert('')
        
    def InputRight(self):
        ''' input directory of the right camera '''
        self.RightPath = tkinter.filedialog.askdirectory()
        self.Insert('Path right camera:')
        self.Insert(self.RightPath)
        self.Insert('')
        
    def CheckInput(self):
        ''' check the inputs (directories, square size) '''
        
        # SQUARE SIZE --------------------------------------------------------
        # has to be a number
        # dot as decimal seperator
        
        try:
            self.SquareSize = self.entry.get()
        except:
            self.Insert('[ERROR] Fehlerhafte Angabe der Square Size.')
            return False
        
        # DIRECTORIES --------------------------------------------------------
        
        left = str(self.LeftPath); right = str(self.RightPath)
        
        # at least one directory has to be specified
        # decision if single or stereo camera
        
        if left == '' and right == '':
            self.Insert('[ERROR] Keine Ordner angegeben.')
            return False                
        else:
            self.SingleOrStereo(left, right)
            
        # left and right directory cannot be the same
        
        if left == right:
            self.Insert('[ERROR] Linker und Rechter Ordner sind identisch')
            return False
        
        # directories cannot be empty
        # images have to be the same datatype
        # possible types: bmp, jpeg, jpg, png, tiff, tif
        
        types = ['bmp', 'jpeg', 'jpg', 'png', 'tiff', 'tif']
        
        if self.Art=='Stereo' or self.Seite=='L':
            l = os.listdir(left)
            if len(l) == 0:
                self.Insert('[ERROR] Linker Ordner ist leer.')
                return False
            
            endsL = []
            for i in range(len(l)):
                partsL = l[i].split('.'); endsL.append(partsL.pop())
                
            endsL = list(set(endsL))
            if len(endsL) != 1:
                self.Insert('[ERROR] Im linken Ordner existieren mehrere Dateitypen.')
                return False
            
            if not endsL[0].lower() in types:
                self.Insert('[ERROR] Ungültiger Dateityp: {}'.format(endsL[0].lower()))
                return False
            
        if self.Art=='Stereo' or self.Seite=='R':
            r = os.listdir(right)
            if len(r) == 0:
                self.Insert('[ERROR] Rechter Ordner ist leer.')
                return False
            
            endsR = []
            for i in range(len(r)):
                partsR = r[i].split('.'); endsR.append(partsR.pop())
                
            endsR = list(set(endsR))
            if len(endsR) != 1:
                self.Insert('[ERROR] Im rechten Ordner existieren mehrere Dateitypen.')
                return False
            
            if not endsR[0].lower() in types:
                self.Insert('[ERROR] Ungültiger Dateityp: {}'.format(endsR[0].lower()))
                return False
            
        # same number of images for both cameras for stereo calibration
        
        if self.Art == 'Stereo':
            if len(l) != len(r):
                self.Insert('[ERROR] Pro Kamera müssen gleich viele Bilder existieren.')
                return False
        
        return True
    
    def SingleOrStereo(self, left, right):
        ''' decide if calibrating a single or a stereo camera '''
        if left == '' or right == '':
            self.Art = 'Single'
            if left == '':
                self.Seite = 'R'; self.SinglePath = right
            else:
                self.Seite = 'L'; self.SinglePath = left
        else:
            self.Art = 'Stereo'
            self.Seite = ''
            self.SinglePath = ''
    
    def StartButton(self):
        if self.CheckInput():
            
            self.ClearConsole()
            self.CalBegonnen = True
            self.StatusLabelText.set('Calibrating. Please wait ...')
            self.SwitchButtonState('DISABLED')
            
            if self.Art == 'Stereo':
                
                self.StartTime = time.perf_counter(); self.timestopper = 0
                self.Insert('--------------------------------------------------------------------\n')
                self.Insert('INPUT PARAMETERS:\n')
                self.Insert('Path left camera:')
                self.Insert(self.LeftPath); self.Insert('')
                self.Insert('Path right camera:')
                self.Insert(self.RightPath); self.Insert('')
                self.Insert('Square Size: {} mm\n'.format(self.SquareSize))
                self.Insert('--------------------------------------------------------------------\n')
                self.Insert('STEREO CAMERA CALIBRATION\n')
                self.Insert('--------------------------------------------------------------------\n')
                self.StereoParams = StereoCamera(self.LeftPath, self.RightPath, self.SquareSize)
                
                if not self.StereoParams == None:
                    self.StatusLabelText.set('Calibration done.')
                    self.CalibrationCompleted = True
                    
                if self.CalibrationCompleted:
                    end = time.perf_counter() - self.StartTime - self.timestopper * self.timepause
                    self.Insert('time for calibration: {:.4f} seconds\n'.format(end))
                    self.Insert('--------------------------------------------------------------------\n')
                    self.Insert('CALIBRATION COMPLETED\n')
                    self.Insert('--------------------------------------------------------------------\n')
                    
            elif self.Art == 'Single':
                
                self.StartTime = time.perf_counter(); self.timestopper = 0
                self.Insert('--------------------------------------------------------------------\n')
                self.Insert('INPUT PARAMETERS:\n')
                self.Insert('Path camera:')
                self.Insert(self.SinglePath); self.Insert('')
                self.Insert('Square Size: {} mm\n'.format(self.SquareSize))
                self.Insert('--------------------------------------------------------------------\n')
                self.Insert('SINGLE CAMERA CALIBRATION\n')
                self.Insert('--------------------------------------------------------------------\n')
                self.CameraParams = SingleCamera(self.SinglePath, self.SquareSize)
                
                if not self.CameraParams == None:
                    self.StatusLabelText.set('Calibration done.')
                    self.CalibrationCompleted = True
                    
                if self.CalibrationCompleted:
                    end = time.perf_counter() - self.StartTime - self.timestopper * self.timepause
                    self.Insert('time for calibration: {:.4f} seconds\n'.format(end))
                    self.Insert('--------------------------------------------------------------------\n',)
                    self.Insert('CALIBRATION COMPLETED\n')
                    self.Insert('--------------------------------------------------------------------\n')
                    
            if self.CalibrationCompleted == False:
                self.StatusLabelText.set('Error while calibrating.')
                
            self.InfoAfterCalibration()
            self.SwitchButtonState('NORMAL')
    
    def SwitchButtonState(self, state):
        if state == 'DISABLED':
            self.InputButtonLeft['state'] = tkinter.DISABLED
            self.InputButtonRight['state'] = tkinter.DISABLED
            self.InputButtonStart['state'] = tkinter.DISABLED
            
        if state == 'NORMAL':
            self.InputButtonLeft['state'] = tkinter.NORMAL
            self.InputButtonRight['state'] = tkinter.NORMAL
            self.InputButtonStart['state'] = tkinter.NORMAL
    
    def InfoAfterCalibration(self):
        if not self.CalibrationCompleted:
            return
        
        self.Insert('INFORMATION:\n')
        self.Insert('- export parameters before closing the window!',1)
        self.Insert('  Menu -> Options -> Save Parameters\n',1)
        self.Insert('- displayed values are rounded.',1)
        self.Insert('  saved with all decimal places.',1)
        
        self.Insert('\n--------------------------------------------------------------------\n',1)

#####################################################################################################################
# Class Images:
# in this class we discribe the calibration images
# analyze the pictures and detect the points
#####################################################################################################################

class Images():
    ''' load and analyze the images '''
    
    def __init__(self, path, SquareSize):
        self.ImageData = {}
        self.Check = True
        self.ImageData['OrdnerPfad'] = path
        self.ImageData['SquareSize'] = SquareSize
        self.SortImageNames()
        self.GetBoardSize()
        self.GetChessboard()
        
    def SortImageNames(self):
        '''
        read all the files in the directory
        sort by name
        '''
        # extract all files
        imagelist = os.listdir(self.ImageData['OrdnerPfad'])
        imagelist = sorted(imagelist)
        
        # length of filenames
        lengths = []
        for name in imagelist:
            lengths.append(len(name))
        lengths = sorted(list(set(lengths)))
        
        # sort by name
        ImageNames = []
        ImageNamesRaw = []
        for l in lengths:
            for name in imagelist:
                if len(name) == l:
                    ImageNames.append(os.path.join(self.ImageData['OrdnerPfad'],name))
                    ImageNamesRaw.append(name)
        
        self.ImageData['ImagePfade'] = ImageNames
        self.ImageData['ImageNamesRaw'] = ImageNamesRaw
        
    def GetBoardSize(self):
        '''
        analyze one image to detect the checkerboard size
        possible from min. (3,4) to max. (13,14)
        quadratic is not possible
        '''
        self.BoardSizeFehler = False
        imagepath = self.ImageData['ImagePfade'][0]
        img = cv2.imread(imagepath)
        
        # convert the image to 20% of original size to save time
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray,(0,0),fx=0.2,fy=0.2) # 20%
        
        # possible board sizes
        sizes = np.array([[7,11],[6,9],[5,7],
                          [3,4],[3,5],[3,6],[3,7],[3,8],[4,5],[4,6],[4,7],[4,8],[4,9],
                          [5,6],[5,8],[5,9],[5,10],[6,7],[6,8],[6,10],[6,11],
                          [7,8],[7,9],[7,10],[7,12],[8,9],[8,10],[8,11],[8,12],[8,13],
                          [9,10],[9,11],[9,12],[9,13],[9,14],[10,11],[10,12],[10,13],[10,14],
                          [11,12],[11,13],[11,14],[12,13],[12,14],[13,14]])
        
        # check all sizes in the array above
        for k in range(sizes.shape[0]):
            size = tuple(sizes[k,:])
            ret, _ = cv2.findChessboardCorners(gray, size)
            if ret:
                break
            
        # if not found we try the same with 50% of original size
        if ret == False:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray,(0,0),fx=0.5,fy=0.5) # 50%
            for k in range(sizes.shape[0]):
                size = tuple(sizes[k,:])
                ret, _ = cv2.findChessboardCorners(gray, size)
                if ret:
                    break
                if k == (sizes.shape[0]-1):
                    self.BoardSizeFehler = True
                   
        size = np.array(size)
        BoardSize = (size.max(), size.min())
        self.ImageData['BoardSize'] = BoardSize
        self.ImageData['ImageSize'] = tuple(img.shape[:2])
        
    def GetChessboard(self):
        ''' search for checkerboard and save points '''
        paths = self.ImageData['ImagePfade']
        boardSize = self.ImageData['BoardSize']
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # Objectpoints 
        objp = np.zeros((boardSize[0]*boardSize[1],3), np.float32)
        objp[:,:2] = np.mgrid[0:boardSize[0],0:boardSize[1]].T.reshape(-1,2)
        objp *= self.ImageData['SquareSize']
        
        objpoints = []; imgpoints = []
        
        # Imagepoints
        for name in paths:
            img = cv2.imread(name)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, boardSize)
            if ret:
                objpoints.append(objp)
                corners2 = cv2.cornerSubPix(gray, corners, (4,4), (-1,-1), criteria)
                imgpoints.append(corners2)
            else:
                return None
            
        self.ImageData['Objpoints'] = objpoints
        self.ImageData['Imgpoints'] = imgpoints

#####################################################################################################################
# Class Camera:
# calibrating the camera
# need a application of Images first
#####################################################################################################################

class Camera():
    
    def __init__(self, ImageData):
        self.CameraParams = {}
        self.CameraParams['Objpoints'] = ImageData['Objpoints']
        self.CameraParams['Imgpoints'] = ImageData['Imgpoints']
        self.CameraParams['ImagePfade'] = ImageData['ImagePfade']
        self.CameraParams['BoardSize'] = ImageData['BoardSize']
        self.CameraParams['ImageSize'] = ImageData['ImageSize']
        self.CameraParams['SquareSize'] = ImageData['SquareSize']
        self.ImageNamesRaw = ImageData['ImageNamesRaw']
        
        self.Calibration()
        self.Errors()
        self.PrintResults()
        
    def Calibration(self):
        '''
        calibration of the camera
        save all values in CameraParams
        '''
        gray = cv2.cvtColor(cv2.imread(self.CameraParams['ImagePfade'][0]), cv2.COLOR_BGR2GRAY)
        g = gray.shape[::-1]
        
        # HINT: additional settings can be set here
        flags = 0
        # flags |= cv2.CALIB_RATIONAL_MODEL # 6 instead of 3 radial parameters
        
        # calibration
        (ret, mtx, dist, rvecs, tvecs) = cv2.calibrateCamera(self.CameraParams['Objpoints'], self.CameraParams['Imgpoints'], g, None, None, flags=flags)
        
        # calculation of the rotationmatrix and transformmatrix
        Rmtx = []; Tmtx = []; k = 0
        for r in rvecs: 
            Rmtx.append(cv2.Rodrigues(r)[0])
            Tmtx.append(np.vstack((np.hstack((Rmtx[k],tvecs[k])),np.array([0,0,0,1]))))
            k += 1
        
        # additional intrinsic matrix with distortion
        img = cv2.imread(self.CameraParams['ImagePfade'][0],0)
        h,w = img.shape[:2]
        newmtx, roi = cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
        
        if np.sum(roi) == 0:
            roi = (0,0,w-1,h-1)
        
        self.CameraParams['Intrinsic'] = mtx
        self.CameraParams['Distortion'] = dist
        self.CameraParams['DistortionROI'] = roi
        self.CameraParams['DistortionIntrinsic'] = newmtx
        self.CameraParams['RotVektor'] = rvecs
        self.CameraParams['RotMatrix'] = Rmtx
        self.CameraParams['Extrinsics'] = Tmtx
        self.CameraParams['TransVektor'] = tvecs
    
    def Errors(self):
        ''' Reprojection Errors '''
        objp = np.array(self.CameraParams['Objpoints'][0])
        imgp = np.array(self.CameraParams['Imgpoints'])
        imgp = imgp.reshape((imgp.shape[0], imgp.shape[1], imgp.shape[3]))
        K = np.array(self.CameraParams['Intrinsic'])
        D = np.array(self.CameraParams['Distortion'])
        R = np.array(self.CameraParams['RotVektor'])
        T = np.array(self.CameraParams['TransVektor'])
        N = imgp.shape[0] # Views
        
        # Neue imgp berechnen
        imgpNew = []
        for i in range(N):
            temp, _ = cv2.projectPoints(objp, R[i], T[i], K, D)
            imgpNew.append(temp.reshape((temp.shape[0], temp.shape[2])))
        imgpNew = np.array(imgpNew)
        
        # calculate error of every point (x and y)
        err = []
        for i in range(N):
            err.append(imgp[i] - imgpNew[i])
        err = np.array(err)
        
        # mean Errors
        def RMSE(err):
            return np.sqrt(np.mean(np.sum(err**2, axis=1)))
        
        errall = np.copy(err[0])
        rmsePerView = [RMSE(err[0])]
        
        for i in range(1,N):
            errall = np.vstack((errall, err[i]))
            rmsePerView.append(RMSE(err[i]))
            
        rmseAll = RMSE(errall)
        
        self.CameraParams['Errors'] = rmsePerView
        self.CameraParams['MeanError'] = rmseAll
        self.CameraParams['Reprojectedpoints'] = imgpNew
    
    def PrintResults(self):
        ''' write the results in the window '''
        app.Insert('general data:\n' +
                   '  Image Size:       {} x {}\n'.format(self.CameraParams['ImageSize'][0], self.CameraParams['ImageSize'][1]) +
                   '  Board Size:       {} x {}\n'.format(self.CameraParams['BoardSize'][0], self.CameraParams['BoardSize'][1]) +
                   '  Image Quantaty:   {}\n'.format(len(self.CameraParams['Objpoints'])) + 
                   '  Points per Image: {}\n'.format(self.CameraParams['Objpoints'][0].shape[0]))
        
        app.Insert('Intrinsic Matrix:\n'+str(self.CameraParams['Intrinsic'])+'\n')
        
        D = np.round(self.CameraParams['Distortion'],5)[0]
        if D.shape[0] > 5:
            app.Insert('Distortion:\n'+
                       '  radial:     '+str(D[0])+' '+str(D[1])+' '+str(D[4])+' '+str(D[5])+' '+str(D[6])+' '+str(D[7])+'\n'
                       '  tangential: '+str(D[2])+' '+str(D[3])+'\n')
        else:
            app.Insert('Distortion:\n'+
                       '  radial:     '+str(D[0])+'  '+str(D[1])+'  '+str(D[4])+'\n'
                       '  tangential: '+str(D[2])+'  '+str(D[3])+'\n')

        app.Insert('Extrinsic Matrices:')
        for i in range(len(self.CameraParams['Extrinsics'])):
            t = self.CameraParams['Extrinsics'][i]
            app.Insert('from Image '+str(i+1)+': ({})\n'.format(self.ImageNamesRaw[i])+str(t)+'\n')
            
        app.Insert('Mean Reprojection Error per Image [Pixel]:')
        k = 1
        for e in self.CameraParams['Errors']:
            app.Insert(' {:3}) {:<10.6f}'.format(k, e), 1)
            k += 1
        app.Insert('')
        app.Insert('Mean Reprojection Error [Pixel]: '+str(np.round(self.CameraParams['MeanError'],5))+'\n')
        
        if self.CameraParams['MeanError'] > 1:
            app.Insert('Attention, Reprojection Error over 1!\n', form='warn')

#####################################################################################################################
# Class Stereo:
# calibrating a stereo camera set
#####################################################################################################################

class Stereo():
    def __init__(self, LeftData, RightData):
        self.StereoParams = {}
        self.Left = LeftData
        self.Right = RightData

        self.ExtractCameraParams()
        self.Calibration()
        self.PrintResults()

    def ExtractCameraParams(self):
        ''' extract the parameters of the left and right camera '''
        # general data without präfix
        self.StereoParams['BoardSize'] = self.Left.pop('BoardSize'); self.Right.pop('BoardSize')
        self.StereoParams['SquareSize'] = self.Left.pop('SquareSize'); self.Right.pop('SquareSize')
        self.StereoParams['ImageSize'] = self.Left.pop('ImageSize'); self.Right.pop('ImageSize')
        
        # specific parameters of left camera with 'L_'
        for Lkey in self.Left.keys():
            name = 'L_'+str(Lkey)
            self.StereoParams[name] = self.Left[Lkey]
            
        # specific parameters of right camera with 'R_'
        for Rkey in self.Right.keys():
            name = 'R_'+str(Rkey)
            self.StereoParams[name] = self.Right[Rkey]
    
    def Calibration(self):
        ''' Calculating the stereo camera parameters '''
        obj = self.StereoParams['L_Objpoints']
        img1 = self.StereoParams['L_Imgpoints']
        k1 = self.StereoParams['L_Intrinsic']
        d1 = self.StereoParams['L_Distortion']
        img2 = self.StereoParams['R_Imgpoints']
        k2 = self.StereoParams['R_Intrinsic']
        d2 = self.StereoParams['R_Distortion']
        
        grayL1 = cv2.imread(self.StereoParams['L_ImagePfade'][0], 0)
        g = grayL1.shape[::-1]
        
        # HINT: additional settings for stereoCalibrate function
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)
        flags = 0
        flags |= cv2.CALIB_FIX_INTRINSIC
        # flags |= cv2.CALIB_USE_INTRINSIC_GUESS
        # flags |= cv2.CALIB_FIX_FOCAL_LENGTH
        # flags |= cv2.CALIB_ZERO_TANGENT_DIST
        
        # stereo camera calibration
        (ret, K1, D1, K2, D2, R, t, E, F) = cv2.stereoCalibrate(obj, img1, img2, k1, d1, k2, d2, g, criteria=criteria, flags=flags)
        
        # transformation matrix
        T = np.vstack((np.hstack((R,t)),np.array([0,0,0,1])))
        
        self.StereoParams['Transformation'] = T
        self.StereoParams['Essential'] = E
        self.StereoParams['Fundamental'] = F
        self.StereoParams['MeanError'] = ret
        
        # HINT: uncomment follwing rows if you wish a new calculation of the specific intrinsics
        # self.StereoParams['L_Intrinsic'] = K1
        # self.StereoParams['L_Distortion'] = D1
        # self.StereoParams['R_Intrinsic'] = K2
        # self.StereoParams['R_Distortion'] = D2
    
    def PrintResults(self):
        ''' plot the results '''
        app.Insert('Transformationmatrix:\n'+str(self.StereoParams['Transformation'])+'\n')
        
        app.Insert('Essentialmatrix:\n'+str(self.StereoParams['Essential'])+'\n')
        
        np.set_printoptions(suppress=False, precision=5)
        app.Insert('Fundamentalmatrix:\n'+str(self.StereoParams['Fundamental'])+'\n')
        np.set_printoptions(suppress=True, precision=5)
        
        app.Insert('Overall Mean Reprojection Error: '+str(np.round(self.StereoParams['MeanError'],5))+'\n')
        
        if self.StereoParams['MeanError'] > 1:
            app.Insert('Attention, Reprojection Error over 1!\n', form='warn')
    
#####################################################################################################################
# Calibration
#####################################################################################################################

def SingleCamera(path, SquareSize):
    try:
        Image = Images(path, SquareSize)
        ImageData = Image.ImageData
    except:
        app.Insert('[ERROR] Error while analyzing the images.')
        return None
    if Image.BoardSizeFehler == True:
        app.Insert('[ERROR] Error while detecting the Board Size.')
        return None
    try:
        Cam = Camera(ImageData)
        CameraData = Cam.CameraParams
        return CameraData
    except:
        app.Insert('[ERROR] Error while Calibration.')
        return None
    
def StereoCamera(pathL, pathR, SquareSize):
    app.Insert('CALIBRATION LEFT CAMERAA\n')
    
    LeftData = SingleCamera(pathL, SquareSize)
    if LeftData == None:
        return None
    
    app.Insert('--------------------------------------------------------------------\n')
    app.Insert('CALIBRATION RIGHT CAMERA\n')
    
    RightData = SingleCamera(pathR, SquareSize)
    if RightData == None:
        return None
    
    app.Insert('--------------------------------------------------------------------\n')
    app.Insert('CALIBRATING THE STEREO CAMERA\n')

    try:
        St = Stereo(LeftData, RightData)
        StereoData = St.StereoParams
        return StereoData
    
    except:
        app.Insert('[ERROR] Error while calibrating the stereo camera.')
        return None
    
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
