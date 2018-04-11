import urllib
import cv2
import numpy as np
import math

# Replace the URL with your own IPwebcam shot.jpg IP:port
#url='http://192.168.0.4:8080/shot.jpg'


ramp=30
cap=cv2.VideoCapture(0)

for i in xrange(ramp):
    # Use urllib to get the image and convert into a cv2 usable format
    # imgResp=urllib.urlopen(url)
    # imgNp=np.array(bytearray(imgResp.read()),dtype=np.uint8)
    # img2=cv2.imdecode(imgNp,-1)
    #
    # img = cv2.imdecode(imgNp, -1)

    ret, img2= cap.read()
    ret, img= cap.read()
    #ret, img3 = cap.read()

    #To give the processor some less stress
    #time.sleep(0.1)
    #print i
    name=str(i)

    #to print a counter on the screen
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img2, name, (37, 185), font, 4, (255, 255, 255), 2, cv2.LINE_AA)

    # put the image on screen
    cv2.imshow('IPWebcam', img2)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

def get_image():
    return img

print("Taking image...")

camera_capture = get_image()

cv2.imwrite('click_n_close.png', camera_capture)
cv2.destroyAllWindows()

#print 'show'

# cv2.imshow('click_n_close.png',camera_capture)
# cv2.waitKey(0)
# print 'shown'






im = cv2.imread("click_n_close.png")
i=1;
while i<=2:

    # Select ROI
    r = cv2.selectROI(im)

    # Crop image
    imCrop = im[int(r[1]):int(r[1] + r[3]), int(r[0]):int(r[0] + r[2])]

    # Display cropped image
    #cv2.imshow("Image", imCrop)
    #k = cv2.waitKey(0)
    #if k == 27:
    image="new"+str(i)+".png"
    print image
    cv2.imwrite(image, imCrop)
    i=i+1

cv2.destroyAllWindows()

fgbg = cv2.createBackgroundSubtractorMOG2()


def calculateDistance(x1, y1, x2, y2):
    dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dist

while True:


    # Use urllib to get the image and convert into a cv2 usable format
    # imgResp = urllib.urlopen(url)
    # imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
    # img = cv2.imdecode(imgNp, -1)

    #ret, frame = cv2.imread(img)
    ret,img=cap.read()
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fgmask = fgbg.apply(img)

    template1 = cv2.imread('new1.png', 0)
    w1, h1 = template1.shape[::-1]

    template2 = cv2.imread('new2.png', 0)
    w2, h2 = template2.shape[::-1]

    res1 = cv2.matchTemplate(img_gray, template1, cv2.TM_CCOEFF_NORMED)
    res2 = cv2.matchTemplate(img_gray, template2, cv2.TM_CCOEFF_NORMED)


    threshold = 0.85
    loc1 = np.where(res1 >= threshold)
    loc2 = np.where(res2 >= threshold)
    # print (type(loc2))
    # if (loc1.any() and loc2.any()):
    #     font = cv2.FONT_HERSHEY_SIMPLEX
    #     cv2.putText(img, 'DETECTED', (37, 185), font, 4, (255, 255, 255), 2, cv2.LINE_AA)

        # cv2.imshow("new image", img_new)

    # for pt in zip(*loc1[::-1]):
    #     cv2.rectangle(img, pt, (pt[0] + w1, pt[1] + h1), (0, 255, 255), 2)
    #
    # for pt in zip(*loc2[::-1]):
    #     cv2.rectangle(img, pt, (pt[0] + w2, pt[1] + h2), (255, 255, 0), 2)

    for pt1 in zip(*loc1[::-1]):
        cv2.rectangle(img, pt1, (pt1[0] + w1, pt1[1] + h1), (0, 255, 255), 2)

    for pt2 in zip(*loc2[::-1]):
        cv2.rectangle(img, pt2, (pt2[0] + w2, pt2[1] + h2), (255, 255, 0), 2)

    # print "1st"
    # print pt1
    #
    # print "2nd"
    # print pt2
    #
    # print "distance"
    # print calculateDistance(pt1[0],pt2[0],pt1[1],pt2[1])

    dis=calculateDistance(pt1[0],pt1[1],pt2[0],pt2[1])
    dis_threshold=200
    #
    if (loc1[0].size and loc1[1].size and loc2[0].size and loc2[1].size):

        print "1st"
        print pt1

        print "2nd"
        print pt2

        print dis

        if (dis < dis_threshold):
            print "detected"
            ret, img3 = cap.read()
            detected = img3
            cv2.imwrite('detected.png', detected)


    #experimental
    # if(res1>=threshold):
    #     font = cv2.FONT_HERSHEY_SIMPLEX
    #     cv2.putText(img, 'detected', (37, 185), font, 4, (0, 255, 255), 2, cv2.LINE_AA)

    cv2.imshow('Detected', img)
    k = cv2.waitKey(30) & 0xFF
    if k == 27:
        break




