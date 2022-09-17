import time
import mss
import numpy as np
import cv2
import math
import keyboard
import serial

# Map Size 1.1
# Map Zoom 0.9


ser = serial.Serial('COM6', baudrate=2000000, timeout=1)


def scan_circle(img, radius, x_offset, y_offset):
    for theta in range(360):
        x = int(radius * math.cos(theta)) + x_offset
        y = int(radius * math.sin(theta)) + y_offset
        # mask_marked = cv2.circle(mask_marked, (x, y), 1, (1, 255, 1), 1)
        #print(theta)
        if img[y, x] != 0:
            # print(radius)
            return x, y
    return None


def send_rotation(degree):
    move_per_degree = 10626/360
    move = move_per_degree * degree
    mod = move
    val = 0
    if move > 999:
        val = int(move / 999)
        mod = int(move % 999)

    send_cord = ""

    for n in range(val):
        send_cord += "X999"
    send_cord += parse_cords("X", mod)

    encode_and_send(send_cord)
    # ser.write(str("X999X999X999X999X999X999X999X999X999X999X636").encode())
    # ser.write(str("X999X999X999X999X999X999X999X999X999X999X635").encode()) 35 to 36


def encode_and_send(str_en):
    ser.write(str(str_en).encode())


def parse_cords(sign, value): # Fix Cords in valmain
    value = str(value)
    cords = str(sign + (value.zfill(3)))
    return cords


def map_range(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def angle(point_a, point_b):

    #if point_b[0] - point_a[0] == 0:
    #    b_slope = 0.00000001
    #else:
    #    b_slope = (point_b[0] - point_a[0])
    #slope = (point_b[1] - point_a[1]) / b_slope

    #return math.degrees(math.atan(slope))
    deg = math.degrees(math.atan2((point_b[1] - point_a[1]), (point_b[0] - point_a[0])))
    if deg < 0:
        deg = map_range(deg, -0, -180, 0, 180)
        # deg = map_range(deg, -0, -180, 180, 360)
    else:
        deg = map_range(deg, 0, 180, 360, 180)
        # deg = map_range(deg, 0, 180, 0, 180)
    if deg == 360:
        deg = 0

    return deg


with mss.mss() as sct:
    while True:
        monitor = {"left": 50, "top": 25, "width": 375, "height": 400}
        mask = np.array(sct.grab(monitor))
        mask_marked = mask.copy()
        # mask = cv2.inRange(cv2.cvtColor(np.array(mask), cv2.COLOR_BGR2HSV),
        #                         np.array([29, 80, 220]),
        #                         np.array([30, 100, 255]))
        mask = cv2.inRange(cv2.cvtColor(np.array(mask), cv2.COLOR_BGR2HSV),
                                 np.array([29, 80, 220]),
                                 np.array([30, 100, 255]))

        mask = cv2.dilate(mask, np.ones((2, 2), np.uint8), iterations=1)

        #circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, 20,
        #                           param1=10, param2=15, minRadius=0, maxRadius=0)
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, 20,
                                   param1=1, param2=15, minRadius=0, maxRadius=0)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # draw the outer circle
                cv2.circle(mask_marked, (i[0], i[1]), i[2], (0, 255, 0), 2)
                # draw the center of the circle
                cv2.circle(mask_marked, (i[0], i[1]), 2, (0, 0, 255), 3)

            r = 18
            # r = 20
            while True:
                largest_offset = scan_circle(mask, r, circles[0][0][0], circles[0][0][1])
                if largest_offset is None:
                    r -= 1
                else:
                    break
            #largest_offset = scan_circle(mask, 15, circles[0][0][0], circles[0][0][1])
            #print(largest_offset)
            mask_marked = cv2.circle(mask_marked, largest_offset, 2, (255, 1, 1), 2)




        # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2)))
        cv2.imshow("mask7", mask)
        cv2.imshow("mask8", mask_marked)
        #cv2.waitKey(2000)
        if circles is not None and largest_offset is not None:
            rot = angle((circles[0][0][0], circles[0][0][1]), largest_offset)
            send_rotation(rot)
            # send_rotation(largest_offset[2])
            # print(largest_offset[2])

        cv2.waitKey(500)
        # send_rotation(360)

        #if keyboard.is_pressed('k') and largest_offset is not None:
            # align

        if keyboard.is_pressed('='):
            cv2.destroyAllWindows()
            break
