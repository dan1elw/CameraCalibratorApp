# IMPORTS
import cv2
import numpy as np

#####################################################################################################################
# Class Camera:
# calibrating the camera
# need a application of Images first
#####################################################################################################################

class Camera():
    
    def __init__(self, ImageData, app=None):
        self.app = app
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
        if self.app:
            self.app.Insert('general data:\n' +
                       '  Image Size:       {} x {}\n'.format(self.CameraParams['ImageSize'][0], self.CameraParams['ImageSize'][1]) +
                       '  Board Size:       {} x {}\n'.format(self.CameraParams['BoardSize'][0], self.CameraParams['BoardSize'][1]) +
                       '  Image Quantaty:   {}\n'.format(len(self.CameraParams['Objpoints'])) + 
                       '  Points per Image: {}\n'.format(self.CameraParams['Objpoints'][0].shape[0]))
        
            self.app.Insert('Intrinsic Matrix:\n'+str(self.CameraParams['Intrinsic'])+'\n')
        
            D = np.round(self.CameraParams['Distortion'],5)[0]
            if D.shape[0] > 5:
                self.app.Insert('Distortion:\n'+
                           '  radial:     '+str(D[0])+' '+str(D[1])+' '+str(D[4])+' '+str(D[5])+' '+str(D[6])+' '+str(D[7])+'\n'
                           '  tangential: '+str(D[2])+' '+str(D[3])+'\n')
            else:
                self.app.Insert('Distortion:\n'+
                           '  radial:     '+str(D[0])+'  '+str(D[1])+'  '+str(D[4])+'\n'
                           '  tangential: '+str(D[2])+'  '+str(D[3])+'\n')

            self.app.Insert('Extrinsic Matrices:')
            for i in range(len(self.CameraParams['Extrinsics'])):
                t = self.CameraParams['Extrinsics'][i]
                self.app.Insert('from Image '+str(i+1)+': ({})\n'.format(self.ImageNamesRaw[i])+str(t)+'\n')
                
            self.app.Insert('Mean Reprojection Error per Image [Pixel]:')
            k = 1
            for e in self.CameraParams['Errors']:
                self.app.Insert(' {:3}) {:<10.6f}'.format(k, e), 1)
                k += 1
            self.app.Insert('')
            self.app.Insert('Mean Reprojection Error [Pixel]: '+str(np.round(self.CameraParams['MeanError'],5))+'\n')
        
            if self.CameraParams['MeanError'] > 1:
                self.app.Insert('Attention, Reprojection Error over 1!\n', form='warn')

#####################################################################################################################
# Class Stereo:
# calibrating a stereo camera set
#####################################################################################################################

class Stereo():
    def __init__(self, LeftData, RightData, app=None):
        self.app = app
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
        if self.app:
            self.app.Insert('Transformationmatrix:\n'+str(self.StereoParams['Transformation'])+'\n')
            
            self.app.Insert('Essentialmatrix:\n'+str(self.StereoParams['Essential'])+'\n')
            
            np.set_printoptions(suppress=False, precision=5)
            self.app.Insert('Fundamentalmatrix:\n'+str(self.StereoParams['Fundamental'])+'\n')
            np.set_printoptions(suppress=True, precision=5)
            
            self.app.Insert('Overall Mean Reprojection Error: '+str(np.round(self.StereoParams['MeanError'],5))+'\n')
            
            if self.StereoParams['MeanError'] > 1:
                self.app.Insert('Attention, Reprojection Error over 1!\n', form='warn')
    