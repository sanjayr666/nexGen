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
showCentroid = True

img_counter = 1
composite = ""




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




def get_keys(width, height):
    """
    this function is used to design the keyboard.
    it returns the 4 parameter that are needed to design the keys.
    they are key label, top right corner coordinate, bottom left corner coordinate, and center coordinate
    """
    max_keys_in_a_row = 11  # max number of keys in any row is 10 i.e the first row which contains 1234567890'backspace'
    key_width = int(
        width / max_keys_in_a_row)  # width of one key. width is divided by 10 as the max number of keys in a single row is 11.

    row0_key_width = key_width * 11  # width of zeroth or numeric row of keys
    row1_key_width = key_width * 10  # width of first row
    row2_key_width = key_width * 9  # width of second row
    row3_key_width = key_width * 7  # width of third row
    row4_key_width = key_width * 5  # width of space
    row_keys = []  # stores the keys along with its 2 corner coordinates and the center coordinate

    # for the zeroth row
    x1, y1 = 0, int((
                        height - key_width * 5) / 2)  # 5 is due to the fact that we will have 5 rows. y1 is set such that the whole keyboard has equal margin on both top and bottom
    x2, y2 = key_width + x1, key_width + y1
    c1, c2 = x1, y1  # copying x1, x2, y1 and y2
    keys = "1 2 3 4 5 6 7 8 9 0 <-"
    keys = keys.split(" ")
    for key in keys:
        if key == "<-":
            row_keys.append([key, (x1, y1), (x2, y2), (int((x2 + x1) / 2) - 25, int((y2 + y1) / 2) + 10)])
        else:
            row_keys.append([key, (x1, y1), (x2, y2), (int((x2 + x1) / 2) - 5, int((y2 + y1) / 2) + 10)])
        x1 += key_width
        x2 += key_width
    x1, y1 = c1, c2  # copying back from c1, c2, c3 and c4

    # for the first row
    x1, y1 = int((row0_key_width - row1_key_width) / 2) + x1, y1 + key_width
    x2, y2 = key_width + x1, key_width + y1
    c1, c2 = x1, y1  # copying x1, x2, y1 and y2
    keys = "qwertyuiop"
    for key in keys:
        row_keys.append([key, (x1, y1), (x2, y2), (int((x2 + x1) / 2) - 5, int((y2 + y1) / 2) + 10)])
        x1 += key_width
        x2 += key_width
    x1, y1 = c1, c2  # copying back from c1, c2, c3 and c4

    # for second row
    x1, y1 = int((
                     row1_key_width - row2_key_width) / 2) + x1, y1 + key_width  # x1 is set such that it leaves equal margin on both left and right side
    x2, y2 = key_width + x1, key_width + y1
    c1, c2 = x1, y1
    keys = "asdfghjkl"
    for key in keys:
        row_keys.append([key, (x1, y1), (x2, y2), (int((x2 + x1) / 2) - 5, int((y2 + y1) / 2) + 10)])
        x1 += key_width
        x2 += key_width
    x1, y1 = c1, c2

    # for third row
    x1, y1 = int((row2_key_width - row3_key_width) / 2) + x1, y1 + key_width
    x2, y2 = key_width + x1, key_width + y1
    c1, c2 = x1, y1
    keys = "zxcvbnm"
    for key in keys:
        row_keys.append([key, (x1, y1), (x2, y2), (int((x2 + x1) / 2) - 5, int((y2 + y1) / 2) + 10)])
        x1 += key_width
        x2 += key_width
    x1, y1 = c1, c2

    # for the space bar
    x1, y1 = int((row3_key_width - row4_key_width) / 2) + x1, y1 + key_width
    x2, y2 = 5 * key_width + x1, key_width + y1
    c1, c2 = x1, y1
    keys = " "
    for key in keys:
        row_keys.append([key, (x1, y1), (x2, y2), (int((x2 + x1) / 2) - 5, int((y2 + y1) / 2) + 10)])
        x1 += key_width
        x2 += key_width
    x1, y1 = c1, c2

    return row_keys


