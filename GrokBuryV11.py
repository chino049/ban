#!/usr/bin/env python3
import sys
import time
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from datetime import time as dtime
import pandas as pd
from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt, QThreadPool, QRunnable, pyqtSignal, QObject
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QStyle, QTableWidgetItem, QHeaderView
import yfinance as yf
from qtd3 import Ui_MainWindow

# ----------------------------------------------------------------------
# Worker signals (only price and movers now)
# ----------------------------------------------------------------------
class WorkerSignals(QObject):
    price_result = pyqtSignal(str, float, float, float)  # sym, price, prev, %change
    movers = pyqtSignal(list)
    finished = pyqtSignal()

# ----------------------------------------------------------------------
# Safe yfinance wrapper
# ----------------------------------------------------------------------
def safe_history(ticker, **kwargs):
    for _ in range(3):
        try:
            return ticker.history(**kwargs)
        except Exception as e:
            print(f"yfinance retry: {e}")
            time.sleep(random.uniform(0.5, 1.5))
    return pd.DataFrame()

# ----------------------------------------------------------------------
# Price-update worker (unchanged)
# ----------------------------------------------------------------------
class PriceUpdateWorker(QRunnable):
    def __init__(self, rows):
        super().__init__()
        self.rows = rows
        self.signals = WorkerSignals()

    def run(self):
        now = datetime.now()
        print("Running current price...", now.strftime("%Y-%m-%d %I:%M:%S %p"))
        for row in self.rows:
            sym = row[0].text().strip()
            if not sym: continue
            try:
                time.sleep(.5)
                t = yf.Ticker(sym)
                d = safe_history(t, period="2d", interval="1d")
                if len(d) < 2:
                    print("ERROR: 83 ", sym, d)
                    continue
                price = float(d["Close"].iloc[-1])
                prev = float(d["Close"].iloc[-2])
                change = ((price - prev) / prev) * 100
                print("..", sym, price, prev, change)
                self.signals.price_result.emit(sym, price, prev, change)
            except Exception as e:
                print(f"Price error {sym}: {e}")
        self.signals.finished.emit()

# ----------------------------------------------------------------------
# Top Movers worker (unchanged)
# ----------------------------------------------------------------------
class TopMoversWorker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    def _load_symbols(self):
        default = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN"]
        try:
            with open("stocksSymbols", "r") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            return lines if lines else default
        except FileNotFoundError:
            return default
        except Exception as e:
            print(f"TopMovers: error reading symbols: {e}")
            return default

    def run(self):
        symbols = self._load_symbols()
        records = []
        print(f"TopMovers: fetching {len(symbols)} symbols...")
        for sym in symbols:
            try:
                t = yf.Ticker(sym)
                d = safe_history(t, period="2d", interval="1d")
                if len(d) < 2: continue
                price = float(d["Close"].iloc[-1])
                prev = float(d["Close"].iloc[-2])
                pct = ((price - prev) / prev) * 100
                records.append(dict(sym=sym, price=price, pct=pct))
                time.sleep(0.12)
            except Exception as e:
                print(f"TopMovers error {sym}: {e}")
                continue
        records.sort(key=lambda x: x['pct'], reverse=True)
        top_10 = records[:10]
        self.signals.movers.emit(top_10)
        self.signals.finished.emit()

# ----------------------------------------------------------------------
# Alerts & Movers windows (unchanged)
# ----------------------------------------------------------------------
class AlertsWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alerts")
        self.setFixedSize(600, 400)
        self.lst = QtWidgets.QListWidget()
        self.lst.setStyleSheet(
            "QListWidget {background:#2d2d2d; color:#00ff00; font-weight:bold;}"
            "QListWidget::item {padding:6px;}"
        )
        self.clear_btn = QtWidgets.QPushButton("Clear")
        self.clear_btn.clicked.connect(self.lst.clear)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.lst)
        layout.addWidget(self.clear_btn)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def add(self, txt):
        self.lst.addItem(txt)
        self.lst.scrollToBottom()

class TopMoversWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Top 10 Movers (Gainers)")
        self.setFixedSize(460, 380)
        self.table = QtWidgets.QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Symbol", "Price $", "% Change"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setStyleSheet(
            "QTableWidget {background:#2d2d2d; color:#e0e0e0; gridline-color:#444;}"
            "QTableWidget::item {padding:4px;}"
            "QHeaderView::section {background:#555; color:white; font-weight:bold;}"
        )
        self.refresh_btn = QtWidgets.QPushButton("Refresh Now")
        self.refresh_btn.clicked.connect(self.manual_refresh)
        lay = QtWidgets.QVBoxLayout()
        lay.addWidget(self.table)
        lay.addWidget(self.refresh_btn, alignment=Qt.AlignRight)
        container = QtWidgets.QWidget()
        container.setLayout(lay)
        self.setCentralWidget(container)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.manual_refresh)

    def start_auto(self):
        self.manual_refresh()
        self.timer.start(120_000)

    def stop_auto(self):
        self.timer.stop()

    def manual_refresh(self):
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("Loading...")
        worker = TopMoversWorker()
        worker.signals.movers.connect(self.display_movers)
        worker.signals.finished.connect(self.refresh_done)
        QThreadPool.globalInstance().start(worker)

    def display_movers(self, records):
        self.table.setRowCount(0)
        for rec in records:
            row = self.table.rowCount()
            self.table.insertRow(row)
            sym_item = QTableWidgetItem(rec['sym'])
            price_item = QTableWidgetItem(f"{rec['price']:.2f}")
            pct_item = QTableWidgetItem(f"{rec['pct']:+.2f}%")
            color = "#00ff00" if rec['pct'] > 0 else "#ff0000"
            pct_item.setForeground(QtGui.QColor(color))
            pct_item.setFont(QFont("Consolas", 10, QFont.Bold))
            self.table.setItem(row, 0, sym_item)
            self.table.setItem(row, 1, price_item)
            self.table.setItem(row, 2, pct_item)

    def refresh_done(self):
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("Refresh Now")

