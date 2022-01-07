#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Camera Calibrator App

Created by Daniel Weber. Copyright 2020
Technische Hochschule Mittelhessen
Version 1.1

GUI zur einfachen Kalibrierung einer Single- oder Stereokamera. Kalibrierung
erfolgt dabei durch die Funktionen der OpenCV Bibliothek, welche auf den 
theoretischen Grundlagen des Zhang-Verfahrens beruhen. Ausgabe der Parameter
in einer Numpy-Datei um ein weiteres Verwenden dieser möglich zu machen.

Anwendung benötigt als Eingabeparameter zwei unabhängige Ordner mit den
Kalibrierungsbildern sowie die Square Size des Schachbrettmusters. Weitere
Informationen zur richtigen Verwendung im Menü unter Help.
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

# %% ################################################################################################################
# Klasse App:
# Diese Klasse dient der Erstellung der Graphischen Benutzeroberfläche.
# Hier wird der Dateninput abgewickelt und die Kalibrierung angestossen.
# Ebenso erfolgt in einer Konsole die "live" Ausgabe der Ergebnisse.
#####################################################################################################################

class App():
    def __init__(self, master):
        ''' 
        Diese Funktion dient der Initialisierung der GUI-Anwendung.
        Festsetzung der Geometrie und des standardmässigen Textinhaltes.
        '''
        self.master = master
        self.master.title('Camera Calibrator App')
        self.master.resizable(0,0)
        self.timestopper = 0; self.timepause = 0.02
        self.VERSIONINDEX = '1.1' # Versions-Index
        
        # DEFINE AREA's
        self.console = ttk.Frame(master)
        self.console.grid(column=0, row=0, sticky='nwes')
        
        self.vertical = ttk.PanedWindow(master, orient=VERTICAL)
        self.vertical.grid(column=0, row=0, sticky='nsew')
        self.horizontal = ttk.PanedWindow(self.vertical, orient=HORIZONTAL)
        self.vertical.add(self.horizontal)
        
        self.formframe = ttk.Labelframe(self.horizontal, text='Eingabe')
        self.formframe.columnconfigure(1, weight=1)
        self.horizontal.add(self.formframe, weight=1)
        
        self.console = ttk.Labelframe(self.horizontal, text='Ausgabefenster')
        self.console.columnconfigure(0, weight=1)
        self.console.rowconfigure(0, weight=1)
        self.horizontal.add(self.console, weight=1)
        
        # INPUT
        ttk.Label(self.formframe, text=' ', font='Arial 2').grid(row=0, column=0, sticky='nw')
        ttk.Label(self.formframe, text='Angabe der Ordner:', font='TkDefaultFont 12 bold').grid(row=10, column=0, columnspan=3, sticky='nw')
        ttk.Label(self.formframe, text=' ', font='Arial 2').grid(row=11, column=0, sticky='nw')
        ttk.Label(self.formframe, text='Linke Kamera:                ').grid(row=15, column=0, sticky='w')
        self.InputButtonLeft = ttk.Button(self.formframe, text='Durchsuchen', command=self.InputLeft)
        self.InputButtonLeft.grid(row=15,column=1,sticky='nw')
        ttk.Label(self.formframe, text='Rechte Kamera:').grid(row=16, column=0 ,sticky='w')
        self.InputButtonRight = ttk.Button(self.formframe, text='Durchsuchen', command=self.InputRight)
        self.InputButtonRight.grid(row=16,column=1,sticky='nw')
        
        ttk.Label(self.formframe, text=' ').grid(row=20, column=0 ,sticky='nw')
        ttk.Label(self.formframe, text='Schachbrettmuster:', font='TkDefaultFont 12 bold').grid(row=21, column=0, columnspan=3, sticky='nw')
        ttk.Label(self.formframe, text=' ', font='Arial 2').grid(row=22, column=0, sticky='nw')
        ttk.Label(self.formframe, text='Square Size [mm]:').grid(row=25, column=0 ,sticky='nw')
        self.entry = tkinter.DoubleVar(); self.entry.set(30.0)
        tkinter.Entry(self.formframe, textvariable=self.entry, justify='right', width=12).grid(row=25,column=1,sticky='nw',columnspan=8)
        
        ttk.Label(self.formframe, text=' ').grid(row=30, column=0 ,sticky='nw')
        ttk.Label(self.formframe, text='Kalibrierung:', font='TkDefaultFont 12 bold').grid(row=31, column=0, sticky='w')
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
        self.scrollarea.tag_config('warn', foreground='#FF8000')
        self.createMenu()
        self.ClearConsole()
        
        # VARIABLES
        self.LeftPath=''
        self.RightPath=''
        self.Art = ''
        self.CalibrationCompleted = False
        self.CalBegonnen = False
        