def do_keypress(img, center, row_keys_points, file):
    # this fuction presses a key and marks the pressed key with blue color
    word = ''
    global composite
    for row in row_keys_points:
        arr1 = list(np.int0(np.array(center) >= np.array(
            row[1])))  # center of the contour has greater value than the top left corner point of a key
        arr2 = list(np.int0(np.array(center) <= np.array(
            row[2])))  # center of the contour has less value than the bottom right corner point of a key
        if arr1 == [1, 1] and arr2 == [1, 1]:
            if row[0] == '<-':
                # gui.press('backspace')
                composite = composite[:-1]
            else:
                # gui.press(row[0])
                word = row[0]
                font = cv2.FONT_HERSHEY_SIMPLEX
                composite = composite + word
                # cv2.putText(img, word, (50, 50), font, 2, (0, 0, 0), 4)

                print row[0]
            cv2.fillConvexPoly(img, np.array([np.array(row[1]), \
                                              np.array([row[1][0], row[2][1]]), \
                                              np.array(row[2]), \
                                              np.array([row[2][0], row[1][1]])]), \
                               (255, 0, 0))

    return img, composite


# virtual keyboard function
def keyboard():
    global composite
    cam = cap
    hsv_lower = yellow_range[0]
    hsv_upper = yellow_range[1]

    hsv_lower_g = green_range[0]
    hsv_upper_g = green_range[1]

    width = cam.get(cv2.CAP_PROP_FRAME_WIDTH)  # width of video captured by the webcam
    height = cam.get(cv2.CAP_PROP_FRAME_HEIGHT)  # height of the video captured by the webcam

    row_keys_points = get_keys(width, height)
    new_area, old_area = 0, 0
    c, c2 = 0, 0  # c stores the number of iterations for calculating the difference b/w present area and previous area
    # c2 stores the number of iterations for calculating the difference b/w present center and previous center
    flag_keypress = False  # if a key is pressed then this flag is True
    z = ""
    i = 0
    file = open("test.txt", "w+")
    while True:
        img = cam.read()[1]
        img = cv2.flip(img, 1)
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(imgHSV, hsv_lower, hsv_upper)
        g_mask = cv2.inRange(imgHSV,hsv_lower_g,hsv_upper_g)

        blur = cv2.medianBlur(mask, 15)
        blur = cv2.GaussianBlur(blur, (5, 5), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[1]


        if len(contours) > 0:
            cnt = max(contours, key=cv2.contourArea)

            if cv2.contourArea(cnt) > 350:
                # draw a rectangle and a center
                rect = cv2.minAreaRect(cnt)
                center = list(rect[0])
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                #cv2.circle(img, tuple(np.int0(center)), 2, (0, 255, 0), 2)
                #cv2.drawContours(img, [box], 0, (0, 0, 255), 2)

                # calculation of difference of area and center
                new_area = cv2.contourArea(cnt)
                new_center = np.int0(center)
                if c == 0:
                    old_area = new_area
                c += 1
                diff_area = 0
                if c > 3:  # after every 3rd iteration difference of area is calculated
                    diff_area = new_area - old_area
                    c = 0
                if c2 == 0:
                    old_center = new_center
                c2 += 1
                diff_center = np.array([0, 0])
                if c2 > 5:  # after every 5th iteration difference of center is claculated
                    diff_center = new_center - old_center
                    c2 = 0

                # setting some thresholds
                center_threshold = 10
                area_threshold = 200
                if abs(diff_center[0]) < center_threshold or abs(diff_center[1]) < center_threshold:
                    print "dif"
                    print(diff_area)
                    if diff_area < area_threshold and flag_keypress == False:
                        img, z = do_keypress(img, new_center, row_keys_points, file)
                        print "z" + z
                        flag_keypress = True
                    elif diff_area < -(area_threshold) and flag_keypress == True:
                        flag_keypress = False
            else:
                flag_keypress = False
        else:
            flag_keypress = False

        # displaying the keyboard
        for key in row_keys_points:
            cv2.putText(img, key[0], key[3], cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0))
            cv2.rectangle(img, key[1], key[2], (0, 255, 0), thickness=2)
            cv2.putText(img, z, (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 4)
            i = i + 1

        font = cv2.FONT_HERSHEY_SIMPLEX
        img = cv2.rectangle(img, (0, 419), (170, 499), (0, 0, 0), 2)
        cv2.putText(img, "DRAW", (40, 459), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

        g_cen = drawCentroid(img, g_area, g_mask, True)
        cv2.circle(img, g_cen, 5, (0, 255, 0), -1)

        y_cen = drawCentroid(img, y_area, mask, True)
        cv2.circle(img, y_cen, 5, (0, 255, 255), -1)

        if g_cen != None and y_cen != None:
            if (g_cen[0] > 0 and g_cen[0] < 170 and g_cen[1] > 419 and g_cen[1] < 499) and (
                                    y_cen[0] > 0 and y_cen[0] < 170 and y_cen[1] > 419 and y_cen[1] < 499 ):
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(img, "gotcha", (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
                file.write(composite)
                file.close()
                break


        cv2.imshow("img", img)


        if cv2.waitKey(1) == ord('q'):
            file.write(composite)
            file.close()
            break

        #g_mask = makeMask(hsv, green_range)
        #y_mask = makeMask(hsv, yellow_range)



    cv2.destroyWindow('img')


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
    yellowPoints = []

    while(1):
        _, frameinv = cap.read()
        frame1 = cv2.flip(frameinv, 1)

        #frame1 = cv2.GaussianBlur(frame, (35, 35), 100)


        hsv = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)

        # green_lower_bound = green_range[0]
        # green_upper_bound = green_range[1]
        #
        # yellow_lower_bound = yellow_range[0]
        # yellow_upper_bound = yellow_range[1]
        #
        # greenThreshImg = cv2.inRange(hsvFrame, green_lower_bound, green_upper_bound)
        # yellowThreshImg = cv2.inRange(hsvFrame, yellow_lower_bound, yellow_upper_bound)

        yellowThreshImg = makeMask(hsv, yellow_range)
        greenThreshImg = makeMask(hsv, green_range)

        g_cen = drawCentroid(frame1, g_area, greenThreshImg, True)
        cv2.circle(frame1, g_cen, 5, (0, 255, 0), -1)

        y_cen = drawCentroid(frame1, y_area, yellowThreshImg, True)
        cv2.circle(frame1, y_cen, 5, (0, 255, 255), -1)

        frame1  = cv2.rectangle(frame1, (0, 0), (170, 80), (0, 255, 0), 5)

        # frame1 = cv2.bitwise_and(frame1, frame1, mask=greenThreshImg)
        # frame1 = cv2.bitwise_and(frame1, frame1, mask=yellowThreshImg)



        if g_cen != None and y_cen != None:
            if (g_cen[0] > 0 and g_cen[0] < 170 and g_cen[1] > 0 and g_cen[1] < 80) and (
                                        y_cen[0] > 0 and y_cen[0] < 170 and y_cen[1] > 0 and y_cen[1] < 80):
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            cv2.putText(frame1, "gotcha", (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
                            flag = 1
                            while (1):
                                _, frameinv = cap.read()
                                frame1 = cv2.flip(frameinv, 1)

                                filterFrame = cv2.GaussianBlur(frame1, (35, 35), 25)

                                hsvFrame = cv2.cvtColor(filterFrame, cv2.COLOR_BGR2HSV)

                                # lower_bound = np.array([30, 100, 100])
                                # upper_bound = np.array([80, 255, 255])

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


        cv2.imshow('HSV', frame1)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            print 'Drawing Mode OFF...'
            break

    cv2.destroyWindow('HSV')



# def draw():
#     greenPoints = []
#     yellowPoints = []
#
#     flag = 0
#
#     while (1):
#
#         _, frameinv = cap.read()
#         frame1 = cv2.flip(frameinv, 1)
#
#         filterFrame = cv2.GaussianBlur(frame1, (35, 35), 25)
#
#         hsvFrame = cv2.cvtColor(filterFrame, cv2.COLOR_BGR2HSV)
#
#         # lower_bound = np.array([30, 100, 100])
#         # upper_bound = np.array([80, 255, 255])
#
#         green_lower_bound = green_range[0]
#         green_upper_bound = green_range[1]
#
#         yellow_lower_bound = yellow_range[0]
#         yellow_upper_bound = yellow_range[1]
#
#         greenThreshImg = cv2.inRange(hsvFrame, green_lower_bound, green_upper_bound)
#         yellowThreshImg = cv2.inRange(hsvFrame, yellow_lower_bound, yellow_upper_bound)
#
#         _, green_contours, _ = cv2.findContours(greenThreshImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#         _, yellow_contours, _ = cv2.findContours(yellowThreshImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#
#         finalImg = cv2.bitwise_and(frame1, frame1, mask=greenThreshImg)
#         finalImg = cv2.bitwise_and(finalImg, finalImg, mask=yellowThreshImg)
#
#         finalImg = cv2.drawContours(finalImg, green_contours, -1, (0, 255, 0), 1)  # Outline of detected marker
#         finalImg = cv2.drawContours(finalImg, yellow_contours, -1, (0, 255, 255), 1)  # Outline of detected marker
#
#         finalImg = cv2.rectangle(finalImg, (0, 0), (170, 80), (0, 255, 0), 5)
#         finalImg = cv2.rectangle(finalImg, (180, 0), (340, 80), (0, 255, 0), 5)
#
#         g_cen = drawCentroid(finalImg, g_area, greenThreshImg, True)
#         cv2.circle(finalImg, g_cen, 5, (0, 255, 0), -1)
#
#         y_cen = drawCentroid(finalImg, y_area, yellowThreshImg, True)
#         cv2.circle(finalImg, y_cen, 5, (0, 255, 255), -1)
#
#         # print g_cen
#         if g_cen != None and y_cen != None:
#             if (g_cen[0] > 0 and g_cen[0] < 170 and g_cen[1] > 0 and g_cen[1] < 80) and (
#                             y_cen[0] > 0 and y_cen[0] < 170 and y_cen[1] > 0 and y_cen[1] < 80):
#                 font = cv2.FONT_HERSHEY_SIMPLEX
#                 cv2.putText(finalImg, "gotcha", (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
#
#         Gc, Yc = 0, 0
#         GX, YX = 0, 0
#         GY, YY = 0, 0
#
#         key = cv2.waitKey(1)
#
#         if flag == 1:
#             if g_cen != None and y_cen != None:
#                 if (g_cen[0] > 0 and g_cen[0] < 170 and g_cen[1] > 0 and g_cen[1] < 80) and (
#                                         y_cen[0] > 0 and y_cen[0] < 170 and y_cen[1] > 0 and y_cen[1] < 80):
#                     font = cv2.FONT_HERSHEY_SIMPLEX
#                     cv2.putText(finalImg, "gotcha", (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
#                     for item in green_contours:
#                         for i in item:
#                             GX += i[0][0]
#                             GY += i[0][1]
#                             Gc += 1
#                     try:
#                         greenPoints.append([int(GX / Gc), int(GY / Gc)])
#                     except:
#                         pass
#
#             for item in yellow_contours:
#                 for i in item:
#                     YX += i[0][0]
#                     YY += i[0][1]
#                     Yc += 1
#             try:
#                 yellowPoints.append([int(YX / Yc), int(YY / Yc)])
#             except:
#                 pass
#
#         if (key & 0xFF == ord('s')) and flag == 0:
#             flag = 1
#
#         elif key & 0xFF == ord('s') and flag == 1:
#             flag = 0
#
#         for p in greenPoints:
#             cv2.circle(finalImg, tuple(p), 10, (0, 255, 0), -1)
#
#         for p in yellowPoints:
#             cv2.circle(finalImg, tuple(p), 10, (0, 255, 255), -1)
#
#         # if g_cen[0] > 0 and g_cen[0] < 170 and g_cen[1] > 0 and g_cen[1] < 80:
#         #     font = cv2.FONT_HERSHEY_SIMPLEX
#         #     cv2.putText(finalImg, "gotcha", (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
#
#         cv2.imshow('HSV', finalImg)
#         cv2.imwrite('draw_result.png', finalImg)
#
#         if key & 0xFF == ord('q'):
#             print 'Drawing Mode OFF...'
#             break
#
#             # draw = not draw
#
#     cv2.destroyWindow('HSV')


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

    elif key == ord('k'):
        print 'Keyboard Mode ON...'
        keyboard()

    else:
        pass




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
# print '	Press P to turn ON and OFF mouse simulation.'
print '	Press C to display the centroid of various colours.'
print '	Press R to recalibrate color ranges.'
print '    Press D to enter Drawing Mode.'
print '    Press K to enter Keyboard Mode.'
print '	Press ESC to exit.'
print '**********************************************************************'



def click():
    global img_counter
    while True:
        _,img = cap.read()

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        b_mask = makeMask(hsv, blue_range)
        r_mask = makeMask(hsv, red_range)
        y_mask = makeMask(hsv, yellow_range)
        g_mask = makeMask(hsv, green_range)

        b_cen = drawCentroid(img, b_area, b_mask, True)
        r_cen = drawCentroid(img, r_area, r_mask, True)
        y_cen = drawCentroid(img, y_area, y_mask, True)
        g_cen = drawCentroid(img, g_area, g_mask, True)

        cv2.circle(img, b_cen, 5, (255, 0, 0), -1)
        cv2.circle(img, r_cen, 5, (0, 0, 255), -1)
        cv2.circle(img, y_cen, 5, (0, 255, 255), -1)
        cv2.circle(img, g_cen, 5, (0, 255, 0), -1)


        if b_cen != None and r_cen != None and g_cen != None and y_cen != None:
            if distance(b_cen, y_cen) < 40 and distance(b_cen, y_cen) > 0 and distance(r_cen, g_cen) < 40 and distance(r_cen,g_cen) > 0:
                print "Get Ready !! Pic will be taken in 3 seconds !!"
                for i in xrange(30):
                    _, img2 = cap.read()
                    # To give the processor some less stress
                    #time.sleep(1)
                    print i
                    name = str(i)

                    # to print a counter on the screen
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cv2.putText(img2, name, (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.imshow('Frame1', img2)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                cv2.destroyWindow('Frame1')
                # ret, img3 = cap.read()
                # detected = img3
                _, frameinv = cap.read()
                # flip horizontaly to get mirror image in camera
                img3 = cv2.flip(frameinv, 1)
                # cv2.imwrite('clicked.png', img3)

                img_name = "Clicked_image_{}.png".format(img_counter)
                cv2.imwrite(img_name, img3)
                print("{} Clicked!".format(img_name))
                img_counter += 1

                # print "clicked"


        font = cv2.FONT_HERSHEY_SIMPLEX
        img = cv2.rectangle(img, (0, 419), (170, 499), (0, 0, 0), 2)
        cv2.putText(img, "QUIT", (40, 459), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

        if g_cen != None and y_cen != None:
            if (g_cen[0] > 0 and g_cen[0] < 170 and g_cen[1] > 419 and g_cen[1] < 499) and (
                                    y_cen[0] > 0 and y_cen[0] < 170 and y_cen[1] > 419 and y_cen[1] < 499 ):
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(img, "gotcha", (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
                break

        cv2.imshow("click", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print 'Click Mode OFF...'
            break

    cv2.destroyWindow('click')

# def click():
#     global img_counter
#
#     while(1):
#
#         _, img = cap.read()
#
#         b_mask = makeMask(hsv, blue_range)
#         r_mask = makeMask(hsv, red_range)
#         y_mask = makeMask(hsv, yellow_range)
#         g_mask = makeMask(hsv, green_range)
#
#         b_cen = drawCentroid(img, b_area, b_mask, showCentroid)
#         r_cen = drawCentroid(img, r_area, r_mask, showCentroid)
#         y_cen = drawCentroid(img, y_area, y_mask, showCentroid)
#         g_cen = drawCentroid(img, g_area, g_mask, showCentroid)
#
#         if b_cen != None and r_cen != None and g_cen != None and y_cen != None:
#             if distance(b_cen, y_cen) < 40 and distance(b_cen, y_cen) > 0 and distance(r_cen, g_cen) < 40 and distance(
#                     r_cen,
#                     g_cen) > 0:
#                 break
#
#     print "Get Ready !! Pic will be taken in 3 seconds !!"
#     for i in xrange(30):
#         _, img = cap.read()
#         #time.sleep(1)
#         print i
#         name = str(i)
#         font = cv2.FONT_HERSHEY_SIMPLEX
#         cv2.putText(img, name, (250, 250), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
#
#         cv2.imshow('IPWebcam', img)
#
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#
#     _, frameinv = cap.read()
#     img3 = cv2.flip(frameinv, 1)
#     img_name = "Clicked_image_{}.png".format(img_counter)
#     cv2.imwrite(img_name, img3)
#     print("{} Clicked!".format(img_name))
#     img_counter += 1


# def click():
#     global img_counter
#     # font = cv2.FONT_HERSHEY_SIMPLEX
#     # cv2.putText(img, 'pic will be clicked in 3 second. Get Ready...', (37, 185), font, 4, (0, 255, 255), 2, cv2.LINE_AA)
#     # time.sleep(3)
#     print "Get Ready !! Pic will be taken in 3 seconds !!"
#     for i in xrange(3):
#         _, img = cap.read()
#         # To give the processor some less stress
#         time.sleep(1)
#         print i
#         name = str(i)
#
#         # to print a counter on the screen
#         # font = cv2.FONT_HERSHEY_SIMPLEX
#         # cv2.putText(img, name, (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
#         # cv2.imshow('Frame1', img)
#
#     # ret, img3 = cap.read()
#     # detected = img3
#     _, frameinv = cap.read()
#     # flip horizontaly to get mirror image in camera
#     img3 = cv2.flip(frameinv, 1)
#     # cv2.imwrite('clicked.png', img3)
#
#     img_name = "Clicked_image_{}.png".format(img_counter)
#     cv2.imwrite(img_name, img3)
#     print("{} Clicked!".format(img_name))
#     img_counter += 1
#
#     # print "clicked"











while (1):

    k = cv2.waitKey(10) & 0xFF
    changeStatus(k)

    _, frameinv = cap.read()
    # flip horizontaly to get mirror image in camera
    frame = cv2.flip(frameinv, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # lower mask (0-10)
    lower_red = np.array([0, 50, 50])
    upper_red = np.array([10, 255, 255])
    mask0 = cv2.inRange(hsv, lower_red, upper_red)

    # upper mask (170-180)
    lower_red = np.array([170,50,50])
    upper_red = np.array([180,255,255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    # join my masks
    r_mask = mask0 + mask1





    font = cv2.FONT_HERSHEY_SIMPLEX
    frame = cv2.rectangle(frame, (0, 0), (170, 80), (0, 0, 0), 2)
    cv2.putText(frame, "DRAW", (40, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


    frame = cv2.rectangle(frame, (180, 0), (350, 80), (0, 0, 0), 2)
    cv2.putText(frame, "CLICK", (220, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


    frame = cv2.rectangle(frame, (360, 0), (600, 80), (0, 0, 0), 2)
    cv2.putText(frame, "KEYBOARD", (400, 50), font, 1, (255, 255, 255), 2, cv2.LINE_AA)


    b_mask = makeMask(hsv, blue_range)
    #r_mask = makeMask(hsv, red_range)
    y_mask = makeMask(hsv, yellow_range)
    g_mask = makeMask(hsv, green_range)

    py_pos = y_pos

    b_cen = drawCentroid(frame, b_area, b_mask, showCentroid)
    r_cen = drawCentroid(frame, r_area, r_mask, showCentroid)
    y_cen = drawCentroid(frame, y_area, y_mask, showCentroid)
    g_cen = drawCentroid(frame, g_area, g_mask, showCentroid)

    cv2.circle(frame, b_cen, 5, (255, 0, 0), -1)
    cv2.circle(frame, r_cen, 5, (0, 0, 255), -1)
    cv2.circle(frame, y_cen, 5, (0, 255, 255), -1)
    cv2.circle(frame, g_cen, 5, (0, 255, 0), -1)

    if g_cen != None and y_cen != None:
        if (g_cen[0] > 0 and g_cen[0] < 170 and g_cen[1] > 0 and g_cen[1] < 80) and (
                        y_cen[0] > 0 and y_cen[0] < 170 and y_cen[1] > 0 and y_cen[1] < 80):
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, "gotcha", (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
            draw()

    if g_cen != None and y_cen != None:
        if (g_cen[0] > 360 and g_cen[0] < 600 and g_cen[1] > 0 and g_cen[1] < 80) and (
                                y_cen[0] > 360 and y_cen[0] < 600 and y_cen[1] > 0 and y_cen[1] < 80):
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, "gotcha", (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
            keyboard()

    if g_cen != None and y_cen != None:
        if (g_cen[0] > 180 and g_cen[0] < 350 and g_cen[1] > 0 and g_cen[1] < 80) and (
                                y_cen[0] > 180 and y_cen[0] < 350 and y_cen[1] > 0 and y_cen[1] < 80):
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, "gotcha", (37, 185), font, 2, (255, 255, 255), 2, cv2.LINE_AA)
            click()

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

    # if b_cen != None and r_cen != None and g_cen != None and y_cen != None:
    #     if distance(b_cen, y_cen) < 40 and distance(b_cen, y_cen) > 0 and distance(r_cen, g_cen) < 40 and distance(r_cen,
    #                                                                                                                g_cen) > 0:
    #         click()

    if k == 27:
        break

cv2.destroyAllWindows()