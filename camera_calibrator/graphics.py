# IMPORTS
import tkinter
import tkinter.filedialog
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk, HORIZONTAL, VERTICAL
import time
import os
import numpy as np

# INTERNAL IMPORTS
from .cal import SingleCamera, StereoCamera

# VARIABLES
#from .__init__ import LEFT_PATH, RIGHT_PATH, SQUARE_SIZE
LEFT_PATH = './example/example_left_30mm/'
RIGHT_PATH = './example/example_right_30mm/'
SQUARE_SIZE = 30.0  # in mm

# SETTINGS
np.set_printoptions(suppress=True, precision=5)

########################################################
# Class App:
# in this class we create the graphical user interface
# handle the data input for the calibration
# plot the results live
########################################################

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
                self.StereoParams = StereoCamera(self, self.LeftPath, self.RightPath, self.SquareSize)
                
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
                self.CameraParams = SingleCamera(self, self.SinglePath, self.SquareSize)
                
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
