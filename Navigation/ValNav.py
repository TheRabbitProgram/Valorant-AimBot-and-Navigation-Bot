import keyboard
import time
import mss
import numpy as np
import cv2
import math
import serial


# Map Size 1.1
# Map Zoom 0.9

ser = serial.Serial('COM6', baudrate=2000000, timeout=1)


def raycast(img, point_a, point_b):
    # assume black is void/ boundary
    if point_b[0] - point_a[0] == 0:
        b_slope = 0.00000001
    else:
        b_slope = (point_b[0] - point_a[0])

    slope = (point_b[1] - point_a[1])/b_slope
    y_intercept = point_b[1] - (slope * point_b[0])
    # print(point_b[0] - point_a[0])
    ##print(point_a[0] - point_b[0])
    # print(point_a[0])
    ##print(point_b[0])
    traversal = -1

    if point_a[0] > point_b[0]:
        traversal = 1

    for x in range(point_b[0], point_a[0], traversal):
        y = int(int(slope * x) + y_intercept)
        # img = cv2.circle(img, (x, y), 2, (1, 255, 1), 2)
        # print(str(x) + "," + str(int(slope * x)))
        # print(str(img[y, x]))
        if img[y, x][0] == 0 and img[y, x][1] == 0 and img[y, x][2] == 0:
            return False

    if slope != 0:
        if point_a[1] > point_b[1]:
            traversal = 1
        else:
            traversal = -1

        for y in range(point_b[1], point_a[1], traversal):
            x = int((y - y_intercept) / slope)
            # img = cv2.circle(img, (x, y), 2, (1, 255, 1), 2)
            # print(str(x) + "," + str(int(slope * x)))
            # print(str(img[y, x]))
            if img[y, x][0] == 0 and img[y, x][1] == 0 and img[y, x][2] == 0:
                return False

    return True


def draw_raycast(img, point_a, point_b):
    # assume black is void/ boundary
    if point_b[0] - point_a[0] == 0:
        b_slope = 0.00000001
    else:
        b_slope = (point_b[0] - point_a[0])

    slope = (point_b[1] - point_a[1])/b_slope
    y_intercept = point_b[1] - (slope * point_b[0])
    traversal = -1

    if point_a[0] > point_b[0]:
        traversal = 1

    for x in range(point_b[0], point_a[0], traversal):
        y = int(int(slope * x) + y_intercept)
        img = cv2.circle(img, (x, y), 1, (1, 255, 1), 1)
        if img[y, x][0] == 0 and img[y, x][1] == 0 and img[y, x][2] == 0:
            return False

    if slope != 0:
        if point_a[1] > point_b[1]:
            traversal = 1
        else:
            traversal = -1

        for y in range(point_b[1], point_a[1], traversal):
            x = int((y - y_intercept) / slope)
            img = cv2.circle(img, (x, y), 1, (1, 255, 1), 1)
            if img[y, x][0] == 0 and img[y, x][1] == 0 and img[y, x][2] == 0:
                return False

    return img


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

    sign = "X"
    if degree < 0:
        sign = "C"

    degree = math.fabs(degree)

    move = move_per_degree * degree
    mod = move
    val = 0
    if move > 999:
        val = int(move / 999)
        mod = int(move % 999)

    send_cord = ""

    for n in range(val):
        send_cord += sign + "999"
    send_cord += parse_cords(sign, mod)

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


def distance(point_a, point_b):
    x = (point_b[0] - point_a[0])
    y = (point_b[1] - point_a[1])
    return math.sqrt((x * x) + (y * y))


def find_closest_point(point_a, point_list):
    point = None
    best_dis = 999999999
    for n in range(len(point_list)):
        dis = distance(point_a, point_list[n])
        if dis < best_dis:
            best_dis = dis
            point = point_list[n]
    return point


