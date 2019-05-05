#!/usr/bin/python
import sys
from PyQt4 import QtCore, QtGui #framework for GUI
from ctypes import * #Library for wrapper
from time import strftime, sleep, time
from subprocess import Popen #this module is for running external scripts from this program
import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime


#This is the PyWrap Class with functions for communicatong with camera
class coptonix_PyWrap:
    def __init__(self, dllName, pixels):
        copDll = CDLL(dllName)
        self.copDll = copDll                                                # My DLL call
        self.dwRead = c_uint(2*pixels)                                      # number of bytes to read
        self.lpBuffer = (c_ushort * pixels)()                               # buffer used to store data
        self.p_lpBuffer = cast(self.lpBuffer, POINTER(c_ushort * pixels))   # pointer to buffer

    def my_closedevice(self):
        dwErr = self.copDll.ls_closedevice
        dwErr.restype = c_uint
        dwErr = self.copDll.ls_closedevice()
        return dwErr

    def my_currentdeviceindex(self):
        myDevice_index = self.copDll.ls_currentdeviceindex()
        return myDevice_index

    def my_enumdevices(self):
        num_devices = self.copDll.ls_enumdevices
        num_devices.restype = c_int
        num_devices = self.copDll.ls_enumdevices()
        if num_devices >= 0:
            return num_devices
        else:
            self.textbox.append ("Error: enumerating devices")

    def my_geterrorstring(self, dwErr):
        errorstring = self.copDll.ls_geterrorstring
        errorstring.restype = c_char_p
        my_dwErr = c_uint(dwErr)
        errorstring = self.copDll.ls_geterrorstring(my_dwErr)
        return errorstring

    def my_getinttime(self, dwIntTime, ucTimeOut):
        dwErr = self.copDll.ls_getinttime
        dwErr.restype = c_ubyte
        my_dwIntTime = c_uint(dwIntTime)
        my_ucTimeOut = c_ubyte(ucTimeOut)
        dwErr = self.copDll.ls_getinttime(byref(my_dwIntTime), my_ucTimeOut)
        return dwErr, my_dwIntTime.value
    
    def my_initialize(self, pipesize, packetlength):
        dwErr = self.copDll.ls_initialize
        dwErr.restype = c_uint
        my_pipesize = c_uint(pipesize)
        my_packetlength = c_uint(packetlength)
        dwErr = self.copDll.ls_initialize(my_pipesize, my_packetlength)
        return dwErr

    def my_getmcu1version(self, Index):
        mcu1version = self.copDll.ls_getmcu1version
        mcu1version.restype = c_ushort
        mcu1version.argtype = c_int
        mcu1version = self.copDll.ls_getmcu1version(Index)
        return mcu1version

    def my_getmcu2sensortype(self, wSensorType, ucTimeOut):
        dwErr = self.copDll.ls_getmcu2sensortype
        dwErr.restype = c_uint
        my_ucTimeOut = c_ubyte(ucTimeOut)
        dwErr = self.copDll.ls_getmcu2sensortype(wSensorType, my_ucTimeOut)
        return dwErr

    def my_getmode(self, ucMode, ucTimeOut):
        dwErr = self.copDll.ls_getmode
        dwErr.restype = c_uint
        my_ucMode = c_ubyte(ucMode)
        my_ucTimeOut = c_ubyte(ucTimeOut)
        dwErr = self.copDll.ls_getmode(byref(my_ucMode), my_ucTimeOut)
        return dwErr, my_ucMode.value

    def my_getpipe(self):
        dwErr = self.copDll.ls_getpipe
        dwErr.restype = c_uint
        dwErr = self.copDll.ls_getpipe(self.p_lpBuffer, self.dwRead, byref(self.dwRead))
        return dwErr, self.lpBuffer[:], self.dwRead.value

    def my_getproductname(self, Index):
        productName = self.copDll.ls_getproductname
        productName.restype = c_char_p
        my_Index = c_uint(Index)
        productName = self.copDll.ls_getproductname(my_Index)
        return productName

    def my_getsensorname(self, wSensorType):
        sensorname = self.copDll.ls_getsensorname
        sensorname.restype = c_char_p
        #sensorname.argtype = c_ushort
        sensorname = self.copDll.ls_getsensorname(wSensorType)
        return sensorname

    def my_getsensortype(self):
        dwErr = self.copDll.ls_getsensortype
        dwErr.restype = c_uint
        wSensorType = c_ushort()
        wPixelCount = c_ushort()
        dwErr = self.copDll.ls_getsensortype(byref(wSensorType), byref(wPixelCount))
        return dwErr, wSensorType.value, wPixelCount.value

    def my_getserialnumber(self, Index):
        serialnumber = self.copDll.ls_getserialnumber
        serialnumber.restype = c_char_p
        serialnumber.argtype = c_int
        serialnumber = self.copDll.ls_getserialnumber(Index)
        return serialnumber

    def my_getstate(self, ucState, ucTimeOut):
        state = self.copDll.ls_getstate
        state.restype = c_uint
        my_ucState = c_ubyte(ucState)
        my_ucTimeOut = c_ubyte(ucTimeOut)
        state = self.copDll.ls_getstate(byref(my_ucState), my_ucTimeOut)
        return state, my_ucState.value

    def my_getvendorname(self, Index):
        vendorName = self.copDll.ls_getvendorname
        vendorName.restype = c_char_p
        vendorName.argtype = c_int
        vendorName = self.copDll.ls_getvendorname(Index)
        return vendorName

    def my_opendevicebyindex(self, Index):
        myDevice_index = self.copDll.ls_opendevicebyindex
        myDevice_index.restype = c_uint
        myDevice_index = self.copDll.ls_opendevicebyindex(Index)
        return myDevice_index

    def my_resetfifo(self):
        dwErr = self.copDll.ls_resetfifo
        dwErr.restype = c_uint
        dwErr = self.copDll.ls_resetfifo()
        return dwErr

    def my_savesettings(self):
        dwErr = self.copDll.ls_savesettings
        dwErr.restype = c_uint
        dwErr = self.copDll.ls_savesettings()
        return dwErr

    def my_setinttime(self, dwIntTime, ucTimeOut):
        dwErr = self.copDll.ls_setinttime
        dwErr.restype = c_uint
        my_dwIntTime = c_uint(dwIntTime)
        my_ucTimeOut = c_ubyte(ucTimeOut)
        dwErr = self.copDll.ls_setinttime(my_dwIntTime, my_ucTimeOut)
        return dwErr

    def my_setmode(self, ucMode, ucTimeOut):
        dwErr = self.copDll.ls_setmode
        dwErr.restype = c_uint
        my_ucMode = c_ubyte
        my_ucTimeOut = c_ubyte(ucTimeOut)
        dwErr = self.copDll.ls_setmode(ucMode, my_ucTimeOut)
        return dwErr

    def my_setstate(self, ucState, ucTimeOut):
        state = self.copDll.ls_setstate
        state.restype = c_uint
        my_ucTimeOut = c_ubyte(ucTimeOut)
        state = self.copDll.ls_setstate(ucState, my_ucTimeOut)
        return state

    def my_waitforpipe(self, dwTimeOut):
        dwErr = self.copDll.ls_waitforpipe
        dwErr.restype = c_uint
        my_dwTimeOut = c_uint(dwTimeOut)
        dwErr = self.copDll.ls_waitforpipe(my_dwTimeOut)
        return dwErr

