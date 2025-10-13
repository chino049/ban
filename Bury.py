import traceback
import time
import datetime

import pytz

from qtd3 import Ui_MainWindow

from PyQt5 import uic, QtWidgets, QtGui

from PySide2 import QtCore #, QtGui
from PySide2.QtWidgets import *
from PySide2.QtGui import *

import os, sys
import requests
import time
import json

import yfinance as yf

class AlertsWindow(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        self.threadpool = QtCore.QThreadPool()

        self.setupUi(self)
        # self.connectMe()
        self.setWindowTitle("Ban")
        # self.setFixedWidth(1000)
        # self.setFixedHeight(1000)

        #self.vboxMain = QVBoxLayout(self)

        self.startButton.clicked.connect(self.run)
        #self.startButton_2.clicked.connect(self.runWeek)
        self.startButton_2.clicked.connect(self.populateWeek)

        #self.vboxMain.addWidget(self.startButton)

        self.stopButton.clicked.connect(self.stop)

        self.radioButtonAlerts.clicked.connect(self.runAlerts)
        #self.vboxMain.addWidget(self.stopButton)

        #self.progressbar = QProgressBar(self)
        self.progressBar.setRange(0, 1)
        #self.vboxMain.addWidget(self.progressBar)

        #self.info = QTextEdit(self)
        #self.info.append('Starting...')
        #self.info.setFixedWidth(300)
        #self.info.setFixedHeight(50)

       # print("JOP", self.le1s.setText("BTG"))

        fo = open("stocksSymbols", "r")
        folist = fo.readlines()
        # for rr in folist:
        #     print("JOP", rr)

        self.st = [[self.le1s, self.le1p, self.le1c, self.le1w, self.le1m, self.le1t, self.le1f, self.le1l, self.hs1],
                   [self.le2s, self.le2p, self.le2c, self.le2w, self.le2m, self.le2t, self.le2f, self.le2l, self.hs2],
                   [self.le3s, self.le3p, self.le3c, self.le3w, self.le3m, self.le3t, self.le3f, self.le3l, self.hs3],
                   [self.le4s, self.le4p, self.le4c, self.le4w, self.le4m, self.le4t, self.le4f, self.le4l, self.hs4],
                   [self.le5s, self.le5p, self.le5c, self.le5w, self.le5m, self.le5t, self.le5f, self.le5l, self.hs5],
                   [self.le6s, self.le6p, self.le6c, self.le6w, self.le6m, self.le6t, self.le6f, self.le6l, self.hs6],
                   [self.le7s, self.le7p, self.le7c, self.le7w, self.le7m, self.le7t, self.le7f, self.le7l, self.hs7],
                   [self.le8s, self.le8p, self.le8c, self.le8w, self.le8m, self.le8t, self.le8f, self.le8l, self.hs8],
                   [self.le9s, self.le9p, self.le9c, self.le9w, self.le9m, self.le9t, self.le9f, self.le9l, self.hs9],
                   [self.le10s, self.le10p, self.le10c, self.le10w, self.le10m, self.le10t, self.le10f, self.le10l, self.hs10],
                   [self.le11s, self.le11p, self.le11c, self.le11w, self.le11m, self.le11t, self.le11f, self.le11l, self.hs11],
                   [self.le12s, self.le12p, self.le12c, self.le12w, self.le12m, self.le12t, self.le12f, self.le12l, self.hs12],
                   [self.le13s, self.le13p, self.le13c, self.le13w, self.le13m, self.le13t, self.le13f, self.le13l, self.hs13],
                   [self.le14s, self.le14p, self.le14c, self.le14w, self.le14m, self.le14t, self.le14f, self.le14l, self.hs14],
                   [self.le15s, self.le15p, self.le15c, self.le15w, self.le15m, self.le15t, self.le15f, self.le15l, self.hs15],
                   [self.le16s, self.le16p, self.le16c, self.le16w, self.le16m, self.le16t, self.le16f, self.le16l, self.hs16],
                   [self.le17s, self.le17p, self.le17c, self.le17w, self.le17m, self.le17t, self.le17f, self.le17l, self.hs17],
                   [self.le18s, self.le18p, self.le18c, self.le18w, self.le18m, self.le18t, self.le18f, self.le18l, self.hs18],
                   [self.le19s, self.le19p, self.le19c, self.le19w, self.le19m, self.le19t, self.le19f, self.le19l, self.hs19],
                   [self.le20s, self.le20p, self.le20c, self.le20w, self.le20m, self.le20t, self.le20f, self.le20l, self.hs20]
                   ]

        self.le1s.setText(folist[0])
        self.le2s.setText(folist[1])
        self.le3s.setText(folist[2])
        self.le4s.setText(folist[3])
        self.le5s.setText(folist[4])
        self.le6s.setText(folist[5])
        self.le7s.setText(folist[6])
        self.le8s.setText(folist[7])
        self.le9s.setText(folist[8])
        self.le10s.setText(folist[9])

        self.le11s.setText(folist[10])
        self.le12s.setText(folist[11])
        self.le13s.setText(folist[12])
        self.le14s.setText(folist[13])
        self.le15s.setText(folist[14])
        self.le16s.setText(folist[15])
        self.le17s.setText(folist[16])
        self.le18s.setText(folist[17])
        self.le19s.setText(folist[18])
        self.le20s.setText(folist[19])
        # qtlist = ["self.le1s", "self.le2s"]
        #
        # # for rrr in qtlist:
        # #     print(rrr)
        #
        # for index, qtlist in enumerate(qtlist):
        #     print(".....", folist[index], qtlist[index])

        # co = 0
        # st = ['l1','l2','l3']
        #
        # while co < 100 :
        #     print(co)
        #     for rst in st:
        #         print(">", rst)
        #         co +=1
        #         self.populateOne(rst)

    # ['NIO', '002594.SZ', '601633.SS', '600104.SS', '000625.SZ', '601238.SS', '601127.SS', '600733.SS', '489.HK',
    #  '000800.SZ', 'NIO']
    # NIO
    # buzz
    # 0.3243
    # NIO
    # sentiment
    # bearish
    # 0.5
    # sentiment
    # bullish
    # 0.5
    # ALERT
    # BAD
    # currentRatioAnnual
    # 3.3061
    # ALERT
    # GOOD
    # currentRatioQuarterly
    # 3.06035
    # ALERT
    # GOOD
    # quickRatioAnnual
    # 3.22871
    # ALERT
    # GOOD
    # quickRatioQuarterly
    # 2.95761
    # ALERT
    # GOOD
    # roeRfy - 53.77115
    # ALERT
    # BAD
    # roeTTM - 10.62916
    # ALERT
    # BAD
    # Strong
    # Buy: 6
    # Strong
    # Sell: 0
    # Period: 2021 - 05 - 01
    # ALERT
    # GOOD
    # Strong
    # Buy: 5
    # Strong
    # Sell: 0
    # Period: 2021 - 04 - 01
    # ALERT
    # GOOD
    # Strong
    # Buy: 4
    # Strong
    # Sell: 0
    # Period: 2021 - 03 - 01
    # ALERT
    # GOOD

    def runAlerts(self):
        # childAl = AlertsWindow()
        #childAl.setProperty("Alerts","A")
        childAl.setWindowTitle("Alerts")
        childAl.setFixedWidth(600)
        childAl.setFixedHeight(400)
        childAl.show()

    def stop(self):
        #self.info("Stopping...")
        print("Stopping...")
        self.stopped=True
        return

    def completed(self):
        self.progressBar.setRange(0,1)
        return

    def run(self):
        #self.setCursor(Qt.WaitCursor)
        #self.info.append('Starting...')
        self.stopped = False
        self.run_threaded_process1(self.populateOne, self.completed)
        time.sleep(1)

    def runWeek(self):
        #self.setCursor(Qt.WaitCursor)
        #self.info.append('Starting...')
        #self.stopped = False
        self.run_threaded_process2(self.populateWeek)
        #time.sleep(1)

    def progress_fn(self, msg):
        #print("7 progress fn", str(msg))
        self.info.append(str(msg))
        return


    def run_threaded_process1(self, process, on_complete):
        """Execute a function in the background with a worker"""
        worker1 = Worker(fn=process)
        self.threadpool.start(worker1)
        worker1.signals.finished.connect(on_complete)
        worker1.signals.progress.connect(self.progress_fn)
        self.progressBar.setRange(0,0)
        return

    def run_threaded_process2(self, process):
        """Execute a function in the background with a worker"""
        worker2 = Worker2(fn=process)
        self.threadpool.start(worker2)
        #worker2.signals.finished.connect(on_complete)
        worker2.signals.progress.connect(self.progress_fn)
        #self.progressBar.setRange(0,0)
        return

    def populateWeek(self, progress_callback):
        la = int(time.time())
        no = la - 7257000
        print(no, la)

        for rst in self.st:
            #if rst[0] == self.le1:
            symbol = rst[0].text()
            #sp = rst[0]
            #pc = rst[1]
            #wp = rst[3]
            try:
                print(">>", symbol)
                ticker = yf.Ticker(symbol.strip())
                fir = pytz.UTC.localize(datetime.datetime(2099, 10, 20))
                las = pytz.UTC.localize(datetime.datetime(1967, 10, 20))
                # print("fir", fir)
                # print("las", las)
                firp=0.00
                lasp=0.00

                for row in ticker.history(period='7d').itertuples():
                   # print("row", row)
                   # print("7day close", row[0].strftime('%Y-%m-%d'), '%.4f' % row[4])
                    if row[0] > las:
                        las = row[0]
                        lasp = row[4]
                    if row[0] < fir:
                        fir = row[0]
                        firp = row[4]

                # print("first W", fir, firp)
                # print("last W", las, lasp)


                #wProfit = ((r_dict['c'][vaa - 1] - r_dict['c'][53]) * 100) / r_dict['c'][vaa - 1]
                wProfit = round(lasp,2) - round(firp, 2)

                print("W", round(wProfit, 2))
                if float(wProfit) > 5:
                    rst[3].setStyleSheet("background-color: #43bd02; color: white")
                elif float(wProfit) > 0:
                    rst[3].setStyleSheet("background-color: darkGreen; color: white")
                elif float(wProfit) == 0:
                    rst[3].setStyleSheet("background-color: gray; color: white")
                elif float(wProfit) < -25:
                    rst[3].setStyleSheet("background-color: #420e01; color: white")
                elif float(wProfit) < -15:
                    rst[3].setStyleSheet("background-color: darkRed; color: white")
                else:
                    rst[3].setStyleSheet("background-color: Orange; color: white")
                #rst[3].setText(str(round(wProfit, 2)) + "%   " + str(round(wProfit, 2)) + "$")
                rst[3].setText(str(round(wProfit, 2)) + "$   " + str(round((wProfit*100)/firp, 2)) + "%")
                #rst[3].setText(str(round(wProfit, 2)) + "%   " + str(round(r_dict['c'][53], 2)) + "$")

                time.sleep(.5)
                #self.update()
                #self.show()

                fir = pytz.UTC.localize(datetime.datetime(2099, 10, 20))
                las = pytz.UTC.localize(datetime.datetime(1967, 10, 20))
                firp = 0.00
                lasp = 0.00
                print("fir", fir)
                print("las", las)
                for row in ticker.history(period='30d').itertuples():
                    # print("7day close", row[0].strftime('%Y-%m-%d'), '%.4f' % row[4])
                    if row[0] > las:
                        las = row[0]
                        lasp = row[4]
                    if row[0] < fir:
                        fir = row[0]
                        firp = row[4]

                # print("first M", fir, firp)
                # print("last M", las, lasp)

                mProfit = round(lasp, 2) - round(firp, 2)

                # # print(r_dict['c'][vaa - 1], r_dict['c'][40])
                # # mProfit = r_dict['c'][vaa-1] - r_dict['c'][40]
                #
                # mProfit = ((r_dict['c'][vaa - 1] - r_dict['c'][40]) * 100) / r_dict['c'][vaa - 1]
                print("M", mProfit)
                if float(mProfit) > 10:
                    rst[4].setStyleSheet("background-color: #43bd02; color: white")
                elif float(mProfit) > 0:
                    rst[4].setStyleSheet("background-color: darkGreen; color: white")
                elif float(mProfit) == 0:
                    rst[4].setStyleSheet("background-color: gray; color: white")
                elif float(mProfit) < -25:
                    rst[4].setStyleSheet("background-color: #420e01; color: white")
                elif float(mProfit) < -15:
                    rst[4].setStyleSheet("background-color: darkRed; color: white")
                else:
                    rst[4].setStyleSheet("background-color: Orange; color: white")

                rst[4].setText(str(round(mProfit, 2)) + "$   " + str(round((mProfit * 100) / firp, 2)) + "%")
                #rst[4].setText(str(round(mProfit, 2)) + "%    " + str(round(r_dict['c'][40], 2)) + "$")
                # tProfit = r_dict['c'][vaa-1] - r_dict['c'][0]
                #tProfit = ((r_dict['c'][vaa - 1] - r_dict['c'][0]) * 100) / r_dict['c'][vaa - 1]
                #
                time.sleep(.5)
                fir = pytz.UTC.localize(datetime.datetime(2099, 10, 20))
                las = pytz.UTC.localize(datetime.datetime(1967, 10, 20))
                firp = 0.00
                lasp = 0.00

                for row in ticker.history(period='90d').itertuples():
                    # print("7day close", row[0].strftime('%Y-%m-%d'), '%.4f' % row[4])
                    if row[0] > las:
                        las = row[0]
                        lasp = row[4]
                    if row[0] < fir:
                        fir = row[0]
                        firp = row[4]

                # print("first S", fir, firp)
                # print("last S", las, lasp)

                tProfit = round(lasp, 2) - round(firp, 2)

                #
                print("S", tProfit)
                if float(tProfit) > 15:
                    rst[5].setStyleSheet("background-color: #43bd02; color: white")
                elif float(tProfit) > 0:
                    rst[5].setStyleSheet("background-color: darkGreen; color: white")
                elif float(tProfit) == 0:
                    rst[5].setStyleSheet("background-color: gray; color: white")
                elif float(tProfit) < -25:
                    rst[5].setStyleSheet("background-color: #420e01; color: white")  # 420e01
                elif float(tProfit) < -15:
                    rst[5].setStyleSheet("background-color: darkRed; color: white")
                else:
                    rst[5].setStyleSheet("background-color: Orange; color: white")
                rst[5].setText(str(round(tProfit, 2)) + "$   " + str(round((tProfit * 100) / firp, 2)) + "%")

                # fir = pytz.UTC.localize(datetime.datetime(2099, 10, 20))
                # las = pytz.UTC.localize(datetime.datetime(1967, 10, 20))
                # firp = 0.00
                # lasp = 0.00
                min_value = 10000.00
                max_value = 0.00

                for row in ticker.history(period='1y').itertuples():
                    # print("7day close", row[0].strftime('%Y-%m-%d'), '%.4f' % row[4])

                    if row[4] > max_value:
                        #las = row[0]
                        max_value = row[4]
                    if row[4] < min_value:
                        #fir = row[0]
                        min_value = row[4]
                    last_row = row[4]

                print(min_value, max_value)
                print(last_row)
                # ilasp=int(lasp)
                # ifirp=int(firp)
                #
                # slasp=str(lasp)
                # sfirp=str(firp)
                #
                # print(ilasp, ifirp)

                # rst[5].setText(str(round(tProfit, 2)) + "%    " + str(round(r_dict['c'][0], 2)) + "$")
                #
                # # self.horizontalSlider(3,4,56)
                # # self.horizontalSlider.setTickInterval(10)
                # # print("///", min(r_dict['c']), max(r_dict['c']))
                #rst[8].setMinimum(min(ifirp))
                #rst[8].setMaximum(max(ilasp))
                # # # self.horizontalSlider.setRange(self, 23, 89)
                rst[6].setText(str(min_value) + " $")
                rst[7].setText(str(max_value) + " $")
                #rst[6].setText("1 $")
                #rst[7].setText("2 $")
                rst[8].setValue(last_row)

                #time.sleep(.5)
                print("Next")
            except Exception as eee:
                print("ERROR:", eee)
                pass
            # self.stopped = True
            #
            # if self.stopped == True:
            # return
    def populateWeekOLD(self, progress_callback):
        la = int(time.time())
        no = la - 7257000
        print(no, la)

        for rst in self.st:
            #if rst[0] == self.le1:
            symbol = rst[0].text()
            #sp = rst[0]
            #pc = rst[1]
            #wp = rst[3]

            print(">>", symbol)


            #le = datetime.datetime.now()
            #lee = le.timestamp()
            #print(la,  le, lee)

            #2419000 # 4 weeks
            #604800 # week
            #1210000 # 2 weeks
            #7257000 # 12 weeks


            URL = 'https://finnhub.io/api/v1/stock/candle?symbol=' + symbol + \
                  '&resolution=D&from='+ str(no) +\
                  '&to=' + str(la) +\
                  '&token=c0l9kd748v6orbr0vi90'

            r = requests.get(URL);
            r_dict = json.loads(r.text)
            print("..",r_dict)
            #print(len(r_dict['c']))
            if (r_dict['s'] != "no_data"):
                vaa = len(r_dict['c'])
                #print(r_dict['c'][vaa-1] ,r_dict['c'][0])

                #print(r_dict['c'][vaa - 1], r_dict['c'][53])
                #wProfit = r_dict['c'][vaa - 1] - r_dict['c'][53]
                try :
                    wProfit = ((r_dict['c'][vaa - 1] - r_dict['c'][53])*100)/ r_dict['c'][vaa - 1]
                    print("W", wProfit)
                    if float(wProfit) > 5:
                        rst[3].setStyleSheet("background-color: #43bd02; color: white")
                    elif float(wProfit) > 0:
                        rst[3].setStyleSheet("background-color: darkGreen; color: white")
                    elif float(wProfit) == 0:
                        rst[3].setStyleSheet("background-color: gray; color: white")
                    elif float(wProfit) < -25:
                        rst[3].setStyleSheet("background-color: #420e01; color: white")
                    elif float(wProfit) < -15:
                        rst[3].setStyleSheet("background-color: darkRed; color: white")
                    else:
                        rst[3].setStyleSheet("background-color: Orange; color: white")
                    rst[3].setText(str(round(wProfit, 2))+"%   "+str(round(r_dict['c'][53], 2))+"$")

                    time.sleep(.5)

                    #print(r_dict['c'][vaa - 1], r_dict['c'][40])
                    # mProfit = r_dict['c'][vaa-1] - r_dict['c'][40]
                    mProfit = ((r_dict['c'][vaa - 1] - r_dict['c'][40]) * 100) / r_dict['c'][vaa - 1]
                    print("M", mProfit)
                    if float(mProfit) > 10:
                        rst[4].setStyleSheet("background-color: #43bd02; color: white")
                    elif float(mProfit) > 0:
                        rst[4].setStyleSheet("background-color: darkGreen; color: white")
                    elif float(mProfit) == 0:
                        rst[4].setStyleSheet("background-color: gray; color: white")
                    elif float(mProfit) < -25:
                        rst[4].setStyleSheet("background-color: #420e01; color: white")
                    elif float(mProfit) < -15:
                        rst[4].setStyleSheet("background-color: darkRed; color: white")
                    else:
                        rst[4].setStyleSheet("background-color: Orange; color: white")
                    rst[4].setText(str(round(mProfit, 2)) + "%    " + str(round(r_dict['c'][40], 2)) + "$")
                    # tProfit = r_dict['c'][vaa-1] - r_dict['c'][0]
                    tProfit = ((r_dict['c'][vaa - 1] - r_dict['c'][0]) * 100) / r_dict['c'][vaa - 1]

                    time.sleep(.5)

                    print("T", tProfit)
                    if float(tProfit) > 15:
                        rst[5].setStyleSheet("background-color: #43bd02; color: white")
                    elif float(tProfit) > 0:
                        rst[5].setStyleSheet("background-color: darkGreen; color: white")
                    elif float(tProfit) == 0:
                        rst[5].setStyleSheet("background-color: gray; color: white")
                    elif float(tProfit) < -25:
                        rst[5].setStyleSheet("background-color: #420e01; color: white")  # 420e01
                    elif float(tProfit) < -15:
                        rst[5].setStyleSheet("background-color: darkRed; color: white")
                    else:
                        rst[5].setStyleSheet("background-color: Orange; color: white")
                    rst[5].setText(str(round(tProfit, 2)) + "%    " + str(round(r_dict['c'][0],2)) + "$")

                    #self.horizontalSlider(3,4,56)
                    # self.horizontalSlider.setTickInterval(10)
                    #print("///", min(r_dict['c']), max(r_dict['c']))
                    rst[8].setMinimum(min(r_dict['c']))
                    rst[8].setMaximum(max(r_dict['c']))
                    #self.horizontalSlider.setRange(self, 23, 89)
                    rst[6].setText(str(min(r_dict['c']))+"$")
                    rst[7].setText(str(max(r_dict['c']))+"$")
                    rst[8].setValue(r_dict['c'][vaa -1])

                    time.sleep(.5)
                except Exception as eee:
                    print("ERROR:", eee)
                    pass

        # self.stopped = True
        #
        # if self.stopped == True:
        #return

    def populateOne(self, progress_callback):

        total = 50
        for i in range(0, total):
            for rst in self.st:

                #self.insertData(rst[0], rst[1], rst[2])

                try:

                    symbol = rst[0].text()
                    print(rst[0].text())
                    URL = 'https://finnhub.io/api/v1/quote?symbol=' + symbol + '&token=c0l9kd748v6orbr0vi90'

                    r = requests.get(URL);
                    r_dict = json.loads(r.text)
                    # print(r_dict)
                    # c is change, pc is previous close price
                    print("1..", symbol, str(r_dict['c']), str(r_dict['pc']))
                    if (r_dict['c'] != 0 and  r_dict['pc'] != 0) :
                        dProfit = (float(r_dict['c'] - float(r_dict['pc'])) * 100) / float(r_dict['c'])

                        print("..", dProfit, str(round(dProfit,2)))
                        rst[1].setText(str(round(dProfit, 2)) + "%   " + str(r_dict['c']) + "$ ")
                        #time.sleep(.5)
                        rst[2].setText(str(r_dict['pc']) + "$")
                        time.sleep(.5)
                        if float(dProfit) > 3:
                            rst[1].setStyleSheet("background-color: #43bd02; color: white")
                        elif float(dProfit) > 0:
                            rst[1].setStyleSheet("background-color: darkGreen; color: white")
                        elif float(dProfit) == 0:
                            rst[1].setStyleSheet("background-color: gray; color: white")
                        elif float(dProfit) < -5:
                            rst[1].setStyleSheet("background-color: #420e01; color: white")  # 420e01
                        elif float(dProfit) < -3:
                            rst[1].setStyleSheet("background-color: darkRed; color: white")
                        else:
                            rst[1].setStyleSheet("background-color: Orange; color: white")

                        time.sleep(.5)
                except ConnectionError as ce:
                    print("Error:", ce)
                    pass

            if self.stopped == True:
                return
            else:
                time.sleep(300)

    def insertData(self, l, ll, lll):
        #if rst[0] == self.le1:
        symbol = l.text()
        # sp = ll
        # pc = lll

        try :
            print(symbol)
            URL = 'https://finnhub.io/api/v1/quote?symbol=' + symbol + '&token=c0l9kd748v6orbr0vi90'

            r = requests.get(URL);
            r_dict = json.loads(r.text)
            #print(r_dict)
            # c is change, pc is previous close price
            print("1..", symbol, str(r_dict['c']), str(r_dict['pc']))
            dProfit = (float(r_dict['c']-float(r_dict['pc']))*100)/float(r_dict['c'])

            ll.setText(str(round(dProfit,2))+ "%   "+str(r_dict['c'])+"$ ")
            lll.setText(str(r_dict['pc'])+"$")
            if float(dProfit) > 3:
                ll.setStyleSheet("background-color: #43bd02; color: white")
            elif float(dProfit) > 0:
                ll.setStyleSheet("background-color: darkGreen; color: white")
            elif float(dProfit) == 0:
                ll.setStyleSheet("background-color: gray; color: white")
            elif float(dProfit) < -5:
                ll.setStyleSheet("background-color: #420e01; color: white")  # 420e01
            elif float(dProfit) < -3:
                ll.setStyleSheet("background-color: darkRed; color: white")
            else:
                ll.setStyleSheet("background-color: Orange; color: white")

            time.sleep(.25)
        except ConnectionError as ce:
            print("Error:", ce)
            pass




# https://www.learnpyqt.com/courses/concurren
# t-execution/multithreading-pyqt-applications-qthreadpool/
class Worker(QtCore.QRunnable):
    """Worker thread for running background tasks."""
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.Slot()
    def run(self):
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class Worker2(QtCore.QRunnable):
    """Worker thread for running background tasks."""
    def __init__(self, fn, *args, **kwargs):
        super(Worker2, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @QtCore.Slot()
    def run(self):
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()

class WorkerSignals(QtCore.QObject):
    """
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
        No data
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        `object` data returned from processing, anything
    """
    # print("3 define signals for a running worker thread")
    finished = QtCore.Signal()
    error = QtCore.Signal(tuple)
    result = QtCore.Signal(object)
    progress = QtCore.Signal(int)





    # def connectMe(self):
    #     self.pushButton.clicked.connect(self.slotButton)
    #
    # def slotButton(self):
    #     self.label.setText("Hello from Badprog :D ")


if (__name__ == '__main__'):
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    default_palette = QPalette()
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)
    mainWindow = MainWindow()

    mainWindow.show()
    print("..")

    childAl = AlertsWindow()

    #childAl.show()

    sys.exit(app.exec_())