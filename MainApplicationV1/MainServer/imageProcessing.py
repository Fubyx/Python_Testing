import cv2
import numpy as np
import threading
import time

class ImageProcessing():

    MIN_RADIUS = 6
    COLOR_TOLERANCE = 35        #darf nicht kleiner als 35 sein

    def __init__(self):
        self.frame = None
        self.mode = None # 0 = Balldetection; 1 = TargetDetection
        # Variables for color thresholds; 
        # _2 for orange as its threshold goes from ~350 to ~10
        self.ball_lowercolor = np.array([190/2, 30*255/100, 25*255/100])
        self.ball_uppercolor = np.array([235/2, 90*255/100, 60*255/100])
        self.ball_lowercolor_2 = None
        self.ball_uppercolor_2 = None

        self.lightlevel = None # 0 = Light (lights off); 1 = dark (lights on)

        # Variable for saving current color strings so that the color can be
        # edited on light level change
        self.currentBallColor = None
        self.currentTargetColor = None

        # For opening the stream locally
        self.masked_frame = None
        self.cont = None
        threading.Thread(target=self.display_frame, daemon=True).start()  # Start display thread



    def display_frame(self): # not needed in production
        while True:
            if self.frame is not None and self.cont is not None and self.masked_frame is not None:
                cv2.imshow('frame Stream', self.frame)
                cv2.imshow('contour Stream', self.cont)
                cv2.imshow('mask Stream', self.masked_frame)
                if cv2.waitKey(1) == ord('q'):  # Exit on 'q' key press
                    break



        # For opening the stream locally
        self.masked_frame = None
        self.cont = None
        threading.Thread(target=self.display_frame, daemon=True).start()  # Start display thread



    def display_frame(self): # not needed in production
        while True:
            if self.frame is not None and self.cont is not None and self.masked_frame is not None:
                cv2.imshow('frame Stream', self.frame)
                cv2.imshow('contour Stream', self.cont)
                cv2.imshow('mask Stream', self.masked_frame)
                if cv2.waitKey(1) == ord('q'):  # Exit on 'q' key press
                    break



    def applyBallColorMask(self):
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        # Erzeuge einen Maskenbereich für die angegebene Farbe
        mask = cv2.inRange(hsv, self.ball_lowercolor, self.ball_uppercolor)
        if self.ball_lowercolor_2 is not None:
            mask2 = cv2.inRange(hsv, self.ball_lowercolor_2, self.ball_uppercolor_2)
            #Combine the 2 masks into mask
            mask = cv2.bitwise_or(mask, mask2)
        return mask

    def getContours(self, img):
        
        #img = cv2.GaussianBlur(img, (15, 15), 0)
        self.cont = img

        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.imshow('Camera Stream', contours)
        return contours

    def findCircles(self, contours):
        circles = []
        masked_frame = None
        for contour in contours:
            # Berechne das Zentrum und den Radius des Balls
            (x, y), radius = cv2.minEnclosingCircle(contour)
            radius = int(radius)
            # Überprüfe, ob der Radius größer als der Mindestradius ist
            if radius > self.MIN_RADIUS: #and radius > (0.24*y-8) * 0.8 and  radius < (0.24*y-8) * 1.3: #maybe auskommentieren
                # Erzeuge eine Maske für den Kreisbereich
                mask_circle = np.zeros_like(self.frame[:, :, 0], dtype="uint8")
                cv2.circle(mask_circle, (int(x), int(y)), radius, (255, 255, 255), -1)
                


                # Wende die Maske an, um die Farbinformationen innerhalb des Kreises zu extrahieren
                masked_frame = cv2.bitwise_and(self.frame, self.frame, mask=mask_circle)

                # Überprüfe die Farbkonsistenz anhand der Standardabweichung
                color_variance = np.std(masked_frame[mask_circle == 255], axis=0)
                if np.all(color_variance < self.COLOR_TOLERANCE):
                    # Zeichne den Kreis, wenn die Farbe konsistent ist
                    # cv2.circle(self.frame, (int(x), int(y)), radius, (0, 255, 0), 2)
                    circles.append((x, y, radius))
        if (masked_frame is not None):
            self.masked_frame = mask_circle
        return circles
    
    def getBallCoords(self, frame, check_interval=20, consistency_threshold=0.2):
        self.frame = frame
        consistent_circles = []
        # Track circle detections for consistency check
        circle_history = {}

        for _ in range(check_interval):
            # Ball detection logic (assuming you have these functions)
            ball_circles = self.findCircles(
                self.getContours(
                    self.applyBallColorMask()
                )
            )

            # Update circle history with radius
            for x, y, radius in ball_circles:
                key = (int(x), int(y))  # Use x and y for unique identifier
                if key in circle_history:
                    circle_history[key].append(radius)
                else:
                    circle_history[key] = [radius]

        # Filter circles based on consistency
        for key, radius_history in circle_history.items():
            if len(radius_history) / check_interval >= consistency_threshold:
            # Calculate average radius for consistency
                average_radius = sum(radius_history) / len(radius_history)
                consistent_circles.append((key[0], key[1], average_radius))
                #cv2.circle(self.frame, key, int(average_radius), (0, 255, 0), 2)

        # Print or utilize the detected consistent circles (consistent_circles list)
        if len(consistent_circles) > 0:
            #print("Consistent circles: " + str(consistent_circles))
            pass
        
        # Reset circle history for next frame
        circle_history = {}
        return consistent_circles

        

    def setModeToBall(self):
        self.mode = 0

    def setModeToTarget(self):
        self.mode = 1
    
    #Farbe für den Ball setzen
    def setBallColor(self, color): # Color string
        self.currentBallColor = color
        # Farben Stand 29.04 12:15
        if(self.lightlevel == 0):
            match(color):
                case "blue":
                    self.ball_lowercolor = np.array([190/2, 30*255/100, 25*255/100])
                    self.ball_uppercolor = np.array([235/2, 90*255/100, 60*255/100])
                case "pink":
                    self.ball_lowercolor = np.array([320/2, 30*255/100, 50*255/100])
                    self.ball_uppercolor = np.array([330/2, 50*255/100, 90*255/100])
                case "orange":
                    self.ball_lowercolor = np.array([355/2, 50*255/100, 70*255/100])
                    self.ball_uppercolor = np.array([359/2, 100*255/100, 100*255/100])
                    self.ball_lowercolor_2 = np.array([0/2, 50*255/100, 70*255/100])
                    self.ball_uppercolor_2 = np.array([15/2, 100*255/100, 100*255/100])
                case "red":
                    self.ball_lowercolor = np.array([345/2, 20*255/100, 40*255/100])
                    self.ball_uppercolor = np.array([359/2, 40*255/100, 80*255/100])
                    self.ball_lowercolor_2 = np.array([0/2, 20*255/100, 40*255/100])
                    self.ball_uppercolor_2 = np.array([5/2, 40*255/100, 80*255/100])
                case "yellow":
                    self.ball_lowercolor = np.array([65/2, 40*255/100, 60*255/100])
                    self.ball_uppercolor = np.array([80/2, 90*255/100, 90*255/100])
        else:
            match(color):
                case "blue":
                    self.ball_lowercolor = np.array([210/2, 30*255/100, 10*255/100])
                    self.ball_uppercolor = np.array([240/2, 100*255/100, 70*255/100])
                case "pink":
                    self.ball_lowercolor = np.array([290/2, 30*255/100, 20*255/100])
                    self.ball_uppercolor = np.array([320/2, 50*255/100, 100*255/100])
                case "orange":
                    self.ball_lowercolor = np.array([0/2, 40*255/100, 60*255/100])
                    self.ball_uppercolor = np.array([30/2, 100*255/100, 100*255/100])
                case "red":
                    self.ball_lowercolor = np.array([230/2, 20*255/100, 20*255/100])
                    self.ball_uppercolor = np.array([359/2, 80*255/100, 80*255/100])
                case "yellow":
                    self.ball_lowercolor = np.array([65/2, 10*255/100, 60*255/100])
                    self.ball_uppercolor = np.array([80/2, 100*255/100, 100*255/100])

        
    #Farbe für das Ziel setzen
    def setTargetColor(self, color):
        self.currentTargetColor = color
        if (self.lightlevel == 0):
            match color:
                case "blue":
                    self.target_lowercolor = np.array([190/2, 70*255/100, 70*255/100])
                    self.target_uppercolor = np.array([205/2, 100*255/100, 100*255/100])
                case "red":
                    self.target_lowercolor = np.array([5/2, 70*255/100, 70*255/100])
                    self.target_uppercolor = np.array([20/2, 100*255/100, 100*255/100])
                
                case "green":
                    self.target_lowercolor = np.array([105/2, 30*255/100, 65*255/100])
                    self.target_uppercolor = np.array([120/2, 50*255/100, 80*255/100])
                case "yellow":
                    self.target_lowercolor = np.array([50/2, 80*255/100, 80*255/100])
                    self.target_uppercolor = np.array([65/2, 100*255/100, 100*255/100])
        else:
            match color:
                case "green":
                    self.target_lowercolor = np.array([100/2, 30*255/100, 30*255/100])
                    self.target_uppercolor = np.array([140/2, 60*255/100, 100*255/100])
                case "yellow":
                    self.target_lowercolor = np.array([55/2, 50*255/100, 30*255/100])
                    self.target_uppercolor = np.array([75/2, 100*255/100, 100*255/100])
                case "blue":
                    self.target_lowercolor = np.array([175/2, 80*255/100, 30*255/100])
                    self.target_uppercolor = np.array([230/2, 100*255/100, 100*255/100])
                case "red":
                    self.target_lowercolor = np.array([340/2, 60*255/100, 40*255/100])
                    self.target_uppercolor = np.array([359/2, 80*255/100, 100*255/100])

    def setLightLevel(self, lightlevel):
        self.lightlevel = lightlevel
        # Update color thresholds on light change
        self.setBallColor(self.currentBallColor)
        self.setTargetColor(self.currentTargetColor)

    #die Koordinaten des Ziels ermitteln
    def getTargetCoords(self, frame):
        return
    
    #Array von Koordinaten zurückgeben, das die Daten der Hindernisse enthält
    def getObstacles(self, frame):
        return

