import threading
import sys
import time
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import wave
import speech_recognition as sr
from speech_recognition import AudioData
from colorama import Fore,Style

stop_event=threading.Event()

def wait_for_enter():
    input(Fore.YELLOW +"\nPress Enter to stop recording...\n" + Style.RESET_ALL)
    stop_event.set()

def spinner():
    spinner_chars='|/-\\'
    idx=0
    while not stop_event.is_set():
        sys.stdout.write(Fore.BLUE +'\rRecording...'+ Style.RESET_ALL+spinner_chars[idx% len(spinner_chars)])
        sys.stdout.flush()
        idx+=1
        time.sleep(0.1)
    sys.stdout.write('\rRecording stopped.\n')

def record_until_enter():
    p=pyaudio.PyAudio()
    format=pyaudio.paInt16
    channels=1
    rate=16000
    frames_per_buffer=1024

    stream=p.open(format=format,channels=channels,rate=rate,input=True,frames_per_buffer=frames_per_buffer)
    frames=[]

    threading.Thread(target=wait_for_enter).start()
    threading.Thread(target=spinner).start()

    while not stop_event.is_set():
        try:
            data=stream.read(frames_per_buffer)
            frames.append(data)
        except Exception as e:
            print("Error reading stream:",e)
            break

    stream.stop_stream()
    stream.close()
    sample_width=p.get_sample_size(format)
    p.terminate()

    Audio_data=b''.join(frames)
    return Audio_data,rate,sample_width

def save_audio(data,rate,width,filename="audio.way"):
    with wave.open(filename,"wb")as wf:
        wf.setnchannels(1)
        wf.setsampwidth(width)
        wf.setframerate(rate)
        wf.writeframes(data)
    print(f"Saved:{filename}")

def transcribed_audio(data,rate,width,filename="transcription.txt"):
    r=sr.Recognizer()
    audio=AudioData(data,rate,width)
    try:
        text=r.recognize_google(audio)
    except sr.UnknownValueError:
        text="Could not understand the audio."
    except sr.RequestError as e:
        text=f"API Error:{e}"
    print("Transcription:",text)
    with open(filename,"w")as f:
        f.write(text)
    print(f"Saved:{filename}")

def show_waveform(data,rate):
    samples=np.frombuffer(data,dtype=np.int16)
    time_axis=np.linspace(0,len(samples)/rate,num=len(samples))
    plt.plot(time_axis,samples)
    plt.title("Audio Wavwform")
    plt.xlabel("Time(s)")
    plt.ylabel("Amplitude")
    plt.tight_layout()
    plt.show()

def main():
    print(Fore.GREEN +"Start speaking. Press Enter to stop." + Style.RESET_ALL)
    audio_data,rate,width=record_until_enter()
    save_audio(audio_data,rate,width)
    transcribed_audio(audio_data,rate,width)
    show_waveform(audio_data,rate)

if __name__=="__main__":
    main()