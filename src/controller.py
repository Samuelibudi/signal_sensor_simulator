import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
import serial

# Import our custom modules
from frontend import SignalSimulator, FourierDialog
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
        self.data_buffer = []  
        self.time_buffer = [] # Initialize here to be safe
        
        # Timer for the simulation loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_loop)
        
        # Fourier State
        self.custom_a = [0.0]
        self.custom_b = [1.0]
        
        # Connect UI Signals
        self.setup_connections()

    def setup_connections(self):
        """Links the frontend widgets to controller logic."""
        self.view.run_button.clicked.connect(self.toggle_simulation)
        self.view.connect_btn.clicked.connect(self.toggle_serial)
        self.view.reset_button.clicked.connect(self.reset_simulation)
        self.view.wave_type.currentTextChanged.connect(self.handle_wave_change)

    def handle_wave_change(self, text):
        if text == "Custom":
            dialog = FourierDialog(self.view)
            if dialog.exec():
                self.custom_a, self.custom_b = dialog.get_coeffs()
            else:
                self.view.wave_type.setCurrentIndex(0) 

    def toggle_simulation(self):
        if not self.timer.isActive():
            try:
                fs = float(self.view.fs_input.text())
                # Ensure interval is at least 1ms to prevent GUI freeze
                interval_ms = max(1, int(1000 / fs))
                
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
        """Modified to use manual text input from QLineEdit."""
        if self.serial_connection is None or not self.serial_connection.is_open:
            # 1. Get port path and baudrate from the new UI fields
            port = self.view.port_input.text().strip()
            try:
                baud = int(self.view.baud_selector.currentText())
                
                # 2. Attempt connection
                # timeout=0.1 prevents the UI from locking up if the port is non-responsive
                self.serial_connection = serial.Serial(port, baud, timeout=0.1)
                
                self.view.connect_btn.setText("Disconnect")
                self.view.connect_btn.setStyleSheet("background-color: #ffa000;")
                self.view.status_label.setText(f"Status: Connected to {port}")
                self.view.status_label.setStyleSheet("color: #00ffcc; font-style: normal; font-weight: bold;")
                
            except Exception as e:
                self.view.status_label.setText("Status: Connection Failed")
                self.view.status_label.setStyleSheet("color: #ff5555; font-style: normal;")
                QMessageBox.critical(self.view, "Serial Error", f"Failed to connect to {port}:\n{e}")
        else:
            # 3. Handle Disconnection
            self.serial_connection.close()
            self.serial_connection = None
            self.view.connect_btn.setText("Connect")
            self.view.connect_btn.setStyleSheet("")
            self.view.status_label.setText("Status: Disconnected")
            self.view.status_label.setStyleSheet("color: #aaaaaa; font-style: italic;")

    def process_loop(self):
        """The main simulation heartbeat."""
        try:
            wave_type = self.view.wave_type.currentText()
            f0 = float(self.view.freq_input.text() or 0)
            amp = float(self.view.amp_input.text() or 0)
            snr = float(self.view.snr_input.text() or 0)
            fs = float(self.view.fs_input.text() or 1)
            noise_type = self.view.noise_type.currentText()

            if wave_type == "Custom":
                t, val = self.engine.generate_fourier_point(
                    f0, amp, self.custom_a, self.custom_b, fs
                )
                val = self.engine._apply_noise(val, amp, noise_type, snr)
            else:
                t, val = self.engine.generate_point(
                    wave_type, f0, amp, noise_type, snr, fs
                )

            self.data_buffer.append(val)
            self.time_buffer.append(t)

            if len(self.data_buffer) > 1000:
                self.data_buffer.pop(0)
                self.time_buffer.pop(0)

            self.view.curve.setData(self.time_buffer, self.data_buffer)

            # Stream data
            if self.serial_connection and self.serial_connection.is_open:
                try:
                    self.serial_connection.write(f"{val:.4f}\n".encode('ascii'))
                except serial.SerialTimeoutException:
                    pass # Buffer full or port slow

        except (ValueError, ZeroDivisionError):
            pass 

    def reset_simulation(self):
        self.data_buffer = []
        self.time_buffer = []
        self.engine.current_step = 0 
        self.view.curve.setData([], [])
        if self.timer.isActive():
            self.toggle_simulation()

    def run(self):
        self.view.show()
        sys.exit(self.app.exec())

if __name__ == "__main__":
    controller = SignalController()
    controller.run()