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
VERSIONINDEX = '1.2.0'

# SETTINGS
np.set_printoptions(suppress=True, precision=5)

########################################################
# Class App:
# in this class we create the graphical user interface
# handle the data input for the calibration and plot 
# the results live
########################################################

class App():
    '''
    Main Application Class for the Camera Calibrator App
    creates the GUI and handles user inputs
    '''
    
    def __init__(self, master):
        '''
        Initialising the GUI
        '''

        self.master = master
        self.master.title('Camera Calibrator App')
        self.master.resizable(0,0)
        self.timestopper = 0
        self.timepause = 0.02
        self.VERSIONINDEX = VERSIONINDEX
        
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
        self.scrollarea = Console(self.console, height=25, width=70)
        self.scrollarea.VERSIONINDEX = self.VERSIONINDEX
        self.scrollarea.timepause = self.timepause
        self.scrollarea.timestopper = self.timestopper
        self.scrollarea.clear()

        self._create_menu()

        # VARIABLES
        self.LeftPath = LEFT_PATH
        self.RightPath = RIGHT_PATH
        self.Art = ''
        self.CalibrationCompleted = False
        self.CalBegonnen = False

    def _create_menu(self):
        '''
        create the menu of the application
        with options for saving, new calibration and exit
        '''

        menu = tkinter.Menu(self.master, tearoff=False)
        self.master.config(menu=menu)

        # OPTIONS
        filemenu = tkinter.Menu(menu, tearoff=False)
        menu.add_cascade(label='Options', menu=filemenu)
        filemenu.add_command(label='Save Parameters', command=self._menu_save_parameters)
        filemenu.add_command(label='Save Log', command=self._menu_save_log)
        filemenu.add_command(label='New Calibration', command=self._menu_new_calibration)
        filemenu.add_separator()
        filemenu.add_command(label='Exit App', command=self.master.destroy)
        
        # HELP
        filemenu = tkinter.Menu(menu, tearoff=False)
        menu.add_cascade(label='Help', menu=filemenu)
        filemenu.add_command(label='About', command=self._menu_about)
        filemenu.add_command(label='Help', command=self._menu_help)
        
    def _menu_save_parameters(self):
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
                
            self.scrollarea.print('\n--------------------------------------------------------------------\n')
            self.scrollarea.print('Parameters saved under:\n{}'.format(file))
            self.scrollarea.print('\n--------------------------------------------------------------------\n')
        else:
            self.scrollarea.print('[ERROR] No Parameters. Calibrate first!')
        
    def _menu_save_log(self):
        '''
        save the console content as a txt file
        '''

        ftypes = [('All files', '*'), ('Text Documents (.txt)', '.txt')]
        file = tkinter.filedialog.asksaveasfilename(initialfile='CalibrateLog.txt', filetypes=ftypes, defaultextension='.txt')
        txt = self.scrollarea.get('1.0', tkinter.END)
        if file=='':
            return
        f = open(file, 'w')
        f.write(txt)
        f.close()
        
        self.scrollarea.print('\n--------------------------------------------------------------------\n')
        self.scrollarea.print('Log saved under:\n{}'.format(file))
        self.scrollarea.print('\n--------------------------------------------------------------------\n')
        
    def _menu_new_calibration(self):
        '''
        Reset the whole application in order to start a new calibration
        '''

        self.StatusLabelText.set(' ')
        self.SwitchButtonState('NORMAL')
        self.entry.set(30.0)
        self.formframe.update()
        self.scrollarea.clear()
        
        self.LeftPath = ''
        self.RightPath = ''
        self.Art = ''
        self.CalibrationCompleted = False
        self.CalBegonnen = False
        self.timestopper = 0
        
    def _menu_about(self):
        '''
        popup window with about text
        '''

        txt = "Camera Calibrator App\nCreated by Daniel (https://github.com/dan1elw)\nCopyright 2026. Version {}".format(self.VERSIONINDEX)
        tkinter.messagebox.showinfo('Camera Calibrator App - About',txt)
        
    def _menu_help(self):
        '''
        "I need help!"
        '''

        txt = 'HELP:\n\n'
        txt += 'for detailed help look at the README file.'
        
        self.scrollarea.print('--------------------------------------------------------------------\n')
        self.scrollarea.print(txt)
        self.scrollarea.print('\n--------------------------------------------------------------------\n')

    def InputLeft(self):
        '''
        input directory of the left camera
        '''

        self.LeftPath = tkinter.filedialog.askdirectory()
        self.scrollarea.print('Path left camera:')
        self.scrollarea.print(self.LeftPath)
        self.scrollarea.print('')
        
    def InputRight(self):
        '''
        input directory of the right camera
        '''

        self.RightPath = tkinter.filedialog.askdirectory()
        self.scrollarea.print('Path right camera:')
        self.scrollarea.print(self.RightPath)
        self.scrollarea.print('')
        
    def CheckInput(self):
        '''
        check the inputs (directories, square size)
        '''
        
        # SQUARE SIZE --------------------------------------------------------
        # has to be a number
        # dot as decimal seperator
        
        try:
            self.SquareSize = self.entry.get()
        except:
            self.scrollarea.print('[ERROR] Fehlerhafte Angabe der Square Size.')
            return False
        
        # DIRECTORIES --------------------------------------------------------
        
        left = str(self.LeftPath); right = str(self.RightPath)
        
        # at least one directory has to be specified
        # decision if single or stereo camera
        
        if left == '' and right == '':
            self.scrollarea.print('[ERROR] Keine Ordner angegeben.')
            return False                
        else:
            self.SingleOrStereo(left, right)
            
        # left and right directory cannot be the same
        
        if left == right:
            self.scrollarea.print('[ERROR] Linker und Rechter Ordner sind identisch')
            return False
        
        # directories cannot be empty
        # images have to be the same datatype
        # possible types: bmp, jpeg, jpg, png, tiff, tif
        
        types = ['bmp', 'jpeg', 'jpg', 'png', 'tiff', 'tif']
        
        if self.Art=='Stereo' or self.Seite=='L':
            l = os.listdir(left)
            if len(l) == 0:
                self.scrollarea.print('[ERROR] Linker Ordner ist leer.')
                return False
            
            endsL = []
            for i in range(len(l)):
                partsL = l[i].split('.'); endsL.append(partsL.pop())
                
            endsL = list(set(endsL))
            if len(endsL) != 1:
                self.scrollarea.print('[ERROR] Im linken Ordner existieren mehrere Dateitypen.')
                return False
            
            if not endsL[0].lower() in types:
                self.scrollarea.print('[ERROR] Ungültiger Dateityp: {}'.format(endsL[0].lower()))
                return False
            
        if self.Art=='Stereo' or self.Seite=='R':
            r = os.listdir(right)
            if len(r) == 0:
                self.scrollarea.print('[ERROR] Rechter Ordner ist leer.')
                return False
            
            endsR = []
            for i in range(len(r)):
                partsR = r[i].split('.'); endsR.append(partsR.pop())
                
            endsR = list(set(endsR))
            if len(endsR) != 1:
                self.scrollarea.print('[ERROR] Im rechten Ordner existieren mehrere Dateitypen.')
                return False
            
            if not endsR[0].lower() in types:
                self.scrollarea.print('[ERROR] Ungültiger Dateityp: {}'.format(endsR[0].lower()))
                return False
            
        # same number of images for both cameras for stereo calibration
        
        if self.Art == 'Stereo':
            if len(l) != len(r):
                self.scrollarea.print('[ERROR] Pro Kamera müssen gleich viele Bilder existieren.')
                return False
        
        return True
    
    def SingleOrStereo(self, left, right):
        '''
        decide if calibrating a single or a stereo camera
        '''

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
        '''
        Start Button definition
        starts the calibration process after checking the inputs
        '''

        if self.CheckInput():
            
            self.scrollarea.clear()
            self.CalBegonnen = True
            self.StatusLabelText.set('Calibrating. Please wait ...')
            self.SwitchButtonState('DISABLED')
            
            if self.Art == 'Stereo':
                
                self.StartTime = time.perf_counter(); self.timestopper = 0
                self.scrollarea.print('--------------------------------------------------------------------\n')
                self.scrollarea.print('INPUT PARAMETERS:\n')
                self.scrollarea.print('Path left camera:')
                self.scrollarea.print(self.LeftPath); self.scrollarea.print('')
                self.scrollarea.print('Path right camera:')
                self.scrollarea.print(self.RightPath); self.scrollarea.print('')
                self.scrollarea.print('Square Size: {} mm\n'.format(self.SquareSize))
                self.scrollarea.print('--------------------------------------------------------------------\n')
                self.scrollarea.print('STEREO CAMERA CALIBRATION\n')
                self.scrollarea.print('--------------------------------------------------------------------\n')
                self.StereoParams = StereoCamera(self, self.LeftPath, self.RightPath, self.SquareSize)
                
                if not self.StereoParams == None:
                    self.StatusLabelText.set('Calibration done.')
                    self.CalibrationCompleted = True
                    
                if self.CalibrationCompleted:
                    end = time.perf_counter() - self.StartTime - self.timestopper * self.timepause
                    self.scrollarea.print('time for calibration: {:.4f} seconds\n'.format(end))
                    self.scrollarea.print('--------------------------------------------------------------------\n')
                    self.scrollarea.print('CALIBRATION SUCCESSFULL\n', format='success')
                    self.scrollarea.print('--------------------------------------------------------------------\n')
                    
            elif self.Art == 'Single':
                
                self.StartTime = time.perf_counter(); self.timestopper = 0
                self.scrollarea.print('--------------------------------------------------------------------\n')
                self.scrollarea.print('INPUT PARAMETERS:\n')
                self.scrollarea.print('Path camera:')
                self.scrollarea.print(self.SinglePath); self.scrollarea.print('')
                self.scrollarea.print('Square Size: {} mm\n'.format(self.SquareSize))
                self.scrollarea.print('--------------------------------------------------------------------\n')
                self.scrollarea.print('SINGLE CAMERA CALIBRATION\n')
                self.scrollarea.print('--------------------------------------------------------------------\n')
                self.CameraParams = SingleCamera(self, self.SinglePath, self.SquareSize)
                
                if not self.CameraParams == None:
                    self.StatusLabelText.set('Calibration done.')
                    self.CalibrationCompleted = True
                    
                if self.CalibrationCompleted:
                    end = time.perf_counter() - self.StartTime - self.timestopper * self.timepause
                    self.scrollarea.print('time for calibration: {:.4f} seconds\n'.format(end))
                    self.scrollarea.print('--------------------------------------------------------------------\n')
                    self.scrollarea.print('CALIBRATION SUCCESSFULL\n', format='success')
                    self.scrollarea.print('--------------------------------------------------------------------\n')
                    
            if self.CalibrationCompleted == False:
                self.StatusLabelText.set('Error while calibrating.')
                
            self.InfoAfterCalibration()
            self.SwitchButtonState('NORMAL')
    
    def SwitchButtonState(self, state):
        '''
        Enable or disable input buttons. (gray out)
        '''

        if state == 'DISABLED':
            self.InputButtonLeft['state'] = tkinter.DISABLED
            self.InputButtonRight['state'] = tkinter.DISABLED
            self.InputButtonStart['state'] = tkinter.DISABLED
            
        if state == 'NORMAL':
            self.InputButtonLeft['state'] = tkinter.NORMAL
            self.InputButtonRight['state'] = tkinter.NORMAL
            self.InputButtonStart['state'] = tkinter.NORMAL
    
    def InfoAfterCalibration(self):
        '''
        Will add some information after the calibration is completed.
        Currently disabled.
        '''

        if not self.CalibrationCompleted:
            return
        return
        self.scrollarea.print('INFORMATION:\n')
        self.scrollarea.print('- export parameters before closing the window!',1)
        self.scrollarea.print('  Menu -> Options -> Save Parameters\n',1)
        self.scrollarea.print('- displayed values are rounded.',1)
        self.scrollarea.print('  saved with all decimal places.',1)
        
        self.scrollarea.print('\n--------------------------------------------------------------------\n',1)

