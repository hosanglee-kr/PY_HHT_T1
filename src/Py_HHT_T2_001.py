import numpy as np
import matplotlib.pyplot as plt
from PyEMD import EEMD
from scipy.signal import hilbert
from scipy.io import wavfile
import threading
import queue

import os

# Print the current working directory
print("Py_HHT_T2_001.py Current working directory:", os.getcwd())


# Settings
filename = '../src/boat1.wav'  # Path to your WAV file
buffer_size = 44100  # Buffer size for processing (1 second of data)

# EEMD object creation
eemd = EEMD()
eemd.trials = 100  # Number of trials
eemd.noise_seed(42)  # Noise seed for reproducibility

# Queue creation
data_queue = queue.Queue()

def read_wav_file():
    fs, data = wavfile.read(filename)
    if len(data.shape) > 1:  # If stereo, convert to mono
        data = np.mean(data, axis=1)
    # Split data into chunks
    for i in range(0, len(data), buffer_size):
        chunk = data[i:i + buffer_size]
        if len(chunk) < buffer_size:
            chunk = np.pad(chunk, (0, buffer_size - len(chunk)), 'constant')
        data_queue.put(chunk)

def process_data():
    plt.ion()  # Interactive mode on
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    ax1.set_xlim(0, buffer_size / fs)
    ax1.set_ylim(-1, 1)
    ax1.set_title("Real-time Audio Signal")
    
    ax2.set_xlim(0, buffer_size / fs)
    ax2.set_ylim(0, 50)  # Adjust as needed
    ax2.set_title("Hilbert Spectrum")
    
    plt.show()
    
    last_data = np.zeros(buffer_size)
    while not data_queue.empty() or not data_queue.empty():
        if not data_queue.empty():
            try:
                # Get data from queue
                new_data = data_queue.get()
                
                # Padding and IMF analysis
                signal = np.concatenate((last_data, new_data))
                imfs = eemd.eemd(signal)
                if imfs.shape[1] > buffer_size:
                    imfs = imfs[:, -buffer_size:]  # Use only recent data
                
                # Hilbert Spectrum calculation and visualization
                ax1.clear()
                ax1.plot(np.linspace(0, buffer_size / fs, len(new_data)), new_data, 'b-')
                ax1.set_xlim(0, buffer_size / fs)
                ax1.set_ylim(-1, 1)
                ax1.set_title("Real-time Audio Signal")

                ax2.clear()
                ax2.set_xlim(0, buffer_size / fs)
                ax2.set_ylim(0, 50)  # Adjust as needed
                ax2.set_title("Hilbert Spectrum")
                
                for i in range(imfs.shape[0]):
                    analytic_signal = hilbert(imfs[i])
                    instantaneous_phase = np.unwrap(np.angle(analytic_signal))
                    instantaneous_frequency = np.diff(instantaneous_phase) / (2.0 * np.pi * (1/fs))
                    time_axis = np.linspace(0, buffer_size / fs, len(instantaneous_frequency))
                    
                    ax2.plot(time_axis, instantaneous_frequency, label=f'IMF {i+1}')
                
                ax2.legend()
                plt.draw()
                plt.pause(0.01)
                
                last_data = new_data
            except Exception as e:
                print(f"Error during processing: {e}")
    
    plt.ioff()  # Interactive mode off
    plt.show()

def main():
    print("Py_HHT_T2_001.py Current working directory:", os.getcwd())

    # Read WAV file and populate queue
    ## read_wav_file()
    
    # Start data processing and visualization
    ## process_data()

if __name__ == "__main__":
    main()
