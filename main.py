from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QFileDialog, QTableWidgetItem, QMessageBox, QWidget, QPushButton, 
    QHBoxLayout, QVBoxLayout, 
    QGroupBox, 
    QSizePolicy,
    QHeaderView, 
)

from PyQt5.QtGui import QImage, QPixmap, QColor, QIcon

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from GUI import Ui_MainWindow 

import numpy as np 
import sys
from scipy.stats import norm
import numpy as np 


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):

        super(MyMainWindow, self).__init__(parent)
        QMainWindow.__init__(self, parent)

        # this creates the UI and places all the widgets as placed in QtDesigner
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Title and dark theme
        self.setWindowTitle("System simulation")
        self.setStyleSheet('background-color: #333; color: white;')



        # System Attributes & callbacks 
        self.xmin = None 
        self.xmax = None 
        self.a = None 
        self.b = None 
        self.u = None 
        self.v = None 
        self.system_type = None 
        self.canvas_system = None  # the mpl widget we will add 
        

        # Noise Attributes 
        self.std = None 
        self.mean = None 
        self.min = None 
        self.max = None 
        self.noise = None
        self.noise_type = None 
    
        self.canvas_noise_freq = None 
        self.canvas_noise_hist = None 


        # Synthetic Data attributes 
        self.canvas_syntData = None
        # ...

        # Resulsts Attributes 
        # ... 
    

        self.ui.btn_plot_system.clicked.connect(self.callback_plot_system)
        self.ui.btn_plot_noise.clicked.connect(self.callback_plot_noise)
        self.ui.btn_plot_synData.clicked.connect(self.calback_plot_synt_data)


    def _rm_plot(self, window=None): 

        _window2layout = {
            1:self.ui.verticalLayout_1,
            2:self.ui.verticalLayout_2,
            6:self.ui.verticalLayout_6,
            8:self.ui.verticalLayout_8,
        }
        

        _window2canvas = {
            1:self.canvas_system,
            2:self.canvas_syntData,
            6:self.canvas_noise_freq,
            8:self.canvas_noise_hist,
        }


        layout = _window2layout[window]
        canvas = _window2canvas[window]

        
        if(canvas is not None): 
            layout.removeWidget(canvas)
            canvas.close()
        




# ====== for linear system ===========

    def _plot_linaer_system(self): 
        try:
            # generate linear system 
            xmin = float(self.ui.lineEdit_xmin.text())
            xmax = float(self.ui.lineEdit_xmax.text())
            a = self.ui.slider_a.value()
            b = self.ui.slider_b.value()

            self.x = np.linspace(xmin, xmax, 1000)
            self.y = a * self.x + b
            
            # plot the linear system 
            fig = Figure()
            self.canvas_system = FigureCanvas(fig)

            self.ui.verticalLayout_1.addWidget(self.canvas_system)

            ax = fig.add_subplot(111)

            ax.plot(self.x, self.y, label=f"y = {a}x + {b}")

            ax.set_title('Linear system')
            ax.set_xlabel("x", fontsize=14)
            ax.set_ylabel("y", fontsize=14)
            ax.legend()

            self.canvas_system.draw()
        except Exception: 
                print('Exception occured : ', Exception)

    def _plot_exponential_system(self): 
        try:
            # Get parameters from UI
            xmin = float(self.ui.lineEdit_xmin.text())
            xmax = float(self.ui.lineEdit_xmax.text())
            u = self.ui.slider_u.value()
            v = self.ui.slider_v.value()

            self.x = np.linspace(xmin, xmax, 1000)
            self.y = u * np.exp(v * self.x)
            

            fig = Figure()
            self.canvas_system = FigureCanvas(fig)
            self.ui.verticalLayout_1.addWidget(self.canvas_system)

            ax = fig.add_subplot(111)
            ax.plot(self.x, self.y, label=f"y = {u} * exp({v} * x)")

            # Set titles and labels
            ax.set_title('Exponential system')
            ax.set_xlabel("x", fontsize=14)
            ax.set_ylabel("y", fontsize=14)
            ax.legend()

            # Redraw the canvas
            self.canvas_system.draw()

        except Exception as e:
            print('Exception occurred:', e)

    def callback_plot_system(self): 

        self._rm_plot(window=1)
        type = self.ui.combo_System.currentText()

        type2func = {
            'linear': self._plot_linaer_system,
            'exponential': self._plot_exponential_system, 
        }

        type2func[type]()




