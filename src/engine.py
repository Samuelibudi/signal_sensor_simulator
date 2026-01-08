import numpy as np
import time

class SignalEngine:
    def __init__(self):
        self.current_step = 0

    def generate_point(self, wave_type, freq, amp, noise_type, snr, fs):
        """
        Generates a single data point based on the current time and parameters.
        """
        # Calculate t based on the sample index and sample rate
        # t = index / sampling_frequency
        t = self.current_step / fs
        
        # Increment step for the NEXT point
        self.current_step += 1
        
        # 1. Generate Raw Signal
        if wave_type == "Sine":
            signal = amp * np.sin(2 * np.pi * freq * t)
        elif wave_type == "Square":
            signal = amp if np.sin(2 * np.pi * freq * t) >= 0 else -amp
        elif wave_type == "Sawtooth":
            # Linear ramp from -amp to +amp
            signal = 2 * amp * (freq * t - np.floor(0.5 + freq * t))
        elif wave_type == "Triangle":
            signal = (2 * amp / np.pi) * np.arcsin(np.sin(2 * np.pi * freq * t))
        else:
            signal = 0.0

        # 2. Apply Noise Profile
        if noise_type != "None":
            signal = self._apply_noise(signal, amp, noise_type, snr)

        return t, signal

    def _apply_noise(self, signal, amplitude, noise_type, snr_db):
        """
        Calculates and adds noise based on the Signal-to-Noise Ratio.
        """
        # Convert SNR from dB to linear scale
        # SNR_db = 10 * log10(P_signal / P_noise)
        snr_linear = 10**(snr_db / 10)
        
        # Calculate signal power (RMS squared)
        # For a sine wave, Power = (A^2) / 2
        signal_power = (amplitude**2) / 2
        noise_power = signal_power / snr_linear
        
        # Standard deviation (RMS voltage of noise)
        noise_std = np.sqrt(noise_power)

        if noise_type == "Gaussian White":
            noise = np.random.normal(0, noise_std)
        elif noise_type == "Pink Noise":
            # Approximation of 1/f noise
            noise = self._generate_pink_noise(noise_std)
        elif noise_type == "Brownian":
            # Integral of white noise (1/f^2)
            noise = self._generate_brownian_noise(noise_std)
        else:
            noise = 0

        return signal + noise

    def _generate_pink_noise(self, std):
        # Simplified pink noise via Voss-McCartney algorithm or filtered white noise
        return np.random.normal(0, std) * 0.7  # Placeholder for spectral density logic

    def _generate_brownian_noise(self, std):
        # Random walk approximation
        if not hasattr(self, '_last_brownian'): self._last_brownian = 0
        white = np.random.normal(0, std * 0.1)
        self._last_brownian += white
        return self._last_brownian