# ----------------------------------------------------------------------
# Main Window – MODIFIED SECTION
# ----------------------------------------------------------------------
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Ban – Stock Monitor")
        self.stopped = True
        self.wms_busy = False
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.trigger_price_update)
        self.pool = QThreadPool()
        self.run_once = "yes"
        self.countdown = 300
        self.countdown_timer = QtCore.QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start(1000)

        # ---- FLASHING ----
        self.semester_pct = {}
        self.flash_state = False
        self.flash_timer = QtCore.QTimer()
        self.flash_timer.timeout.connect(self._flash_step)
        self.flash_timer.start(500)

        # ---- control buttons ----
        self.startButton.clicked.connect(self.start_updates)
        self.stopButton.clicked.connect(self.stop_updates)
        self.startButton_2.clicked.connect(self.populate_week_month_semester)  # ← Now single-loop
        self.radioButtonAlerts.clicked.connect(self.show_alerts)
        self.radioButton.clicked.connect(self.show_movers)

        self.progressBar.setRange(0, 1)
        self.progressBar.setTextVisible(False)
        self.startButton.setToolTip("Start live updates (every 60 s)")
        self.stopButton.setToolTip("Stop updates")
        self.startButton_2.setToolTip("Load week / month / semester data")

        self.load_symbols()

        # ---- ROWS (9 widgets: s, p, c, w, m, t, f, l, hs) ----
        self.rows = [
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
            [self.le20s, self.le20p, self.le20c, self.le20w, self.le20m, self.le20t, self.le20f, self.le20l, self.hs20],
        ]

        # Center-align
        for row in self.rows:
            for w in row[1:6]:
                w.setAlignment(Qt.AlignCenter)

        # Clear fields
        for row in self.rows:
            try:
                for i in range(1, 6): row[i].setText("")
            except IndexError: pass

        # Fill symbols
        for i, s in enumerate(self.symbols):
            if i < len(self.rows):
                self.rows[i][0].setText(s)

        self.alert_win = None
        self.movers_win = None
        self.update_countdown()

    # ------------------------------------------------------------------
    # NEW: Single-loop W/M/S update (replaces worker)
    # ------------------------------------------------------------------
    def populate_week_month_semester(self):
        if self.wms_busy:
            return
        self.wms_busy = True
        self.startButton_2.setEnabled(False)
        self.startButton_2.setText("Loading...")

        def run_wms():
            for row in self.rows:
                sym = row[0].text().strip()
                if not sym:
                    continue
                try:
                    t = yf.Ticker(sym)
                    info = t.info
                    price = info.get("regularMarketPrice", 0.0)
                    high_52 = info.get("fiftyTwoWeekHigh", 0.0)
                    low_52 = info.get("fiftyTwoWeekLow", 0.0)

                    # --- Helper to get % change for any period ---
                    def get_change(period):
                        d = safe_history(t, period=period, interval="1d")
                        if len(d) >= 2:
                            start = float(d["Close"].iloc[0])
                            end = float(d["Close"].iloc[-1])
                            if start != 0:
                                return end - start, (end - start) / start * 100
                        return 0.0, 0.0

                    w_d, w_p = get_change("7d")
                    m_d, m_p = get_change("1mo")
                    s_d, s_p = get_change("6mo")

                    # Update UI
                    QtCore.QMetaObject.invokeMethod(self, "_update_wms_row",
                        Qt.QueuedConnection,
                        QtCore.Q_ARG(str, sym),
                        QtCore.Q_ARG(float, w_d), QtCore.Q_ARG(float, w_p),
                        QtCore.Q_ARG(float, m_d), QtCore.Q_ARG(float, m_p),
                        QtCore.Q_ARG(float, s_d), QtCore.Q_ARG(float, s_p),
                        QtCore.Q_ARG(float, high_52), QtCore.Q_ARG(float, low_52),
                        QtCore.Q_ARG(float, price)
                    )
                    time.sleep(0.3)  # Be gentle
                except Exception as e:
                    print(f"WMS local error {sym}: {e}")

            QtCore.QMetaObject.invokeMethod(self, "_wms_done", Qt.QueuedConnection)

        # Run in thread
        worker = QRunnable.create(run_wms)
        self.pool.start(worker)

    @QtCore.pyqtSlot(str, float, float, float, float, float, float, float, float, float)
    def _update_wms_row(self, sym, w_d, w_p, m_d, m_p, s_d, s_p, h52, l52, price):
        for r in self.rows:
            if r[0].text().strip() != sym: continue
            # Weekly
            color = self.get_color(w_p)
            r[3].setStyleSheet(f"color:{color}; font-weight:bold;")
            r[3].setText(f"{w_d:+.2f}$ {w_p:+.2f}%")
            # Monthly
            color = self.get_color(m_p)
            r[4].setStyleSheet(f"color:{color}; font-weight:bold;")
            r[4].setText(f"{m_d:+.2f}$ {m_p:+.2f}%")
            # Semester
            color = self.get_color(s_p)
            r[5].setStyleSheet(f"color:{color}; font-weight:bold;")
            r[5].setText(f"{s_d:+.2f}$ {s_p:+.2f}%")
            self.semester_pct[sym] = s_p  # For flashing
            # 52W
            r[6].setText(f"{l52:.2f}")
            r[7].setText(f"{h52:.2f}")
            r[8].setMinimum(int(l52))
            r[8].setMaximum(int(h52))
            r[8].setValue(int(price))
            break

    @QtCore.pyqtSlot()
    def _wms_done(self):
        self.startButton_2.setEnabled(True)
        self.startButton_2.setText("Update W/M/S")
        self.wms_busy = False

    # ------------------------------------------------------------------
    # Flashing (unchanged, safe)
    # ------------------------------------------------------------------
    def _flash_step(self):
        self.flash_state = not self.flash_state
        target = QColor("white") if self.flash_state else QColor("black")
        for row in self.rows:
            if len(row) < 6: continue
            sym = row[0].text().strip()
            if not sym: continue
            pct = self.semester_pct.get(sym, 0.0)
            le_sem = row[5]
            if pct > 20 or pct < -20:
                pal = le_sem.palette()
                pal.setColor(QPalette.Base, target)
                le_sem.setPalette(pal)
            else:
                le_sem.setPalette(QtWidgets.QApplication.palette())

    # ------------------------------------------------------------------
    # Rest of your methods (unchanged): load_symbols, closeEvent, etc.
    # ------------------------------------------------------------------
    def load_symbols(self):
        default = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA", "AMZN"]
        try:
            with open("stocksSymbols", "r") as f:
                lines = [ln.strip() for ln in f if ln.strip()]
            self.symbols = lines if lines else default
        except FileNotFoundError:
            self.symbols = default
            print("stocksSymbols not found – using defaults")
        except Exception as e:
            self.symbols = default
            print(f"Error reading symbols: {e}")

    def closeEvent(self, event):
        try:
            with open("stocksSymbols", "w") as f:
                for row in self.rows:
                    sym = row[0].text().strip()
                    if sym:
                        f.write(sym + "\n")
        except Exception as e:
            print(f"Failed to save symbols: {e}")
        super().closeEvent(event)

    def update_countdown(self):
        if not self.stopped:
            self.statusBar().showMessage(f"Next update in {self.countdown}s")
            self.countdown -= 1
            if self.countdown < 0:
                self.countdown = 300

    def show_alerts(self):
        if not self.alert_win:
            self.alert_win = AlertsWindow()
            self.alert_win.show()
            self.alert_win.raise_()
            self.alert_win.activateWindow()

    def show_movers(self):
        if not self.movers_win:
            self.movers_win = TopMoversWindow()
            if not self.stopped:
                self.movers_win.start_auto()
            self.movers_win.show()
            self.movers_win.raise_()
            self.movers_win.activateWindow()

    def start_updates(self):
        if not self.stopped: return
        self.stopped = False
        self.progressBar.setRange(0, 0)
        self.countdown = 60
        self.timer.start(300_000)
        self.trigger_price_update()
        if self.movers_win:
            self.movers_win.start_auto()

    def stop_updates(self):
        self.stopped = True
        self.timer.stop()
        self.countdown_timer.stop()
        self.progressBar.setRange(0, 1)
        self.statusBar().showMessage("Updates stopped")
        if self.movers_win:
            self.movers_win.stop_auto()

    def trigger_price_update(self):
        if self.stopped: return
        ny_tz = ZoneInfo("America/New_York")
        now_est_weekends = datetime.now(ny_tz)
        now_est = datetime.now(ZoneInfo("America/New_York"))
        current_time = now_est.time()
        start_time = dtime(9, 30)
        end_time = dtime(16, 0)

        #print("start and end times", start_time, end_time)
        if not (start_time <= current_time <= end_time) and now_est_weekends.weekday() >= 5:
            #print("Market is closed")
            mins_left = int((datetime.combine(now_est.date(), start_time) - datetime.combine(now_est.date(), current_time)).total_seconds() / 60)
            #print("mins left", mins_left)
            if mins_left > 0:
                print(f"Waiting for market open... Next update in ~{mins_left} min")
                self.statusBar().showMessage(f"Waiting for market open... Next update in ~{mins_left} min")
            else:
                mins_until_tomorrow = int((datetime.combine(now_est.date(), start_time) - datetime.combine(now_est.date(), current_time) + timedelta(days=1)).total_seconds() / 60)
                print(f"Market closed. Next update in ~{mins_until_tomorrow} min")
                self.statusBar().showMessage(f"Market closed. Next update in ~{mins_until_tomorrow} min")

            if self.run_once == "yes":
                if self.alert_win: self.alert_win.lst.clear()
                self.countdown = 120
                self.statusBar().showMessage("Updating prices... (Market closed but running once only)")
                print("Updating prices... (Market closed but running once only)")

                w = PriceUpdateWorker(self.rows)
                w.signals.price_result.connect(self.handle_price)
                w.signals.finished.connect(self.price_done)
                self.pool.start(w)
                self.run_once = "no"
            return
        else:
            print("st and et", start_time, end_time)

        if self.alert_win: self.alert_win.lst.clear()
        self.countdown = 120
        self.statusBar().showMessage("Updating prices... (Market Open)")
        w = PriceUpdateWorker(self.rows)
        w.signals.price_result.connect(self.handle_price)
        w.signals.finished.connect(self.price_done)
        self.pool.start(w)

    def price_done(self):
        if not self.stopped:
            self.progressBar.setRange(0, 1)
            now_est = datetime.now(ZoneInfo("America/New_York"))
            if dtime(6, 0) <= now_est.time() <= dtime(13, 0):
                self.timer.start(120_000)
            else:
                print("Market closed. Updates paused until 9:30 AM EST.")
                self.statusBar().showMessage("Market closed. Updates paused until 9:30 AM EST.")

    def handle_price(self, sym, price, prev, change):
        for row in self.rows:
            if row[0].text().strip() != sym: continue
            self.set_button_bg(row[1], change)
            row[1].setToolTip(f"Prev: {prev:.2f} | Change: {change:+.2f}%")
            row[1].setText(f"{change:+.2f}% {price:.2f}$")
            row[2].setText(f"{prev:.2f}$")
            if abs(change) > 5:
                self.add_alert(f"ALERT: {sym} {change:+.2f}%!")
            break

    def get_color(self, pct):
        if pct > 3: return "#00ff00"
        if pct > 0: return "#00cc00"
        if pct == 0: return "white"
        if pct < -5: return "#ff0000"
        if pct < -3: return "#cc0000"
        return "#ffaa00"

    def set_button_bg(self, btn, pct):
        styles = {
            "lime": "background:#00ff00; color:white; border-radius:8px; padding:6px; font-weight:bold;",
            "green": "background:#00cc00; color:white; border-radius:8px; padding:6px; font-weight:bold;",
            "gray": "background:#333333; color:white; border-radius:8px; padding:6px;",
            "red": "background:#ff0000; color:white; border-radius:8px; padding:6px; font-weight:bold;",
            "darkred": "background:#cc0000; color:white; border-radius:8px; padding:6px; font-weight:bold;",
            "orange": "background:#ffaa00; color:white; border-radius:8px; padding:6px; font-weight:bold;",
        }
        key = ("lime" if pct > 3 else "green" if pct > 0 else "gray" if pct == 0 else "red" if pct < -5 else "darkred" if pct < -3 else "orange")
        btn.setStyleSheet(styles[key])

    def add_alert(self, txt):
        if not self.alert_win:
            self.show_alerts()
        if self.alert_win.lst.count() == 0:
            now = datetime.now(ZoneInfo("America/Los_Angeles"))
            header = f"── NEW ALERTS ── {now.strftime('%I:%M:%S %p')} ──"
            header_item = QtWidgets.QListWidgetItem(header)
            header_item.setForeground(QtGui.QColor("#8888ff"))
            header_item.setFont(QFont("Consolas", 9, QFont.Bold))
            header_item.setTextAlignment(Qt.AlignCenter)
            self.alert_win.lst.addItem(header_item)
        try:
            pct = float(txt.split()[-1].rstrip('%!'))
        except:
            pct = 0
        item = QtWidgets.QListWidgetItem(txt)
        if pct <= -5:
            item.setForeground(QtGui.QColor("#ff0033"))
            item.setBackground(QtGui.QColor(50, 0, 0))
        elif pct >= 5:
            item.setForeground(QtGui.QColor("#00ff00"))
            item.setBackground(QtGui.QColor(0, 40, 0))
        else:
            item.setForeground(QtGui.QColor("#ffaa00"))
        font = QFont("Consolas", 10, QFont.Bold)
        item.setFont(font)
        self.alert_win.lst.addItem(item)
        self.alert_win.lst.scrollToBottom()

