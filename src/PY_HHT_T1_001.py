# 힐베르트-황 변환(HHT)에서 힐베르트 스펙트럼(Instantaneous Frequency Spectrogram)은 IMF 신호의 순간 주파수를 시각화하는 유용한 도구입니다. 
# 이 스펙트럼을 시각화하려면 각 IMF의 순간 주파수와 이를 시간에 따라 플롯하는 방법을 사용합니다. 
# 아래는 `matplotlib`을 사용하여 힐베르트 스펙트럼을 시각화하는 예제 코드입니다.
 
### 전체 코드 예제

#pip freeze > requirements.txt

#```python

import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from PyEMD import EEMD
from scipy.signal import hilbert
import threading
import queue
import time
 
# 설정
duration = 10  # 총 실행 시간 (초)
fs = 44100  # 샘플링 속도 (Hz)
buffer_size = fs  # 실시간 처리 버퍼 크기 (1초의 데이터)
 
# EEMD 객체 생성
eemd = EEMD()
eemd.trials = 100  # 트라이얼 횟수 설정
eemd.noise_seed(42)  # 재현성을 위한 노이즈 시드 설정
 
# 큐 생성
data_queue = queue.Queue()
 
def audio_callback(indata, frames, time, status):
    data_queue.put(indata.flatten())
 
def data_collection():
    with sd.InputStream(samplerate=fs, channels=1, callback=audio_callback, blocksize=buffer_size):
        while True:
            time.sleep(1)  # 데이터를 계속 수집하기 위해 대기
 
def process_data():
    last_data = np.zeros(buffer_size)
    plt.ion()  # 대화형 모드 활성화
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    ax1.set_xlim(0, buffer_size / fs)
    ax1.set_ylim(-1, 1)
    ax1.set_title("Real-time Audio Signal")
 
    ax2.set_xlim(0, buffer_size / fs)
    ax2.set_ylim(0, 50)  # 순간 주파수의 범위는 데이터에 따라 조정 필요
    ax2.set_title("Hilbert Spectrum")
 
    plt.show()
 
    while True:
        if not data_queue.empty():
            # 큐에서 데이터 가져오기
            new_data = data_queue.get()
            # 패딩 및 IMF 분석
            signal = np.concatenate((last_data, new_data))
            imfs = eemd.eemd(signal)
            if imfs.shape[1] > buffer_size:
                imfs = imfs[:, -buffer_size:]  # 패딩된 신호에서 최근 데이터만 사용
 
            # 힐베르트 스펙트럼 계산 및 시각화
            ax1.plot(np.linspace(0, buffer_size / fs, len(new_data)), new_data, 'b-')
            ax1.relim()
            ax1.autoscale_view()
 
            ax2.clear()
            ax2.set_xlim(0, buffer_size / fs)
            ax2.set_ylim(0, 50)  # 순간 주파수의 범위는 데이터에 따라 조정 필요
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
def main():
 
    # 데이터 수집 스레드 생성 및 시작
    collection_thread = threading.Thread(target=data_collection, daemon=True)
    collection_thread.start()
 
    # 데이터 처리 및 시각화
    process_data()


if __name__ == "__main__":
    main()

#```
 
#   ### 코드 설명
#    
#   1. **대화형 모드 활성화**:
#      - `plt.ion()`을 사용하여 대화형 모드를 활성화합니다. 그래프가 실시간으로 업데이트됩니다.
#    
#   2. **서브플롯 설정**:
#      - `plt.subplots(2, 1, figsize=(12, 10))`을 사용하여 두 개의 서브플롯을 생성합니다. 첫 번째 서브플롯은 실시간 오디오 신호를, 두 번째 서브플롯은 힐베르트 스펙트럼을 표시합니다.
#    
#   3. **실시간 데이터 수집**:
#      - `data_collection` 함수는 `sounddevice`를 사용하여 실시간으로 오디오 데이터를 수집하고 큐(`data_queue`)에 저장합니다.
#    
#   4. **데이터 처리 및 시각화**:
#      - `process_data` 함수는 큐에서 데이터를 가져와 EEMD를 수행하고 IMF를 계산합니다.
#      - 각 IMF에 대해 힐베르트 변환을 수행하여 순간 주파수를 계산하고, 이를 두 번째 서브플롯에 시각화합니다.
#      - `ax2.clear()`를 사용하여 이전 프레임의 내용을 지우고, 새로운 IMF의 순간 주파수를 플롯합니다.
#    
#   5. **스레드와 큐**:
#      - `threading.Thread`를 사용하여 데이터 수집을 별도의 스레드에서 실행합니다. 데이터 수집과 처리 및 시각화를 병렬로 수행할 수 있습니다.
#      - `queue.Queue`는 스레드 간의 안전한 데이터 전송을 제공합니다.
#    
#   ### 주의사항
#    
#   - **주파수 범위 조정**: 힐베르트 스펙트럼의 y축 범위(`ax2.set_ylim(0, 50)`)는 데이터에 따라 조정이 필요할 수 있습니다.
#   - **서브플롯 조정**: IMF의 수와 분석할 데이터의 양에 따라 서브플롯 수를 조정하거나, 서브플롯 크기를 변경할 수 있습니다.
#   - **성능**: 실시간 데이터 수집과 시각화는 시스템의 성능에 따라 제한될 수 있습니다. 데이터 버퍼 크기와 오버랩을 조정하여 성능을 최적화할 수 있습니다.
#    
#   이 예제는 모든 IMF의 힐베르트 스펙트럼을 실시간으로 시각화하는 기본적인 구조를 제공하며, 필요에 따라 추가적인 조정과 최적화가 필요할 수 있습니다.
