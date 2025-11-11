#  pyuic5 Ban.ui -o qtd3.py

#!/usr/bin/env python3
import sys
import datetime
import pytz
import yfinance as yf
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from qtd3 import Ui_MainWindow


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

        self.stopped = True
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_prices)

        # Connect buttons
        self.startButton.clicked.connect(self.start_updates)
        self.stopButton.clicked.connect(self.stop_updates)
        self.startButton_2.clicked.connect(self.populate_week_month)
        self.radioButtonAlerts.clicked.connect(self.show_alerts)

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

        # Populate symbols
        for i, line in enumerate(folist[:len(self.st)]):
            self.st[i][0].setText(line)

        self.alertWindow = None

    # -------------------------------
    # Button Handlers
    # -------------------------------
    def show_alerts(self):
        if not self.alertWindow:
            self.alertWindow = AlertsWindow()
        self.alertWindow.show()

    def start_updates(self):
        self.stopped = False
        self.progressBar.setRange(0, 0)  # busy indicator
        self.timer.start(60 * 1000)  # update every 60 seconds
        self.update_prices()  # immediate update

    def stop_updates(self):
        self.stopped = True
        self.timer.stop()
        self.progressBar.setRange(0, 1)
        print("Updates stopped.")

    # -------------------------------
    # Update Prices (non-threaded)
    # -------------------------------
    def update_prices(self):
        if self.stopped:
            return

        for row in self.st:
            symbol = row[0].text().strip()
            if not symbol:
                continue
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="2d")
                if len(data) < 2:
                    continue

                current_price = float(data["Close"].iloc[-1])
                prev_close = float(data["Close"].iloc[-2])
                change = ((current_price - prev_close) / prev_close) * 100

                self.update_ui(symbol, current_price, prev_close, change)
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")

    # -------------------------------
    # Update UI safely
    # -------------------------------
    def update_ui(self, symbol, price, prev, change):
        for row in self.st:
            if row[0].text().strip() == symbol:
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
                row[1].setText(f"{change:.2f}%   {price:.2f}$")
                row[2].setText(f"{prev:.2f}$")
                break

    # -------------------------------
    # Weekly & Monthly Updates
    # -------------------------------
    def populate_week_month(self):
        for row in self.st:
            symbol = row[0].text().strip()
            if not symbol:
                continue
            try:
                ticker = yf.Ticker(symbol)

                # Weekly (last 1 month)
                data_week = ticker.history(period="1mo")
                if not data_week.empty:
                    start = float(data_week["Close"].iloc[0])
                    end = float(data_week["Close"].iloc[-1])
                    diff = end - start
                    pct_week = (diff / start) * 100
                    self.update_week_ui(symbol, diff, pct_week)
                else:
                    self.update_week_ui(symbol, 0, 0)

                # Monthly (last 3 months)
                data_month = ticker.history(period="3mo")
                if not data_month.empty:
                    start_m = float(data_month["Close"].iloc[0])
                    end_m = float(data_month["Close"].iloc[-1])
                    diff_m = end_m - start_m
                    pct_month = (diff_m / start_m) * 100
                    self.update_month_ui(symbol, diff_m, pct_month)
                else:
                    self.update_month_ui(symbol, 0, 0)

            except Exception as e:
                print(f"Error updating {symbol}: {e}")

    def update_week_ui(self, symbol, diff, pct):
        for row in self.st:
            if row[0].text().strip() == symbol:
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

    def update_month_ui(self, symbol, diff, pct):
        for row in self.st:
            if row[0].text().strip() == symbol:
                color = "gray"
                if pct > 10:
                    color = "#43bd02"
                elif pct > 0:
                    color = "darkgreen"
                elif pct == 0:
                    color = "gray"
                elif pct < -20:
                    color = "darkred"
                else:
                    color = "orange"

                row[4].setStyleSheet(f"background-color: {color}; color: white;")
                row[4].setText(f"{diff:.2f}$   {pct:.2f}%")
                break


# -------------------------------
# Main Application
# -------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
