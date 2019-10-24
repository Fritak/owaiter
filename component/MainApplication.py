import time
import pyautogui
import qrcode
import threading
import tkinter
import configparser
import socket

from component.ImageTester import ImageTester
from component.ApiServer import ApiServer

from fractions import Fraction
from tkinter import messagebox


class MainApplication:
    def __init__(self, *args, **kwargs):
        self.tk = tkinter.Tk()

        # loads config
        self._loadConfig()

        # image
        try:
            self.tk.iconbitmap("../resources/icon.ico")
        except tkinter.TclError:
            print('Error loading img')

        # Gets the requested values of the height and width.
        self.windowWidth = int(self.tk.winfo_screenwidth() / 5)
        self.windowHeight = int(self.tk.winfo_screenwidth() / 4)
        self._setWindowDimensions()

        self._setMisc()
        self._setButtonsAndLabels()

    def run(self):
        self.tk.mainloop()

    def _loadConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read('config/parameters.ini')

    def _setWindowDimensions(self):
        # Gets both half the screen width/height and window width/height
        positionRight = int(self.tk.winfo_screenwidth() / 2 - self.windowWidth / 2)
        positionDown = int(self.tk.winfo_screenheight() / 2 - self.windowHeight / 2)

        # Positions the window in the center of the page
        self.tk.geometry("{}x{}+{}+{}".format(self.windowWidth, self.windowHeight, positionRight, positionDown))

    def _setMisc(self):
        self.tk.title(self.config["app"]["TitleName"])
        self.tk.configure(background='black')

    def _setButtonsAndLabels(self):
        halfScreen = int(self.windowWidth / 2)
        width = int(self.windowWidth / 3)
        height = int(self.windowHeight / 12)
        btnStep = int(self.windowHeight / 6)

        self.startButton = tkinter.Button(self.tk, text=self.config["btn"]["StartName"],
                                          bg=self.config["btn"]["BgColor"],
                                          fg=self.config["btn"]["FgColor"], bd=0, command=lambda: self._start())

        self.startButton.place(x=halfScreen - width / 2, y=btnStep * 1, width=width, height=height)

        self.qrButton = tkinter.Button(self.tk, text=self.config["btn"]["QrName"], bg=self.config["btn"]["BgColor"],
                                       state="disabled", fg=self.config["btn"]["FgColor"], bd=0,
                                       command=lambda: self._showQr())

        self.qrButton.place(x=halfScreen - width / 2, y=btnStep * 2, width=width, height=height)

        self.infoLabelFrame = tkinter.LabelFrame(self.tk)
        self.infoLabelFrame.place(x=int(halfScreen - int(int(self.windowWidth / 1.5)/2)), y=btnStep * 3,
                                  width=int(self.windowWidth / 1.5),  height=int(self.windowHeight / 4))

        self.labelStart = tkinter.Label(self.infoLabelFrame, text="Waiting for start")
        self.labelStart.pack()

        self.labelText = tkinter.Label(self.infoLabelFrame, text=self.config["app"]["Searching"])

        self.quitButton = tkinter.Button(self.tk, text=self.config["btn"]["QuitName"], bg=self.config["btn"]["BgColor"],
                                         fg=self.config["btn"]["FgColor"], bd=0, command=lambda: self._close())

        self.quitButton.place(x=halfScreen - width / 2, y=btnStep * 5, width=width, height=height)

    def _start(self):
        # test resolution
        screenWidth, screenHeight = pyautogui.size()

        if Fraction(screenWidth, screenHeight) != Fraction(16, 9):
            messagebox.showwarning("Error", "Sorry, your screen resolution is not supported yet :(\n"
                                            "The app may not work. Please create request for your resolution!")

        api = ApiServer(True, self.config)
        threading.Thread(target=api.run, daemon=True).start()

        self.startButton.configure(state="disabled")
        self.qrButton.configure(state="normal")
        self.labelStart.forget()
        self.labelText.pack()

        # test for comp every second (yes, yes api MAY do that too, but it MAY NOT ^^)
        threading.Thread(target=self._test, daemon=True).start()

    def _test(self):
        imageTester = ImageTester(self.config['app']['OverwatchAppName'])
        while True:
            isComp, isQp = imageTester.analyze()

            if isComp:
                newText = self.config['app']['SearchingComp']
            elif isQp:
                newText = self.config['app']['SearchingQp']
            else:
                newText = self.config["app"]["Searching"]

            self.labelText.configure(text=newText)
            time.sleep(1)

    def _showQr(self):
        try:
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
        except:
            messagebox.showwarning("Error", "Sorry, unable to get Hostname and IP :(\n"
                                            "Trying to use 127.0.0.1, it may work!")
            host_ip = "127.0.0.1"

        img = qrcode.make("http://" + host_ip + ":5000")
        img.show()

    def _close(self):
        self.tk.destroy()
