import time
import cv2
import mss
import numpy as np
import skimage
#from imutils import contours
#import argparse
#import imutils
import math
import keyboard
# import pyautogui
#import mouse
import serial  # pyserial
#from multiprocessing import Process, Queue
#import rivalcfg
import socket
import _thread
import json

#import d3dshot
#import paramiko

# Set Game to 0.5 sense
# Set Game to 0.84 # 0.85 zoom sense, 0.9 to tracking moving targets
# Set Game to 1920 x 1080
# Set Game to Show Purple
# Set Game to Hide Corpses
# Set Game to Transparent Cursor
# Set Game FPS to 144
# Set Walk to P (secondary)
# Set Zoom to O (secondary)
# Set Move Up to Up Arrow
# Set Move Down to Down Arrow
# Set Move Left to Left Arrow
# Set Move Right to Right Arrow
# (Optional) Set AA to MSAA 4x for long range precision

# Global Variables

monitor_width = 1920  # 1920 # 1280
monitor_height = 1080  # 1080 # 720

kill_reset_time_threshold = 0.05
aim_down_activation_threshold = 40  # 25 for killscan # 31

# Global Variables (DO NOT TOUCH)
cd_time = time.time()
cd_burst_time = time.time()
burstcount = 0
scope_state = False
no_target = True
alt_profile = False
is_shooting = False
spin_bot = False
spin_counter = 0
prediction_buffer = [0, 0]
up_is_pressed = False
down_is_pressed = False
left_is_pressed = False
right_is_pressed = False
walk_is_pressed = False
allow_mouse_inputs = True
blocking_during_scan = False
temp_pause = False

tracking_range = 3
subactive = "[ON]"
mainactive = "[ON]"
paused = True
kill_reset_time = 0
allow_tracking_resize = True
last_time_main = time.time()
frame_delay_options = [5, 10, 15, 20, 25]
frame_delay = 3
editing_selected = False
predictive_smoothing = False
passive_shoot_offset = 0
passive_shoot_offset_apply = 0
passive_hold_shoot_timer = time.time()
last_deep_tracking_ms = 0
deep_tracking_ms = 0
enemy_seen_delay_ms = 0

previous_process_time = 0

enemy_seen_delay_ms_still = 50
enemy_seen_delay_ms_walk = 100
enemy_seen_delay_ms_run = 155  # 175

distance_division_offset = [7, 9, 12]  # 7, 9
distance_threshold = [12, 9, 5]  # 12, 9
distance_max_threshold = [18, 18, 16]  # 18, 18, 16 # 12, 9
distance_names = ["Aim Low", "Aim Mid", "Aim High"]  # 12, 9
distance_selector = 1

prediction_ratio = [1, 1.5, 2, 0.00001]
prediction_selector = 3

prediction_scalar = [1, 2.124]
prediction_scalar_selector = 0

was_in_paused_state = False
target_nearest_post_paused_state = False

filter_names = ["Basic Filter", "Advanced-Fast Filter", "Advanced-Slow Filter"]
filter_selector = 1

last_height = 0
is_using_passive_aim = False
is_using_passive_aim_lock = False
manual_shooting = False
manual_scope = False

#use_d3d = False
#use_ssh = False

settings = {}

with open('valkset.json') as json_file:
    settings = json.load(json_file)

#host = '192.168.1.197'  # client ip  # CHANGE THIS
host = settings['client-ip']#'192.168.1.15'  # client ip  # CHANGE THIS
port = int(settings['client-port'])
server = (settings['host-ip'], int(settings['host-port'])) #107

#if use_ssh:
#    ssh = paramiko.SSHClient()
#    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Initial Initialization
#ser = serial.Serial('COM6', baudrate=2000000, timeout=1)  # 115200#250000#2000000
serMouse = serial.Serial('COM3', baudrate=2000000, writeTimeout=0)  # 115200#250000#2000000
serKeyboard = serial.Serial('COM4', baudrate=2000000, writeTimeout=0)  # 115200#250000#2000000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))

# Aim Profiles
"""
class WeaponProfilesBak:
    class ProfileTemplate:
        def __int__(self, offset_x=5, offset_y=4, down_offset_y=45, fire_cd=0.1, ato_scope=False, ato_scope_adv=False):
            self.aim_offset_x = offset_x
            self.aim_offset_y = offset_y
            self.aim_down_offset_y = down_offset_y
            self.shoot_cd = fire_cd
            self.auto_scope = ato_scope
            self.auto_scope_adv = ato_scope_adv

    class BodyShot:
        Guardian = WeaponProfiles.ProfileTemplate(5, 4, 45, 0.1, False, False)

    class HeadShot:
        GuardianZoom = WeaponProfiles.ProfileTemplate(2, 4, 0, 0.375, False, True)
        Guardian = WeaponProfiles.ProfileTemplate(2, 4, 0, 0.375, False, False)
        Sheriff = WeaponProfiles.ProfileTemplate(2, 7, 0, 0.375, False, False)
"""


class WeaponProfiles:
    class BodyShot:
        class Guardian:
            aim_offset_x = 1  # 5
            aim_offset_y = 4  # 45 # 50 shoots between legs at mid range
            aim_down_offset_y = 45  # 60
            shoot_cd = 0.1  # 0.2 # 0.1 # 0.07
            auto_scope = False
            auto_scope_adv = False

        class GuardianZoom:
            aim_offset_x = 1  # 5
            aim_offset_y = 4  # 45 # 50 shoots between legs at mid range
            aim_down_offset_y = 45  # 60
            shoot_cd = 0.1  # 0.2 # 0.1 # 0.07
            auto_scope = False
            auto_scope_adv = True

    class HeadShot:
        class GuardianZoom:
            aim_offset_x = 1  # 0 # 2 # 7 was good
            aim_offset_y = 4  # 4 # 14 for anti simp # 7 Was original # 5 was original # 3 good against hanzo # 7 was good against sage # 15 # 13 is good
            #walk_aim_offset_y = 0  # 5 originally # 7 was pretty good
            aim_down_offset_y = 0
            #moving_aim_down_offset_y = 0
            #moving_aim_down_speed_multiplier = 1
            shoot_cd = 0.375  # 0.355 #  0.375  # 0.4 original
            #shoot_cd_strafe = 0.45
            auto_scope = False
            auto_scope_adv = True

        class Guardian:
            aim_offset_x = 1  # 0 # 2  # 7 was good
            aim_offset_y = 4  # 4 # 5 was original # 3 good against hanzo # 7 was good against sage # 15 # 13 is good
            #walk_aim_offset_y = 0  # 5 originally # 7 was pretty good
            aim_down_offset_y = 0
            #moving_aim_down_offset_y = 0
            #moving_aim_down_speed_multiplier = 1
            shoot_cd = 0.375  # 0.355 #  0.375  # 0.4 original
            #shoot_cd_strafe = 0.45
            auto_scope = False
            auto_scope_adv = False

        class GuardianNoXOffset:
            aim_offset_x = 0  # 7 was good
            aim_offset_y = 4  # 4 # 5 was original # 3 good against hanzo # 7 was good against sage # 15 # 13 is good
            #walk_aim_offset_y = 0  # 5 originally # 7 was pretty good
            aim_down_offset_y = 0
            #moving_aim_down_offset_y = 0
            #moving_aim_down_speed_multiplier = 1
            shoot_cd = 0.375  # 0.355 #  0.375  # 0.4 original
            #shoot_cd_strafe = 0.45
            auto_scope = False
            auto_scope_adv = False

        class Sheriff:
            aim_offset_x = 2  # 7 was good
            aim_offset_y = 7  # 5 was original # 3 good against hanzo # 7 was good against sage # 15 # 13 is good
            #walk_aim_offset_y = 0  # 7 was pretty good
            aim_down_offset_y = 0
            #moving_aim_down_offset_y = 0
            #moving_aim_down_speed_multiplier = 1
            shoot_cd = 0.375  # 0.5 original  # 0.4 original
            #shoot_cd_strafe = 0.5
            # you need a burst cooldown timer
            auto_scope = False
            auto_scope_adv = False


# Color Profiles
class Colors:
    yellow = ((np.array([30, 160, 240]),  np.array([30, 255, 255])),  # aggressive filtering, for range 2-3
              (np.array([30, 160, 240]),  np.array([30, 255, 255])),  # gracious for range 0-1
              (np.array([30, 160, 240]),  np.array([30, 255, 255])))  # lenient filtering for square mask in range 0-1

    purple = ((np.array([145, 150, 240]),  np.array([150, 255, 255])),  # aggressive filtering, for range 2-3
              (np.array([140, 70, 80]),        np.array([155, 255, 255])),  # gracious for range 0-1
              (np.array([140, 70, 80]),         np.array([170, 255, 255])))  # lenient filtering for square mask in range 0-1

    antiphoenix = ((np.array([145, 150, 240]),  np.array([150, 255, 255])),  # aggressive filtering, for range 2-3
                   (np.array([140, 70, 204]),        np.array([150, 255, 255])),  # gracious for range 0-1
                   #(np.array([16, 194, 150]),          np.array([17, 235, 200])))  # phoenix hair tracking
                    (np.array([15, 194, 150]),          np.array([18, 235, 200])))  # phoenix hair tracking

    primary = ((np.array([145, 180, 240]),       np.array([149, 255, 255])),  # HYPER aggressive filtering, for range 2-3
               (np.array([140, 70, 204]),        np.array([150, 255, 255])),  # gracious for range 0-1
                   #(np.array([16, 194, 150]),          np.array([17, 235, 200])))  # phoenix hair tracking
               (np.array([15, 194, 150]),          np.array([18, 235, 200])),# phoenix hair tracking
               (np.array([140, 70, 80]), np.array([170, 255, 255])))# lenient purple


    aggressive = (([0,0,0], [0,0,0]),  # Red
                  (np.array([145, 110, 125]), np.array([150, 255, 255])),  # Purple
                  (np.array([145, 150, 240]), np.array([150, 255, 255])),  # Purple Increase Precision
                  (np.array([30, 150, 200]), np.array([30, 165, 255])))  # Yellow

    standard = (([0,0,0], [0,0,0]),  # Red
                (np.array([140, 70, 100]), np.array([150, 255, 255])),  # Purple
                (np.array([140, 70, 204]), np.array([150, 255, 255])),  # 204 240 Purple Increase Precision 150
                (np.array([30, 125, 150]), np.array([30, 255, 255])))  # Yellow

    test = ((np.array([0, 0, 0]),       np.array([0, 0, 0])),  # Red
            (np.array([0, 0, 0]),       np.array([255, 255, 0])),  # blk
            (np.array([79, 180, 250]),  np.array([80, 190, 255])),  # lime green
            (np.array([0, 0, 245]),     np.array([0, 0, 255])),  # white
            (np.array([30, 125, 150]),  np.array([30, 255, 255])),  # Yellow
            (np.array([0, 0, 0]),      np.array([0, 0, 0])),  # Red
            (np.array([15, 100, 100]),  np.array([16, 230, 230])),  # Orng
            (np.array([15, 100, 100]),  np.array([16, 230, 230])),  # Orng
            (np.array([30, 125, 150]),  np.array([30, 255, 255])),  # Yellow
            (np.array([15, 234, 0]), np.array([20, 235, 255])),  # phenix brown
            (np.array([17, 234, 0]), np.array([18, 235, 255])),  # phenix hair specific
            (np.array([0, 125, 0]), np.array([10, 130, 255])),      # phenix brown
            (np.array([15, 194, 0]),          np.array([20, 235, 255])))  # a bit gracious but works better at long range

    kill = ((np.array([70, 0, 200]),    np.array([90, 50, 255])),  # white lime
            (np.array([0, 0, 240]),     np.array([0, 0, 255])),  # white
            (np.array([79, 180, 250]),  np.array([80, 190, 255])),  # lime green
            (np.array([79, 180, 250]),  np.array([80, 190, 255])))  # lime green


