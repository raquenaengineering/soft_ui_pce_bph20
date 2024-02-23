

import sys
import time
import logging


logging.basicConfig(level = logging.WARNING)


# qt imports #
from PyQt5.QtWidgets import (
	QApplication,
	QMainWindow,
	QVBoxLayout,
	QHBoxLayout,
	QLabel,
	QComboBox,
	QLineEdit,
	QPushButton,
	QMenuBar,
	QToolBar,
	QStatusBar,
	QDialog,
	QFileDialog,
	QMessageBox,														# Dialog with extended functionality.
	QShortcut,
	QCheckBox,

	QSystemTrayIcon,
	QTextEdit,
	QMenu,
	QAction,
	QWidget
)

from PyQt5 import *

from PyQt5.QtGui import (
	QIcon,
	QKeySequence,
	QColor,
	QFont
)

from PyQt5.QtCore import(
	Qt,
	QThreadPool,
	QRunnable,
	QObject,
	QSize,
	pyqtSignal,															# those two are pyqt specific.
	pyqtSlot,
	QTimer																# nasty stuff
)

import pyqtgraph as pg


from soft_lib_pce_bph20.pce_bph20 import pce_bph20
import config


class pce_bph20_widget(QWidget):
	def __init__(self, log_window=False):
		super().__init__()

		logging.debug("ph_meter_widget")

		self.max_points_plot = 100
		self.plot_title_size = "9pt"

		# connection to ph meter #
		self.ph_meter = pce_bph20()
		self.ph_meter.enable_data_logging()  # special message needs to be sent to start data logging
		self.ph_meter.start_collecting_data()
		time.sleep(1)  # give some time to the device to start collecting data

		# timers #

		# timer to get data #
		self.timer_read_ph_meter = QTimer()
		self.timer_read_ph_meter.setInterval(1000)
		self.timer_read_ph_meter.timeout.connect(self.get_ph_meter_data)
		self.timer_read_ph_meter.start()

		# # timer to update plot #
		# self.timer_update_plots_and_vals = QTimer()
		# self.timer_update_plots_and_vals.setInterval(1000)
		# self.timer_update_plots_and_vals.timeout.connect(self.update_plots_and_vals)
		# self.timer_update_plots_and_vals.start()

		# data structures for plots and so on #
		self.data_plot_ph = []
		self.data_plot_ec = []
		self.data_plot_temp = []
		self.data_plot_timestamp = []


		# LAYOUT #

		# general top layout #
		self.layout_main = QVBoxLayout()
		self.setLayout(self.layout_main)

		# value display #
		self.layout_values = QHBoxLayout()
		self.layout_main.addLayout(self.layout_values)


		# ph related #
		self.layout_ph_val = QVBoxLayout()
		self.layout_values.addLayout(self.layout_ph_val)

		self.label_ph_name = QLabel("PH VAL:")
		self.layout_ph_val.addWidget(self.label_ph_name)

		self.label_ph_val = QLabel("---")
		self.layout_ph_val.addWidget(self.label_ph_val)


		# EC related #
		self.layout_ec_val = QVBoxLayout()
		self.layout_values.addLayout(self.layout_ec_val)

		self.label_ec_name = QLabel("EC VAL:")
		self.layout_ec_val.addWidget(self.label_ec_name)

		self.label_ec_val = QLabel("---")
		self.layout_ec_val.addWidget(self.label_ec_val)


		# temp related #
		self.layout_temp_val = QVBoxLayout()
		self.layout_values.addLayout(self.layout_temp_val)

		self.label_temp_name = QLabel("TEMP VAL:")
		self.layout_temp_val.addWidget(self.label_temp_name)

		self.label_temp_val = QLabel("---")
		self.layout_temp_val.addWidget(self.label_temp_val)

		# plots #
		self.layout_plots = QVBoxLayout()
		self.layout_main.addLayout(self.layout_plots)



		# plot nozzle feed pressure #

		self.plot_ph = pg.PlotWidget()
		self.plot_ph.setBackground('w')
		self.plot_ph.setXRange(0,self.max_points_plot)
		self.plot_ph.setYRange(-0.1, 14.1)
		self.plot_ph.setLimits(xMin=0, xMax=self.max_points_plot ,yMin=-0.1, yMax=14.5)
		self.plot_ph.setTitle("PH Val", size = self.plot_title_size)

		self.layout_plots.addWidget(self.plot_ph)


		self.plot_ec = pg.PlotWidget()
		self.plot_ec.setBackground('w')
		self.plot_ec.setXRange(0,self.max_points_plot)
		self.plot_ec.setLimits(xMin=0, xMax=self.max_points_plot, yMin = -10, yMax = 2010)
		self.plot_ec.setTitle("EC Val (uS/cm)", size = self.plot_title_size)

		self.layout_plots.addWidget(self.plot_ec)

		self.plot_temp = pg.PlotWidget()
		self.plot_temp.setBackground('w')
		self.plot_temp.setXRange(0,self.max_points_plot)
		self.plot_temp.setLimits(xMin=0, xMax=self.max_points_plot, yMin=-1, yMax = 51)
		self.plot_temp.setTitle("Temp. Value (°C)", size = self.plot_title_size)

		self.layout_plots.addWidget(self.plot_temp)



		self.pen_g = pg.mkPen(color = 'g')
		self.pen_r = pg.mkPen(color = 'r')
		self.pen_b = pg.mkPen(color = 'b')


		self.data_line_ph = self.plot_ph.plot(self.data_plot_timestamp, self.data_plot_ph, pen = self.pen_g)
		self.data_line_ec = self.plot_ec.plot(self.data_plot_timestamp, self.data_plot_ec, pen = self.pen_r)
		self.data_line_temp = self.plot_temp.plot(self.data_plot_timestamp, self.data_plot_temp, pen = self.pen_b)

	# ui related methods #



	def get_ph_meter_data(self):

		timestamp, data_vals = self.ph_meter.get_sensor_data()
		ph,potential,temp,ec = data_vals
		print("ph:")
		print(ph)
		print("potential:")
		print(potential)
		print("ec:")
		print(ec)
		print("temp:")
		print(temp)

		# update labels #

		max_plot_points = config.max_plot_points

		self.label_ph_val.setText(str(ph))
		self.label_ec_val.setText(str(ec))
		self.label_temp_val.setText(str(temp))

		self.data_plot_ph.append(ph)
		self.data_plot_ec.append(ec)
		self.data_plot_temp.append(temp)

		x_len = len(self.data_plot_temp)
		self.data_plot_timestamp = range(x_len)
		# self.data_plot_timestamp(str(timestamp))

		# update plots #

		self.data_line_ph.setData(self.data_plot_timestamp, self.data_plot_ph)
		self.data_line_ec.setData(self.data_plot_timestamp, self.data_plot_ec)
		self.data_line_temp.setData(self.data_plot_timestamp, self.data_plot_temp)






class MainWindow(QMainWindow):

	# constructor #
	def __init__(self):

		super().__init__()

		self.setWindowIcon(QIcon("media/theion_logo_10mm.png"))

		# self.print_timer = QTimer()  # we'll use timer instead of thread
		# self.print_timer.timeout.connect(self.add_incoming_lines_to_log)
		# self.print_timer.start(LOG_WINDOW_REFRESH_PERIOD_MS)  # period needs to be relatively short

		#self.widget = QWidget()
		self.ph_meter_widget = pce_bph20_widget()
		self.setCentralWidget(self.ph_meter_widget)
		# stylesheet, so I don't get blind with tiny characters #
		self.sty = "QWidget {font-size: 10pt}"
		self.setStyleSheet(self.sty)
		self.setWindowTitle("pce_bph20 widget")

		font = self.font()
		font.setPointSize(24)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle("Fusion")  # required to use it here
	window = MainWindow()
	window.show()
	app.exec_()