#####################################################################################################################        
# CONSOLE

    def Insert(self, text, pause=0, form='normal'):
        '''
        Funktion zum Plotten von Text innerhalb des Konsolenfensters.
        Error-Meldungen werden rot ausgegeben.
        Die Fähigkeit zu Schreiben im Fenster ist für den Benutzer deaktiviert.
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
        
        # Bei der Ausgabe wird immer eine gewisse zeit gewartet, dass die Ausgabe
        # im Fenster flüssiger wirkt. Ansonsten wird immer der ganze Block gleichzeitig ausgegeben.
        if pause == 0:
            self.timestopper += 1
            time.sleep(self.timepause)
        
    def ClearConsole(self):
        '''
        Diese Funktion setzt das Konsolenfenster zurück.
        Der Header wird wieder hergestellt.
        '''
        self.scrollarea.configure(state='normal')
        self.scrollarea.delete('1.0', tkinter.END)
        self.Insert("--------------------------------------------------------------------",1)
        self.Insert("Camera Calibrator App\nCreated by Daniel Weber. Copyright 2020. Version {}\nTechnische Hochschule Mittelhessen".format(self.VERSIONINDEX),1)
        self.Insert("--------------------------------------------------------------------\n\nTime: {}\n".format(time.strftime('%d.%m.%Y , %H:%M:%S Uhr')),1)
        self.scrollarea.configure(state='disabled')
        self.scrollarea.update()

#####################################################################################################################
# MENÜ

    def createMenu(self):
        '''
        Erstellung der Menu Leiste. Dort exisiteren folgende Reiter:
        Options: Speichern der Parameter oder des Protokolls, Neue Kalibrierung, Beenden der Anwendung.
        Help: About und Hilfe zur Anwendung
        '''
        menu = tkinter.Menu(self.master, tearoff=False)
        self.master.config(menu=menu)

        # Options Menü. Speichern, Neue Kalibrierung und Beenden.
        filemenu = tkinter.Menu(menu, tearoff=False)
        menu.add_cascade(label='Options', menu=filemenu)
        filemenu.add_command(label='Save Parameters', command=self.MENUSaveParams)
        filemenu.add_command(label='Save Protokoll', command=self.MENUSaveConsole)
        filemenu.add_command(label='New Calibration', command=self.MENUNewCalibration)
        filemenu.add_separator()
        filemenu.add_command(label='Beenden', command=self.master.destroy)
        
        # Help Menü mit Hilfestellungen zur richtigen Verwendung der App.
        filemenu = tkinter.Menu(menu, tearoff=False)
        menu.add_cascade(label='Help', menu=filemenu)
        filemenu.add_command(label='About', command=self.MENUAbout)
        filemenu.add_command(label='Hilfe', command=self.MENUHelp)
        
    def MENUSaveParams(self):
        '''
        Sichern der Parameter als npz-Datei. Für die Datei kann dann ein geeigneter Speicherplatz ausgewählt werden.
        Die Datei kann dann in beliebigen anderen Python-Skripts eingeladen und verwendet werden.
        '''
        # Nur verfügbar, wenn die Kalibrierung erfolgreich abgeschlossen ist.
        if self.CalibrationCompleted == True:
            # Verzeichnis abfragen, wo das Dokument gespeichert werden soll.
            ftypes = [('All files', '*'), ('Numpy Array Datei (.npz)', '.npz')]
            file = tkinter.filedialog.asksaveasfilename(initialfile='Kalibrierungsparameter.npz', filetypes=ftypes, defaultextension='.npz')
            if file == '':
                return
            
            # Speichern der Single-Kamera Parameter
            if self.Art == 'Single':
                d = self.CameraParams
                np.savez(file, **d)
                npz = dict(np.load(file))
                size = (npz['Imgpoints'].shape[0], npz['Imgpoints'].shape[1], npz['Imgpoints'].shape[3])
                npz['Imgpoints'] = np.resize(npz.pop('Imgpoints'), size)
                np.savez(file, **npz)
                
            # Speichern der Stereo-Kamera Parameter
            elif self.Art == 'Stereo':
                d = self.StereoParams
                np.savez(file, **d)
                npz = dict(np.load(file))
                size = (npz['L_Imgpoints'].shape[0], npz['L_Imgpoints'].shape[1], npz['L_Imgpoints'].shape[3])
                npz['L_Imgpoints'] = np.resize(npz.pop('L_Imgpoints'), size)
                npz['R_Imgpoints'] = np.resize(npz.pop('R_Imgpoints'), size)
                np.savez(file, **npz)
                
            self.Insert('\n--------------------------------------------------------------------\n')
            self.Insert('Die Parameter wurden gesichert unter:\n{}'.format(file))
            self.Insert('\n--------------------------------------------------------------------\n')
        else:
            self.Insert('[ERROR] Keine Parameter vorhanden. Erst Kalibrierung durchführen!')
        
    def MENUSaveConsole(self):
        '''
        Sichern des Inhaltes der Konsole als txt-Datei.
        '''
        # Verzeichnis abfragen, wo das Dokument gespeichert werden soll.
        ftypes = [('All files', '*'), ('Text Documents (.txt)', '.txt')]
        file = tkinter.filedialog.asksaveasfilename(initialfile='Kalibrierungsprotokoll.txt', filetypes=ftypes, defaultextension='.txt')
        
        # Wenn Verzeichnis ausgewählt, wird der gesamte Inhalt des Ausgabefensters abgespeichert.
        txt = self.scrollarea.get('1.0', tkinter.END)
        if file=='':
            return
        f = open(file, 'w')
        f.write(txt)
        f.close()
        
        self.Insert('\n--------------------------------------------------------------------\n')
        self.Insert('Das Protokoll wurde gesichert unter:\n{}'.format(file))
        self.Insert('\n--------------------------------------------------------------------\n')
        
    def MENUNewCalibration(self):
        '''
        Zurücksetzung aller Einstellungen. (quasi wie ein erneutes Öffnen der Anwendung)
        Eine erneute Kalibrierung ist möglich.
        '''
        # App zurücksetzen
        self.StatusLabelText.set(' ')
        self.SwitchButtonState('NORMAL')
        self.entry.set(30.0)
        self.formframe.update()
        self.ClearConsole()
        
        # Variablen neu definieren
        self.LeftPath = ''
        self.RightPath = ''
        self.Art = ''
        self.CalibrationCompleted = False
        self.CalBegonnen = False
        self.timestopper = 0
        
    def MENUAbout(self):
        '''
        Öffnet ein Popup Fenster, in welchem ein kurzer About Text steht.
        Infos zum Erstelldatum, Version der Anwendung und Copyright text.
        '''
        c = 2020  # Copyright Year
        txt = 'Camera Calibrator App\nCreated by Daniel Weber. Copyright {}\nTechnische Hochschule Mittelhessen\nVersion {}'.format(c,self.VERSIONINDEX)
        tkinter.messagebox.showinfo('Camera Calibrator App - About',txt)
        
    def MENUHelp(self):
        '''
        Hilfetext zur Bedienung des Programms. 
        '''
        txt = 'HILFE:\n\n'
        
        txt += 'Benutzen der Kalibrierung:\n'
        txt += 'Die Stereokamera-Kalibrierung benötigt drei Eingabewerte. Für die linke und rechte '
        txt += 'Kamera muss je ein Ordner mit den Kalibrierbildern eines Schachbrettmusters, sowie '
        txt += 'die Seitenlänge der Quadrate auf dem Schachbrett angegeben sein. Mit dem Startbutton beginnt die '
        txt += 'Kalibrierung. Bei der Angabe eines einzelnen Ordners beginnt automatisch die '
        txt += 'Kalibrierung der einzelnen Kamera. Bei zwei die der Stereokamera.'
        
        txt += '\n\nAnforderungen an die Kalibrierbilder:\n'
        txt += 'Das Kalibrierobjekt sollte von beiden Kameras gut zu sehen sein. Bei jedem Bild '
        txt += 'sollte das Objekt leicht gedreht werden, um mehrere Blickwinkel zu erhalten. '
        txt += 'Die besten Ergebnisse werden erziehlt, wenn 10-20 Bilder (oder noch mehr) '
        txt += 'aufgenommen werden. Die Bilder sollten als jpg, png oder tiff Datei vorliegen. '
        txt += 'Das Kalibrierobjekt selbst muss ein assymetrisches Schachbrettmuster sein.'
        
        txt += '\n\nSpeichern der Parameter:\n'
        txt += 'Unter dem Menüpunkt Options -> Save Parameters können die berechneten Kameraparameter '
        txt += 'an einem beliebigen Ort auf Ihrem Computer abgespeichert werden. Standardmäßig liegen '
        txt += 'die Dateien als npz-Datei vor. Dieses Dateiformat ermöglicht es Numpy Arrays '
        txt += 'innerhalb von Python sehr einfach zu sichern. Für weitere Informationen wird hier ' 
        txt += 'auf die numpy Online Dokumentation verwiesen. '
        txt += 'Ein Speichern des Konsoleninhaltes als txt-Datei ist ebenfalls möglich.'
        
        self.Insert('--------------------------------------------------------------------\n')
        self.Insert(txt)
        self.Insert('\n--------------------------------------------------------------------\n')
           
#####################################################################################################################  
# INPUT

    def InputLeft(self):
        '''
        Regelt den Input des Linken Ordners und speichert den Pfad ab.
        '''
        self.LeftPath = tkinter.filedialog.askdirectory()
        self.Insert('Pfad Linke Kamera:')
        self.Insert(self.LeftPath)
        self.Insert('')
        
    def InputRight(self):
        '''
        Regelt den Input des Rechten Ordners und speichert den Pfad ab.
        '''
        self.RightPath = tkinter.filedialog.askdirectory()
        self.Insert('Pfad Rechte Kamera:')
        self.Insert(self.RightPath)
        self.Insert('')
        
    def CheckInput(self):
        '''
        Überprüfung der Eingabewerte.
        '''
        
        # SQUARE SIZE --------------------------------------------------------
        # Muss eine Zahl sein. Dezimal-Trennzeichen ein Punkt.
        
        try:
            self.SquareSize = self.entry.get()
        except:
            self.Insert('[ERROR] Fehlerhafte Angabe der Square Size.')
            return False
        
        
        # ORDNER -------------------------------------------------------------
        # 1. Ordner müssen angegeben sein.
        #    Entscheidung Single oder Stereo - Kalibration
        # 2. linker und rechter Ordner dürfen nicht gleich sein.
        # 3. Der Ordner darf nicht leer sein.
        #    Im Ordner dürfen sich nur Bilder vom selben Typ befinden.
        #    Dateityp muss bmp, jpeg, jpg, png, tiff oder tif sein.
        # 4. Es müssen pro Kamera gleich viele Bilder existieren.
        
        left = str(self.LeftPath); right = str(self.RightPath)
        
        # 1. -----------------------------------------------------------------
        
        if left == '' and right == '':
            self.Insert('[ERROR] Keine Ordner angegeben.')
            return False
        
        elif left == '' or right == '':
            self.Art = 'Single'
            if left == '':
                self.Seite = 'R'; self.SinglePath = right
            else:
                self.Seite = 'L'; self.SinglePath = left
                
        else:
            self.Art = 'Stereo'
            self.Seite = ''; self.SinglePath = ''
            
        # 2. -----------------------------------------------------------------
        
        if left == right:
            self.Insert('[ERROR] Linker und Rechter Ordner sind identisch')
            return False
        
        # 3. -----------------------------------------------------------------
        
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
            
        # 4. -----------------------------------------------------------------
        
        if self.Art == 'Stereo':
            if len(l) != len(r):
                self.Insert('[ERROR] Pro Kamera müssen gleich viele Bilder existieren.')
                return False
        
        # Wenn alle Eingaben korrekt, wird True zurückgegeben und die 
        # Kalibrierung kann starten.
        return True

#####################################################################################################################
# START

    def StartButton(self):
        if self.CheckInput():
            
            self.ClearConsole()
            self.CalBegonnen = True
            self.StatusLabelText.set('Kalibrierung läuft. Bitte warten...')
            self.SwitchButtonState('DISABLED')
            
            if self.Art == 'Stereo':
                
                self.StartTime = time.perf_counter(); self.timestopper = 0
                self.Insert('--------------------------------------------------------------------\n')
                self.Insert('EINGABE PARAMETER:\n')
                self.Insert('Pfad Linke Kamera:')
                self.Insert(self.LeftPath); self.Insert('')
                self.Insert('Pfad Rechte Kamera:')
                self.Insert(self.RightPath); self.Insert('')
                self.Insert('Square Size des Schachbrettmusters: {} mm\n'.format(self.SquareSize))
                self.Insert('--------------------------------------------------------------------\n')
                self.Insert('STEREO CAMERA CALIBRATION\n')
                self.Insert('--------------------------------------------------------------------\n')
                self.StereoParams = StereoCamera(self.LeftPath, self.RightPath, self.SquareSize)
                
                if not self.StereoParams == None:
                    self.StatusLabelText.set('Kalibrierung beendet.')
                    self.CalibrationCompleted = True
                    
                if self.CalibrationCompleted:
                    end = time.perf_counter() - self.StartTime - self.timestopper * self.timepause
                    self.Insert('benötigte Zeit für Kalibrierung: {:.4f} Sekunden\n'.format(end))
                    self.Insert('--------------------------------------------------------------------\n')
                    self.Insert('CALIBRATION COMPLETED\n')
                    self.Insert('--------------------------------------------------------------------\n')
                    
            elif self.Art == 'Single':
                
                self.StartTime = time.perf_counter(); self.timestopper = 0
                self.Insert('--------------------------------------------------------------------\n')
                self.Insert('EINGABE PARAMETER:\n')
                self.Insert('Pfad der Kamera:')
                self.Insert(self.SinglePath); self.Insert('')
                self.Insert('Square Size des Schachbrettmusters: {} mm\n'.format(self.SquareSize))
                self.Insert('--------------------------------------------------------------------\n')
                self.Insert('SINGLE CAMERA CALIBRATION\n')
                self.Insert('--------------------------------------------------------------------\n')
                self.CameraParams = SingleCamera(self.SinglePath, self.SquareSize)
                
                if not self.CameraParams == None:
                    self.StatusLabelText.set('Kalibrierung beendet.')
                    self.CalibrationCompleted = True
                    
                if self.CalibrationCompleted:
                    end = time.perf_counter() - self.StartTime - self.timestopper * self.timepause
                    self.Insert('benötigte Zeit für Kalibrierung: {:.4f} Sekunden\n'.format(end))
                    self.Insert('--------------------------------------------------------------------\n',)
                    self.Insert('CALIBRATION COMPLETED\n')
                    self.Insert('--------------------------------------------------------------------\n')
                    
            if self.CalibrationCompleted == False:
                self.StatusLabelText.set('Fehler bei der Kalibrierung.')
                
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
        
        self.Insert('INFORMATIONEN:\n')
        self.Insert('- Vor dem Schliessen des Fensters bitte die Parameter exportieren!',1)
        self.Insert('  Menu -> Options -> Save Parameters\n',1)
        self.Insert('- Die hier dargestellten Ergebnisse sind gerundet.',1)
        self.Insert('  Gespeichert werden alle verfügbaren Nachkommastellen.',1)
        
        self.Insert('\n--------------------------------------------------------------------\n',1)

# %% ################################################################################################################
# Klasse Images:
# Diese Klasse dient zum Beschreiben der Kalibrierungsbilder.
# Hier werden die Bilder analysiert und die Punkte detektiert.
# Als Input Parameter dient der Pfad des Kamera-Ordners und die SquareSize des Schachbrettmusters.
#####################################################################################################################

class Images():
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
        Diese Funktion analysiert den gegebenen Kamerapfad zum entsprechenden Ordner.
        Die Dateien werden betrachtet und dann geordnet in eine Liste geschrieben.
        '''
        # Extrahieren aller Dateinamen aus dem gegebenen Verzeichnis.
        imagelist = os.listdir(self.ImageData['OrdnerPfad'])
        imagelist = sorted(imagelist)
        
        # Welche längen haben die gegebenen Strings? Speichern in Liste
        lengths = []
        for name in imagelist:
            lengths.append(len(name))
        lengths = sorted(list(set(lengths)))
        
        # sortieren der Namen.
        ImageNames = []
        ImageNamesRaw = []
        for l in lengths:
            for name in imagelist:
                if len(name) == l:
                    ImageNames.append(os.path.join(self.ImageData['OrdnerPfad'],name))
                    ImageNamesRaw.append(name)
        
        # Ergebnisse speichern
        self.ImageData['ImagePfade'] = ImageNames
        self.ImageData['ImageNamesRaw'] = ImageNamesRaw
        
    def GetBoardSize(self):
        '''
        Diese Funktion berechnet sich die Größe des Schachbrettmusters. Dabei muss auf dem Schachbrett eine
        minimale Größe von (3,4) bis maximal (13,14) vorliegen.
        Quadratische Muster sind nicht erlaubt.
        '''
        self.BoardSizeFehler = False
        imagepath = self.ImageData['ImagePfade'][0]
        img = cv2.imread(imagepath)
        
        # Bild auf 20% der Originalgröße reduzieren, um Rechenzeit einzusparen.
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray,(0,0),fx=0.2,fy=0.2) # 20%
        
        # Mögliche Board Sizes.
        # HINT: Wenn nötig kann eine fehlende Board Size hier noch nachträglich definiert werden.
        sizes = np.array([[7,11],[6,9],[5,7],
                          [3,4],[3,5],[3,6],[3,7],[3,8],[4,5],[4,6],[4,7],[4,8],[4,9],
                          [5,6],[5,8],[5,9],[5,10],[6,7],[6,8],[6,10],[6,11],
                          [7,8],[7,9],[7,10],[7,12],[8,9],[8,10],[8,11],[8,12],[8,13],
                          [9,10],[9,11],[9,12],[9,13],[9,14],[10,11],[10,12],[10,13],[10,14],
                          [11,12],[11,13],[11,14],[12,13],[12,14],[13,14]])
        
        # Durchgehen aller BoardSizes, und Überprüfung ob die richtige vorliegt.
        for k in range(sizes.shape[0]):
            size = tuple(sizes[k,:])
            ret, _ = cv2.findChessboardCorners(gray, size)
            if ret:
                break
            
        # Falls nicht gefunden, werden die Sizes nochmals durchgegangen.
        # Diesmal wird das Bild aber nur auf die Hälfte verkleinert.
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
                   
        # Größerer Wert zuerst darstellen.
        size = np.array(size)
        BoardSize = (size.max(), size.min())
        
        # Ergebnisse speichern
        self.ImageData['BoardSize'] = BoardSize
        self.ImageData['ImageSize'] = tuple(img.shape[:2])
        
    def GetChessboard(self):
        paths = self.ImageData['ImagePfade']
        boardSize = self.ImageData['BoardSize']
        
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # Erstellung der Objectpoints. Verrechnug mit der SquareSize.
        objp = np.zeros((boardSize[0]*boardSize[1],3), np.float32)
        objp[:,:2] = np.mgrid[0:boardSize[0],0:boardSize[1]].T.reshape(-1,2)
        objp *= self.ImageData['SquareSize']
        
        objpoints = []; imgpoints = []
        
        # Detektieren der Imagepoints
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
            
        # Ergebnisse speichern
        self.ImageData['Objpoints'] = objpoints
        self.ImageData['Imgpoints'] = imgpoints

