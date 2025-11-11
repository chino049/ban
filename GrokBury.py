#!/usr/bin/env python3
import sys
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSignal, QObject
from PyQt5.QtGui import QPalette, QColor
import yfinance as yf
from qtd3 import Ui_MainWindow  # From Qt Designer


# -------------------------------
# Worker Signals
# -------------------------------
class WorkerSignals(QObject):
    price_result = pyqtSignal(str, float, float, float)  # symbol, price, prev, change
    wms_result = pyqtSignal(str, float, float, float, float, float, float)  # symbol, w_diff, w_pct, m_diff, m_pct, s_diff, s_pct
    finished = pyqtSignal()


# -------------------------------
# Price Update Worker
# -------------------------------
class PriceUpdateWorker(QRunnable):
    def __init__(self, stock_rows):
        super().__init__()
        self.stock_rows = stock_rows
        self.signals = WorkerSignals()

    def run(self):
        for row in self.stock_rows:
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
                self.signals.price_result.emit(symbol, current_price, prev_close, change)
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
        self.signals.finished.emit()


# -------------------------------
# W/M/S Update Worker
# -------------------------------
class WMSUpdateWorker(QRunnable):
    def __init__(self, stock_rows):
        super().__init__()
        self.stock_rows = stock_rows
        self.signals = WorkerSignals()

    def run(self):
        for row in self.stock_rows:
            symbol = row[0].text().strip()
            if not symbol:
                continue
            try:
                ticker = yf.Ticker(symbol)

                # Weekly (1mo)
                data_w = ticker.history(period="1mo")
                w_diff = w_pct = 0
                if not data_w.empty:
                    start = float(data_w["Close"].iloc[0])
                    end = float(data_w["Close"].iloc[-1])
                    w_diff = end - start
                    w_pct = (w_diff / start) * 100

                # Monthly (3mo)
                data_m = ticker.history(period="3mo")
                m_diff = m_pct = 0
                if not data_m.empty:
                    start = float(data_m["Close"].iloc[0])
                    end = float(data_m["Close"].iloc[-1])
                    m_diff = end - start
                    m_pct = (m_diff / start) * 100

                # Semester (6mo)
                data_s = ticker.history(period="6mo")
                s_diff = s_pct = 0
                if not data_s.empty:
                    start = float(data_s["Close"].iloc[0])
                    end = float(data_s["Close"].iloc[-1])
                    s_diff = end - start
                    s_pct = (s_diff / start) * 100

                self.signals.wms_result.emit(symbol, w_diff, w_pct, m_diff, m_pct, s_diff, s_pct)
            except Exception as e:
                print(f"Error updating {symbol}: {e}")
        self.signals.finished.emit()


