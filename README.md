SIGNAL & SENSOR SIMULATOR: TECHNICAL DOCUMENTATION

1. Project Overview

This software is a high-fidelity Python-based tool designed for research and industrial sensor emulation. It utilizes a Model-View-Controller (MVC) architecture to generate periodic waveforms, synthesize custom signals via Fourier Series, and inject controlled noise for testing data processing pipelines.

2. System Architecture

The project is divided into three functional layers:

> Engine (Model): Handles the mathematical computation of signal points and noise application using high-precision NumPy floats.

> Frontend (View): A PyQt6-based graphical interface that provides real-time data visualization via PyQtGraph.

> Controller: Manages the simulation heartbeat, synchronizes data buffers, and handles Serial I/O communication.

3. Mathematical Methodology

3.1 Temporal Integrity
To prevent "jagged" waveforms and temporal aliasing, the simulator rejects the system wall-clock. Instead, it uses a discrete step-counter logic:

                                 t = n/F_s

Where:

n: The current sample index (integer counter).
F_s: The user-defined Sampling Rate (Hz).

3.2 Fourier Synthesis (Custom Waves)

The custom wave engine implements the Trigonometric Fourier Series:

x(t) = \sum_{k=1}^{N} [a_k \cos(2\pi k f_0 t) + b_k \sin(2\pi k f_0 t)]

This allows for the recreation of complex mechanical signatures by defining the coefficients for the fundamental frequency ($f_0$) and its harmonics ($k$).

4. Operational Requirements

4.1 Software Dependencies

Python 3.10+

NumPy: Vectorized mathematical operations.

PyQt6: UI Framework.

PyQtGraph: High-performance scientific plotting.

PySerial: Serial communication for hardware emulation.

4.2 Hardware Emulation (Serial)

On Ubuntu, use socat to create a virtual bridge for testing: socat -d -d pty,raw,echo=0 pty,raw,echo=0

5. Directory Structure

signal_sensor_simulator/
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── src/
│   ├── engine.py         # Signal & Noise math
│   ├── frontend.py       # UI & Dialog definitions
│   └── controller.py     # Main loop & Serial logic