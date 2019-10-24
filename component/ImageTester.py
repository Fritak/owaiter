# test on linux - it doesn't have win32 & ImageGrab
try:
    import win32gui
    import win32ui
    import win32con
except ImportError:
    print('win32 not loaded')

try:
    from PIL import ImageGrab
except ImportError:
    print('ImageGrab not loaded')

from tkinter import messagebox
from PIL import Image
import pyautogui


class ImageTester:
    def __init__(self, name):
        self.overwatchWindowName = name
        self.compColor = (178, 0, 255)
        self.compColor2 = (178, 0, 255, 255)  # because of png
        self.qpColor = (28, 117, 188)
        self.qpColor2 = (28, 117, 188, 255)  # because of png

    def getImage(self):
        screenWidth, screenHeight = pyautogui.size()

        try:
            hwnd = win32gui.FindWindow(None, self.overwatchWindowName)

            # load image
            wDC = win32gui.GetWindowDC(hwnd)
            myDC = win32ui.CreateDCFromHandle(wDC)
            newDC = myDC.CreateCompatibleDC()

            # bitmap
            myBitMap = win32ui.CreateBitmap()
            myBitMap.CreateCompatibleBitmap(myDC, screenWidth, screenHeight)
            newDC.SelectObject(myBitMap)

            newDC.BitBlt((0, 0), (screenWidth, screenHeight), myDC, (0, 0), win32con.SRCCOPY)

            # load image from buffer
            bmpinfo = myBitMap.GetInfo()
            bmpstr = myBitMap.GetBitmapBits(True)
            image = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)

            # free resources
            myDC.DeleteDC()
            newDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, wDC)
            win32gui.DeleteObject(myBitMap.GetHandle())

            return image
        except NameError:
            print("win32gui module not found.")

    def analyze(self, image=None):
        # load image
        if image is None:
            image = self.getImage()
        elif type(image) is str:
            image = Image.open(image)

        # even after all this we don't have image?
        if image is None:
            print("Couldn't load screen.")
            return None

        pix = image.load()

        # calculate where to look for pixels
        width, height = image.size

        checkHeight = int(height / 13.5)
        checkHeightSkirmish = int(height / 6.96774193548)
        checkHeightQp = int(height / 12)
        checksWidth = [int(width / 2.313253), int(width / 2.28571428571)]

        isComp = True
        isQp = True
        for widthCheck in checksWidth:
            # normal search
            if pix[widthCheck, checkHeight] != self.compColor and pix[widthCheck, checkHeight] != self.compColor2:
                # skirmish
                if pix[widthCheck, checkHeightSkirmish] != self.compColor and \
                   pix[widthCheck, checkHeightSkirmish] != self.compColor2:
                    isComp = False
            if pix[widthCheck, checkHeightQp] != self.qpColor and pix[widthCheck, checkHeightQp] != self.qpColor2:
                isQp = False

        # free resources
        image.close()

        return isComp, isQp
