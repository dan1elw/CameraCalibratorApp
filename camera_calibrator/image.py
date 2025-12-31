# IMPORTS
import os
import cv2
import numpy as np

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
