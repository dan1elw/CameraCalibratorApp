# IMPORTS
from .image import Images
from .camera import Camera, Stereo

#####################################################################################################################
# Calibration
#####################################################################################################################

def SingleCamera(app, path, SquareSize):
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
        Cam = Camera(ImageData, app)
        CameraData = Cam.CameraParams
        return CameraData
    except:
        app.Insert('[ERROR] Error while Calibration.')
        return None
    
def StereoCamera(app, pathL, pathR, SquareSize):
    app.Insert('CALIBRATION LEFT CAMERAA\n')
    
    LeftData = SingleCamera(app, pathL, SquareSize)
    if LeftData == None:
        return None
    
    app.Insert('--------------------------------------------------------------------\n')
    app.Insert('CALIBRATION RIGHT CAMERA\n')
    
    RightData = SingleCamera(app, pathR, SquareSize)
    if RightData == None:
        return None
    
    app.Insert('--------------------------------------------------------------------\n')
    app.Insert('CALIBRATING THE STEREO CAMERA\n')

    try:
        St = Stereo(LeftData, RightData, app)
        StereoData = St.StereoParams
        return StereoData
    
    except:
        app.Insert('[ERROR] Error while calibrating the stereo camera.')
        return None
    