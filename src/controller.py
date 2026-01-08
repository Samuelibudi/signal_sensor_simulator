import sys
import time
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
import serial

# Import our custom modules
from frontend import SignalSimulator
from engine import SignalEngine

class SignalController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        
        # Initialize View and Model
        self.view = SignalSimulator()
        self.engine = SignalEngine()
        
        # Internal State
        self.serial_connection = None
        self.data_buffer = []  # To keep track of points for the plot
        
        # Timer for the simulation loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_loop)
        
        # Connect UI Signals to Controller Methods
        self.setup_connections()

    def setup_connections(self):
        """Links the frontend buttons to controller logic."""
        self.view.run_button.clicked.connect(self.toggle_simulation)
        self.view.connect_btn.clicked.connect(self.toggle_serial)
        self.view.reset_button.clicked.connect(self.reset_simulation)
        # Note: 'refresh_btn' and 'get_available_ports' are handled 
        # internally by the view as they are UI-specific.

    def toggle_simulation(self):
        if not self.timer.isActive():
            try:
                # Calculate interval based on Sample Rate (Hz)
                fs = float(self.view.fs_input.text())
                interval_ms = int(1000 / fs)
                
                self.timer.start(interval_ms)
                self.view.run_button.setText("STOP SIMULATION")
                self.view.run_button.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
            except ValueError:
                QMessageBox.warning(self.view, "Input Error", "Invalid Sample Rate.")
        else:
            self.timer.stop()
            self.view.run_button.setText("START SIMULATION")
            self.view.run_button.setStyleSheet("background-color: #2e7d32; color: white; font-weight: bold;")

    def toggle_serial(self):
        if self.serial_connection is None or not self.serial_connection.is_open:
            try:
                port = self.view.port_selector.currentText()
                baud = int(self.view.baud_selector.currentText())
                self.serial_connection = serial.Serial(port, baud, timeout=0)
                
                self.view.connect_btn.setText("Disconnect")
                self.view.connect_btn.setStyleSheet("background-color: #ffa000;")
            except Exception as e:
                QMessageBox.critical(self.view, "Serial Error", f"Failed to connect: {e}")
        else:
            self.serial_connection.close()
            self.view.connect_btn.setText("Connect")
            self.view.connect_btn.setStyleSheet("")

    def process_loop(self):
        """The main simulation heartbeat."""
        try:
            # 1. Gather parameters from UI
            params = {
                'wave_type': self.view.wave_type.currentText(),
                'freq': float(self.view.freq_input.text()),
                'amp': float(self.view.amp_input.text()),
                'noise_type': self.view.noise_type.currentText(),
                'snr': float(self.view.snr_input.text()),
                'fs': float(self.view.fs_input.text())
            }

            # 2. Generate point from Engine
            t, val = self.engine.generate_point(**params)

            # 3. Update UI Plot (Rolling window of 200 points)
            self.data_buffer.append(val)
            if len(self.data_buffer) > 200:
                self.data_buffer.pop(0)
            self.view.curve.setData(self.data_buffer)

            # 4. Stream to Serial
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.write(f"{val:.4f}\n".encode('ascii'))

        except ValueError:
            pass # Ignore malformed numeric inputs during typing

    def reset_simulation(self):
        """Clears the data buffers and resets the simulation step counter."""
        # 1. Clear the internal data buffers
        self.data_buffer = []
        self.time_buffer = []

        # 2. Reset the engine's internal step counter to 0
        # This ensures the math starts at t=0 exactly
        self.engine.current_step = 0 

        # 3. Clear the visual plot immediately
        self.view.curve.setData([], [])

        # 4. Stop the timer if it's currently running
        if self.timer.isActive():
            self.toggle_simulation()

    def run(self):
        self.view.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = SignalController()
    controller.run()