# -------------------------------
# Alerts Window
# -------------------------------
class AlertsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alerts")
        self.setFixedSize(600, 400)
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { 
                background-color: #2d2d2d; 
                color: #00ff00; 
                font-size: 11pt;
                font-weight: bold;
            }
            QListWidget::item { padding: 8px; }
        """)
        self.setCentralWidget(self.list_widget)

    def add_alert(self, text):
        self.list_widget.addItem(text)
        self.list_widget.scrollToBottom()


# -------------------------------
# Main Window
# -------------------------------
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Ban - Stock Monitor")

        self.stopped = True
        self.populating_wms = False
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.trigger_price_update)
        self.threadpool = QThreadPool()

        # Connect buttons
        self.startButton.clicked.connect(self.start_updates)
        self.stopButton.clicked.connect(self.stop_updates)
        self.startButton_2.clicked.connect(self.populate_week_month_semester)
        self.radioButtonAlerts.clicked.connect(self.show_alerts)

        # Progress bar
        self.progressBar.setRange(0, 1)
        self.progressBar.setTextVisible(False)

        # Tooltips
        self.startButton.setToolTip("Start live updates (every 60s)")
        self.stopButton.setToolTip("Stop updates")
        self.startButton_2.setToolTip("Load weekly, monthly, semester data")

        # Load symbols
        self.load_stock_symbols()

        # Organize rows
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
        for i, symbol in enumerate(self.symbols):
            if i < len(self.st):
                self.st[i][0].setText(symbol)

        self.alertWindow = None

    def load_stock_symbols(self):
        try:
            with open("stocksSymbols", "r") as f:
                self.symbols = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN"]
            print("stocksSymbols not found. Using default symbols.")

    # -------------------------------
    # Button Handlers
    # -------------------------------
    def show_alerts(self):
        if not self.alertWindow:
            self.alertWindow = AlertsWindow()
        self.alertWindow.show()
        self.alertWindow.raise_()
        self.alertWindow.activateWindow()

    def start_updates(self):
        if not self.stopped:
            return
        self.stopped = False
        self.progressBar.setRange(0, 0)
        self.timer.start(60 * 1000)
        self.trigger_price_update()

    def stop_updates(self):
        self.stopped = True
        self.timer.stop()
        self.progressBar.setRange(0, 1)
        print("Updates stopped.")

    def trigger_price_update(self):
        if self.stopped:
            return
        worker = PriceUpdateWorker(self.st)
        worker.signals.price_result.connect(self.handle_price_update)
        worker.signals.finished.connect(self.price_update_finished)
        self.threadpool.start(worker)

    def price_update_finished(self):
        if not self.stopped:
            self.progressBar.setRange(0, 1)

    def handle_price_update(self, symbol, price, prev, change):
        for row in self.st:
            if row[0].text().strip() == symbol:
                # Update BUTTON background color based on change
                self.update_button_color(row[8], change)

                # Update PRICE text: always white, bold
                row[1].setStyleSheet("color: white; font-weight: bold;")
                row[1].setText(f"{change:+.2f}%   {price:.2f}$")

                # Update PREVIOUS close
                row[2].setText(f"{prev:.2f}$")

                # Alert if >5%
                if abs(change) > 5:
                    self.add_alert(f"ALERT: {symbol} {change:+.2f}%!")

                break

    def populate_week_month_semester(self):
        if self.populating_wms:
            return
        self.populating_wms = True
        self.startButton_2.setEnabled(False)
        self.startButton_2.setText("Loading...")

        worker = WMSUpdateWorker(self.st)
        worker.signals.wms_result.connect(self.handle_wms_update)
        worker.signals.finished.connect(self.wms_update_finished)
        self.threadpool.start(worker)

    def handle_wms_update(self, symbol, w_diff, w_pct, m_diff, m_pct, s_diff, s_pct):
        for row in self.st:
            if row[0].text().strip() == symbol:
                # Week
                color = self.get_change_color(w_pct)
                row[3].setStyleSheet(f"color: {color};")
                row[3].setText(f"{w_diff:+.2f}$   {w_pct:+.2f}%")

                # Month
                color = self.get_change_color(m_pct)
                row[4].setStyleSheet(f"color: {color};")
                row[4].setText(f"{m_diff:+.2f}$   {m_pct:+.2f}%")

                # Semester
                color = self.get_change_color(s_pct)
                row[5].setStyleSheet(f"color: {color};")
                row[5].setText(f"{s_diff:+.2f}$   {s_pct:+.2f}%")
                break

    def wms_update_finished(self):
        self.startButton_2.setEnabled(True)
        self.startButton_2.setText("Update W/M/S")
        self.populating_wms = False

    # -------------------------------
    # UI Helpers
    # -------------------------------
    def get_change_color(self, change):
        if change > 3:
            return "#00ff00"  # Lime green
        elif change > 0:
            return "#00cc00"  # Dark green
        elif change == 0:
            return "white"
        elif change < -5:
            return "#ff0000"  # Red
        elif change < -3:
            return "#cc0000"  # Dark red
        else:
            return "#ffaa00"  # Orange

    def update_button_color(self, button, change):
        """Set button background color based on price change. Text always white."""
        styles = {
            "lime":     "background-color: #00ff00; color: white; border-radius: 8px; font-weight: bold; padding: 6px;",
            "green":    "background-color: #00cc00; color: white; border-radius: 8px; font-weight: bold; padding: 6px;",
            "white":    "background-color: #333333; color: white; border-radius: 8px; padding: 6px;",
            "red":      "background-color: #ff0000; color: white; border-radius: 8px; font-weight: bold; padding: 6px;",
            "darkred":  "background-color: #cc0000; color: white; border-radius: 8px; font-weight: bold; padding: 6px;",
            "orange":   "background-color: #ffaa00; color: white; border-radius: 8px; font-weight: bold; padding: 6px;"
        }

        if change > 3:
            style = styles["lime"]
        elif change > 0:
            style = styles["green"]
        elif change == 0:
            style = styles["white"]
        elif change < -5:
            style = styles["red"]
        elif change < -3:
            style = styles["darkred"]
        else:
            style = styles["orange"]

        button.setStyleSheet(style)

    def add_alert(self, text):
        if not self.alertWindow:
            self.show_alerts()
        self.alertWindow.add_alert(text)


# -------------------------------
# Main Application
# -------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    # Dark palette
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(45, 45, 45))
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

    # Global style
    app.setStyleSheet("""
        QPushButton { 
            padding: 8px 16px; 
            border-radius: 6px; 
            font-weight: bold;
            min-width: 80px;
        }
        QPushButton:disabled { 
            background-color: #555; 
            color: #aaa; 
        }
        QLabel { 
            font-size: 10pt; 
        }
        QProgressBar {
            border: 1px solid #555;
            border-radius: 5px;
            text-align: center;
            height: 20px;
        }
        QProgressBar::chunk {
            background-color: #42a5f5;
            border-radius: 4px;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())