#This class is for GUI 
class BoxLayout(QtGui.QMainWindow):
    if __name__ == '__main__':  
        # Root to DLL file (change accordingly):
            dllName = '/home/pi/linecamera/libusblcpi.so'
        # Some variable declarations:
            ucTimeOut = 100  #time out interval in ms
            dwIntTime = 27  #integration time in ms
            ucMode = 0
            ucState = 1
            dwTimeOut = 100
            my_pixels = 4096
            # Create my class object:
            my_class = coptonix_PyWrap(dllName, my_pixels)
            a1 = my_class.my_initialize(128, 8192)
            
    #This function is the initializing function for GUI window        
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.setWindowTitle('Camera Reader')
        self.setGeometry(50,50,500,400)
      
        self.start = QtGui.QPushButton('Start',self)
        self.start.move(100,10)
        self.stop = QtGui.QPushButton('Stop',self)
        self.stop.move(300,10)
        self.textbox = QtGui.QTextEdit(self)
        self.textbox.resize(300,300)
        self.textbox.move(100,50)
        self.show()
        self.start.clicked.connect(self.start_measure)
        self.stop.clicked.connect(self.stop_measure)
        self.started = False
        
    #This function executes, when "start" button is pressed 
    def start_measure(self):
            if not self.started:
                self.started = True
            
            # List devices and execute code if any device is found:
            a = self.my_class.my_enumdevices()
            if a > 0:
                self.textbox.append("\na - %d device found." % (a))
                # Open connected device:
                b = self.my_class.my_opendevicebyindex(0)
                if b != 0x00000000:
                    n = self.my_class.my_geterrorstring(b)
                    self.textbox.append ("b - ERROR opening device: ", n)
                else:
                    # Fetch index assigned to current device:
                    c = self.my_class.my_currentdeviceindex()
                    # Get vendor and product names, MCU1 version and serial number:
                    d = self.my_class.my_getvendorname(c)
                    self.textbox.append ("d - Vendor: %s" % d)
                    f = self.my_class.my_getproductname(c)
                    self.textbox.append ("f - Product: %s" % f)
                    e = self.my_class.my_getmcu1version(c)
                    self.textbox.append ("e - MCU1 version: %d" % e)
                    g = self.my_class.my_getserialnumber(c)
                    self.textbox.append ("g - Serial number: %s" % g)
                    # Get sensory type and number of pixels:
                    h, wSensorType, wPixelCount = self.my_class.my_getsensortype()
                    if h == 0:
                        i = self.my_class.my_getsensorname(wSensorType)
                        self.textbox.append ("h&i-Sensor %s has %d pixels" % (i, wPixelCount))
                    else:
                        n = self.my_class.my_geterrorstring(h)
                        self.textbox.append ("h - ERROR getting sensor type and number of pixels: ", n)
                    # Setting integration time to 50 us:
                    j = self.my_class.my_setinttime(self.dwIntTime, self.ucTimeOut)
                    if j == 0:
                        self.textbox.append ("j - Setting integration time to 50 us: OK")
                    else:
                        n = self.my_class.my_geterrorstring(j)
                        self.textbox.append ("j - ERROR setting integration time to 50 us: ", n)
                    # Get integration time:
                    k, intTime = self.my_class.my_getinttime(self.dwIntTime, self.ucTimeOut)
                    if k == 0:
                        self.textbox.append ("k - Current integration time is %d us" % intTime)
                    else:
                        n = self.my_class.my_geterrorstring(k)
                        self.textbox.append ("k - ERROR getting integration time: ", n)
                    # Find minimum integration time:
                    l = self.my_class.my_setinttime(0, self.ucTimeOut)
                    if l == 0:
                        self.textbox.append ("l - Setting to minimum integration time: OK")
                    else:
                        n = self.my_class.my_geterrorstring(l)
                        self.textbox.append ("l - ERROR finding minimum integration time: ", n)
                    # Get minimum integration time:
                    m, intTime = self.my_class.my_getinttime(self.dwIntTime, self.ucTimeOut)
                    if m == 0:
                        self.textbox.append ("m - Minimum integration time is %d us" % intTime)
                    else:
                        n = self.my_class.my_geterrorstring(m)
                        self.textbox.append ("m - ERROR getting minimum integration time: ", n)
                    # Let's read some data. First, we reset the FIFO:
                    p = self.my_class.my_resetfifo()
                    if p == 0:
                        self.textbox.append ("p - Resetting FIFO: OK")
                    else:
                        n = self.my_class.my_geterrorstring(p)
                        self.textbox.append ("p - ERROR reseting FIFO: ", n)
                    # Then, we choose the continuous mode:
                    q = self.my_class.my_setmode(0x02, self.ucTimeOut)
                    if q == 0:
                        self.textbox.append ("q - Setting continuous mode: OK")
                    else:
                        n = self.my_class.my_geterrorstring(q)
                        self.textbox.append ("q - ERROR setting continuous mode: ", n)
                    # Read selected mode:
                    r, mode = self.my_class.my_getmode(self.ucMode, self.ucTimeOut)
                    if mode == 0x00:
                        self.textbox.append ("r - Current mode: one-shot")
                    elif mode == 0x01:
                        self.textbox.append ("r - Current mode: ext-trigger")
                    elif mode == 0x02:
                        self.textbox.append ("r - Current mode: free-running")
                    else:
                        n = self.my_class.my_geterrorstring(r)
                        self.textbox.append ("r - ERROR fetching mode: ", n)
                    # Run data acquisition:
                    s = self.my_class.my_setstate(0x01, self.ucTimeOut)
                    if s == 0:
                        self.textbox.append ("s - Starting data acquisition: OK")
                    else:
                        n = self.my_class.my_geterrorstring(s)
                        self.textbox.append ("s - ERROR starting data acquisition: ", n)
                    # Read state (the device needs a delay to start running):
                    sleep(0.1)
                    #bytesRead = 4096
                    t, state = self.my_class.my_getstate(self.ucState, self.ucTimeOut)
                    if t == 0:
                        self.textbox.append ("t - Getting state: OK")
                    else:
                        n = self.my_class.my_geterrorstring(t)
                        self.textbox.append ("t - ERROR getting state: ", n)
                    if state == 0x00:
                        self.textbox.append ("    Acquisition stopped")
                    if state == 0x01:
                        self.textbox.append ("    Acquisition running")
                    
                        self.textbox.append ("\n*** Entering loop ***\n")
                        
                        
                        n = np.arange(0,4096) #This array stores pixel positions from 0 to 4095
                        
                        
                        self.cont_pix = []    #The positions of middle pixel with highest value of intensity are stored in this container
                        
                        #This function finds the middle pixel from all pixels with maximum value
                        def arrsummean(numlist):
                            sum = 0
                            mean = 0
                            for i in numlist:
                                sum = sum + i
                                mean = round(sum/len(numlist))
                            return mean
                        
                        #This function defines the data for animation
                        '''def animate(i):
                            line.set_data([self.cont_pix[len(self.cont_pix)-1],self.cont_pix[len(self.cont_pix)-1]],[0,10])
                            return line,
                        
                        fig = plt.figure()
                        ax = plt.axes(xlim = (0,4096), ylim = (0,10)) #defining the range of plot
                        line, = ax.plot([],[], lw = 2)
                        ani = animation.FuncAnimation(fig, animate,frames = 500, interval = 1, blit=True) #matplotlib function that runs animation
                        
                        plt.show()'''            #initialization of plot
                        self.storage_time = [] # #This array stores timestamps for each measurement
                        k = 0                  # counter for establishing the frequency of data recording
                        
                        #Main loop in which data is recorded
                        while self.started == True:
                            storage_pix = [] # This temporary container stores positions of the pixels, that had values higher than treshold
                            storage_val = [] # This temporary container values of intensity that are higher than treshold
                            cont = []        # This container stores only those pixels, that have highest intensity value
                            v2 = self.my_class.my_waitforpipe(self.dwTimeOut) #This function is not working
                            f2, data, bytesRead = self.my_class.my_getpipe()  #Getting data from pipe
                            if  k % 48  == 0: #because of high measurement speed, this computer can't handle this temp. for this, we reducing measurement frequency.this condition reads every n-th measurement, to keep the frequency approx 10 Hz  n = 6 for plotting, n = 48 without plotting
                                self.storage_time.append(datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S.%f')[:-3]) #recording the timestamp of each measurement
                                #iteration through every pixel in camera
                                for i in range(0,4095):
                                    # setting the value treshold
                                    if data[i] > 50000:
                                        #if value passes this treshold it appends to the temporary container
                                        storage_pix.append(i)
                                        storage_val.append(data[i])
                                #iteration trough data, that passed treshold        
                                for i in range (0, len(storage_pix)):
                                    #condition of maximum value in array
                                    if storage_val[i] == max(storage_val):
                                        #appending only pixels that had maximum value
                                        cont.append(storage_pix[i])
                                 #finally appending only one middle pixel to permanent container       
                                self.cont_pix.append(arrsummean(cont))
                                print(self.cont_pix[len(self.cont_pix)-1], self.storage_time[len(self.storage_time)-1])
                            #function for processing of all actions in GUI    
                            QtGui.qApp.processEvents()
                            #incresing the counter
                            k +=1
            else:
                self.textbox.append ("No device found")
    #This function executes, when "stop" button is pressed           
    def stop_measure(self):
        self.started = False
        
        w = self.my_class.my_setstate(0x00, self.ucTimeOut)
        if w == 0:
            self.textbox.append ("\nw - Stoping data acquisition: OK")
        else:
            n = self.my_class.my_geterrorstring(w)
            self.textbox.append ("w - ERROR stoping data acquisition :", n)
                    # Read state:
        x, state = self.my_class.my_getstate(self.ucState, self.ucTimeOut)
        if x == 0:
            self.textbox.append ("x - Getting state: OK")
        else:
            n = self.my_class.my_geterrorstring(x)
            self.textbox.append ("x - ERROR getting state: ", n)
        if state == 0x00:
            self.textbox.append ("    Acquisition stopped")
        if state == 0x01:
            self.textbox.append ("    Acquisition running")
                    # Close device
        z = self.my_class.my_closedevice()
        if z == 0:
            self.textbox.append ("z - Closing device: OK")
        else:
            n = self.my_class.my_geterrorstring(z)
            self.textbox.append ("z - ERROR closing device: ", n)
        print (len(self.cont_pix), len(self.storage_time))
        #recording the processed data into the text file
        file = open('/home/pi/results/result.txt', 'w')
        for i in range(0, len(self.cont_pix)):
            file.write(str(self.cont_pix[i]) + ':' + str(self.storage_time[i]) + '\n')
        file.close()
        
def run():
    app = QtGui.QApplication(sys.argv)
    qb = BoxLayout()
    sys.exit(app.exec_())
run()
Popen('./server.py')

