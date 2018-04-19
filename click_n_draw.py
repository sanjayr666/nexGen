import cv2
import numpy as np
import pyautogui
import time


# Some global variables or others that need prior intialization are initalized here

# colour ranges for feeding to the inRange funtions
blue_range = np.array([[88, 78, 67], [128, 255, 255]])
yellow_range = np.array([[21, 70, 80], [61, 255, 255]])
red_range = np.array([[158, 85, 72], [180, 255, 255]])
green_range = np.array([[63, 48, 52], [80, 255, 255]])

# Prior initialization of all centers for safety
b_cen, y_pos, r_cen, g_cen = [240, 320], [240, 320], [240, 320], [240, 320]
cursor = [960, 540]

# Area ranges for contours of different colours to be detected
r_area = [100, 1700]
b_area = [100, 1700]
y_area = [100, 1700]
g_area = [100, 1700]

# Rectangular kernal for eroding and dilating the mask for primary noise removal
kernel = np.ones((7, 7), np.uint8)

# Status variables defined globally
perform = False
showCentroid = False

img_counter = 1

# 'nothing' function is useful when creating trackbars
# It is passed as last arguement in the cv2.createTrackbar() function
def nothing(x):
    pass


# To bring to the top the contours with largest area in the specified range
# Used in drawContour()
def swap(array, i, j):
    temp = array[i]
    array[i] = array[j]
    array[j] = temp


# Distance between two centroids
def distance(c1, c2):
    distance = pow(pow(c1[0] - c2[0], 2) + pow(c1[1] - c2[1], 2), 0.5)
    return distance