# Pre Compute Resolution Profiles
class MonitorProcessing:
    class ResolutionProfile:
        def __int__(self):
            self.width = 0
            self.height = 0
            self.height_offset = 0
            self.res_w = 0
            self.res_h = 0
            self.monitor = None
            self.monitor_d3d = None

    @staticmethod
    def monitor_pre_cal(monitor_width, monitor_height):
        mon = (MonitorProcessing.ResolutionProfile(), MonitorProcessing.ResolutionProfile(), MonitorProcessing.ResolutionProfile(),
               MonitorProcessing.ResolutionProfile(), MonitorProcessing.ResolutionProfile(), MonitorProcessing.ResolutionProfile(),
               MonitorProcessing.ResolutionProfile(), MonitorProcessing.ResolutionProfile(), MonitorProcessing.ResolutionProfile(),
               MonitorProcessing.ResolutionProfile())

        half_width = math.floor((monitor_width / 2))
        half_height = math.floor((monitor_height / 2))

        mon[0].width = 100  # 70  # 100
        mon[0].height = 130
        mon[0].height_offset = 35

        mon[1].width = 100
        mon[1].height = 175
        mon[1].height_offset = 0

        mon[2].width = 800  # 800 # 500  # 600
        mon[2].height = 350  # 800 # 200  # 200
        mon[2].height_offset = -70

        mon[3].width = 800  # 800 # 600
        mon[3].height = 350  # 350 # 200
        mon[3].height_offset = -70

        mon[4].width = 0  # 600
        mon[4].height = 0  # 200
        mon[4].height_offset = 0

        mon[5].width = 0  # 600
        mon[5].height = 0  # 200
        mon[5].height_offset = 0

        mon[6].width = 100  # 600
        mon[6].height = 200  # 200
        mon[6].height_offset = 0

        mon[7].width = 75  # 600
        mon[7].height = 150  # 200
        mon[7].height_offset = 0

        mon[8].width = 150  # 600
        mon[8].height = 150  # 200
        mon[8].height_offset = 0

        mon[9].width = 250  # 600
        mon[9].height = 150  # 200
        mon[9].height_offset = 0
        # mon[3].width = 800
        # mon[3].height = 250

        for x in mon:
            x.res_w = math.floor(x.width / 2)
            x.res_h = math.floor(x.height / 2)

            x.monitor = {"left": (half_width - x.res_w), "top": (half_height - x.res_h + x.height_offset),
                         "width": x.width, "height": x.height}

            x.monitor_d3d = ((half_width - x.res_w), (half_height - x.res_h + x.height_offset),
                            (half_width + x.res_w), (half_height + x.res_h - x.height_offset))

            print(x.monitor)

        return mon

    @staticmethod
    def monitor_kill_indicators(monitor_width, monitor_height):
        mon = (MonitorProcessing.ResolutionProfile(), MonitorProcessing.ResolutionProfile())

        #mon[0].monitor = {"left": round(monitor_width * 0.53802083333), "top": round(monitor_height * 0.801851851),  # original scans
        #                  "width": 1, "height": 1}
        #mon[1].monitor = {"left": round(monitor_width * 0.46145833333), "top": round(monitor_height * 0.802777777),
        #                  "width": 1, "height": 1}

        #mon[0].monitor = {"left": 885, "top": 867,
        #                  "width": 2, "height": 2}
        #mon[1].monitor = {"left": 1033, "top": 866,
        #                  "width": 2, "height": 2}

        mon[0].monitor = {"left": 885, "top": 909,
                          "width": 1, "height": 1}
        mon[1].monitor = {"left": 1033, "top": 909,
                          "width": 1, "height": 1}


        #mon[0].monitor = {"left": round(monitor_width * 0.4671875), "top": round(monitor_height * 0.7962962),  # new scans
        #                  "width": 1, "height": 1}
        #mon[1].monitor = {"left": round(monitor_width * 0.53177083), "top": round(monitor_height * 0.7962962),
        #                  "width": 1, "height": 1}
        return mon

    @staticmethod
    def monitor_indicators_zone(monitor_width, monitor_height):
        mon = MonitorProcessing.ResolutionProfile()

        mon.monitor = {"left": 885, "top": 909,
                          "width": 149, "height": 1}

        return mon


# Prediction Engine
class PredictionEngine:
    @staticmethod
    def add_cords_for_prediction(x):
        prediction_buffer[0] = prediction_buffer[1]
        prediction_buffer[1] = x

    @staticmethod
    def run_prediction_engine():
        x = 0
        if prediction_buffer[0] == prediction_buffer[1]:
            x = prediction_buffer[0]

        cords = ""
        if x > 0:
            cords += HidController.parse_cords("X", x)
        else:
            cords += HidController.parse_cords("C", x)

        HidController.encode_and_send_mouse(cords)
        return x


# Image Manipulation
class ImageProcessing:
    class ImageCords:
        def __int__(self):
            self.img = None
            self.cords = (None, None)

    @staticmethod
    def screen_capture(tracking_range):
        #global use_d3d
        #global d
        #if use_d3d:
        #    return d.screenshot(region=mon[tracking_range].monitor_d3d)
        #else:
        return np.array(sct.grab(mon[tracking_range].monitor))

    class Filtering:
        @staticmethod
        def test(tracking_range, colors, array_value):  # original purps filters
            color_mask = cv2.inRange(cv2.cvtColor(ImageProcessing.screen_capture(tracking_range), cv2.COLOR_BGR2HSV),
                                     colors[array_value][0],  # 140,70,100 # 75 to 90
                                     colors[array_value][1])  # 200

            return color_mask

        @staticmethod
        def aggressive(tracking_range, colors):
            color_mask = cv2.inRange(cv2.cvtColor(ImageProcessing.screen_capture(tracking_range), cv2.COLOR_BGR2HSV),
                                     colors[0][0],
                                     colors[0][1])  # 200
            return color_mask

        @staticmethod
        def standard(tracking_range, colors):  # original purps filters
            color_mask = cv2.inRange(cv2.cvtColor(ImageProcessing.screen_capture(tracking_range), cv2.COLOR_BGR2HSV),
                                     colors[1][0], #140,70,100 # 75 to 90
                                     colors[1][1])  # 200

            #color_mask2 = cv2.inRange(cv2.cvtColor(np.array(sct.grab(mon[tracking_range].monitor)), cv2.COLOR_BGR2HSV),
            #                         np.array(colors[1][0]), #140,70,100 # 75 to 90
            #                         np.array(colors[1][1]))  # 200

            #color_mask = cv2.add(color_mask, color_mask2)

            return color_mask

        @staticmethod
        def advanced_split_standard(tracking_range, colors, height_upper, height_lower, width):  # original purps filters
            return ImageProcessing.Filtering.advanced_split(tracking_range, colors, height_upper, height_lower, width, 1, 2)

        @staticmethod
        def advanced_split_standard_3(tracking_range, colors, height_upper, height_lower, width):  # original purps filters
            return ImageProcessing.Filtering.advanced_split_3(tracking_range, colors, height_upper, height_lower, width, 1, 2, 3)

        @staticmethod
        def advanced_split_aggressive(tracking_range, colors, height_upper, height_lower, width):  # original purps filters
            return ImageProcessing.Filtering.advanced_split(tracking_range, colors, height_upper, height_lower, width, 0, 1)

        @staticmethod
        def advanced_split(tracking_range, colors, height_upper, height_lower, width, color_1, color_2):  # original purps filters
            #last_time_main = time.time()  # timing
            capture = ImageProcessing.screen_capture(tracking_range)
            #n = (time.time() - last_time_main)  # timing
            #print(str(n))
            center = (mon[tracking_range].width/2, (mon[tracking_range].height/2) - mon[tracking_range].height_offset)
            color_mask = cv2.inRange(cv2.cvtColor(capture, cv2.COLOR_BGR2HSV),
                                     colors[color_1][0],
                                     colors[color_1][1])

            color_mask_2 = cv2.inRange(cv2.cvtColor(capture, cv2.COLOR_BGR2HSV),
                                     colors[color_2][0],
                                     colors[color_2][1])

            rect_mask = np.zeros(color_mask.shape, dtype="uint8")
            rect_mask = cv2.rectangle(rect_mask, (int(center[0]-(width/2)), int(center[1]-height_upper)),
                                      (int(center[0]+(width/2)), int(center[1]+height_lower)), (255, 24, 206), -1)

            color_mask_2 = cv2.bitwise_and(color_mask_2, color_mask_2, mask=rect_mask)

            img_out = cv2.add(color_mask, color_mask_2)

            return img_out  # Find The Height of target in color_mask then use that to determine the crop size of color_mask_2
            # scan the cropped image, apply offsets to center the image, find first pixel, apply offsets to first pixel, recalcuate height

            #run kill indicator on another thread, usually u go get the kills, so yeah, u might as well?
