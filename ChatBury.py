

#  pyuic5 Ban.ui -o qtd3.py


#!/usr/bin/env python3
import sys
import time
import datetime
import traceback
import pytz
import yfinance as yf
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from qtd3 import Ui_MainWindow


# -------------------------------
# Worker Signals
# -------------------------------
class WorkerSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    result = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(object)


# -------------------------------
# Worker Thread
# -------------------------------
class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs["progress_callback"] = self.signals.progress

    @QtCore.pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


# -------------------------------
# Alerts Window
# -------------------------------
class AlertsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alerts")
        self.setFixedSize(600, 400)
        label = QtWidgets.QLabel("Alerts will appear here...", self)
        label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(label)


# -------------------------------
# Main Window
# -------------------------------
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Ban")
        self.threadpool = QtCore.QThreadPool()
        self.stopped = False

        # Connect buttons
        self.startButton.clicked.connect(self.run)
        self.stopButton.clicked.connect(self.stop)
        self.startButton_2.clicked.connect(self.populateWeek)
        self.radioButtonAlerts.clicked.connect(self.showAlerts)

        # Progress bar setup
        self.progressBar.setRange(0, 1)

        # Load stock symbols
        with open("stocksSymbols", "r") as fo:
            folist = [line.strip() for line in fo.readlines() if line.strip()]

        # Organize stock rows
        self.st = [
            [self.le1s, self.le1p, self.le1c, self.le1w, self.le1m, self.le1t, self.le1f, self.le1l, self.hs1],
            [self.le2s, self.le2p, self.le2c, self.le2w, self.le2m, self.le2t, self.le2f, self.le2l, self.hs2],
            [self.le3s, self.le3p, self.le3c, self.le3w, self.le3m, self.le3t, self.le3f, self.le3l, self.hs3],
            [self.le4s, self.le4p, self.le4c, self.le4w, self.le4m, self.le4t, self.le4f, self.le4l, self.hs4],
            [self.le5s, self.le5p, self.le5c, self.le5w, self.le5m, self.le5t, self.le5f, self.le5l, self.hs5],
            [self.le6s, self.le6p, self.le6c, self.le6w, self.le6m, self.le6t, self.le6f, self.le6l, self.hs6],
            [self.le7s, self.le7p, self.le7c, self.le7w, self.le7m, self.le7t, self.le7f, self.le7l, self.hs7],
            [self.le8s, self.le8p, self.le8c, self.le8w, self.le8m, self.le8t, self.le8f, self.le8l, self.hs8],
            [self.le9s, self.le9p, self.le9c, self.le9w, self.le9m, self.le9t, self.le9f, self.le9l, self.hs9],
            [self.le10s, self.le10p, self.le10c, self.le10w, self.le10m, self.le10t, self.le10f, self.le10l, self.hs10]
        ]

        for i, line in enumerate(folist[:len(self.st)]):
            self.st[i][0].setText(line)

        self.alertWindow = None

    # -------------------------------
    # Button Handlers
    # -------------------------------
    def showAlerts(self):
        if not self.alertWindow:
            self.alertWindow = AlertsWindow()
        self.alertWindow.show()

    def stop(self):
        self.stopped = True
        print("Stopping...")

    def completed(self):
        self.progressBar.setRange(0, 1)
        print("Completed background job")

    # -------------------------------
    # Main Data Worker: Daily Refresh
    # -------------------------------
    def run(self):
        self.stopped = False
        worker = Worker(self.populatePrices)
        worker.signals.progress.connect(self.updateUI)
        worker.signals.finished.connect(self.completed)
        self.threadpool.start(worker)
        self.progressBar.setRange(0, 0)  # show busy

    # -------------------------------
    # Background Function (Stock prices)
    # -------------------------------
    def populatePrices(self, progress_callback):
        while not self.stopped:
            for row in self.st:
                symbol = row[0].text().strip()
                if not symbol:
                    continue
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    data = ticker.history(period="2d")
                    if len(data) < 2:
                        continue

                    current_price = float(data["Close"].iloc[-1])
                    prev_close = float(data["Close"].iloc[-2])
                    change = ((current_price - prev_close) / prev_close) * 100

                    result = {
                        "symbol": symbol,
                        "price": current_price,
                        "prev": prev_close,
                        "change": change,
                    }
                    progress_callback.emit(result)
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")

            time.sleep(60)  # update every minute
        return "stopped"

    # -------------------------------
    # Update UI safely (from main thread)
    # -------------------------------
    @QtCore.pyqtSlot(object)
    def updateUI(self, result):
        symbol = result["symbol"]
        for row in self.st:
            if row[0].text().strip() == symbol:
                change = result["change"]
                color = "gray"
                if change > 3:
                    color = "#43bd02"
                elif change > 0:
                    color = "darkgreen"
                elif change == 0:
                    color = "gray"
                elif change < -5:
                    color = "#420e01"
                elif change < -3:
                    color = "darkred"
                else:
                    color = "orange"

                row[1].setStyleSheet(f"background-color: {color}; color: white;")
                row[1].setText(f"{result['change']:.2f}%   {result['price']:.2f}$")
                row[2].setText(f"{result['prev']:.2f}$")
                break

    # -------------------------------
    # One-Time Weekly Data Fetch
    # -------------------------------
    def populateWeek(self):
        worker = Worker(self.calcWeekly)
        worker.signals.progress.connect(self.updateWeek)
        self.threadpool.start(worker)

    def calcWeekly(self, progress_callback):
        for row in self.st:
            symbol = row[0].text().strip()
            if not symbol:
                continue
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1mo")
                if data.empty:
                    continue

                start = float(data["Close"].iloc[0])
                end = float(data["Close"].iloc[-1])
                diff = end - start
                pct = (diff / start) * 100

                result = {"symbol": symbol, "diff": diff, "pct": pct}
                progress_callback.emit(result)
            except Exception as e:
                print(f"Error (weekly) {symbol}: {e}")
        return "done"

    @QtCore.pyqtSlot(object)
    def updateWeek(self, result):
        symbol = result["symbol"]
        for row in self.st:
            if row[0].text().strip() == symbol:
                diff = result["diff"]
                pct = result["pct"]
                color = "gray"
                if pct > 5:
                    color = "#43bd02"
                elif pct > 0:
                    color = "darkgreen"
                elif pct == 0:
                    color = "gray"
                elif pct < -15:
                    color = "darkred"
                else:
                    color = "orange"

                row[3].setStyleSheet(f"background-color: {color}; color: white;")
                row[3].setText(f"{diff:.2f}$   {pct:.2f}%")
                break


# -------------------------------
# Run the Application
# -------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.Text, Qt.white)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QtGui.QPalette.BrightText, Qt.red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
