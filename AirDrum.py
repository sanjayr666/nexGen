import pygame
import cv2
import numpy as np
import sys



# Class to run free play air drums
class FreePlay(object):

    # Define dimensions of window
    def __init__(self, width, height):
        self.width = width
        self.height = height

    # Define initial values for freeplay mode
    def initAnimation(self):
        # Initialize pygame module
        pygame.init()
        # Create window based on dimensions
        self.window = pygame.display.set_mode((self.width, self.height))

        # Define all text to be black
        self.textColor = (0, 0, 0)
        # Define parameter for when this run is over
        self.run = True
        # Retrieve sound data for all parts of drum set.
        self.snareSound = pygame.mixer.Sound("snare2short.wav")
        self.highhatSound = pygame.mixer.Sound("highhatshort.wav")
        self.tomSound = pygame.mixer.Sound("lowsnare.wav")
        self.smashSound = pygame.mixer.Sound("smash.wav")
        # Initialize coordinates of location of red and blue
        self.blueX0, self.blueY0 = 0, 0
        self.redX0, self.redY0 = 0, 0
        self.blueX1, self.blueY1 = 0, 0
        self.redX1, self.redY1 = 0, 0
        # Assume red and blue at start is not inside drum
        self.blueInsidePrevious = False
        self.redInsidePrevious = False
        self.blueInside = False
        self.redInside = False
        # Fill window with black background before going onto camera input
        self.window.fill((0, 0, 0))

    # Run function for free play modde
    def run(self):
        self.initAnimation()
        # Initialized vidocapture
        vidCapture = cv2.VideoCapture(0)
        while True:
            # Perform all drawings and camera operations
            self.drawQuitButton()
            self.respondToActions()
            ret, self.frame = vidCapture.read()
            self.resizeCameraInput()
            self.drawDrums()
            self.performBlueTracking()
            self.performRedTracking()
            self.drawBlueTrackers()
            self.drawRedTrackers()
            # Reset variable values with every frame
            self.blueX0, self.blueY0 = self.blueX1, self.blueY1
            self.redX0, self.redY0 = self.redX1, self.redY1
            self.blueInsidePrevious = self.blueInside
            self.redInsidePrevious = self.redInside
            # Convert open cv2 image to show in pygame
            image = self.cvimage_to_pygame()
            # Show frame in pygame window and update screen
            self.window.blit(image, (0, 0))
            pygame.display.update()
            # End run if value for run changes upon user input
            if not self.run:    break

    # Resize camera frame
    # Learned how to do this here
    # http://www.pyimagesearch.com/2014/01/20/basic-image-manipulations-in-
    # python-and-opencv-resizing-scaling-rotating-and-cropping/
    # and
    # http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/
    # py_imgproc/py_geometric_transformations/py_geometric_transformations.html
    def resizeCameraInput(self):
        ratio = 1000.0 / self.frame.shape[1]
        dim = (1000, int(self.frame.shape[0] * ratio))
        self.frame = cv2.resize(self.frame, dim, interpolation=cv2.INTER_CUBIC)

    # Draw button for user to quit and return to start menu
    def drawQuitButton(self):
        # Orient button near bottom left of screen
        startX = 20
        startY = 750
        buttonWidth = 80
        buttonHeight = 50
        rect = (startX, startY, buttonWidth, buttonHeight)
        color = (213, 165, 33)
        outlineWidth = 0
        pygame.draw.rect(self.window, color, rect, outlineWidth)
        pygame.draw.rect(self.window, (0, 0, 0), rect, 1)
        # Store button rect for user mousepresses
        self.quitButton = pygame.Rect(startX, startY, buttonWidth, buttonHeight)

        header = "Quit"
        fontSize = 30
        textX = startX + buttonWidth / 2
        textY = startY + buttonHeight / 2
        font = pygame.font.Font(None, fontSize)
        text = font.render(header, 1, (0, 0, 0))

        textPosition = text.get_rect()
        textPosition.centerx = textX
        textPosition.centery = textY
        self.window.blit(text, textPosition)

    # Respond to user actions on freeplay screen
    def respondToActions(self):
        for event in pygame.event.get():
            # Respond to user mousepresses
            if event.type == pygame.MOUSEBUTTONDOWN:
                coord = pygame.mouse.get_pos()
                # Quit freeplay window if user clicks on quit button
                if self.quitButton.collidepoint(coord):
                    self.run = False
            # Quit application if user x's out window
            elif event.type == pygame.QUIT:
                sys.exit()

    # Determine trackers for blue color
    # Learned about contours with opencv documentation
    # http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/
    # py_contours/py_contour_features/py_contour_features.html
    def drawBlueTrackers(self):
        try:
            # Determine areas of blue region in frame
            areas = self.blueContours[0]
            # Determine the center moment of inertia of the found blue contours
            moment = cv2.moments(areas)
            # This method to extract moment data is copied verbatim from cv2
            self.blueX1 = int(moment['m10'] / moment['m00'])
            self.blueY1 = int(moment['m01'] / moment['m00'])
            # Determine speed of stick based on previous position
            speed = FreePlay.determineDistance(self.blueX0, self.blueY0,
                                               self.blueX1, self.blueY1)
            # Draw blue circle to follow stick
            radius, color, thickness = 15, (255, 255, 255), 4
            cv2.circle(self.frame, (self.blueX1, self.blueY1),
                       radius, color, thickness)
            # Determine sound to make with drum stick
            self.determineBlueSound(speed)
        # If no contours are found in image, code above will crash.
        # Do nothing if no blue is found.
        except:
            pass

    # Determine trackers for red color
    # Learned about contours with opencv documentation
    # http://docs.opencv.org/trunk/doc/py_tutorials/py_imgproc/
    # py_contours/py_contour_features/py_contour_features.html
    def drawRedTrackers(self):
        try:
            # Determine areas of red region in frame
            areas = self.redContours[0]
            # Determine the center moment of inertia of the found recd contours
            moment = cv2.moments(areas)

            # Determine coordinates of current moment
            # This extraction of moment data is copied verbatim fromm cv2 docs
            self.redX1 = int(moment['m10'] / moment['m00'])
            self.redY1 = int(moment['m01'] / moment['m00'])

            # Determine speed based on prior red coordinates
            speed = FreePlay.determineDistance(self.redX0, self.redY0,
                                               self.redX1, self.redY1)

            radius, color, thickness = 15, (255, 255, 255), 4
            # Draw red circle to follow red sticks
            cv2.circle(self.frame, (self.redX1, self.redY1),
                       radius, color, thickness)
            # Determine sound that red stick should make based on location
            self.determineRedSound(speed)
        # If no contours are found, then above code will crash.
        # Raise exception in case no red is found,
        except:
            self.redInside = False

    def determineBlueSound(self, speed):
        # Determine if blue falls within one of drum set regions
        # and if it's fast enough to play the sound
        if (self.snareX0 < self.blueX1 < self.snareX1 and
                self.snareY0 < self.blueY1 < self.snareY1 and speed > 10):
            # Define blue as inside a region if it is
            self.blueInside = True
            # Only play a sound if blue wasn't previously in drum
            if self.blueInside and not self.blueInsidePrevious:
                self.snareSound.play()
        elif (self.highhatX0 < self.blueX1 < self.highhatX1 and
              self.highhatY0 < self.blueY1 < self.highhatY1 and speed > 10):
            # Define blue as inside a region if it is
            self.blueInside = True
            # Only play a sound if blue wasn't previously in drum
            if self.blueInside and not self.blueInsidePrevious:
                self.highhatSound.play()
        elif (self.tomX0 < self.blueX1 < self.tomX1 and
              self.tomY0 < self.blueY1 < self.tomY1 and speed > 10):
            # Define blue as inside a region if it is
            self.blueInside = True
            # Only play a sound if blue wasn't previously in drum
            if self.blueInside and not self.blueInsidePrevious:
                self.tomSound.play()
        elif (self.smashX0 < self.blueX1 < self.smashX1 and
              self.smashY0 < self.blueY1 < self.smashY1 and speed > 10):
            # Define blue as inside a region if it is
            self.blueInside = True
            # Only play a sound if blue wasn't previously in drum
            if self.blueInside and not self.blueInsidePrevious:
                self.smashSound.play()
        # Drum not in region if none applicable
        else:
            self.blueInside = False

    # Determine what sound red tracking should make
    def determineRedSound(self, speed):
        # Determine if red falls within one of drum set regions
        # and if it's fast enough to play the sound
        if (self.snareX0 < self.redX1 < self.snareX1 and
                self.snareY0 < self.redY1 < self.snareY1 and speed > 10):
            # Define red as inside a region if it is
            self.redInside = True
            # Only play sound if red wasn't previously in drum
            if self.redInside and not self.redInsidePrevious:
                self.snareSound.play()
        elif self.highhatX0 < self.redX1 < self.highhatX1 and self.highhatY0 < self.redY1 < self.highhatY1:
            # Define red as inside a region if it is
            self.redInside = True
            # Only play sound if red wasn't previously in drum
            if self.redInside and not self.redInsidePrevious:
                self.highhatSound.play()
        elif self.tomX0 < self.redX1 < self.tomX1 and self.tomY0 < self.redY1 < self.tomY1:
            # Define red as inside a region if it is
            self.redInside = True
            # Only play sound if red wasn't previously in drum
            if self.redInside and not self.redInsidePrevious:
                self.tomSound.play()
        elif self.smashX0 < self.redX1 < self.smashX1 and self.smashY0 < self.redY1 < self.smashY1:
            # Define red as inside a region if it is
            self.redInside = True
            # Only play sound if red wasn't previously in drum
            if self.redInside and not self.redInsidePrevious:
                self.smashSound.play()
        # Drum not in region if not applicable
        else:
            self.redInside = False

    # Draw drum regions on frame
    def drawDrums(self):
        # Define regions to be white hollow rectangles
        color = (255, 255, 255)
        drumWidth, drumHeight, outlineWidth = 170, 215, 3
        # Draw each rectangle for each specific drum typee
        highhatStart = (self.highhatX0, self.highhatY0) = (40, 80)
        highhatEnd = (self.highhatX1,
                      self.highhatY1) = (self.highhatX0 + drumWidth,
                                         self.highhatY0 + drumHeight)
        cv2.rectangle(self.frame, highhatStart, highhatEnd, color, 3)
        snareStart = (self.snareX0, self.snareY0) = (290, 455)
        snareEnd = (self.snareX1,
                    self.snareY1) = (self.snareX0 + drumWidth,
                                     self.snareY0 + drumHeight)
        cv2.rectangle(self.frame, snareStart, snareEnd, color, outlineWidth)
        tomStart = (self.tomX0, self.tomY0) = (540, 455)
        tomEnd = (self.tomX1,
                  self.tomY1) = (self.tomX0 + drumWidth,
                                 self.tomY0 + drumHeight)
        cv2.rectangle(self.frame, tomStart, tomEnd, color, outlineWidth)
        smashStart = (self.smashX0, self.smashY0) = (790, 80)
        smashEnd = (self.smashX1,
                    self.smashY1) = (self.smashX0 + drumWidth,
                                     self.smashY0 + drumHeight)
        cv2.rectangle(self.frame, smashStart, smashEnd, color, outlineWidth)

    # Perform tracking for blue color
    # I learned basic image processing on opencv2 documentation
    def performBlueTracking(self):
        # Convert bgr frame to hsv (hue-value-saturation)
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        # Define kernel
        kernel = np.ones((5, 5), np.uint8)
        # Define upper and lower blue thresholds
        lowerBlue = np.array([100, 150, 80], dtype=np.uint8)
        upperBlue = np.array([130, 255, 255], dtype=np.uint8)

        # Mask the frame with the thresholds to only output blue
        mask = cv2.inRange(hsv, lowerBlue, upperBlue)

        # Perform opening to accentuate smaller blue regions
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        # Perform closing to get rid of small blue white noise
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

        # Use threshold of closing to find contours of image. Store contours
        ret, thresh = cv2.threshold(closing, 127, 255, 0)
        _, contours, hierarchy = cv2.findContours(thresh, 1, 2)
        self.blueContours = contours

    # Perform tracking for red color
    # I learned about basic image processing on oopencv2 documentation
    def performRedTracking(self):
        # Convert bgr frame to hsv (hue-value-saturation)
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        # Define kernel
        kernel = np.ones((5, 5), np.uint8)
        # Define upper and lower red thresholds
        lowerRed = np.array([160, 100, 180], dtype=np.uint8)
        upperRed = np.array([180, 255, 255], dtype=np.uint8)

        # Mask the frame with the thresholds to only output red
        mask = cv2.inRange(hsv, lowerRed, upperRed)

        # Perform opening to accentuate smaller red regions
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        # Perform closing to get rid of small red white noise
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

        # Use threshold of closing to find contours if image. Store contours.
        ret, thresh = cv2.threshold(closing, 127, 255, 0)
        _, contours, hierarchy = cv2.findContours(thresh, 1, 2)
        self.redContours = contours

    # Determine distance between two points with distance formula
    @staticmethod
    def determineDistance(x0, y0, x1, y1):
        xComp = abs(x0 - x1)
        yComp = abs(y0 - y1)
        return (xComp ** 2 + yComp ** 2) ** 0.5

    # Convert opencv image to pygame format to show in pygame window
    # This was almost all copied verbatim
    # http://stackoverflow.com/questions/19306211/
    # opencv-cv2-image-to-pygame-image
    def cvimage_to_pygame(self):
        # Switch BGR to RBG
        image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        # Reverse frame so it doesn't look backwards to user
        for row in xrange(len(image)):
            image[row] = image[row][::-1]
        # Perform operation to get pygame image
        return pygame.image.frombuffer(image.tostring(), image.shape[1::-1],
                                       "RGB")


FreePlay(1000, 800).run()