class Console(ScrolledText):
    '''
    Console class for the output window
    '''

    def __init__(self, console, height=25, width=70):
        super().__init__(console, state='disabled', wrap=tkinter.WORD, height=height, width=width)
        #self.scrollarea = ScrolledText(self.console, state='disabled', wrap=tkinter.WORD, height=25, width=70)
        self.grid(column=0)
        self.tag_config('normal', foreground="#000000")
        self.tag_config('success', foreground="#13D60C")
        self.tag_config('error', foreground="#FF0000")
        self.tag_config('warn', foreground="#FFB217")
    
    def clear(self):
        '''
        reset the console to default
        '''

        self.configure(state='normal')
        self.delete('1.0', tkinter.END)
        self.print("--------------------------------------------------------------------",1)
        self.print("Camera Calibrator App\nCreated by Daniel (https://github.com/dan1elw)\nCopyright 2026. Version {}".format(self.VERSIONINDEX),1)
        self.print("--------------------------------------------------------------------\n",1)
        self.print("Time: {}\n".format(time.strftime('%d.%m.%Y , %H:%M Uhr')))
        self.configure(state='disabled')
        self.update()

    def print(self, text, pause=1, format='normal'):
        '''
        function to plot some formatted text into the console.
        '''

        self.configure(state='normal')
        if text[:7] == '[ERROR]':
            self.insert(tkinter.END, text, 'error')
        else:
            self.insert(tkinter.END, text, format)
        self.insert(tkinter.END, '\n')
        self.configure(state='disabled')
        self.yview(tkinter.END)
        self.update()
        
        # waiting a little bit for smoother output
        if pause == 1:
            self.timestopper += 1
            time.sleep(self.timepause)