with mss.mss() as sct:
    monitor = {"left": 50, "top": 25, "width": 375, "height": 400}
    mask = cv2.imread("Maps\Split.jpg")

    filtered_mask = cv2.inRange(cv2.cvtColor(np.array(mask), cv2.COLOR_BGR2HSV),
                       np.array([0, 50, 100]),
                       np.array([10, 255, 255]))  # 200

    filtered_mask_site = cv2.inRange(cv2.cvtColor(np.array(mask), cv2.COLOR_BGR2HSV),
                       np.array([110, 50, 100]),
                       np.array([130, 255, 255]))  # 200

    mask_markup = mask.copy()


    # indices = np.nonzero(filtered_mask)

    rows, cols = filtered_mask.shape
    point_candidates = []

    for i in range(0, rows):
        for j in range(0, cols):
            if filtered_mask[i, j] != 0:
                point_candidates.append((j, i))

    for i in range(0, rows):
        for j in range(0, cols):
            if filtered_mask_site[i, j] != 0:
                point_candidates.append((j, i))

    print(str(point_candidates))

    #print(str(raycast(mask, point_candidates[0], point_candidates[4])))
    #print(str(raycast(mask, point_candidates[0], point_candidates[2])))

    waypoints = []
    waypoints_possibilities = []

    z = True
    if z:
        for x in range(len(point_candidates)):
            waypoints.append(point_candidates[x])
            temp_possibility_list = []
            for y in range(len(point_candidates)):
                if raycast(mask, point_candidates[x], point_candidates[y]):
                    temp_possibility_list.append(point_candidates[y])
                    # mask_markup = cv2.line(mask_markup, point_candidates[x], point_candidates[y], (255, 5, 5), 1)
                    mask_markup = draw_raycast(mask_markup, point_candidates[x], point_candidates[y])
                    print("RAY: " + str(x) + ", " + str(y))
            # print(str(waypoints_possibilities))
            waypoints_possibilities.append(temp_possibility_list)

    for x in range(len(waypoints)):
        for i in range(len(waypoints_possibilities[x])):
            print(str(angle(waypoints[x], waypoints_possibilities[x][i])))

    while keyboard.is_pressed('k') is False:
        cv2.imshow("mask", mask_markup)
        cv2.imshow("mask2", filtered_mask)
        cv2.imshow("mask3", filtered_mask_site)
        cv2.waitKey(100)
    cv2.destroyAllWindows()

    while True:
        mask = np.array(sct.grab(monitor))
        mask_marked = mask.copy()
        mask = cv2.inRange(cv2.cvtColor(np.array(mask), cv2.COLOR_BGR2HSV),
                                 np.array([29, 80, 220]),
                                 np.array([30, 100, 255]))

        mask = cv2.dilate(mask, np.ones((2, 2), np.uint8), iterations=1)
        circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 1, 20,
                                   param1=1, param2=15, minRadius=0, maxRadius=0)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                cv2.circle(mask_marked, (i[0], i[1]), i[2], (0, 255, 0), 2)
                cv2.circle(mask_marked, (i[0], i[1]), 2, (0, 0, 255), 3)

            r = 18
            player_point = (circles[0][0][0], circles[0][0][1])
            while True:
                largest_offset = scan_circle(mask, r, player_point[0], player_point[1])
                if largest_offset is None:
                    r -= 1
                else:
                    break
            mask_marked = cv2.circle(mask_marked, largest_offset, 2, (255, 1, 1), 2)

            #rot = angle((circles[0][0][0], circles[0][0][1]), largest_offset)
            #send_rotation(rot)

            closest_point = find_closest_point(player_point, waypoints)
            mask_marked = cv2.line(mask_marked, player_point, closest_point, (5, 255, 5), 5)

            player_angle = angle(player_point, largest_offset)
            destination_angle = angle(player_point, closest_point)

            desired_rotation = player_angle - destination_angle

            send_rotation(desired_rotation)
            print(desired_rotation)
            #print(player_angle)
            #print(destination_angle)
            # mask_marked = draw_raycast(mask_marked, player_point, closest_point)

        # cv2.imshow("mask7", mask)
        cv2.imshow("colored", mask_marked)

        cv2.waitKey(500)
        # send_rotation(360)

        #if keyboard.is_pressed('k') and largest_offset is not None:
            # align

        if keyboard.is_pressed('='):
            cv2.destroyAllWindows()
            break