def draw():
    points = []

    flag = 0

    while (1):

        _, frameinv = cap.read()
        frame1 = cv2.flip(frameinv, 1)

        filterFrame = cv2.GaussianBlur(frame1, (35, 35), 25)

        hsvFrame = cv2.cvtColor(filterFrame, cv2.COLOR_BGR2HSV)

        #lower_bound = np.array([30, 100, 100])
        #upper_bound = np.array([80, 255, 255])

        lower_bound = green_range[0]
        upper_bound = green_range[1]

        threshImg = cv2.inRange(hsvFrame, lower_bound, upper_bound)

        _, contours, _ = cv2.findContours(threshImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        finalImg = cv2.bitwise_and(frame1, frame1, mask=threshImg)

        finalImg = cv2.drawContours(finalImg, contours, -1, (255, 0, 0), 1)

        c = 0

        X = 0
        Y = 0

        key = cv2.waitKey(1)

        if flag == 1:
            for item in contours:
                for i in item:
                    X += i[0][0]
                    Y += i[0][1]
                    c += 1

            try:
                points.append([int(X / c), int(Y / c)])
            except:
                pass

        if (key & 0xFF == ord('s')) and flag == 0:
            flag = 1

        elif key & 0xFF == ord('s') and flag == 1:
            flag = 0

        for p in points:
            cv2.circle(finalImg, tuple(p), 10, (0, 0, 255), -1)

        cv2.imshow('HSV', finalImg)
        cv2.imwrite('draw_result.png', finalImg)

        if key & 0xFF == ord('q'):
            print 'Drawing Mode OFF...'
            break

        # draw = not draw

    cv2.destroyWindow('HSV')

# To toggle status of control variables
def changeStatus(key):
    global perform
    global showCentroid
    global yellow_range, red_range, blue_range, green_range


    # # toggle mouse simulation
    # if key == ord('p'):
    #     perform = not perform
    #     if perform:
    #         print 'Mouse simulation ON...'
    #     else:
    #         print 'Mouse simulation OFF...'
    #

    # toggle display of centroids
    if key == ord('c'):
        showCentroid = not showCentroid
        if showCentroid:
            print 'Showing Centroids...'
        else:
            print 'Not Showing Centroids...'

    elif key == ord('r'):
        print '**********************************************************************'
        print '	You have entered recalibration mode.'
        print ' Use the trackbars to calibrate and press SPACE when done.'
        print '	Press D to use the default settings'
        print '**********************************************************************'

        yellow_range = calibrateColor('Yellow', yellow_range)
        red_range = calibrateColor('Red', red_range)
        blue_range = calibrateColor('Blue', blue_range)
        green_range = calibrateColor('Green', green_range)

    elif key == ord('d'):
        print 'Drawing Mode ON...'
        print ' Press S to switch between active and passive state'
        print ' Press Q to quit Drawing mode'
        draw()

    else:
        pass


# cv2.inRange function is used to filter out a particular color from the frame
# The result then undergoes morphosis i.e. erosion and dilation
# Resultant frame is returned as mask
def makeMask(hsv_frame, color_Range):
    mask = cv2.inRange(hsv_frame, color_Range[0], color_Range[1])
    # Morphosis next ...
    eroded = cv2.erode(mask, kernel, iterations=1)
    dilated = cv2.dilate(eroded, kernel, iterations=1)

    return dilated


# Contours on the mask are detected.. Only those lying in the previously set area
# range are filtered out and the centroid of the largest of these is drawn and returned
def drawCentroid(vid, color_area, mask, showCentroid):
    _, contour, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    l = len(contour)
    area = np.zeros(l)

    # filtering contours on the basis of area rane specified globally
    for i in range(l):
        if cv2.contourArea(contour[i]) > color_area[0] and cv2.contourArea(contour[i]) < color_area[1]:
            area[i] = cv2.contourArea(contour[i])
        else:
            area[i] = 0

    a = sorted(area, reverse=True)

    # bringing contours with largest valid area to the top
    for i in range(l):
        for j in range(1):
            if area[i] == a[j]:
                swap(contour, i, j)

    if l > 0:
        # finding centroid using method of 'moments'
        M = cv2.moments(contour[0])
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            center = (cx, cy)
            if showCentroid:
                cv2.circle(vid, center, 5, (0, 0, 255), -1)

            return center
    else:
        # return error handling values
        return (-1, -1)


# This function helps in filtering the required colored objects from the background
def calibrateColor(color, def_range):
    global kernel
    name = 'Calibrate ' + color
    cv2.namedWindow(name)
    cv2.createTrackbar('Hue', name, def_range[0][0] + 20, 180, nothing)
    cv2.createTrackbar('Sat', name, def_range[0][1], 255, nothing)
    cv2.createTrackbar('Val', name, def_range[0][2], 255, nothing)
    while (1):
        ret, frameinv = cap.read()
        frame = cv2.flip(frameinv, 1)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        hue = cv2.getTrackbarPos('Hue', name)
        sat = cv2.getTrackbarPos('Sat', name)
        val = cv2.getTrackbarPos('Val', name)

        lower = np.array([hue - 20, sat, val])
        upper = np.array([hue + 20, 255, 255])

        mask = cv2.inRange(hsv, lower, upper)
        eroded = cv2.erode(mask, kernel, iterations=1)
        dilated = cv2.dilate(eroded, kernel, iterations=1)

        cv2.imshow(name, dilated)

        k = cv2.waitKey(5) & 0xFF
        if k == ord(' '):
            cv2.destroyWindow(name)
            return np.array([[hue - 20, sat, val], [hue + 20, 255, 255]])
        elif k == ord('d'):
            cv2.destroyWindow(name)
            return def_range


'''
This function takes as input the center of yellow region (yc) and 
the previous cursor position (pyp). The new cursor position is calculated 
in such a way that the mean deviation for desired steady state is reduced.
'''

cap = cv2.VideoCapture(0)

print '**********************************************************************'
print '	You have entered calibration mode.'
print ' Use the trackbars to calibrate and press SPACE when done.'
print '	Press D to use the default settings.'
print '**********************************************************************'

yellow_range = calibrateColor('Yellow', yellow_range)
red_range = calibrateColor('Red', red_range)
blue_range = calibrateColor('Blue', blue_range)
green_range = calibrateColor('Green', green_range)
print '	Calibration Successful...'

cv2.namedWindow('Frame')
print '**********************************************************************'
print '	Press P to turn ON and OFF mouse simulation.'
print '	Press C to display the centroid of various colours.'
print '	Press R to recalibrate color ranges.'
print '    Press D to to enter Drawing Mode.'
print '	Press ESC to exit.'
print '**********************************************************************'


def click():
    global img_counter
    # font = cv2.FONT_HERSHEY_SIMPLEX
    # cv2.putText(img, 'pic will be clicked in 3 second. Get Ready...', (37, 185), font, 4, (0, 255, 255), 2, cv2.LINE_AA)
    # time.sleep(3)
    print "Get Ready !! Pic will be taken in 3 seconds !!"
    for i in xrange(3):
        _, img = cap.read()
        # To give the processor some less stress
        time.sleep(1)
        print i
        name = str(i)

        # to print a counter on the screen
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # cv2.putText(img, name, (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
        # cv2.imshow('Frame1', img)

    # ret, img3 = cap.read()
    # detected = img3
    _, frameinv = cap.read()
    # flip horizontaly to get mirror image in camera
    img3 = cv2.flip(frameinv, 1)
    #cv2.imwrite('clicked.png', img3)

    img_name = "Clicked_image_{}.png".format(img_counter)
    cv2.imwrite(img_name, img3)
    print("{} Clicked!".format(img_name))
    img_counter += 1

    #print "clicked"


while (1):

    k = cv2.waitKey(10) & 0xFF
    changeStatus(k)

    _, frameinv = cap.read()
    # flip horizontaly to get mirror image in camera
    frame = cv2.flip(frameinv, 1)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    b_mask = makeMask(hsv, blue_range)
    r_mask = makeMask(hsv, red_range)
    y_mask = makeMask(hsv, yellow_range)
    g_mask = makeMask(hsv, green_range)

    py_pos = y_pos

    b_cen = drawCentroid(frame, b_area, b_mask, showCentroid)
    r_cen = drawCentroid(frame, r_area, r_mask, showCentroid)
    y_cen = drawCentroid(frame, y_area, y_mask, showCentroid)
    g_cen = drawCentroid(frame, g_area, g_mask, showCentroid)

    # print "position b"
    # print b_cen
    # print "position y"
    # print y_cen
    # print "distance1"
    # print distance(b_cen,y_cen)
    #
    # print "position r"
    # print r_cen
    # print "position g"
    # print g_cen
    # print "distance2"
    # print distance(r_cen, g_cen)

    # font = cv2.FONT_HERSHEY_SIMPLEX
    # cv2.putText(frame, "pic will be clicked in 3 second.", (37, 185), font, 1, (0, 255, 255), 2, cv2.LINE_AA)
    # cv2.putText(frame, " Get Ready...", (37, 305), font, 1, (0, 255, 255), 2, cv2.LINE_AA)
    cv2.imshow('Frame', frame)

    if distance(b_cen, y_cen) < 40 and distance(b_cen, y_cen) > 0 and distance(r_cen, g_cen) < 40 and distance(r_cen,
                                                                                                               g_cen) > 0:
        click()

    if k == 27:
        break

cv2.destroyAllWindows()
