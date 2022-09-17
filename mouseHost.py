import socket
import keyboard
import pyautogui
from pynput.mouse import Controller
import math
import time
import win32api
import json

#mon_width = 1280
#mon_height = 720

settings = {}

with open('valkset.json') as json_file:
    settings = json.load(json_file)

mon_width = 3840
mon_height = 2160

mon_width = mon_width/2
mon_height = mon_height/2

host = settings['host-ip']  #server mouse is running On
port = int(settings['host-port'])
client = (settings['client-ip'], settings['client-port'])  # CHANGE THIS

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

def parse_cords(cords, sign, value):
    value = str(value)
    cords = str(sign + (value.zfill(3)))
    return cords

print("Server Started")
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
state_left = win32api.GetKeyState(0x01)
state_right = win32api.GetKeyState(0x02)
state_middle = win32api.GetKeyState(0x04)
pause_key = False
paused = False
while True:
    if paused is False:
        pos = pyautogui.position()
       #pyautogui.moveTo(1920, 1080)
        pyautogui.moveTo(mon_width, mon_height)

        x = (pos[0] - mon_width) * 1.3
        y = (pos[1] - mon_height) * 1.3

        cords = ""

        if x != 0:
            abs_x = round(math.fabs(x))
            if abs_x != 0:
                if abs_x > 999:
                    abs_x = 999
                if x > 0:
                    cords += parse_cords(cords, "X", abs_x)
                else:
                    cords += parse_cords(cords, "C", abs_x)

        if y != 0:
            abs_y = round(math.fabs(y))
            if abs_y != 0:
                if abs_y > 999:
                    abs_y = 999
                if y > 0:
                    cords += parse_cords(cords, "Y", abs_y)
                else:
                    cords += parse_cords(cords, "U", abs_y)

        if cords != "":
            data = str(cords)
            print(data)
            s.sendto(data.encode('utf-8'), client)

        if keyboard.is_pressed("[") or keyboard.is_pressed("]") or \
                keyboard.is_pressed("1") or keyboard.is_pressed("2") or keyboard.is_pressed("3") or \
                keyboard.is_pressed("4") or keyboard.is_pressed("5") or keyboard.is_pressed("6"):
            a = True
        else:
            a = False
        if a != pause_key:  # Button state changed
            pause_key = a
            # print(a)
            if a:
                s.sendto("PAUS".encode('utf-8'), client)
                # print("PAUS")
            else:
                s.sendto("UPAU".encode('utf-8'), client)
                # print("UPAUS")

        a = win32api.GetKeyState(0x01)
        if a != state_left:  # Button state changed
            state_left = a
            # print(a)
            if a < 0:
                s.sendto("A000".encode('utf-8'), client)
                # print('Left Button Pressed')
            else:
                s.sendto("B000".encode('utf-8'), client)
                # print('Left Button Released')

        b = win32api.GetKeyState(0x02)
        if b != state_right:  # Button state changed
            state_right = b
            # print(b)
            if b < 0:
                s.sendto("RHTD".encode('utf-8'), client)  # D000
                # print('Right Button Pressed')
            else:
                s.sendto("RHTU".encode('utf-8'), client)  # E000
                # print('Right Button Released')

        c = win32api.GetKeyState(0x04)
        if c != state_middle:  # Button state changed
            state_middle = c
            # print(c)
            if c < 0:
                s.sendto("SPND".encode('utf-8'), client)  # D000
                #print('Middle Button Pressed')
            else:
                s.sendto("SPNU".encode('utf-8'), client)  # E000
                #print('Middle Button Released')

    if keyboard.is_pressed('-'):
        exit(0)
    if keyboard.is_pressed('`'):
        paused = True
    if keyboard.is_pressed('Esc'):
        paused = False

    # n = (time.time() - last_time_main)
    # print(n)
    time.sleep(0.01)
c.close()