# ========= for the noise ===== 

    def _plot_noise_fft(self): 
        try:
            # Assuming self.noise is a NumPy array
            noise = self.noise
            
            # Perform FFT on the noise signal
            noise_fft = np.fft.fft(noise)
            
            # Calculate the corresponding frequencies
            sample_rate = 1  # Modify as per your actual sample rate if needed
            freqs = np.fft.fftfreq(len(noise), d=sample_rate)
            
            # Only take the positive frequencies (since FFT is symmetric)
            positive_freqs = freqs[:len(freqs)//2]
            positive_fft = noise_fft[:len(noise_fft)//2]

            # Plot the FFT of the noise signal
            fig = Figure()
            self.canvas_noise_freq = FigureCanvas(fig)

            self.ui.verticalLayout_6.addWidget(self.canvas_noise_freq)

            ax = fig.add_subplot(111)
            ax.plot(positive_freqs, np.abs(positive_fft))

            ax.set_title('FFT of Noise Signal')
            ax.set_xlabel('Frequency (Hz)', fontsize=14)
            ax.set_ylabel('Magnitude', fontsize=14)
            ax.grid(True)

            self.canvas_noise_freq.draw()
            
        except Exception as e:
            print(f"Exception occurred: {e}")

    def _plot_gaussian_noise(self): 
        try:
            # Get parameters from the UI (mean and standard deviation for the Gaussian noise)
            mean = float(self.ui.lineEdit_mean.text())
            std = float(self.ui.lineEdit_std.text())
            xmin = float(self.ui.lineEdit_xmin.text())
            xmax = float(self.ui.lineEdit_xmax.text())
            
            # Generate Gaussian noise with mean and standard deviation
            self.noise = np.random.normal(mean, std, size=1000)  # 1000 samples for better histogram resolution


            # Create a new figure for the histogram
            fig = Figure()
            self.canvas_noise_hist = FigureCanvas(fig)

            # Add the canvas to the layout
            self.ui.verticalLayout_8.addWidget(self.canvas_noise_hist)

            # Create a subplot for plotting the histogram
            ax = fig.add_subplot(111)

            # Plot the histogram of the Gaussian noise
            ax.hist(self.noise, bins=30, density=True, alpha=0.6, label="Gaussian Noise")

            # Overlay the Gaussian PDF
            xmin_gauss = np.min(self.noise)
            xmax_gauss = np.max(self.noise)
            x_gauss = np.linspace(xmin_gauss, xmax_gauss, 100)
            pdf_gauss = norm.pdf(x_gauss, mean, std)
            
            # Overlay the Gaussian distribution on the histogram
            ax.plot(x_gauss, pdf_gauss, label=f"Gaussian PDF\nMean: {mean}, Std: {std}", color='r', linewidth=2)

            # Set titles and labels
            ax.set_title('Gaussian Noise Distribution')
            ax.set_xlabel("Value", fontsize=14)
            ax.set_ylabel("Density", fontsize=14)
            ax.legend()

            # Redraw the canvas
            self.canvas_noise_hist.draw()

        except Exception as e:
            print('Exception occurred:', e)     
       
    def _plot_uniform_noise(self): 
        try:
            # Get parameters from the UI (min and max values for the uniform noise)
            min_value = float(self.ui.lineEdit_min.text())
            max_value = float(self.ui.lineEdit_max.text())
            
            # Generate uniform noise between min_value and max_value
            self.noise = np.random.uniform(min_value, max_value, size=1000)  # 1000 samples for better visibility

            # Create a new figure for the plot
            fig = Figure()
            self.canvas_noise_hist = FigureCanvas(fig)

            # Add the canvas to the layout
            self.ui.verticalLayout_8.addWidget(self.canvas_noise_hist)

            # Create a subplot for plotting the noise values
            ax = fig.add_subplot(111)

            # Plot the uniform noise values as a line plot (no histogram)
            ax.plot(self.noise, label="Uniform Noise", lw=1)

            # Set titles and labels
            ax.set_title('Uniform Noise Values')
            ax.set_xlabel("Sample Index", fontsize=14)
            ax.set_ylabel("Noise Value", fontsize=14)
            ax.legend()

            # Redraw the canvas
            self.canvas_noise_hist.draw()

        except Exception as e:
            print('Exception occurred:', e)

    def callback_plot_noise(self): 
        self._rm_plot(window=6)
        self._rm_plot(window=8)

        type = self.ui.combo_noise.currentText()

        type2func = {
            'gaussian': self._plot_gaussian_noise,
            'uniform': self._plot_uniform_noise, 
        }

        type2func[type]()
        self._plot_noise_fft()
        



# ============ for synt data ===============
    def calback_plot_synt_data(self): 

        debug = True
        self._rm_plot(window=2)


        try:
            # Assuming self.x, self.y, and self.noise are NumPy arrays
            x = self.x
            y = self.y
            noise = self.noise

            if (debug): 
                print('x shape:', x.shape)
                print('y.shape:', y.shape)
                print('noise.shape:', noise.shape)
            
            # Create noisy data by adding noise to the signal
            noisy_data = y + noise

            if (debug): 
                print('noisy_data[0]: ', noisy_data[0])
                print('y[0]:', y[0])
                print('x[0]: ', x[0])
                print('noise[0]: ', noise[0])
            
            # Plot the noisy data
            fig = Figure()
            self.canvas_syntData = FigureCanvas(fig)

            self.ui.verticalLayout_2.addWidget(self.canvas_syntData)

            ax = fig.add_subplot(111)
            ax.plot(x, noisy_data, label="Noisy data: y + noise")

            ax.set_title('Noisy Data (y + noise)')
            ax.set_xlabel('x', fontsize=14)
            ax.set_ylabel('y + noise', fontsize=14)
            ax.legend()

            self.canvas_syntData.draw()

        except Exception as e:
            print(f"Exception occurred: {e}")   



    def _update_window(self): 


        systype2func = { 
            'linear': self._plot_linaer_system, 
            'exponentai':self._plot_exponential_system , 
        }

        noisetype2func = {
            'gaussian':self._plot_gaussian_noise, 
            'uniform': self._plot_uniform_noise,

        }


        system_type = self.ui.combo_System.currentData()
        noise_type = self.ui.combo_noise.currentData()


        systype2func[system_type]()
        noisetype2func[noise_type]()


        # TODO: 
        # - refactor the callback_synt_data to two functions using an internatl method 
        # - create a github repo 


        

        





if __name__ == '__main__':

    from warnings import filterwarnings
    filterwarnings("ignore", category=DeprecationWarning)

    # To avoid weird behaviors (smaller items, ...) on big resolution screens
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


    app = QApplication(sys.argv)
    app.setStyle("fusion")
    # app.setWindowIcon(QtGui.QIcon(':icons/health.png'))

    def quit_app(): 
        print('Bye...')
        sys.exit(app.exec_())
    
    window = MyMainWindow()
    window.show()
    quit_app()







  