######################################################################################################################################################################################
        @staticmethod
        def advanced_split_3(tracking_range, colors, height_upper, height_lower, width, color_1, color_2, color_3):
            #global rect_mask

            capture = ImageProcessing.screen_capture(tracking_range)
            center = (
            mon[tracking_range].width / 2, (mon[tracking_range].height / 2) - mon[tracking_range].height_offset)
            color_mask = cv2.inRange(cv2.cvtColor(capture, cv2.COLOR_BGR2HSV),
                                     colors[color_1][0],
                                     colors[color_1][1])

            #if rect_mask is None:
            rect_mask = np.zeros(color_mask.shape, dtype="uint8")
            rect_mask = cv2.rectangle(rect_mask, (int(center[0] - (width / 2)), int(center[1] - height_upper)),
                                     (int(center[0] + (width / 2)), int(center[1] + height_lower)), (255, 24, 206), -1)
            #rect_mask_in = rect_mask.copy()

            color_mask_2 = cv2.inRange(cv2.cvtColor(capture, cv2.COLOR_BGR2HSV),
                                       colors[color_2][0],
                                       colors[color_2][1])

            color_mask_3 = cv2.inRange(cv2.cvtColor(capture, cv2.COLOR_BGR2HSV),
                                       colors[color_3][0],
                                       colors[color_3][1])

            color_mask_2 = cv2.bitwise_and(color_mask_2, color_mask_2, mask=rect_mask)
            color_mask_3 = cv2.bitwise_and(color_mask_3, color_mask_3, mask=rect_mask)

            img_out = cv2.add(color_mask, color_mask_2, color_mask_3)

            return img_out

        @staticmethod
        def multi_track(tracking_range):  # original purps filters  # PROOF OF CONCEPT
            #last_time_main = time.time()  # timing

            color_picker = 2
            colors = (([], []),  # Red
                      ([145, 150, 240], [150, 255, 255]),  # Purple Aggressive Increased Precision
                      ([140, 70, 240], [150, 255, 255]),  # Purple Increase Precision
                      ([30, 125, 150], [30, 255, 255]))  # Yellow

            color_mask = cv2.inRange(cv2.cvtColor(ImageProcessing.screen_capture(tracking_range), cv2.COLOR_BGR2HSV),
                                     colors[color_picker][0], #140,70,100 # 75 to 90
                                     colors[color_picker][1])  # 200

            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, np.ones((35, 15)))  # np.ones((55, 20)))
            color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, np.ones((4, 4)))

            color_mask = ImageProcessing.split_targets(color_mask)

            #n = (time.time() - last_time_main)  # timing
            #print(str(n))

            return color_mask

        @staticmethod
        def scan_kill(mon_in, colors):
            #last_time_main = time.time()  # timing

            img = np.array(sct.grab(mon_in[0].monitor))
            img2 = np.array(sct.grab(mon_in[1].monitor))

            #print((time.time() - last_time_main))
            img_out = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV),
                                    colors[0][0],
                                    colors[0][1])

            img_temp = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV),
                                    colors[1][0],
                                    colors[1][1])
            img_out = cv2.add(img_out, img_temp)

            img_out2 = cv2.inRange(cv2.cvtColor(img2, cv2.COLOR_BGR2HSV),
                                    colors[0][0],
                                    colors[0][1])

            img_temp = cv2.inRange(cv2.cvtColor(img2, cv2.COLOR_BGR2HSV),
                                    colors[1][0],
                                    colors[1][1])
            img_out2 = cv2.add(img_out2, img_temp)
            # cv2.imshow("kill confirmed", color_mask)

            #print((time.time() - last_time_main))
            return img_out, img_out2

    @staticmethod
    def kill_indicator_slow(mon_in, colors):
        mask, mask2 = ImageProcessing.Filtering.scan_kill(mon_in, colors)
        #m1 = False
        #m2 = False
        #if mask[0, 0] != 0 or mask[0, 1] != 0 or mask[1, 0] != 0 or mask[1, 1] != 0:
        #    m1 = True
        #if mask2[0, 0] != 0 or mask2[0, 1] != 0 or mask2[1, 0] != 0 or mask2[1, 1] != 0:
        #    m2 = True
        #if m1 is True and m2 is True:
        #    return True
        #print(str(mask[0, 0]) + str(mask2[0, 0]))  # + str(mask3[0, 0]))
        if mask[0, 0] != 0 and mask2[0, 0] != 0:# and mask3[0, 0] != 0:
            return True
        return False

    @staticmethod
    def kill_indicator(mon_in, colors):

        img = np.array(sct.grab(mon_in.monitor))

        # print((time.time() - last_time_main))
        img_out = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV),
                              colors[0][0],
                              colors[0][1])

        img_temp = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV),
                               colors[1][0],
                               colors[1][1])
        img_out = cv2.add(img_out, img_temp)

        if img_out[0, 0] != 0 and img_out[0, 148] != 0:  # and mask3[0, 0] != 0:
            return True
        return False

    @staticmethod
    def crop(color_mask): # crop and search colormask2
        return 0

    @staticmethod
    def split_targets(color_mask):
        masks_array = []
        labels = skimage.measure.label(color_mask, neighbors=8, background=0)
        mask = np.zeros(color_mask.shape, dtype="uint8")
        #countr = 1
        for label in np.unique(labels):
            if label == 0:
                continue
            labelMask = np.zeros(color_mask.shape, dtype="uint8")
            labelMask[labels == label] = 255
            numPixels = cv2.countNonZero(labelMask)

            #if numPixels > 1:
            #print(countr)
            #countr += 1
            masks_array.append([labelMask, numPixels])

            ##img_out = find_first_pixel_npy_argmax_fast(labelMask)
            ##if img_out.cords[0] != None:
            ##    cv2.putText(labelMask, str(len(masks_array)) + ": Alive", (img_out.cords[0], img_out.cords[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (209, 80, 0, 255))

            #cv2.imshow("Set", labelMask)
            #cv2.waitKey(1000)
            ##mask = cv2.add(mask, labelMask)  # reconstruct the mask

        #masks_array.sort()
        #masks_array = sorted(masks_array)

        masks_array.sort(key=lambda x: int(x[1]), reverse=True)

        for i in masks_array:
            #print(i[1])

            img_out = ImageSearch.find_first_pixel_npy_argmax_fast(i[0])
            if img_out.cords[0] is not None:
                x, y, w, h = cv2.boundingRect(i[0])
                i[0] = cv2.rectangle(i[0], (x, y), (x + w, y + h), (209, 80, 0), 2)

                if ImageProcessing.check_life(w, h) == 1:
                    stat = "Alive"
                else:
                    stat = "Dead"

                cv2.putText(i[0], str(i[1]) + ": " + stat, (img_out.cords[0], img_out.cords[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (209, 80, 0, 255))

            mask = cv2.add(mask, i[0])

        return mask
        #        alt_color_mask = cv2.add(alt_color_mask, labelMask)
        #return alt_color_mask

    @staticmethod
    def check_life(w, h):
        if (w / h) > 1.6:  # 3:
            return 0
        return 1

    # Image Details
    @staticmethod
    def apply_text(mask, textA, textB, textC, textD, textE, tracking_range):
        height = mon[tracking_range].height
        cv2.putText(mask, textA, (0, height - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (209, 80, 0, 255))
        cv2.putText(mask, textB, (0, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (209, 80, 0, 255))
        cv2.putText(mask, textC, (0, height - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (209, 80, 0, 255))
        cv2.putText(mask, textD, (0, height - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (209, 80, 0, 255))
        cv2.putText(mask, textE, (0, height - 65), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (209, 80, 0, 255))
        return mask


""""
    @staticmethod
    def kill_detector():
        temp_mon = MonitorProcessing.monitor_kill_indicators(monitor_width, monitor_height)
        temp_last = False
        temp_cnt = 0

        while True:
            new = ImageProcessing.kill_indicator(temp_mon, Colors.kill)
            if new is True and temp_last is False:
                temp_cnt += 1
                print("Kill: " + str(temp_cnt))
            temp_last = new
"""


# Search
class ImageSearch:
    @staticmethod
    def find_first_pixel(color_mask, color_mask_alt, wepprofile, tracking_range, alt_profile):
        # In case the code ever goes to C, consider this method
        second_pass = False
        sp_h = 0
        sp_v = 0
        if tracking_range == 0:
            scan_h = 2#2  # 4  # 2 # 2  # 2
            scan_v = 2#5  # 10  # 6 # 5  # 4
            second_pass = True
            sp_h = 1
            sp_v = 1
        elif tracking_range == 1:
            scan_h = 2  # 2
            scan_v = 5  # 4
        elif tracking_range >= 2:
            scan_h = 15  # 15  # 10 # use 1 FOR HIGH PRECISION!
            scan_v = 16  # 8
            if alt_profile:
                second_pass = True
                sp_h = 2#2  #1 for development testing
                sp_v = 2 #2

        # Search Algorithm

        rows, cols = color_mask.shape
        img_cords = ImageProcessing.ImageCords()

        for i in range(0, rows, scan_h):  # 2 #4 #200 max/ up - down/ vertical
            for j in range(0, cols, scan_v):  # 4 #6
                if color_mask[i, j] != 0:
                    # print(i, j)
                    # Second Pass
                    if second_pass:
                        istart = 0
                        jstart = 0
                        jfin = 0
                        if i > scan_h and j > scan_v:
                            istart = scan_h
                            jstart = scan_v
                        if alt_profile and tracking_range < 2 and color_mask_alt is not None:
                            if (i - (scan_h * 2)) > 0:
                                istart *= 2
                            if (j - (scan_v * 2)) > 0:
                                jstart *= 2
                            if (j + scan_v) < mon[tracking_range].width - 1:
                                jfin = scan_v

                        for k in range(i - istart, i, sp_h):  # 2 #4 #200 up - down
                            for p in range(j - jstart, j + jfin, sp_v):
                                if color_mask_alt[k, p] != 0:
                                    i = k
                                    j = p
                                    break
                            else:
                                continue
                            break

                        color_mask = cv2.circle(color_mask, (j - jstart, i - istart), 5, (255, 24, 206), -1)  # (j, i+15) #(j+10, i-5)

                    x = j  # + wepprofile.aim_offset_x  # 5
                    y = i  # + wepprofile.aim_offset_y  # 15

                    color_mask = cv2.circle(color_mask, (x, y), 5, (255, 24, 206), -1)  # (j, i+15) #(j+10, i-5)
                    img_cords.cords = (x, y)
                    break
            else:
                img_cords.cords = (None, None)
                continue
            break

        img_cords.img = color_mask

        return img_cords

    @staticmethod
    def find_first_pixel_npy(color_mask):
        img_cords = ImageProcessing.ImageCords()
        img_cords.img = color_mask

        zeros = color_mask#np.zeros((100, 100), dtype=np.uint8)
        #zeros[:5, :5] = 255

        #indices = np.where(zeros != 0)
        indices = np.nonzero(zeros)
        #coordinates = zip(indices[0], indices[1])

        #print(indices[0], indices[1])
        if len(indices[0]) > 1 and len(indices[1]) > 1:
            img_cords.cords = (indices[1][0], indices[0][0])
            #print(img_cords.cords)
        else:
            img_cords.cords = (None, None)
        return img_cords

    @staticmethod
    def find_first_pixel_npy_argmax_fast(color_mask):  # , wepprofile, tracking_range):
        img_cords = ImageProcessing.ImageCords()
        img_cords.img = color_mask#[::-1]
        img_cords.cords = (None, None)

        for i, ele in enumerate(np.argmax(color_mask, axis=1, )):
            if ele != 0 or color_mask[i][0] != 0:
                #img_cords.cords = (ele + wepprofile.aim_offset_x,
                #                   i + wepprofile.aim_offset_y + distance_offset + mon[tracking_range].height_offset) # 8 if offset is 7#10 was good for offset with deg besides fighting simp
                img_cords.cords = (ele, i)
                break
        # print(str(img_cords.cords))
        return img_cords

    @staticmethod
    def find_first_pixel_npy_argmax(color_mask, wepprofile, tracking_range, mon, scope_state):
        #global mon
        #global scope_state
        global distance_division_offset
        global distance_threshold
        global distance_max_threshold
        global distance_selector
        global alt_profile
        #global last_height

        img_cords = ImageProcessing.ImageCords()
        img_cords.img = color_mask#[::-1]
        img_cords.cords = (None, None)
        enemy_height = None

        for i, ele in enumerate(np.argmax(color_mask, axis=1, )):
            if ele != 0 or color_mask[i][0] != 0:
                #if tracking_range < 1 and alt_profile:
                #if tracking_range < 2:
                #    height = ImageSearch.reverse_find_first_pixel_npy_argmax(color_mask, wepprofile)
                #else:
                #    height = 0
                #last_time_main = time.time()

                height = ImageSearch.reverse_find_first_pixel_npy_argmax(color_mask, wepprofile)

                #n = (time.time() - last_time_main)  # timing
                #print(str(n) + "TIME")

                enemy_height = mon[tracking_range].height - i - height
                #side_offset = 0
                distance_offset = (enemy_height/distance_division_offset[distance_selector]) - 4  # -4 /7
                if distance_offset < 0:
                    distance_offset = 0
                    #side_offset = -2
                elif distance_offset > distance_threshold[distance_selector]:  #12
                    distance_offset = distance_max_threshold[distance_selector]
                    if alt_profile is False:  # for running and gunning close range
                        distance_offset += 10
                #if (enemy_height/mon[tracking_range].height) < 0.3 and wepprofile.auto_scope_adv:
                #    scope_state = HidController.hold_scope(scope_state)
                if (enemy_height/mon[tracking_range].height) < 0.15 and wepprofile.auto_scope_adv:
                    scope_state = HidController.hold_scope(scope_state)
                #print ("heee: " + str(enemy_height/mon[tracking_range].height))

                #if distance_offset > 100:
                #    distance_offset = 100
    #print(str(distance_offset))
                #print(str(height) + ":" + str(i) + ":" + str(i-height))
                #print(str(ele + wepprofile.aim_offset_x))
                img_cords.cords = (ele + wepprofile.aim_offset_x,  # + side_offset,
                                   i + wepprofile.aim_offset_y + distance_offset + mon[tracking_range].height_offset) # 8 if offset is 7#10 was good for offset with deg besides fighting simp
                #print(distance_offset)
                #img_cords.cords = (int(img_cords.cords[0]), int(img_cords.cords[1]))
                #img_cords.img = cv2.circle(img_cords.img, (ele, i), 5, (255, 24, 206), -1)
                break
        # print(str(img_cords.cords))
        return img_cords, scope_state, enemy_height

    @staticmethod
    def reverse_find_first_pixel_npy_argmax(color_mask, wepprofile):
        height = 0
        #last_time_main = time.time()  # timing
        #for i, ele in enumerate(np.argmax(color_mask[::-1], axis=1, )):
        for i, ele in enumerate(np.argmax(np.flipud(color_mask), axis=1)):
            if ele != 0 or color_mask[i][0] != 0:
                height = i
                # img_cords.img = cv2.circle(color_mask, img_cords.cords, 5, (255, 24, 206), -1)
                break
        # print(str(img_cords.cords))
        #n = (time.time() - last_time_main)  # timing
        #print(str(n) + "TIME")
        return height


# Select Target and Kill
class HidController:
    @staticmethod
    def move_to_target(target, center, wepprofile, allow_tracking_resize, alt_profile, predictive_smoothing,
                       deep_tracking_ms, enemy_seen_delay_ms, en_height):

        global scope_state
        global tracking_range
        global aim_down_activation_threshold
        global no_target
        global spin_bot
        global spin_counter
        global up_is_pressed
        global down_is_pressed
        global left_is_pressed
        global right_is_pressed
        global walk_is_pressed
        global blocking_during_scan
        global allow_mouse_inputs
        global is_shooting
        global enemy_seen_delay_ms_still
        #global last_time_main
        #global frame_delay_options
        #global frame_delay
        #global previous_process_time
        #global enemy_seen_delay_ms_running_offset

        #global kill_mon
        #global kill_last
        #global kill_cnt

        #global d_down
        #global a_down

        if target[0] is None:  # Pass through Mouse?
            #if tracking_range < 2:
            #    is_shooting = HidController.arduino_unshoot(is_shooting)
            #else:
            #    allow_mouse_inputs = True

            if tracking_range > 1:
                allow_mouse_inputs = True

            is_shooting = HidController.arduino_unshoot(is_shooting)

            if alt_profile:
                tracking_range = 2
            else:
                tracking_range = 3
            # print("No Target")
            HidController.reset_mouse()
            HidController.reset_tracking_timers()
            if wepprofile.auto_scope:  # and tracking_range >= 3:
                scope_state = HidController.release_scope(scope_state)
            if wepprofile.auto_scope_adv:
                scope_state = HidController.release_scope(scope_state)
            # encode_and_send_mouse("X0000Y0000")
            # SKIP CV2.WAIT TIME BECAUSE THE MOUSE DIDNT MOVE!!!!!!!!!!!!!!!!!!!!!!!!

            if spin_bot:
                no_target = False
                movement_detected = False
                #encode_and_send_mouse("X999X120") use when not moving
                #encode_and_send_mouse("X966") 11
                #encode_and_send_mouse("X999X772")  # 6
                if keyboard.is_pressed('a') or keyboard.is_pressed('d') or keyboard.is_pressed('w') or keyboard.is_pressed('s'):
                    movement_detected = True

                if movement_detected:
                    spin_counter += 1
                    if spin_counter == 6:
                        spin_counter = 0
                        no_target = False
                    HidController.encode_and_send_mouse("X999X772")
                else:
                    HidController.encode_and_send_mouse("X999X120")
                    spin_counter = 0

            else:
                #no_target = True
                #if spin_counter != 0:
                #    spins_needed = 11 - spin_counter
                #    spins = ""
                #    for _x in range(spins_needed):
                        #spins += "X999X772"
                #        spins += "X966"
                #    encode_and_send_mouse(spins)
                #    spin_counter = 0
                if spin_counter != 0:
                    no_target = False
                    spin_counter += 1
                    if spin_counter == 6:
                        spin_counter = 0
                    HidController.encode_and_send_mouse("X999X772")
                else:
                    no_target = True
        else:
            #if alt_profile:
            allow_mouse_inputs = False
            #else:
                #allow_mouse_inputs = True

            x_dis = target[0] - center[0]
            y_dis = target[1] - center[1]

            #print(x_dis)

            abs_x_dis = math.fabs(x_dis)
            abs_y_dis = math.fabs(y_dis)

            #if tracking_range == 0:
            #    if abs_x_dis > 5 and abs_x_dis < 20:
                  #tim = (time.time() - last_time_main)
                    #print(tim)
            #        abs_x_dis = abs_x_dis * 2 #3 * (tim*100)

            #PredictionEngine.add_cords_for_prediction(x_dis)

            #if HidController.check_mouse_click(wepprofile) is True:  # abs_x_dis > 2 or abs_y_dis > 2 and
                # print(abs_x_dis, abs_y_dis)

            if wepprofile.auto_scope:  # and tracking_range < 2:
                scope_state = HidController.hold_scope(scope_state)

            # abs_x_dis = math.ceil(abs_x_dis * 0.55)  # * 0.52) .51 was okay # 0.515 better # 0.52 better
            # abs_y_dis = math.ceil(abs_y_dis * 0.55)  # * 0.52)
            # if tracking_range < 2:
            #    abs_x_dis = int(abs_x_dis * 0.9)   # 0.49 best one s0 far  # 45 is more accurate in high fps,
            #                                        # but requires multiple itterations maybe
            #    abs_y_dis = int(abs_y_dis * 2)  # * 1)  # 82
            # else:
            cmc = HidController.check_mouse_click(wepprofile)
            if cmc or predictive_smoothing is False or tracking_range > 0:# or tracking_range == 1:
                abs_x_dis = round(abs_x_dis * 2.124)  # 2.124  # 1.062# 1.062 #1.124 was good when lagging # 1.07 good for close# * 0.54) # * 0.52) .51 was okay # 0.515 better # 0.52 better
                abs_y_dis = round(abs_y_dis * 2.124)  # 2.124  # 2.08  # * 0.6)  # * 0.52)
                #ssh_x_mouse = round(x_dis * 2.124)
                #ssh_y_mouse = round(y_dis * 2.124)
            else:
                abs_x_dis = round(abs_x_dis * 1.7)  # 1.5 is good too # 1.4 good but wonky
                abs_y_dis = round(abs_y_dis)

            if abs_x_dis > 999:
                abs_x_dis = 999
            if abs_y_dis > 999:
                abs_y_dis = 999

            cords = ""

            #print(ssh_x_mouse)

            if x_dis > 0:
                cords += HidController.parse_cords("X", abs_x_dis)
            else:
                cords += HidController.parse_cords("C", abs_x_dis)

            if y_dis > 0:
                cords += HidController.parse_cords("Y", abs_y_dis)
            else:
                cords += HidController.parse_cords("U", abs_y_dis)

            #ssh_x_mouse = "1"
            #ssh_y_mouse = "0"

            #print(str(cords))

            #HidController.ssh_move(ssh_x_mouse, ssh_y_mouse)
            HidController.encode_and_send_mouse(cords)

            if allow_tracking_resize:
                if alt_profile:
                    tracking_range = 0
                else:
                    tracking_range = 1

            #print("height: " + str(en_height) + " X_Dis: " + str(x_dis))

            if cmc:
                if alt_profile:
                    if deep_tracking_ms > enemy_seen_delay_ms:  # > for if range < 2 and >= for insta shoot
                        #HidController.simple_predictive_aim(abs_x_dis, x_dis, en_height)
                        #HidController.physics_predictive_aim(abs_x_dis, x_dis, True)
                        is_shooting = HidController.arduino_tap_shoot(is_shooting)
                        tracking_range = 2
                        HidController.reset_tracking_timers()
                else:
                    if tracking_range < 2:
                        if enemy_seen_delay_ms == enemy_seen_delay_ms_still:
                            if deep_tracking_ms > 50:
                                HidController.simple_predictive_aim(abs_x_dis, x_dis, en_height)
                            #HidController.physics_predictive_aim(abs_x_dis, x_dis, False)
                            is_shooting = HidController.arduino_shoot_no_dup(is_shooting)
                        else:
                            if en_height > 65 and deep_tracking_ms > 50:
                                HidController.simple_predictive_aim(abs_x_dis, x_dis, en_height)
                                #HidController.physics_predictive_aim(abs_x_dis, x_dis, False)
                                is_shooting = HidController.arduino_shoot_no_dup(is_shooting)
                            elif deep_tracking_ms > 125:  # 175
                                HidController.simple_predictive_aim(abs_x_dis, x_dis, en_height)
                                ##HidController.physics_predictive_aim(abs_x_dis, x_dis, False)
                                is_shooting = HidController.arduino_shoot_no_dup(is_shooting)

            blocking_during_scan = False
            #print(deep_tracking_ms)
            if alt_profile:
                #if deep_tracking_ms > (enemy_seen_delay_ms + 50):
                    #tracking_range = 2
                    #HidController.reset_tracking_timers()
                if cmc or HidController.time_after_last_shot() > (wepprofile.shoot_cd - 0.025):# and alt_profile: #0.50 for better accuracy
                    if keyboard.is_pressed('a'):
                        right_is_pressed = HidController.move_right_press(right_is_pressed)
                    else:
                        right_is_pressed = HidController.move_right_released(right_is_pressed)

                    if keyboard.is_pressed('d'):
                        left_is_pressed = HidController.move_left_press(left_is_pressed)
                    else:
                        left_is_pressed = HidController.move_left_released(left_is_pressed)

                    if keyboard.is_pressed('w'):
                        down_is_pressed = HidController.move_down_press(down_is_pressed)
                    else:
                        down_is_pressed = HidController.move_down_released(down_is_pressed)

                    if keyboard.is_pressed('s'):
                        up_is_pressed = HidController.move_up_press(up_is_pressed)
                    else:
                        up_is_pressed = HidController.move_up_released(up_is_pressed)
                else:
                    up_is_pressed = HidController.move_up_released(up_is_pressed)
                    down_is_pressed = HidController.move_down_released(down_is_pressed)
                    left_is_pressed = HidController.move_left_released(left_is_pressed)
                    right_is_pressed = HidController.move_right_released(right_is_pressed)
                walk_is_pressed = HidController.walk_released(walk_is_pressed)
            else:
                walk_is_pressed = HidController.walk_press(walk_is_pressed)
                if deep_tracking_ms < enemy_seen_delay_ms:
                    if keyboard.is_pressed('a'):
                        right_is_pressed = HidController.move_right_press(right_is_pressed)
                    else:
                        right_is_pressed = HidController.move_right_released(right_is_pressed)

                    if keyboard.is_pressed('d'):
                        left_is_pressed = HidController.move_left_press(left_is_pressed)
                    else:
                        left_is_pressed = HidController.move_left_released(left_is_pressed)

                    if keyboard.is_pressed('w'):
                        down_is_pressed = HidController.move_down_press(down_is_pressed)
                    else:
                        down_is_pressed = HidController.move_down_released(down_is_pressed)

                    if keyboard.is_pressed('s'):
                        up_is_pressed = HidController.move_up_press(up_is_pressed)
                    else:
                        up_is_pressed = HidController.move_up_released(up_is_pressed)
                else:
                    up_is_pressed = HidController.move_up_released(up_is_pressed)
                    down_is_pressed = HidController.move_down_released(down_is_pressed)
                    left_is_pressed = HidController.move_left_released(left_is_pressed)
                    right_is_pressed = HidController.move_right_released(right_is_pressed)

            spin_counter = 0
            no_target = False
        # return False

            # > 60 medium far
            # > 70 medium
            # > 90 medium close
            # > 120 or > 140 close
            # 100 to 122 cap when head target
            # 165 when full auto

            # target crouching reduces height by ~15%

            # Dis: 85, standstill: 0 ~ 4, running: 10 ~ 15 | 5.666666 | 0.1764
            # Dis: 90, standstill: 0 ~ 4, running: 10 ~ 17 | 5.222222 | 0.1888
            # Dis: 120, standstill: 0 ~ 4, running: 11 ~ 30 | 4       | 0.25

            # suggested ratio: 0.1411 for movment determination

    @staticmethod
    def move_to_target_passive(target, center, wepprofile, alt_profile, en_height, lock):

        global scope_state
        global tracking_range
        global aim_down_activation_threshold
        global no_target
        global spin_bot
        global spin_counter
        global up_is_pressed
        global down_is_pressed
        global left_is_pressed
        global right_is_pressed
        global walk_is_pressed
        # global blocking_during_scan
        global allow_mouse_inputs
        global is_shooting
        global manual_shooting
        #global skip_move_counter

        if target[0] is None:  # Pass through Mouse?
            allow_mouse_inputs = True
            #skip_move_counter = 0
            HidController.reset_tracking_timers()

            if manual_shooting:
                is_shooting = HidController.arduino_shoot_no_dup(is_shooting)
            else:
                is_shooting = HidController.arduino_unshoot(is_shooting)

            if manual_scope:
                scope_state = HidController.hold_scope(scope_state)
            else:
                scope_state = HidController.release_scope(scope_state)
        else:
            x_dis = target[0] - center[0]
            y_dis = target[1] - center[1]
            abs_x_dis = math.fabs(x_dis)
            abs_y_dis = math.fabs(y_dis)

            #cmc = HidController.check_mouse_click(wepprofile)
            #if cmc or predictive_smoothing is False or tracking_range > 0:  # or tracking_range == 1:
            #if is_shooting is False:
            abs_x_dis = round(abs_x_dis * 2.124)
            abs_y_dis = round(abs_y_dis * 2.124)# * 0.75)
            #else:
            #    abs_x_dis = round(abs_x_dis * 1.124)
            #    abs_y_dis = round(abs_y_dis * 1.124)

            if abs_x_dis > 999:
                abs_x_dis = 999
            if abs_y_dis > 999:
                abs_y_dis = 999

            # abs_x_dis_rev = abs_x_dis

            #if abs_x_dis_rev > 20:
            #    abs_x_dis_rev = 20
            #else:
            #    abs_x_dis_rev = 0

            cords = ""
            cords_rev = ""

            if lock is True:
                x_rev = 0.5
                y_rev = 0.8
            else:
                x_rev = 1
                y_rev = 1

            if x_dis > 0:
                cords += HidController.parse_cords("X", abs_x_dis)
                cords_rev += HidController.parse_cords("C", abs_x_dis * x_rev)#- abs_x_dis_rev)
            else:
                cords += HidController.parse_cords("C", abs_x_dis)
                cords_rev += HidController.parse_cords("X", abs_x_dis * x_rev)#- abs_x_dis_rev)

            if y_dis > 0:
                cords += HidController.parse_cords("Y", abs_y_dis)
                cords_rev += HidController.parse_cords("U", abs_y_dis * y_rev)
            else:
                cords += HidController.parse_cords("U", abs_y_dis)
                cords_rev += HidController.parse_cords("Y", abs_y_dis * y_rev)
  
            if manual_scope:
                if scope_state is False and lock is True:
                    HidController.encode_and_send_mouse(cords)
                    cords = None
                    cords_rev = None
                scope_state = HidController.hold_scope(scope_state)
            else:
                scope_state = HidController.release_scope(scope_state)

            if manual_shooting or spin_bot:
                #if lock is True:
                allow_mouse_inputs = False
                #else:
                    #allow_mouse_inputs = True
                HidController.MouseBuffer.playback()
                HidController.MouseBuffer.reset()
                if lock is False:
                    allow_mouse_inputs = True

                if cords is not None:# and skip_move_counter == 0:
                    HidController.encode_and_send_mouse(cords)
                is_shooting = HidController.arduino_shoot(is_shooting)
                #is_shooting = HidController.arduino_shoot_no_dup(is_shooting)
                if cords_rev is not None:
                    HidController.encode_and_send_mouse(cords_rev)
                #HidController.encode_and_send_mouse(cords)
                walk_is_pressed = HidController.walk_press(walk_is_pressed)
                if keyboard.is_pressed('a'):
                    right_is_pressed = HidController.move_right_press(right_is_pressed)
                else:
                    right_is_pressed = HidController.move_right_released(right_is_pressed)

                if keyboard.is_pressed('d'):
                    left_is_pressed = HidController.move_left_press(left_is_pressed)
                else:
                    left_is_pressed = HidController.move_left_released(left_is_pressed)

                if keyboard.is_pressed('w'):
                    down_is_pressed = HidController.move_down_press(down_is_pressed)
                else:
                    down_is_pressed = HidController.move_down_released(down_is_pressed)

                if keyboard.is_pressed('s'):
                    up_is_pressed = HidController.move_up_press(up_is_pressed)
                else:
                    up_is_pressed = HidController.move_up_released(up_is_pressed)
                #skip_move_counter += 1
                #if skip_move_counter > 3:
                #    skip_move_counter = 0
            else:
                allow_mouse_inputs = True
                is_shooting = HidController.arduino_unshoot(is_shooting)
                up_is_pressed = HidController.move_up_released(up_is_pressed)
                down_is_pressed = HidController.move_down_released(down_is_pressed)
                left_is_pressed = HidController.move_left_released(left_is_pressed)
                right_is_pressed = HidController.move_right_released(right_is_pressed)
                walk_is_pressed = HidController.walk_released(walk_is_pressed)
                #skip_move_counter = 0

            spin_counter = 0
            no_target = False

    @staticmethod
    def simple_predictive_aim(abs_x_dis, x_dis, height):
        global frame_delay_options
        global frame_delay
        global prediction_ratio
        global prediction_selector
        #print("height: " + str(height))
        if prediction_selector == 3:
            return  # [1, 1.5, 2, 0.00001]
        #elif prediction_ratio[prediction_selector] == 2:
            #movement check?
        if x_dis == 0:
            return
        #if (height * 0.141176) < abs_x_dis:
        #if height > 70 and 11 < abs_x_dis:  # engage prediction
        frame = frame_delay_options[frame_delay]/20
        if height > 50 and (height * 0.141176 * frame) < abs_x_dis:  # engage prediction
            mov_dist = height * 0.25 * frame
            if mov_dist > 999:
                return
            if x_dis > 0:
                HidController.encode_and_send_mouse(HidController.parse_cords("X", mov_dist))
            else:
                HidController.encode_and_send_mouse(HidController.parse_cords("C", mov_dist))
            print("Engaged_Prediction: " + str(mov_dist))

    @staticmethod
    def physics_predictive_aim(abs_x_dis, x_dis, take_prev_time):
        global last_time_main
        global frame_delay_options
        global frame_delay
        global prediction_ratio
        global prediction_selector
        global prediction_scalar
        global prediction_scalar_selector
        global previous_process_time
        # testing done at capping 120 fps
        # if en_height > 65:
        if abs_x_dis >= (frame_delay_options[frame_delay]/prediction_ratio[prediction_selector]):  # 10 at 20ms
            if take_prev_time:
                mov_vel = abs_x_dis / (previous_process_time + frame_delay_options[frame_delay])  # s = d/t
            else:
                mov_vel = abs_x_dis / (frame_delay_options[frame_delay])  # s = d/t
            proc_tim = (time.time() - last_time_main) * 1000
            mov_dist = mov_vel * proc_tim  # d = s * t
            mov_dist = round(mov_dist * prediction_scalar[prediction_scalar_selector])  # * 2.124 * 2)
            if mov_dist != 0:
                if mov_dist > 100:
                    return
                    #mov_dist = 0
                if x_dis > 0:
                    HidController.encode_and_send_mouse(HidController.parse_cords("X", mov_dist))
                else:
                    HidController.encode_and_send_mouse(HidController.parse_cords("C", mov_dist))
                print("Base: " + str(abs_x_dis) + " | Time: " + str(proc_tim) + " | Result: " + str(mov_dist))

    @staticmethod
    def ssh_move(x, y):
        max_int = 254  # 255

        max_int_x = max_int
        max_int_y = max_int

        if x < 0:
            max_int_x = -1 * max_int
        if y < 0:
            max_int_y = -1 * max_int

        if x == 0 and y == 0:
            return

        x_iter = math.floor(x / max_int_x)
        x_rem = x % max_int

        y_iter = math.floor(y / max_int_y)
        y_rem = y % max_int

        if x > y:
            length = x_iter
        else:
            length = y_iter

        if x_rem != 0 or y_rem != 0:
            length += 1

        for o in range(length):
            x_in = 0
            y_in = 0

            # print("o val: " + str(o) + "x_iter: " + str(x_iter) + " y_iter: " + str(y_iter))

            if x_iter > o:
                x_in = max_int_x
            elif x_iter == o:
                x_in = x_rem

            if y_iter > o:
                y_in = max_int_y
            elif y_iter == o:
                y_in = y_rem

            print("cords: " + str(x_in) + ", " + str(y_in))
            # UNCOMMENT
            #ssh.exec_command("virsh -c qemu:///system qemu-monitor-command Valorant-001 mouse_move " + str(x_in) + " " + str(y_in) +" --hmp")

# Serial Communication
    @staticmethod
    def encode_and_send_mouse(str_en):
        serMouse.write(str(str_en).encode())
        #pass

    @staticmethod
    def encode_and_send_keyboard(str_en):
        serKeyboard.write(str(str_en).encode())

    @staticmethod
    def parse_cords(sign, value):
        value = str(value)
        cords = str(sign + (value.zfill(3)))
        return cords


# Shooting
    @staticmethod
    def arduino_shoot(is_shooting):
        if is_shooting is False:
            #if keyboard.is_pressed("["):
            #    return
            #encode_and_send("S050B000A000")
            HidController.encode_and_send_mouse("A000")
            HidController.reset_mouse_after_shoot()
            # CODE TO AIM DOWN MORE PER SHOT?!
            return True
        else:
            HidController.encode_and_send_mouse("B000A000")
            HidController.reset_mouse_after_shoot()
            return True

    @staticmethod
    def arduino_shoot_no_dup(is_shooting):
        HidController.encode_and_send_mouse("A000") # no dupe
        #HidController.encode_and_send_mouse("B000A000")
        HidController.reset_mouse_after_shoot()
        # CODE TO AIM DOWN MORE PER SHOT?!
        return True

    @staticmethod
    def arduino_unshoot(is_shooting):
        if is_shooting is True:
            HidController.encode_and_send_mouse("B000")
            # CODE TO RESET AIM DOWN!
            return False
        return is_shooting

    @staticmethod
    def arduino_tap_shoot(is_shooting):

        #if keyboard.is_pressed("["):
        #    return
        #encode_and_send("S050B000A000B000")
        HidController.encode_and_send_mouse("B000A000B000")
        HidController.reset_mouse_after_shoot()
        return False
        # CODE TO AIM DOWN MORE PER SHOT?!
        # return is_shooting

    @staticmethod
    def hold_scope(scope_state):
        if scope_state is False:
            # pyautogui.mouseDown(button='right')
            HidController.encode_and_send_mouse("D000")
            return True
        return scope_state

    @staticmethod
    def release_scope(scope_state):
        if scope_state is True:
            # pyautogui.mouseUp(button='right')
            HidController.encode_and_send_mouse("E000")
            return False
        return scope_state

    @staticmethod
    def reset_mouse():
        # global cd_time
        global cd_burst_time
        global burstcount
        global is_shooting

        burstcount = 0
        cd_burst_time = time.time()
        is_shooting = False

    @staticmethod
    def reset_mouse_after_shoot():
        global cd_time
        global cd_burst_time
        global burstcount

        cd_time = time.time()
        cd_burst_time = time.time()
        burstcount += 1

    @staticmethod
    def check_mouse_click(wepprofile):
        global cd_time
        global cd_burst_time
        global burstcount

        #if keyboard.is_pressed("["):  # or tracking_range >= 3:  # or keyboard.is_pressed(""):
        #    return False
        if (time.time() - cd_time) > wepprofile.shoot_cd:
            return True
        return False

    @staticmethod
    def time_after_last_shot():
        global cd_time
        return (time.time() - cd_time)

# Moving
    @staticmethod
    def move_up_press(is_pressed):
        if is_pressed is False:
            # pyautogui.keyDown("Up")
            HidController.encode_and_send_keyboard("A")
            return True
        return is_pressed

    @staticmethod
    def move_down_press(is_pressed):
        if is_pressed is False:
            # pyautogui.keyDown("Down")
            HidController.encode_and_send_keyboard("B")
            return True
        return is_pressed

    @staticmethod
    def move_left_press(is_pressed):
        if is_pressed is False:
            # pyautogui.keyDown("Left")
            HidController.encode_and_send_keyboard("C")
            return True
        return is_pressed

    @staticmethod
    def move_right_press(is_pressed):
        if is_pressed is False:
            # pyautogui.keyDown("Right")
            HidController.encode_and_send_keyboard("D")
            return True
        return is_pressed

    @staticmethod
    def walk_press(is_pressed):
        if is_pressed is False:
            # pyautogui.keyDown('p')
            HidController.encode_and_send_keyboard("E")
            return True
        return is_pressed

    @staticmethod
    def move_up_released(is_pressed):
        if is_pressed is True:
            # pyautogui.keyUp("Up")
            HidController.encode_and_send_keyboard("G")
            return False
        return is_pressed

    @staticmethod
    def move_down_released(is_pressed):
        if is_pressed is True:
            # pyautogui.keyUp("Down")
            HidController.encode_and_send_keyboard("H")
            return False
        return is_pressed

    @staticmethod
    def move_left_released(is_pressed):
        if is_pressed is True:
            # pyautogui.keyUp("Left")
            HidController.encode_and_send_keyboard("I")
            return False
        return is_pressed

    @staticmethod
    def move_right_released(is_pressed):
        if is_pressed is True:
            # pyautogui.keyUp("Right")
            HidController.encode_and_send_keyboard("J")
            return False
        return is_pressed

    @staticmethod
    def walk_released(is_pressed):
        if is_pressed is True:
            # pyautogui.keyUp('p')
            HidController.encode_and_send_keyboard("K")
            return False
        return is_pressed

    class MouseBuffer:
        buffer = []

        @staticmethod
        def add(cords):
            if cords[0] == "X" or cords[0] == "Y" or cords[0] == "C" or cords[0] == "U":
                HidController.MouseBuffer.buffer.append(cords)

        @staticmethod
        def reset():
            HidController.MouseBuffer.buffer = []

        @staticmethod
        def playback():
            for x in HidController.MouseBuffer.buffer:
                x = x.replace("C","J")
                x = x.replace("U","K")
                x = x.replace("X","C")
                x = x.replace("Y","U")
                x = x.replace("J","X")
                x = x.replace("K","Y")
                HidController.encode_and_send_mouse(x)

# Threading
    @staticmethod
    def mouse_relay():
        global allow_mouse_inputs
        global blocking_during_scan
        global temp_pause
        global spin_bot
        global manual_shooting
        global manual_scope

        while True:
            #print("x")
            #while blocking_during_scan:
                #pass
            # s.sendto(message.encode('utf-8'), server)
            data, addr = s.recvfrom(1024)
            data = data.decode('utf-8')
            if data == "PAUS":
                temp_pause = True
            elif data == "UPAU":
                temp_pause = False
            elif data == "RHTD":
                # pyautogui.keyDown('o')
                # HidController.encode_and_send_keyboard("F")
                if is_using_passive_aim is False:
                    serKeyboard.write(str("F").encode())  # O Key
                manual_scope = True
            elif data == "RHTU":

                # HidController.encode_and_send_keyboard("L")
                if is_using_passive_aim is False:
                    serKeyboard.write(str("L").encode())  # O Key
                manual_scope = False
            elif data == "SPND":
                spin_bot = True
            elif data == "SPNU":
                spin_bot = False
            else:
                if is_using_passive_aim:
                    if data == "A000":
                        manual_shooting = True
                        data = ""
                    elif data == "B000":
                        manual_shooting = False
                        data = ""
                if allow_mouse_inputs:
                    # print("Received from server: " + data)
                    if data != "":
                        serMouse.write(str(data).encode())
                        HidController.MouseBuffer.add(data)
                    #print(allow_mouse_inputs)
            # time.sleep(0.001)
            # message = input("-> ")

    @staticmethod
    def reset_tracking_timers():
        global up_is_pressed
        global down_is_pressed
        global left_is_pressed
        global right_is_pressed
        global walk_is_pressed
        global deep_tracking_ms
        global last_deep_tracking_ms

        up_is_pressed = HidController.move_up_released(up_is_pressed)
        down_is_pressed = HidController.move_down_released(down_is_pressed)
        left_is_pressed = HidController.move_left_released(left_is_pressed)
        right_is_pressed = HidController.move_right_released(right_is_pressed)
        walk_is_pressed = HidController.walk_released(walk_is_pressed)
        # non_track_counter = 0
        deep_tracking_ms = 0
        last_deep_tracking_ms = time.time()

#cv2.floodFill(mask,mask1,(0,0),255)

# Runtime
mon = MonitorProcessing.monitor_pre_cal(monitor_width, monitor_height)
subwepprofile = WeaponProfiles.HeadShot.Guardian
mainwepprofile = WeaponProfiles.BodyShot.Guardian
wepprofile = mainwepprofile
img_cords = ImageProcessing.ImageCords()

print(serMouse.name)
print(serKeyboard.name)
_thread.start_new_thread(HidController.mouse_relay, ())
print("Thread Started")
#try:
#    print("Starting Mouse Relay Thread")
#    thread.start_new_thread(mouse_relay)
#except:
#    print("Cannot Start Thread")
#kill_mon = MonitorProcessing.monitor_kill_indicators(monitor_width, monitor_height)
kill_mon = MonitorProcessing.monitor_indicators_zone(monitor_width, monitor_height)
kill_last = False
kill_cnt = 0

#skip_move_counter = 0
#if use_d3d is True:
#    print("Using D3D")
#    d = d3dshot.create(capture_output="numpy")
#else:
#    print("Using MSS")

with mss.mss() as sct:
    settings_mask = ImageProcessing.Filtering.test(tracking_range, Colors.purple, 1)
    while True:
        if temp_pause or paused or keyboard.is_pressed("Tab"):  # or keyboard.is_pressed("]") or keyboard.is_pressed("[")
            allow_mouse_inputs = True
            was_in_paused_state = True
            spin_counter = 0

            if keyboard.is_pressed("esc"):
                paused = False
                is_using_passive_aim = False
            elif keyboard.is_pressed("F1"):
                paused = False
                is_using_passive_aim = True
                is_using_passive_aim_lock = True
            elif keyboard.is_pressed("F2"):
                paused = False
                is_using_passive_aim = True
                is_using_passive_aim_lock = False
            tracking_range = 3

            is_shooting = HidController.arduino_unshoot(is_shooting)
            HidController.reset_mouse()
            HidController.reset_tracking_timers()
            #scope_state = releasescope()

            up_is_pressed = HidController.move_up_released(up_is_pressed)
            down_is_pressed = HidController.move_down_released(down_is_pressed)
            left_is_pressed = HidController.move_left_released(left_is_pressed)
            right_is_pressed = HidController.move_right_released(right_is_pressed)
            walk_is_pressed = HidController.walk_released(walk_is_pressed)
            # print("No Target")

            passive_hold_shoot_timer = (time.time() - passive_hold_shoot_timer)
            passive_shoot_offset -= passive_hold_shoot_timer * 125
            if passive_shoot_offset < -40:
                passive_shoot_offset = -40
            if passive_shoot_offset < 0 or wepprofile.aim_down_offset_y == 0 or alt_profile:
                passive_shoot_offset_apply = 0
            else:
                passive_shoot_offset_apply = passive_shoot_offset
            passive_hold_shoot_timer = time.time()

            if keyboard.is_pressed('`'):
                editing_selected = False
                paused = True

            # if wepprofile.auto_scope and scope_state is True:  # and tracking_range >= 3:
            # if scope_state is True:  # and tracking_range >= 3:
            scope_state = HidController.release_scope(scope_state)

            mask = ImageProcessing.Filtering.test(tracking_range, Colors.purple, 0)
            #mask = settings_mask.copy()

            if keyboard.is_pressed("-"):
                editing_selected = True

            if editing_selected:
                if keyboard.is_pressed("m"):
                    editing_selected = False
                elif keyboard.is_pressed('Tab'):
                    if keyboard.is_pressed('1'):
                        subwepprofile = WeaponProfiles.HeadShot.GuardianNoXOffset
                        mainwepprofile = WeaponProfiles.BodyShot.Guardian
                    elif keyboard.is_pressed('2'):
                        subwepprofile = WeaponProfiles.HeadShot.Guardian
                        mainwepprofile = WeaponProfiles.BodyShot.Guardian
                    elif keyboard.is_pressed('3'):
                        subwepprofile = WeaponProfiles.HeadShot.GuardianZoom
                        mainwepprofile = WeaponProfiles.BodyShot.Guardian
                    elif keyboard.is_pressed('4'):
                        subwepprofile = WeaponProfiles.HeadShot.GuardianZoom
                        mainwepprofile = WeaponProfiles.BodyShot.GuardianZoom
                    elif keyboard.is_pressed('5'):
                        subwepprofile = WeaponProfiles.HeadShot.Sheriff
                        mainwepprofile = WeaponProfiles.BodyShot.Guardian
                    elif keyboard.is_pressed('6'):
                        subwepprofile = WeaponProfiles.HeadShot.Guardian
                        mainwepprofile = WeaponProfiles.BodyShot.Guardian
                    elif keyboard.is_pressed('7'):
                        subwepprofile = WeaponProfiles.HeadShot.Guardian
                        mainwepprofile = WeaponProfiles.BodyShot.Guardian
                    elif keyboard.is_pressed('8'):
                        subwepprofile = WeaponProfiles.HeadShot.Guardian
                        mainwepprofile = WeaponProfiles.BodyShot.Guardian
                    elif keyboard.is_pressed('9'):
                        subwepprofile = WeaponProfiles.HeadShot.Guardian
                        mainwepprofile = WeaponProfiles.BodyShot.Guardian
                    elif keyboard.is_pressed('0'):
                        subwepprofile = WeaponProfiles.HeadShot.Guardian
                        mainwepprofile = WeaponProfiles.BodyShot.Guardian
                elif keyboard.is_pressed("1"):
                    frame_delay = 0
                elif keyboard.is_pressed("2"):
                    frame_delay = 1
                elif keyboard.is_pressed("3"):
                    frame_delay = 2
                elif keyboard.is_pressed("4"):
                    frame_delay = 3
                elif keyboard.is_pressed("5"):
                    frame_delay = 4
                elif keyboard.is_pressed("7"):
                    prediction_selector = 0
                elif keyboard.is_pressed("8"):
                    prediction_selector = 1
                elif keyboard.is_pressed("9"):
                    prediction_selector = 2
                elif keyboard.is_pressed("0"):
                    prediction_selector = 3

                elif keyboard.is_pressed("["):
                    prediction_scalar_selector = 0
                elif keyboard.is_pressed("]"):
                    prediction_scalar_selector = 1

                elif keyboard.is_pressed("k"):
                    #predictive_smoothing = True
                    filter_selector = 0
                elif keyboard.is_pressed("l"):
                    #predictive_smoothing = False
                    filter_selector = 1
                elif keyboard.is_pressed(":"):
                    filter_selector = 2
                elif keyboard.is_pressed("i"):
                    distance_selector = 0
                elif keyboard.is_pressed("o"):
                    distance_selector = 1
                elif keyboard.is_pressed("p"):
                    distance_selector = 2
                elif keyboard.is_pressed("h"):
                    target_nearest_post_paused_state = True
                elif keyboard.is_pressed("j"):
                    target_nearest_post_paused_state = False
                #elif keyboard.is_pressed("u"):
                #    enemy_seen_delay_ms_default = 125
                #elif keyboard.is_pressed("i"):
                #    enemy_seen_delay_ms_default = 0

                mask = ImageProcessing.apply_text(mask, subactive + "[Tab + 1-9] Profile-Sub: " + str(subwepprofile),
                                 "[Tab + 1-9] Profile: "+ str(mainwepprofile),
                                 "[H/J] Target Close After Paused: " + str(target_nearest_post_paused_state) +
                                 " | [I/O/P] Aim Adjustment: " + str(distance_names[distance_selector]) +
                                 " | [7-0] Prediction: " + str(prediction_ratio[prediction_selector]) +
                                 " | [[/]] Pred-Scalar: " + str(prediction_scalar[prediction_scalar_selector]),
                                 "[1-5] Target Delay: " + str(frame_delay_options[frame_delay]) +
                                 #" | [K/L] Overshoot: " + str(predictive_smoothing) +
                                 " | [K/L/:] Filter: " + str(filter_names[filter_selector])
                                 #" | [O/P] Passive Mode: " + str(passive_mode) +
                                 , "Paused: [esc] to Resume | [M] to leave edit", tracking_range)

            else:
                mask = ImageProcessing.apply_text(mask, subactive + "Profile-Sub: " + str(subwepprofile), "Profile: "
                                 + str(mainwepprofile),
                                 "Aim Adjustment: " + str(distance_names[distance_selector]) +
                                 " | Prediction: " + str(prediction_ratio[prediction_selector]) +
                                 " | Pred-Scalar: " + str(prediction_scalar[prediction_scalar_selector]),
                                 "Target Delay: " + str(frame_delay_options[frame_delay]) +
                                 #" | Overshoot: " + str(predictive_smoothing) +
                                 " | Filter: " + str(filter_names[filter_selector]) +
                                 #" | Passive Mode: " + str(passive_mode) +
                                 " | Target Close After Paused: " + str(target_nearest_post_paused_state)
                                 , "Paused: [esc] to Resume | [-] to edit", tracking_range)

            cv2.imshow("Setura", mask)

            cv2.waitKey(1)
            cv2.waitKey(750)

            if keyboard.is_pressed('='):
                #c.close()
                cv2.destroyAllWindows()
                break
        elif is_using_passive_aim is False:  # non passive
# Should it target nearest to cursor after pause key hit??
            if was_in_paused_state and target_nearest_post_paused_state:
                was_in_paused_state = False
                #non_track_counter = 0
                deep_tracking_ms = 0
                last_deep_tracking_ms = time.time()
                if alt_profile:
                    tracking_range = 0
                else:
                    tracking_range = 1
# Mouse Buffer
            if allow_mouse_inputs is False:
                HidController.MouseBuffer.playback()
            HidController.MouseBuffer.reset()
# Scan
            last_time_main = time.time()  # timing
            blocking_during_scan = True
            #tracking_range = 0

            if tracking_range < 2:
                deep_tracking_ms += ((time.time() - last_deep_tracking_ms) * 1000)
                last_deep_tracking_ms = time.time()
                if filter_selector == 0:
                    mask = ImageProcessing.Filtering.advanced_split_standard(tracking_range, Colors.antiphoenix, 20, 0, 20)
                elif filter_selector == 1:
                    mask = ImageProcessing.Filtering.advanced_split_standard_3(tracking_range, Colors.primary, 10, 10, 20)
                elif filter_selector == 2:
                    mask = ImageProcessing.Filtering.advanced_split_standard_3(tracking_range, Colors.primary, 10, 10, 20)

            else:
                # mask = ImageProcessing.Filtering.aggressive(tracking_range, Colors.purple)
                if filter_selector == 0:
                    mask = ImageProcessing.Filtering.aggressive(tracking_range, Colors.purple)
                elif filter_selector == 1:
                    mask = ImageProcessing.Filtering.aggressive(tracking_range, Colors.primary)
                    # mask = ImageProcessing.Filtering.advanced_split_standard(tracking_range, Colors.antiphoenix, 20, 0, 20)
                elif filter_selector == 2:
                    # mask = ImageProcessing.Filtering.aggressive(tracking_range, Colors.purple)
                    # mask = ImageProcessing.Filtering.advanced_split_standard_3(tracking_range, Colors.primary, 10, 10, 20)
                    mask = ImageProcessing.Filtering.advanced_split_aggressive(tracking_range, Colors.primary, 10, 10,
                                                                               20)

            img_cords, scope_state, en_height = ImageSearch.find_first_pixel_npy_argmax(mask, wepprofile, tracking_range, mon, scope_state)

            # last_time_main = time.time()  # timing

            HidController.move_to_target(img_cords.cords, (mon[tracking_range].res_w, mon[tracking_range].res_h -
                                             passive_shoot_offset_apply), wepprofile,
                           allow_tracking_resize, alt_profile, predictive_smoothing, deep_tracking_ms, enemy_seen_delay_ms, en_height)

            previous_process_time = (time.time() - last_time_main)  # timing
            last_time_main = time.time()
            #if tracking_range == 0:
             #   print(n)

            blocking_during_scan = False

            mask = img_cords.img
# Initial KeyPress Checker
            if keyboard.is_pressed("Shift"):
                wepprofile = subwepprofile
                if alt_profile is False and (wepprofile.auto_scope_adv is False or wepprofile.auto_scope is False):
                    scope_state = HidController.release_scope(scope_state)
                alt_profile = True
                mainactive = ""
                subactive = "[ON]"
            else:
                wepprofile = mainwepprofile
                if alt_profile is True and (wepprofile.auto_scope_adv is False or wepprofile.auto_scope is False):
                    scope_state = HidController.release_scope(scope_state)
                alt_profile = False
                mainactive = "[ON]"
                subactive = ""

            if keyboard.is_pressed('a') or keyboard.is_pressed('d') or keyboard.is_pressed('w') or keyboard.is_pressed('s'):
                if alt_profile:
                    enemy_seen_delay_ms = enemy_seen_delay_ms_walk
                else:
                    enemy_seen_delay_ms = enemy_seen_delay_ms_run
            else:
                enemy_seen_delay_ms = enemy_seen_delay_ms_still
# KeyPress Detection
            if keyboard.is_pressed('`'):
                paused = True
            editing_selected = False
# Aim Down
            passive_hold_shoot_timer = (time.time() - passive_hold_shoot_timer)
            if is_shooting:
                passive_shoot_offset += passive_hold_shoot_timer * 125   # 200 # * wepprofile.moving_aim_down_speed_multiplier # 150
                if passive_shoot_offset > wepprofile.aim_down_offset_y:  # + moving_aim_offset:
                    passive_shoot_offset = wepprofile.aim_down_offset_y  # + moving_aim_offset
            else:
                passive_shoot_offset -= passive_hold_shoot_timer * 100
                if passive_shoot_offset < - 20:  # 40 #-60 #-20 #-40
                    passive_shoot_offset = -20  # 40 #-60 #-20 #-40
            #print(str(passive_shoot_offset))
            if passive_shoot_offset < 0 or wepprofile.aim_down_offset_y == 0 or alt_profile:
                passive_shoot_offset_apply = 0
            else:
                passive_shoot_offset_apply = passive_shoot_offset
            passive_hold_shoot_timer = time.time()
# Kill Scanner
            if tracking_range == 1:
                l2time = time.time()
                new = ImageProcessing.kill_indicator(kill_mon, Colors.kill)
                if new is True and kill_last is False:
                    kill_cnt += 1
                    #print("Kill: " + str(kill_cnt))
                    tracking_range = 3
                kill_last = new
                #print("scan time dif: "+str(time.time() - l2time))
# Display

            mask = ImageProcessing.apply_text(mask, subactive + "Profile-Sub: " + str(subwepprofile), mainactive + "Profile: "
                             + str(mainwepprofile),
                             "Aim Adjustment: " + str(distance_names[distance_selector]) +
                             " | Prediction: " + str(prediction_ratio[prediction_selector]) +
                             " | Pred-Scalar: " + str(prediction_scalar[prediction_scalar_selector]),
                             "Target Delay: " + str(frame_delay_options[frame_delay]) +
                             #" | Overshoot: " + str(predictive_smoothing) +
                             " | Filter: " + str(filter_names[filter_selector]) +
                             #" | Passive Mode: " + str(passive_mode) +
                             " | Target Close After Paused: " + str(target_nearest_post_paused_state)
                             , "timing: " + str(previous_process_time), tracking_range)

            cv2.imshow("Setura", mask)

            proposed_delay = int((frame_delay_options[frame_delay]) - ((time.time() - last_time_main) * 1000))
            if proposed_delay < 1:
                proposed_delay = 1

            #print(proposed_delay)

            if no_target:
                cv2.waitKey(1)
            else:
                cv2.waitKey(proposed_delay)  # 5 is risky #15 was really good, but 5 works now? # 10 # desired_frame_time # 20 edge of good
                cv2.waitKey(750)

            #cv2.waitKey(1000)
        else:
            #if manual_scope:
            #    tracking_range = 8
            #else:
            #    tracking_range = 7
            tracking_range = 8
# Mouse Buffer
            #if allow_mouse_inputs is False:
            #    HidController.MouseBuffer.playback()
            HidController.MouseBuffer.reset()
# Scan
            last_time_main = time.time()  # timing
            blocking_during_scan = True

            #deep_tracking_ms += ((time.time() - last_deep_tracking_ms)*1000)
            #last_deep_tracking_ms = time.time()
            if filter_selector == 0:
                mask = ImageProcessing.Filtering.advanced_split_standard(tracking_range, Colors.antiphoenix, 20, 0, 20)
            elif filter_selector == 1:
                mask = ImageProcessing.Filtering.advanced_split_standard_3(tracking_range, Colors.primary, 10, 10, 20)
            elif filter_selector == 2:
                mask = ImageProcessing.Filtering.advanced_split_standard_3(tracking_range, Colors.primary, 10, 10, 20)

            img_cords, scope_state, en_height = ImageSearch.find_first_pixel_npy_argmax(mask, wepprofile,
                                                                                        tracking_range, mon,
                                                                                        scope_state)

            # last_time_main = time.time()  # timing

            HidController.move_to_target_passive(img_cords.cords, (mon[tracking_range].res_w, mon[tracking_range].res_h -
                                                           passive_shoot_offset_apply), wepprofile, alt_profile, en_height, is_using_passive_aim_lock)

            previous_process_time = (time.time() - last_time_main)  # timing
            last_time_main = time.time()
            # if tracking_range == 0:
            #   print(n)

            blocking_during_scan = False

            mask = img_cords.img
# KeyPress Detection
            if keyboard.is_pressed('`'):
                paused = True
            editing_selected = False
# Aim Down
            passive_hold_shoot_timer = (time.time() - passive_hold_shoot_timer)
            if manual_shooting or spin_bot:
                passive_shoot_offset += passive_hold_shoot_timer * 125  # 200 # * wepprofile.moving_aim_down_speed_multiplier # 150
                if passive_shoot_offset > wepprofile.aim_down_offset_y:  # + moving_aim_offset:
                    passive_shoot_offset = wepprofile.aim_down_offset_y  # + moving_aim_offset
            else:
                passive_shoot_offset -= passive_hold_shoot_timer * 100
                if passive_shoot_offset < -40:  # -60 #-20 #-40
                    passive_shoot_offset = -40  # -60 #-20 #-40
            # print(str(passive_shoot_offset))
            if passive_shoot_offset < 0 or wepprofile.aim_down_offset_y == 0 or alt_profile:
                passive_shoot_offset_apply = 0
            else:
                passive_shoot_offset_apply = passive_shoot_offset
            passive_hold_shoot_timer = time.time()

            # Display

            mask = ImageProcessing.apply_text(mask, subactive + "Profile-Sub: " + str(subwepprofile),
                                              mainactive + "Profile: "
                                              + str(mainwepprofile),
                                              "Aim Adjustment: " + str(distance_names[distance_selector]) +
                                              " | Prediction: " + str(prediction_ratio[prediction_selector]) +
                                              " | Pred-Scalar: " + str(prediction_scalar[prediction_scalar_selector]),
                                              "Target Delay: " + str(frame_delay_options[frame_delay]) +
                                              # " | Overshoot: " + str(predictive_smoothing) +
                                              " | Filter: " + str(filter_names[filter_selector]) +
                                              # " | Passive Mode: " + str(passive_mode) +
                                              " | Target Close After Paused: " + str(target_nearest_post_paused_state)
                                              , "timing: " + str(previous_process_time), tracking_range)

            cv2.imshow("Setura", mask)

            proposed_delay = int((frame_delay_options[frame_delay]) - ((time.time() - last_time_main) * 1000))
            if proposed_delay < 1:
                proposed_delay = 1

            # print(proposed_delay)

            if no_target:
                cv2.waitKey(1)
            else:
                cv2.waitKey(proposed_delay)
                cv2.waitKey(750)




# to do:
# when moving mouse faster than x speed, increase tracking range
# test save movment in buffer and reverse playback it if enemy detected
# test right click stuff

# make aimbot move speed depening on ur moment speed