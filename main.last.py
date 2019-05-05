import sys, os
from graphic import *
from scipy import signal
from PyQt5 import QtCore, QtGui, QtWidgets
import urllib.request, urllib.error
import time
import math
import xml.etree.cElementTree as ET
import datetime


# This variables created for retrieving particular type of data:
dir_tzb = 'raw_data/tape_zero_before.txt' #tape zero before data
dir_tza = 'raw_data/tape_zero_after.txt'  #tape zero after data
dir_ptm = 'raw_data/pass_through.txt'     #pass through method data

#This function is for displaying errors
def catch_exceptions(t, val, tb):
    QtWidgets.QMessageBox.critical(None,
                                   "An exception was raised",
                                   "Exception type: {}".format(t))
    old_hook(t, val, tb)
old_hook = sys.excepthook
sys.excepthook = catch_exceptions

#This is the main class of GUI. All functions are stored here
class MyWin(QtWidgets.QMainWindow):

    #Interpolation of the time for each pixel
    def gettime(self, array):
        hours = int(array[11:13:1])
        minutes = int(array[14:16:1])
        seconds = float(array[17:23:1])
        pix_time = hours * 3600 + minutes * 60 + seconds
        hours_pixel = math.floor(pix_time / 3600)
        minutes_pixel = math.floor((pix_time - hours_pixel * 3600) / 60)
        seconds_pixel = round(((pix_time - hours_pixel * 3600) / 60 - minutes_pixel) * 60, 3)
        present_time = str(hours_pixel) + '-' + str(minutes_pixel) + '-' + str(seconds_pixel)
        return pix_time

    #Creating two arrays: middle pixels and its timestamps for each measurement
    def extraction(self, input_file, return_value):
        rd_file = open(input_file, 'r')
        arr = []
        old_arr = []
        pixels = []
        time = []
        r_time = []
        str_cont = []
        for i in rd_file:  # input_file:
            old_arr.append(i)
        for line in old_arr:
            if not line.strip():
                continue
            else:
                arr.append(line)
        count_i = 0
        while count_i < len(arr):
            if arr[count_i][0]=='0':
                arr.pop(count_i)
                count_i -= 1
            count_i += 1
        for i in range(0, len(arr)):
            a, b = arr[i].split(':')
            pixels.append(int(a))
            str_cont.append(b)
        for i in range(0, len(pixels)):
            r_time.append(self.gettime(str_cont[i]))
        if return_value == 2:
            return pixels
        if return_value == 1:
            return r_time
        rd_file.close()

    #Computing tape zero
    def computing_tz(self,path):
        time_cont = self.extraction(path, 1)
        pix_cont = self.extraction(path, 2)
        yhat = signal.savgol_filter(pix_cont, 51, 3)
        rounded = []

        for i in yhat:
            rounded.append(int(i))

        #this filter deletes the elements that are the same as neighbouring
        def filter1():
            i = 1
            while i < len(rounded):
                if rounded[i] == rounded[i - 1]:
                    rounded.pop(i)
                    time_cont.pop(i)
                    i -= 1
                i += 1

        #this filter deletes element that are greater or less then two neighbouring elements
        def filter2():
            i = 2
            while i < len(rounded):
                if rounded[i - 2] > rounded[i - 1] < rounded[i] or rounded[i - 2] < rounded[i - 1] > rounded[i]:
                    rounded.pop(i - 1)
                    time_cont.pop(i - 1)
                    i -= 1
                i += 1

        j = 0
        if max(rounded) - min(rounded) > 10:
            while j < 4:
                filter1()
                filter2()
                j += 1
        store = []

        #transforming pixel array into array of ones and zeros. the position on the edge of zeros and ones is the position of turning pixel
        def null_ones():
            for i in range(1, len(rounded)):
                if rounded[i - 1] > rounded[i]:
                    store.append(0)
                else:
                    store.append(1)

        null_ones()
        turn_pos = []
        # creating the array with turning pixels
        def turning_points():
            for i in range(1, len(store)):
                if store[i - 1] != store[i]:
                    turn_pos.append(rounded[i])

        turning_points()
        if turn_pos[0] > turn_pos[1]:
            #calc_tz()
            turn_pos.pop(0)

        #Some variable declarations for further computations
        left1 = turn_pos[0]
        right1 = turn_pos[1]
        left2 = turn_pos[2]
        right2 = turn_pos[3]
        left3 = turn_pos[4]
        right3 = turn_pos[5] #Here supposed to be [5]
        tz_1 = (left1 + right1) / 2
        tz_2 = (left2 + right2) / 2
        tz_3 = (left3 + right3) / 2
        tz_m = (tz_1 + tz_2 + tz_3) / 3
        return {'left1':left1,'left2':left2,'left3':left3,'right1':right1,'right2':right2,'right3':right3,'mid1':tz_1, 'mid2':tz_2,'mid3':tz_3,'mid_m':tz_m}

    #passing the values to dictionary
    def pass_func_b(self):
        self.dic_b = self.computing_tz(dir_tzb)

    def pass_func_a(self):
        self.dic_a = self.computing_tz(dir_tza)

    #displaying tape zero data in GUI
    def show_tz(self, state):
        if state == 'before':
            self.ui.lineEdit_5.setText(str(self.dic_b['left1']))
            self.ui.lineEdit_8.setText(str(self.dic_b['right1']))
            self.ui.lineEdit_6.setText(str(self.dic_b['left2']))
            self.ui.lineEdit_9.setText(str(self.dic_b['right2']))
            self.ui.lineEdit_7.setText(str(self.dic_b['left3']))
            self.ui.lineEdit_10.setText(str(self.dic_b['right3']))
            self.ui.lineEdit_11.setText(str(self.dic_b['mid1']))
            self.ui.lineEdit_12.setText(str(self.dic_b['mid2']))
            self.ui.lineEdit_13.setText(str(self.dic_b['mid3']))
            self.ui.lineEdit_14.setText(str(round(self.dic_b['mid_m'], 1)))
            self.ui.lineEdit_15.setText(str(round(self.dic_b['mid_m'], 1)))
            self.show_tz_before = True
        if state == 'after':
            self.ui.lineEdit_5.setText(str(self.dic_a['left1']))
            self.ui.lineEdit_8.setText(str(self.dic_a['right1']))
            self.ui.lineEdit_6.setText(str(self.dic_a['left2']))
            self.ui.lineEdit_9.setText(str(self.dic_a['right2']))
            self.ui.lineEdit_7.setText(str(self.dic_a['left3']))
            self.ui.lineEdit_10.setText(str(self.dic_a['right3']))
            self.ui.lineEdit_11.setText(str(self.dic_a['mid1']))
            self.ui.lineEdit_12.setText(str(self.dic_a['mid2']))
            self.ui.lineEdit_13.setText(str(self.dic_a['mid3']))
            self.ui.lineEdit_14.setText(str(round(self.dic_a['mid_m'], 1)))
            self.ui.lineEdit_16.setText(str(round(self.dic_a['mid_m'], 1)))
            self.show_tz_after = True

        if hasattr(self, 'show_tz_before') and hasattr(self, 'show_tz_after'):
            self.mean_tz = (self.dic_b['mid_m'] + self.dic_a['mid_m'])/2
            self.ui.lineEdit_17.setText(str(round(self.mean_tz, 1)))
        if hasattr(self, 'mean_tz') and hasattr(self, 'dw'):
            self.tz_corr = self.mean_tz*self.dw
            self.ui.lineEdit_24.setText(str(round(self.tz_corr,2)))

    def show_z(self, state):
        if state == 'before':
            self.ui.lineEdit_3.setText(self.z_meas_before)
            self.show_z_before = True
        if state == 'after':
            self.ui.lineEdit_3.setText(self.z_meas_after)
            self.show_z_after = True
        if hasattr(self, 'show_z_before') and hasattr(self, 'show_z_after'):
            self.ui.lineEdit_21.setText(str(round(self.dir_to_targ,4)))
            self.ui.lineEdit_27.setText(str(round(float(self.z_meas_before) - float(self.z_meas_after),4)))
    #Function for switching between radiobuttons
    def blanc_field(self):
        self.ui.lineEdit_5.setText('')
        self.ui.lineEdit_8.setText('')
        self.ui.lineEdit_6.setText('')
        self.ui.lineEdit_9.setText('')
        self.ui.lineEdit_7.setText('')
        self.ui.lineEdit_10.setText('')
        self.ui.lineEdit_11.setText('')
        self.ui.lineEdit_12.setText('')
        self.ui.lineEdit_13.setText('')
        self.ui.lineEdit_14.setText('')
        self.ui.lineEdit_16.setText('')
    def blanc_field_z(self):
        self.ui.lineEdit_3.setText('')
    #transforming time for proper time displaying
    def time_transform(self, t):
        min = math.floor(t/60)
        sec = round(t - min*60,1)
        s = ''
        if min < 10:
            s = '0'+str(min)+':'+str(sec)
        else:
            s = str(min)+':'+str(sec)
        return s

    #processing the pass through data
    def computing_ptm(self,path):
        time_cont = self.extraction(path, 1)
        pix_cont = self.extraction(path, 2)
        # count = []
        yhat = signal.savgol_filter(pix_cont, 51, 3)
        rounded = []
        for i in yhat:
            rounded.append(int(i))

        def filter1():
            i = 1
            while i < len(rounded):
                if rounded[i] == rounded[i - 1]:
                    rounded.pop(i)
                    time_cont.pop(i)
                    i -= 1
                i += 1

        def filter2():
            i = 2
            while i < len(rounded):
                if rounded[i - 2] > rounded[i - 1] < rounded[i] or rounded[i - 2] < rounded[i - 1] > rounded[i]:
                    rounded.pop(i - 1)
                    time_cont.pop(i - 1)
                    i -= 1
                i += 1

        j = 0
        while j < 2:
            filter1()
            filter2()
            j += 1
        store = []

        def null_ones():
            for i in range(1, len(rounded)):
                if rounded[i - 1] > rounded[i]:
                    store.append(0)
                else:
                    store.append(1)

        null_ones()
        turn_pos = []

        def turning_points():
            for i in range(1, len(store)):
                if store[i - 1] != store[i]:
                    turn_pos.append(rounded[i])

        turning_points()
        zero_time = []
        for i in range(1, len(rounded)-3):
            if rounded[i] == 2048 and rounded[i-1] != 2048 and rounded[1+1] !=2048:
                zero_time.append(time_cont[i])
            elif rounded[i] == 2048 and rounded[i+1] == 2048 and rounded[i-1] !=2048 and rounded[i+2] !=2048:
                zero_time.append((time_cont[i]+time_cont[i+1])/2)
            elif rounded[i] == 2048 and rounded[i+1] == 2048 and rounded[i+2] == 2048 and rounded[i-1] != 2048 and rounded[i+3] != 2048:
                zero_time.append(time_cont[i+1])
            elif rounded[i] == 2048 and rounded[i+1] == 2048 and rounded[i+2] == 2048 and rounded[i+3] == 2048 and rounded[i-1] != 2048 and rounded[i+4] != 2048:
                zero_time.append((time_cont[i + 1]+time_cont[i+2])/2)
            elif rounded[i] < 2048 and rounded[i+1] > 2048 or rounded[i] > 2048 and rounded[i+1] < 2048:
                zero_time.append((time_cont[i]+time_cont[i+1])/2)


        self.t0 = 0
        self.t1 = zero_time[1] - zero_time[0]
        self.t2 = zero_time[2] - zero_time[0]
        self.t3 = zero_time[3] - zero_time[0]
        self.t4 = zero_time[4] - zero_time[0]
        self.ui.lineEdit_44.setText(self.time_transform(self.t0))
        self.ui.lineEdit_45.setText(self.time_transform(self.t1))
        self.ui.lineEdit_46.setText(self.time_transform(self.t2))
        self.ui.lineEdit_47.setText(self.time_transform(self.t3))
        self.ui.lineEdit_48.setText(self.time_transform(self.t4))
        def calc_ptm():
            self.ui.lineEdit_49.setText(str(turn_pos[0]))
            self.ui.lineEdit_50.setText(str(turn_pos[1]))
            self.ui.lineEdit_51.setText(str(turn_pos[2]))
            self.ui.lineEdit_52.setText(str(turn_pos[3]))

        if turn_pos[0] < turn_pos[1]:
            turn_pos.pop(0)
            calc_ptm()
        else:
            calc_ptm()
        if self.ui.lineEdit_31.text() == '':
            self.ui.lineEdit_60.setText('Please, enter the "c prop" value')
        else:
            c_prop = float(self.ui.lineEdit_31.text())
            self.ar1 = turn_pos[0]
            self.al1 = turn_pos[1]
            self.ar2 = turn_pos[2]
            self.al2 = turn_pos[3]
            a1 = (abs(self.ar1)+abs(self.al1))/2
            a2 = (abs(self.al1)+abs(self.ar2))/2
            a3 = (abs(self.ar2)+abs(self.al2))/2
            delta_t1 = self.t2 - self.t1
            delta_t2 = self.t3 - self.t2
            delta_t3 = self.t4 - self.t3
            self.delta_n1 = c_prop * a1 * delta_t1
            self.delta_n2 = c_prop * a2 * delta_t2
            self.delta_n3 = c_prop * a3 * delta_t3
            self.delta_n_m = (self.delta_n1+self.delta_n2+self.delta_n3)/3
            self.stdev = (((self.delta_n1-self.delta_n_m)**2+(self.delta_n2-self.delta_n_m)**2+(self.delta_n3-self.delta_n_m)**2)/3)**0.5
            self.ui.lineEdit_53.setText(str(round(self.delta_n1,4)))
            self.ui.lineEdit_54.setText(str(round(self.delta_n2,4)))
            self.ui.lineEdit_55.setText(str(round(self.delta_n3,4)))
            self.ui.lineEdit_56.setText(str(round(self.stdev,4)))
            self.ui.lineEdit_57.setText(str(round(self.delta_n_m,4)))
            self.ui.lineEdit_23.setText(str(round(self.delta_n_m,4)))


    #connection with web-sever and downloading data
    def connection(self, store_file):
        link = "http://192.168.137.159:8080" #link may be changed
        f = urllib.request.urlopen(link)
        myfile = f.read()
        passfile = open(store_file, 'w')
        passfile.write(myfile.decode("utf-8"))
        passfile.write('\n')
        passfile.close()

    def apply_settings(self):
        self.ui.lineEdit_20.setText('Pass Through' + ' (' + self.ui.comboBox_4.currentText() + ')')

    #Main Window func
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.dataCollection_tz)
        self.ui.pushButton_2.clicked.connect(self.processing_ptm)
        self.ui.pushButton_3.clicked.connect(self.browse)
        self.ui.pushButton_4.clicked.connect(self.z_measure)
        self.ui.pushButton_5.clicked.connect(self.applyConfig)
        self.ui.pushButton_6.clicked.connect(self.loadProject)
        self.ui.pushButton_9.clicked.connect(self.storeProject)
        self.ui.pushButton_7.clicked.connect(self.processing_tz)
        self.ui.pushButton_8.clicked.connect(self.applySett)
        self.ui.pushButton_10.clicked.connect(self.dataCollection_ptm)
        self.ui.pushButton_11.clicked.connect(self.saveChanges)
        self.ui.pushButton_12.clicked.connect(self.preorient)

        self.ui.radioButton.toggled.connect(lambda:self.btnstate(self.ui.radioButton))
        self.ui.radioButton_2.toggled.connect(lambda: self.btnstate(self.ui.radioButton_2))
        self.ui.tabwidget.setCurrentIndex(0)
        self.ui.lineEdit_20.setText('Pass Through'+ ' (' + self.ui.comboBox_4.currentText() + ')')


    def z_measure(self):
        if self.ui.radioButton.isChecked():
            if self.ui.lineEdit_3.text() != '':
                self.z_meas_before = self.ui.lineEdit_3.text()
                self.ui.lineEdit_60.setText('')
            else:
                self.ui.lineEdit_60.setText('Please, enter the Z value')
        elif self.ui.radioButton_2.isChecked():
            if self.ui.lineEdit_3.text() != '':
                self.z_meas_after = self.ui.lineEdit_3.text()
                self.ui.lineEdit_60.setText('')

            else:
                self.ui.lineEdit_60.setText('Please, enter the Z value')
        else:
            self.ui.lineEdit_60.setText('Please, choose the measurement type')
        if hasattr(self, 'z_meas_before') and hasattr(self, 'z_meas_after'):
            self.dir_to_targ = (float(self.z_meas_before) + float(self.z_meas_after)) / 2
            self.ui.lineEdit_21.setText(str(round((float(self.z_meas_before)+float(self.z_meas_after))/2,4)))
            self.ui.lineEdit_27.setText(str(round(float(self.z_meas_before) - float(self.z_meas_after),4)))
        if hasattr(self, 'dir_to_targ'):
            self.azi = self.dir_to_targ - (self.pre_orient + self.delta_n_m) - self.tz_corr - self.Eval
            self.ui.lineEdit_26.setText(str(round(self.azi, 4)))

    def applySett(self):
        self.apply_settings()

    #Function for switching between radiobuttons
    def btnstate(self, b):
        if hasattr(self, 'dic_b') and hasattr(self, 'dic_a'):
            if b.text() == 'Before measure':
                if b.isChecked() == True:
                    self.show_tz('before')
            if b.text() == 'After measure':
                if b.isChecked() == True:
                    self.show_tz('after')
        elif hasattr(self, 'dic_b') and not hasattr(self, 'dic_a'):
            if b.text() == 'Before measure':
                if b.isChecked() == True:
                    self.show_tz('before')
            if b.text() == 'After measure':
                if b.isChecked() == True:
                    self.blanc_field()
        elif not hasattr(self, 'dic_b') and hasattr(self, 'dic_a'):
            if b.text() == 'Before measure':
                if b.isChecked() == True:
                    self.blanc_field()
            if b.text() == 'After measure':
                if b.isChecked() == True:
                    self.show_tz('after')
        if hasattr(self, 'z_meas_before') and hasattr(self, 'z_meas_after'):
            if b.text() == 'Before measure':
                if b.isChecked() == True:
                    self.show_z('before')
            if b.text() == 'After measure':
                if b.isChecked() == True:
                    self.show_z('after')
        elif hasattr(self, 'z_meas_before') and not hasattr(self, 'z_meas_after'):
            if b.text() == 'Before measure':
                if b.isChecked() == True:
                    self.show_z('before')
            if b.text() == 'After measure':
                if b.isChecked() == True:
                    self.blanc_field_z()
        elif not hasattr(self, 'z_meas_before') and hasattr(self, 'z_meas_after'):
            if b.text() == 'Before measure':
                if b.isChecked() == True:
                    self.blanc_field_z()
            if b.text() == 'After measure':
                if b.isChecked() == True:
                    self.show_z('after')

    #Apply parameters that were entered manually
    def applyConfig(self):
        if self.ui.lineEdit_28.text() == '' or self.ui.lineEdit_29.text() == '' or self.ui.lineEdit_30.text() == '' or self.ui.lineEdit_31.text() == '':
            self.ui.lineEdit_60.setText('Please, enter the missing data')
        else:
            print (self.ui.lineEdit_28.text(),self.ui.lineEdit_29.text(),self.ui.lineEdit_30.text(),self.ui.lineEdit_31.text())
            self.Eval = float(self.ui.lineEdit_28.text())
            self.ui.lineEdit_18.setText(str(self.Eval))
            self.dw_eq = self.ui.lineEdit_29.text()
            self.latitude = self.ui.lineEdit_30.text()
            self.c_prop = self.ui.lineEdit_31.text()
            self.ui.lineEdit_60.setText('Changes have been applied')
            self.ui.lineEdit_25.setText(self.ui.lineEdit_28.text())
            self.dw = float(self.dw_eq)/math.cos(math.radians(float(self.latitude)))
            self.ui.lineEdit_19.setText(str(round(self.dw,4)))

    #Storing the project
    def storeProject(self):

        root = ET.Element('GYRO')
        ET.SubElement(root, "Version").text = 'GYROMAX V1.0.5.7'
        ET.SubElement(root, "StoringDate").text = datetime.datetime.utcnow().strftime('%d/%m/%y')
        ET.SubElement(root, "StoringTime").text = datetime.datetime.utcnow().strftime('%I:%M %p')
        ET.SubElement(root, "Interval").text = self.ui.comboBox_3.currentText()
        prdata = ET.SubElement(root, 'ProjectData')
        ET.SubElement(prdata, 'Project').text = self.ui.lineEdit.text()
        ET.SubElement(prdata, 'Station').text = self.ui.lineEdit_58.text()
        ET.SubElement(prdata, 'Target').text = self.ui.lineEdit_59.text()
        ET.SubElement(prdata, 'FileVersion').text = '0'
        tzb = ET.SubElement(root, 'TapeZeroBefore')
        ET.SubElement(tzb, 'TZB0')
        ET.SubElement(tzb, 'TZB1')
        ET.SubElement(tzb, 'TZB2')
        ET.SubElement(tzb, 'TZB3')
        ET.SubElement(tzb, 'TZB4')
        ET.SubElement(tzb, 'TZB5')
        ET.SubElement(tzb, 'TZB')
        ET.SubElement(tzb, 'ZB')
        tza = ET.SubElement(root, 'TapeZeroAfter')
        ET.SubElement(tza, 'TZA0')
        ET.SubElement(tza, 'TZA1')
        ET.SubElement(tza, 'TZA2')
        ET.SubElement(tza, 'TZA3')
        ET.SubElement(tza, 'TZA4')
        ET.SubElement(tza, 'TZA5')
        ET.SubElement(tza, 'TZA')
        ET.SubElement(tza, 'ZA')
        ptm = ET.SubElement(root, 'PassTroughMethod')
        ET.SubElement(ptm, 't0')
        ET.SubElement(ptm, 'a0')
        ET.SubElement(ptm, 't1')
        ET.SubElement(ptm, 'a1')
        ET.SubElement(ptm, 't2')
        ET.SubElement(ptm, 'a2')
        ET.SubElement(ptm, 't3')
        ET.SubElement(ptm, 'a3')
        ET.SubElement(ptm, 'deltaN0')
        ET.SubElement(ptm, 'deltaN1')
        ET.SubElement(ptm, 'deltaN2')
        ET.SubElement(ptm, 'deltaN')
        ET.SubElement(ptm, 'STD')
        cor = ET.SubElement(root, 'Correction')
        ET.SubElement(cor, 'Latitude')
        ET.SubElement(cor, 'DW')
        ET.SubElement(cor, 'DWe')
        ET.SubElement(cor, 'EValue')
        ET.SubElement(cor, 'CProp')
        ET.SubElement(cor, 'Nstr')
        ET.SubElement(cor, 'C')
        azi = ET.SubElement(root, 'Azimuth')
        ET.SubElement(azi, 'Azimuth')
        ET.SubElement(azi, 'TargetDiff')

        tree = ET.ElementTree(root)
        name2store = self.ui.lineEdit.text() + '_' + self.ui.lineEdit_58.text() + '_' + self.ui.lineEdit_59.text()
        if name2store == '__':
            self.ui.lineEdit_60.setText('Please, type the name of the project')
        else:
            tree.write("D:/MasterThesis/GUI/" + name2store+'.xml')
            self.ui.lineEdit_60.setText('Project has been created')

    #Saving changes in xml-file
    def saveChanges(self):
        import xml.etree.ElementTree as ET
        name2store = self.ui.lineEdit.text() + '_' + self.ui.lineEdit_58.text() + '_' + self.ui.lineEdit_59.text()
        if name2store == '__':
            self.ui.lineEdit_60.setText('Please, type the name of the project')
        else:
            try:
                et = ET.parse('D:/MasterThesis/GUI/' + name2store + '.xml')
                root = et.getroot()
                stor_date = et.find('.//StoringDate')
                stor_date.text = datetime.datetime.utcnow().strftime('%d/%m/%y')
                stor_time = et.find('.//StoringTime')
                stor_time.text = datetime.datetime.utcnow().strftime('%I:%M %p')
                interval = et.find('.//Interval')
                interval.text = self.ui.comboBox_3.currentText()
                file_ver = et.find('.//FileVersion')
                file_ver.text = str(int(file_ver.text) + 1)

                tzb0_xml = et.find('.//TZB0')
                tzb0_xml.text = str(self.dic_b['left1'])
                tzb1_xml = et.find('.//TZB1')
                tzb1_xml.text = str(self.dic_b['right1'])
                tzb2_xml = et.find('.//TZB2')
                tzb2_xml.text = str(self.dic_b['left2'])
                tzb3_xml = et.find('.//TZB3')
                tzb3_xml.text = str(self.dic_b['right2'])
                tzb4_xml = et.find('.//TZB4')
                tzb4_xml.text = str(self.dic_b['left3'])
                tzb5_xml = et.find('.//TZB5')
                tzb5_xml.text = str(self.dic_b['right3'])
                tzb_xml = et.find('.//TZB')
                tzb_xml.text = str(round(self.dic_b['mid_m'], 1))
                tzb_dir = et.find('.//ZB')
                tzb_dir.text = str(self.z_meas_before)

                tza0_xml = et.find('.//TZA0')
                tza0_xml.text = str(self.dic_a['left1'])
                tza1_xml = et.find('.//TZA1')
                tza1_xml.text = str(self.dic_a['right1'])
                tza2_xml = et.find('.//TZA2')
                tza2_xml.text = str(self.dic_a['left2'])
                tza3_xml = et.find('.//TZA3')
                tza3_xml.text = str(self.dic_a['right2'])
                tza4_xml = et.find('.//TZA4')
                tza4_xml.text = str(self.dic_a['left3'])
                tza5_xml = et.find('.//TZA5')
                tza5_xml.text = str(self.dic_a['right3'])
                tza_xml = et.find('.//TZA')
                tza_xml.text = str(round(self.dic_a['mid_m'], 1))
                tza_dir = et.find('.//ZA')
                tza_dir.text = str(self.z_meas_after)

                t0 = et.find('.//t0')
                t0.text = str(round(self.t1, 4))
                t1 = et.find('.//t1')
                t1.text = str(round(self.t2, 4))
                t2 = et.find('.//t2')
                t2.text = str(round(self.t3,4))
                t3 = et.find('.//t3')
                t3.text = str(round(self.t4,4))
                a0 = et.find('.//a0')
                a0.text = str(self.ar1)
                a1 = et.find('.//a1')
                a1.text = str(self.al1)
                a2 = et.find('.//a2')
                a2.text = str(self.ar2)
                a3 = et.find('.//a3')
                a3.text = str(self.al2)
                dN0 = et.find('.//deltaN0')
                dN0.text = str(round(self.delta_n1,4))
                dN1 = et.find('.//deltaN1')
                dN1.text = str(round(self.delta_n2,4))
                dN2 = et.find('.//deltaN2')
                dN2.text = str(round(self.delta_n3,4))
                dN = et.find('.//deltaN')
                dN.text = str(round(self.delta_n_m,4))
                std = et.find('.//STD')
                std.text = str(round(self.stdev,4))

                lat_xml = et.find('.//Latitude')
                lat_xml.text = self.latitude
                dw_xml = et.find('.//DW')
                dw_xml.text = str(round(self.dw,4))
                dweq_xml = et.find('.//DWe')
                dweq_xml.text = self.dw_eq
                Eval_xml = et.find('.//EValue')
                Eval_xml.text = str(self.Eval)
                cprop_xml = et.find('.//CProp')
                cprop_xml.text = str(self.c_prop)
                Nstr = et.find('.//Nstr')
                Nstr.text = str(self.pre_orient)
                c_val = et.find('.//C')
                c_val.text = str(round(self.tz_corr,4))
                azi = et.find('.//Azimuth/Azimuth')
                azi.text = str(round(self.azi,4))
                targ_diff = et.find('.//TargetDiff')
                targ_diff.text = self.ui.lineEdit_27.text()

                et.write("D:/MasterThesis/GUI/" + name2store+'.xml')
                self.ui.lineEdit_60.setText('Changes have been saved')
            except FileNotFoundError:
                self.ui.lineEdit_60.setText('Please, create first the project file')
            """except AttributeError:
                self.ui.lineEdit_60.setText('Please, fill the missing data fields')"""

    #Download button for Tape Zero
    def dataCollection_tz(self):
        try:
            if self.ui.radioButton.isChecked():
                self.ui.lineEdit_60.setText('Button 1 is active')
                self.connection(dir_tzb)
            elif self.ui.radioButton_2.isChecked():
                self.ui.lineEdit_60.setText('Button 2 is active')
                self.connection(dir_tza)
            else:
                self.ui.lineEdit_60.setText('Please, select the data type')
        except urllib.error.URLError as urler:
            self.ui.lineEdit_60.setText('Error: {0}'.format(urler))

    #Download button for Pass Through Method
    def dataCollection_ptm(self):
        try:
            self.connection(dir_ptm)
        except urllib.error.URLError as urler:
            self.ui.lineEdit_60.setText('Error: {0}'.format(urler))

    #Computation button for Tape Zero
    def processing_tz(self):
        self.ui.lineEdit_60.setText('')
        if self.ui.radioButton.isChecked():
            self.pass_func_b()
            #self.calc_tz(dir_tzb)
            self.show_tz('before')
        elif self.ui.radioButton_2.isChecked():
            self.pass_func_a()
            #self.calc_tz(dir_tza)
            self.show_tz('after')
        else:
            self.ui.lineEdit_60.setText('Please, select the data type')

    # Computation button for Pass Through Method
    def processing_ptm(self):
        self.computing_ptm(dir_ptm)

    #Browse button
    def browse(self):
        filepath, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', 'D:\\MasterThesis\\get', '*.txt *.xml')
        self.ui.lineEdit_4.setText(filepath)

    def loadProject(self):
        et = ET.parse(self.ui.lineEdit_4.text())
        root = et.getroot()

        tzb0_xml = et.find('.//TZB0')
        self.ui.lineEdit_5.setText(tzb0_xml.text)
        tzb1_xml = et.find('.//TZB1')
        self.ui.lineEdit_8.setText(tzb1_xml.text)
        tzb2_xml = et.find('.//TZB2')
        self.ui.lineEdit_6.setText(tzb2_xml.text)
        tzb3_xml = et.find('.//TZB3')
        self.ui.lineEdit_9.setText(tzb3_xml.text)
        tzb4_xml = et.find('.//TZB4')
        self.ui.lineEdit_7.setText(tzb4_xml.text)
        tzb5_xml = et.find('.//TZB5')
        self.ui.lineEdit_10.setText(tzb5_xml.text)
        tzb_xml = et.find('.//TZB')
        self.ui.lineEdit_14.setText(tzb_xml.text)
        tzb_dir = et.find('.//ZB')
        self.ui.lineEdit_5.setText(tzb0_xml.text)


        tza0_xml = et.find('.//TZA0')

        tza1_xml = et.find('.//TZA1')

        tza2_xml = et.find('.//TZA2')

        tza3_xml = et.find('.//TZA3')

        tza4_xml = et.find('.//TZA4')

        tza5_xml = et.find('.//TZA5')

        tza_xml = et.find('.//TZA')

        tza_dir = et.find('.//ZA')


        t0 = et.find('.//t0')

        t1 = et.find('.//t1')

        t2 = et.find('.//t2')

        t3 = et.find('.//t3')

        a0 = et.find('.//a0')

        a1 = et.find('.//a1')

        a2 = et.find('.//a2')

        a3 = et.find('.//a3')

        dN0 = et.find('.//deltaN0')

        dN1 = et.find('.//deltaN1')

        dN2 = et.find('.//deltaN2')

        dN = et.find('.//deltaN')

        std = et.find('.//STD')

        lat_xml = et.find('.//Latitude')

        dw_xml = et.find('.//DW')

        dweq_xml = et.find('.//DWe')

        Eval_xml = et.find('.//EValue')

        cprop_xml = et.find('.//CProp')

        Nstr = et.find('.//Nstr')

        c_val = et.find('.//C')

        azi = et.find('.//Azimuth/Azimuth')

        targ_diff = et.find('.//TargetDiff')




    def preorient(self):
        if self.ui.lineEdit_61.text() == '':
            self.ui.lineEdit_60.setText('Please, enter the value')
        else:
            self.pre_orient = float(self.ui.lineEdit_61.text())
            self.ui.lineEdit_22.setText(str(self.pre_orient))
            self.ui.lineEdit_60.setText('')
if __name__=="__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())
    raise RunTimeError
