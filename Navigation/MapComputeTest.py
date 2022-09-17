import time
import mss
import numpy as np
import cv2
import math
import keyboard

# Map Size 1.1
# Map Zoom 0.9


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


def angle(point_a, point_b):

    if point_b[0] - point_a[0] == 0:
        b_slope = 0.00000001
    else:
        b_slope = (point_b[0] - point_a[0])
    slope = (point_b[1] - point_a[1]) / b_slope

    return math.degrees(math.atan(slope))


def distance(point_a, point_b):
    x = (point_b[0] - point_a[0])
    y = (point_b[1] - point_a[1])
    return math.sqrt((x * x) + (y * y))


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

    #mask_markup = cv2.line(mask_markup, point_candidates[9], point_candidates[2], (255, 5, 5), 1)
    #mask_markup = cv2.line(mask_markup, point_candidates[0], point_candidates[4], (255, 5, 5), 1)

    #print(str(indices))


    #while True:

    #    break

    for x in range(len(waypoints)):
        for i in range(len(waypoints_possibilities[x])):
            print(str(angle(waypoints[x], waypoints_possibilities[x][i])))

    while True:
        cv2.imshow("mask", mask_markup)
        cv2.imshow("mask2", filtered_mask)
        cv2.imshow("mask3", filtered_mask_site)


        cv2.waitKey(100)