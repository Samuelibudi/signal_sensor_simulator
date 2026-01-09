import sys
import serial
import serial.tools.list_ports
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QGroupBox, QLineEdit, 
                             QLabel, QComboBox, QPushButton, QDialog, QFormLayout, QDialogButtonBox)
from PyQt6.QtCore import Qt
import pyqtgraph as pg

class SignalSimulator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sensor Signal Simulator - UI Design")
        self.resize(1200, 800)

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # --- UPPER HALF: DISPLAY ---
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#0a0a0a')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Amplitude', units='V')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        
        self.curve = self.plot_widget.plot(pen=pg.mkPen(color='#00ffcc', width=1.5))
        self.main_layout.addWidget(self.plot_widget, stretch=3)

        # --- LOWER HALF: CONTROLS ---
        self.controls_container = QHBoxLayout()

        # Group 1: Signal Parameters
        self.param_group = QGroupBox("Signal Parameters")
        self.param_layout = QGridLayout()

        self.param_layout.addWidget(QLabel("Waveform:"), 0, 0)
        self.wave_type = QComboBox()
        self.wave_type.addItems(["Sine", "Square", "Sawtooth", "Triangle","Custom"])
        self.param_layout.addWidget(self.wave_type, 0, 1)

        self.param_layout.addWidget(QLabel("Frequency (Hz):"), 1, 0)
        self.freq_input = QLineEdit("10.0")
        self.param_layout.addWidget(self.freq_input, 1, 1)

        self.param_layout.addWidget(QLabel("Amplitude (V):"), 2, 0)
        self.amp_input = QLineEdit("1.0")
        self.param_layout.addWidget(self.amp_input, 2, 1)
        
        self.param_group.setLayout(self.param_layout)

        # Group 2: Noise Settings
        self.noise_group = QGroupBox("Noise Profile")
        self.noise_layout = QGridLayout()

        self.noise_layout.addWidget(QLabel("Noise Type:"), 0, 0)
        self.noise_type = QComboBox()
        self.noise_type.addItems(["Gaussian White", "Pink Noise", "Brownian", "None"])
        self.noise_layout.addWidget(self.noise_type, 0, 1)

        self.noise_layout.addWidget(QLabel("SNR (dB):"), 1, 0)
        self.snr_input = QLineEdit("20.0")
        self.noise_layout.addWidget(self.snr_input, 1, 1)

        self.noise_layout.addWidget(QLabel("Sample Rate (Hz):"), 2, 0)
        self.fs_input = QLineEdit("1000")
        self.noise_layout.addWidget(self.fs_input, 2, 1)

        self.noise_group.setLayout(self.noise_layout)

        # Group 3: Serial Port Configuration (MODIFIED FOR MANUAL TYPING)
        self.serial_group = QGroupBox("Serial Communication")
        self.serial_layout = QGridLayout()

        self.serial_layout.addWidget(QLabel("Port Path:"), 0, 0)
        # CHANGED: Using QLineEdit instead of QComboBox
        self.port_input = QLineEdit("/dev/pts/") 
        self.port_input.setPlaceholderText("e.g. /dev/pts/2 or COM3")
        self.serial_layout.addWidget(self.port_input, 0, 1)

        self.serial_layout.addWidget(QLabel("Baudrate:"), 1, 0)
        self.baud_selector = QComboBox()
        self.baud_selector.addItems(["9600", "115200", "230400", "921600"])
        self.baud_selector.setCurrentText("115200")
        self.serial_layout.addWidget(self.baud_selector, 1, 1)

        # Added a status label for connection feedback
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: #aaaaaa; font-style: italic;")
        self.serial_layout.addWidget(self.status_label, 2, 0, 1, 2)

        self.connect_btn = QPushButton("Connect")
        self.serial_layout.addWidget(self.connect_btn, 3, 0, 1, 2)

        self.serial_group.setLayout(self.serial_layout)

        # Add groups to layout
        self.controls_container.addWidget(self.param_group)
        self.controls_container.addWidget(self.noise_group)
        self.controls_container.addWidget(self.serial_group)

        # Action Buttons
        self.button_layout = QVBoxLayout()
        self.run_button = QPushButton("START SIMULATION")
        self.run_button.setMinimumHeight(60)
        self.run_button.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")
        
        self.reset_button = QPushButton("RESET PLOT")
        self.reset_button.setMinimumHeight(40)
        self.reset_button.setStyleSheet("background-color: #424242; color: white;")

        self.export_button = QPushButton("Export Data (CSV)")
        self.button_layout.addWidget(self.reset_button)
        self.button_layout.addWidget(self.run_button)
        self.button_layout.addWidget(self.export_button)
        
        self.controls_container.addLayout(self.button_layout)
        self.main_layout.addLayout(self.controls_container, stretch=1)

class FourierDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Fourier Coefficients")
        layout = QFormLayout(self)

        self.a_input = QLineEdit("0, 0, 0")
        self.b_input = QLineEdit("1, 0.33, 0.2") 
        
        layout.addRow("a_k (Cosines, comma separated):", self.a_input)
        layout.addRow("b_k (Sines, comma separated):", self.b_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def get_coeffs(self):
        a = [float(x.strip()) for x in self.a_input.text().split(",")]
        b = [float(x.strip()) for x in self.b_input.text().split(",")]
        return a, b

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = SignalSimulator()
    window.show()
    sys.exit(app.exec())