# %% ################################################################################################################
# Klasse Kamera:
# Diese Klasse dient der Kalibrierung einer Kamera.
# Benötigt wird eine vorherige Anwendung der Image-Klasse.
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
        Kalibrierung der Kamera. Berechnung der Matrizen und Speichern in CameraParams.
        '''
        gray = cv2.cvtColor(cv2.imread(self.CameraParams['ImagePfade'][0]), cv2.COLOR_BGR2GRAY)
        g = gray.shape[::-1]
        
        # HINT: Hier sind zusätzliche Einstellungen zu calibrateCamera möglich.
        flags = 0
        # flags |= cv2.CALIB_RATIONAL_MODEL # Erstellt statt 3 radiale Verzeichnungsparameter 6.
        
        # Kamera Kalibrierung
        (ret, mtx, dist, rvecs, tvecs) = cv2.calibrateCamera(self.CameraParams['Objpoints'], self.CameraParams['Imgpoints'], g, None, None, flags=flags)
        
        # Umrechnung der Rotationsvektoren in Rotationsmatrizen und bilden der Transformationsmatrix
        Rmtx = []; Tmtx = []; k = 0
        for r in rvecs: 
            Rmtx.append(cv2.Rodrigues(r)[0])
            Tmtx.append(np.vstack((np.hstack((Rmtx[k],tvecs[k])),np.array([0,0,0,1]))))
            k += 1
        
        # Zusätzliche Berechnung der Intrinsischen Matrix unter Berücksichtigung der Distortion.
        img = cv2.imread(self.CameraParams['ImagePfade'][0],0)
        h,w = img.shape[:2]
        newmtx, roi = cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
        
        if np.sum(roi) == 0:
            roi = (0,0,w-1,h-1)
        
        # Ergebnisse speichern
        self.CameraParams['Intrinsic'] = mtx
        self.CameraParams['Distortion'] = dist
        self.CameraParams['DistortionROI'] = roi
        self.CameraParams['DistortionIntrinsic'] = newmtx
        self.CameraParams['RotVektor'] = rvecs
        self.CameraParams['RotMatrix'] = Rmtx
        self.CameraParams['Extrinsics'] = Tmtx
        self.CameraParams['TransVektor'] = tvecs
    
    def Errors(self):
        '''
        Berechnung der Reprojection Errors.
        '''
        objp = np.array(self.CameraParams['Objpoints'][0])
        imgp = np.array(self.CameraParams['Imgpoints'])
        imgp = imgp.reshape((imgp.shape[0], imgp.shape[1], imgp.shape[3]))
        K = np.array(self.CameraParams['Intrinsic'])
        D = np.array(self.CameraParams['Distortion'])
        R = np.array(self.CameraParams['RotVektor'])
        T = np.array(self.CameraParams['TransVektor'])
        N = imgp.shape[0] # Anzahl Views
        
        # Neue imgp berechnen
        imgpNew = []
        for i in range(N):
            temp, _ = cv2.projectPoints(objp, R[i], T[i], K, D)
            imgpNew.append(temp.reshape((temp.shape[0], temp.shape[2])))
        imgpNew = np.array(imgpNew)
        
        # Error per Point berechnen (in x und y)
        err = []
        for i in range(N):
            err.append(imgp[i] - imgpNew[i])
        err = np.array(err)
        
        # Mean Errors berechnen
        def RMSE(err):
            return np.sqrt(np.mean(np.sum(err**2, axis=1)))
        
        errall = np.copy(err[0])
        rmsePerView = [RMSE(err[0])]
        
        for i in range(1,N):
            errall = np.vstack((errall, err[i]))
            rmsePerView.append(RMSE(err[i]))
            
        rmseAll = RMSE(errall)
        
        # Ergebnisse speichern
        self.CameraParams['Errors'] = rmsePerView
        self.CameraParams['MeanError'] = rmseAll
        self.CameraParams['Reprojectedpoints'] = imgpNew
    
    def PrintResults(self):
        '''
        Schreiben der Resultate in das Ausgabefenster.
        '''
        app.Insert('Allgemeine Daten:\n' +
                   '  Bild Size:       {} x {}\n'.format(self.CameraParams['ImageSize'][0], self.CameraParams['ImageSize'][1]) +
                   '  Board Size:      {} x {}\n'.format(self.CameraParams['BoardSize'][0], self.CameraParams['BoardSize'][1]) +
                   '  Anzahl Bilder:   {}\n'.format(len(self.CameraParams['Objpoints'])) + 
                   '  Punkte pro Bild: {}\n'.format(self.CameraParams['Objpoints'][0].shape[0]))
        
        app.Insert('Intrinsische Matrix:\n'+str(self.CameraParams['Intrinsic'])+'\n')
        
        D = np.round(self.CameraParams['Distortion'],5)[0]
        if D.shape[0] > 5:
            app.Insert('Verzeichnung:\n'+
                       '  radial:     '+str(D[0])+' '+str(D[1])+' '+str(D[4])+' '+str(D[5])+' '+str(D[6])+' '+str(D[7])+'\n'
                       '  tangential: '+str(D[2])+' '+str(D[3])+'\n')
        else:
            app.Insert('Verzeichnung:\n'+
                       '  radial:     '+str(D[0])+'  '+str(D[1])+'  '+str(D[4])+'\n'
                       '  tangential: '+str(D[2])+'  '+str(D[3])+'\n')

        app.Insert('Extrinsische Matrizen:')
        for i in range(len(self.CameraParams['Extrinsics'])):
            t = self.CameraParams['Extrinsics'][i]
            app.Insert('von Bild '+str(i+1)+': ({})\n'.format(self.ImageNamesRaw[i])+str(t)+'\n')
            
        app.Insert('Mean Reprojection Error per Image [Pixel]:')
        k = 1
        for e in self.CameraParams['Errors']:
            app.Insert(' {:3}) {:<10.6f}'.format(k, e), 1)
            k += 1
        app.Insert('')
        app.Insert('Mean Reprojection Error [Pixel]: '+str(np.round(self.CameraParams['MeanError'],5))+'\n')
        
        if self.CameraParams['MeanError'] > 1:
            app.Insert('Achtung, Reprojection Error über 1!\n', form='warn')

# %% ################################################################################################################
# Klasse Stereokamera:
# Innerhalb dieser Klasse wird die Stereokamera kalibriert.
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
        '''
        Parameter der linken und rechten Kamera extrtahieren und in das
        StereoParams Dictionary schreiben.
        '''
        # Allgemeine Daten werden ohne Präfix eingespeichert.
        self.StereoParams['BoardSize'] = self.Left.pop('BoardSize'); self.Right.pop('BoardSize')
        self.StereoParams['SquareSize'] = self.Left.pop('SquareSize'); self.Right.pop('SquareSize')
        self.StereoParams['ImageSize'] = self.Left.pop('ImageSize'); self.Right.pop('ImageSize')
        
        # Vor alle spezifischen Parameter der linken Kamera wird 'L_' gesetzt.
        for Lkey in self.Left.keys():
            name = 'L_'+str(Lkey)
            self.StereoParams[name] = self.Left[Lkey]
            
        # Vor alle spezifischen Parameter der rechten Kamera wird 'R_' gesetzt.
        for Rkey in self.Right.keys():
            name = 'R_'+str(Rkey)
            self.StereoParams[name] = self.Right[Rkey]
    
    def Calibration(self):
        '''
        Berechnung der Stereokamera Parameter.
        '''
        obj = self.StereoParams['L_Objpoints']
        img1 = self.StereoParams['L_Imgpoints']
        k1 = self.StereoParams['L_Intrinsic']
        d1 = self.StereoParams['L_Distortion']
        img2 = self.StereoParams['R_Imgpoints']
        k2 = self.StereoParams['R_Intrinsic']
        d2 = self.StereoParams['R_Distortion']
        
        # Auslesen der Bildgröße und spiegelverkehrte Speicherung
        grayL1 = cv2.imread(self.StereoParams['L_ImagePfade'][0], 0)
        g = grayL1.shape[::-1]
        
        # HINT: Hier sind zusätzliche Einstellungen der stereoCalibrate Funktion möglich.
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1e-5)
        flags = 0
        flags |= cv2.CALIB_FIX_INTRINSIC
        # flags |= cv2.CALIB_USE_INTRINSIC_GUESS
        # flags |= cv2.CALIB_FIX_FOCAL_LENGTH
        # flags |= cv2.CALIB_ZERO_TANGENT_DIST
        
        # Stereo Kamera Kalibrierung
        (ret, K1, D1, K2, D2, R, t, E, F) = cv2.stereoCalibrate(obj, img1, img2, k1, d1, k2, d2, g, criteria=criteria, flags=flags)
        
        # Transformationsmatrix zusammensetzen
        T = np.vstack((np.hstack((R,t)),np.array([0,0,0,1])))
        
        # Ergebnisse speichern
        self.StereoParams['Transformation'] = T
        self.StereoParams['Essential'] = E
        self.StereoParams['Fundamental'] = F
        self.StereoParams['MeanError'] = ret
        
        # HINT: Falls eine Neuberechnung der Intrinsik erwünscht ist die folgenden Zeilen auskommentieren.
        # self.StereoParams['L_Intrinsic'] = K1
        # self.StereoParams['L_Distortion'] = D1
        # self.StereoParams['R_Intrinsic'] = K2
        # self.StereoParams['R_Distortion'] = D2
    
    def PrintResults(self):
        '''
        Schreiben der Resultate in das Ausgabefenster.
        '''
        app.Insert('Transformationsmatrix:\n'+str(self.StereoParams['Transformation'])+'\n')
        
        app.Insert('Essentialmatrix:\n'+str(self.StereoParams['Essential'])+'\n')
        
        np.set_printoptions(suppress=False, precision=5)
        app.Insert('Fundamentalmatrix:\n'+str(self.StereoParams['Fundamental'])+'\n')
        np.set_printoptions(suppress=True, precision=5)
        
        app.Insert('Overall Mean Reprojection Error: '+str(np.round(self.StereoParams['MeanError'],5))+'\n')
        
        if self.StereoParams['MeanError'] > 1:
            app.Insert('Achtung, Reprojection Error über 1!\n', form='warn')
    
# %% ################################################################################################################
# Durchführung der Kalibrierung
# Funktion für Single und Stereokamera.
#####################################################################################################################

def SingleCamera(path, SquareSize):
    '''
    Kalibrierungsfunktion einer Kamera. Bilder werden analysiert und die Kamera kalibriert.
    '''
    try:
        Image = Images(path, SquareSize)
        ImageData = Image.ImageData
        
    except:
        app.Insert('[ERROR] Fehler bei der Analyse der Kalibrierungsbilder.')
        return None
    
    if Image.BoardSizeFehler == True:
        app.Insert('[ERROR] Fehler bei Detektion der Board Size.')
        return None
    
    try:
        Cam = Camera(ImageData)
        CameraData = Cam.CameraParams
        return CameraData
    
    except:
        app.Insert('[ERROR] Fehler bei der Kamerakalibrierung.')
        return None
    
def StereoCamera(pathL, pathR, SquareSize):
    '''
    Kalibrierungsfunktion der Stereokamera. Einzelne Kameras werden kalibriert und danach
    die Parameter der Sterokamera berechnet.
    '''
    app.Insert('KALIBRIERUNG LINKE KAMERA\n')
    
    LeftData = SingleCamera(pathL, SquareSize)
    if LeftData == None:
        return None
    
    app.Insert('--------------------------------------------------------------------\n')
    app.Insert('KALIBRIERUNG RECHTE KAMERA\n')
    
    RightData = SingleCamera(pathR, SquareSize)
    if RightData == None:
        return None
    
    app.Insert('--------------------------------------------------------------------\n')
    app.Insert('KALIBRIERUNG DER STEREOKAMERA\n')

    try:
        St = Stereo(LeftData, RightData)
        StereoData = St.StereoParams
        return StereoData
    
    except:
        app.Insert('[ERROR] Fehler bei der Stereokamera Kalibrierung.')
        return None
    
# %% ################################################################################################################
# Main Loop
#####################################################################################################################

if __name__ == '__main__':
    '''
    Hierrin wird das Hauptprogramm aufgerufen. Wird nur ausgeführt, wenn das
    Programm direkt in dieser Datei abgespielt wird.
    '''
    print('\nCamera Calibrator App\nStart: {}'.format(time.strftime('%H:%M:%S Uhr')))
    root = tkinter.Tk()
    app = App(root)
    root.mainloop()
    if app.Art == 'Single' and app.CalibrationCompleted == True:
        Params = app.CameraParams
    elif app.Art == 'Stereo' and app.CalibrationCompleted == True:
        Params = app.StereoParams
    print('Ende:  {}'.format(time.strftime('%H:%M:%S Uhr')))
