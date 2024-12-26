from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QGridLayout, QMenu, QComboBox, QPushButton
from PyQt5.QtCore import QTimer, QDateTime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from datetime import datetime


class MplCanvas(FigureCanvas):
    def __init__(self):
        fig, ax = plt.subplots(1)
        self.fig = fig
        fig.patch.set_facecolor('black')
        self.ax = ax
        ax.set_facecolor('xkcd:grey')
        plt.rcParams.update({'font.size': 16, 'text.color': 'white'})
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.tick_params(color='white', labelcolor='white')
        self.fig.set_tight_layout(True)

        FigureCanvas.__init__(self, self.fig)
        self.setFixedSize(600, 300)



class PlotWindow(QDialog):
    def __init__(self, fname):
        super(PlotWindow, self).__init__()
        self.populate()
        self.show_plot(fname)

    def populate(self):
        self.setWindowTitle("Temperature plot")
        self.canvas = MplCanvas()
        self.nav = NavigationToolbar(self.canvas, self)
        '''Changed nav toolbar'''

        self.layout = QGridLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.nav)
        self.layout.addWidget(self.canvas)

        self.setLayout(self.layout)
        width = self.canvas.width()
        height = self.nav.height() + self.canvas.height()
        self.setFixedSize(width, height)

    def show_plot(self, fname):
        self.canvas.ax.set_facecolor('xkcd:pinkish grey')
        f = np.loadtxt(fname, str, delimiter = ',')
        temp = np.array([float(elt) for elt in f[:, 1]])
        def format_time(t_str):
            words = str.split(t_str)
            return datetime.strptime(words[0] + " " + words[1], "%Y-%m-%d %H:%M:%S")
        ts = np.array([format_time(elt) for elt in f[:, 0]])
        self.canvas.ax.plot(ts, temp, 'k')
        self.canvas.draw()
        