# ----------------------------------------------------------------------
# App entry
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    p = QPalette()
    p.setColor(QPalette.Window, QColor(45, 45, 45))
    p.setColor(QPalette.WindowText, Qt.white)
    p.setColor(QPalette.Base, QColor(25, 25, 25))
    p.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    p.setColor(QPalette.ToolTipBase, Qt.white)
    p.setColor(QPalette.ToolTipText, Qt.white)
    p.setColor(QPalette.Text, Qt.white)
    p.setColor(QPalette.Button, QColor(53, 53, 53))
    p.setColor(QPalette.ButtonText, Qt.white)
    p.setColor(QPalette.BrightText, Qt.red)
    p.setColor(QPalette.Link, QColor(42, 130, 218))
    p.setColor(QPalette.Highlight, QColor(42, 130, 218))
    p.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(p)
    app.setStyleSheet("""
        QPushButton { padding:8px 16px; border-radius:6px; font-weight:bold; min-width:80px; }
        QPushButton:disabled { background:#555; color:#aaa; }
        QProgressBar { border:1px solid #555; border-radius:5px; text-align:center; height:20px; }
        QProgressBar::chunk { background:#42a5f5; border-radius:4px; }
        QLabel { font-size:10pt; }
    """)
    win = MainWindow()
    win.setMinimumSize(1400, 1000)
    win.resize(1000, 720)
    screen = app.primaryScreen().availableGeometry()
    win.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, win.size(), screen))
    win.show()
    sys.exit(app.exec_())