import cv2
import numpy as np

class ImageProcessing():

    MIN_RADIUS = 15
    COLOR_TOLERANCE = 35        #darf nicht kleiner als 35 sein

    def __init__(self):
        self.frame = None
        self.mode = None # 0 = Balldetection; 1 = TargetDetection

    def applyColorMask(self, lower_color, upper_color):
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
    
        # Erzeuge einen Maskenbereich für die angegebene Farbe
        mask = cv2.inRange(hsv, lower_color, upper_color)
        return mask

    def getContours(self, img):
        contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def findCircles(self, contours):
        circles = []
        for contour in contours:
            # Berechne das Zentrum und den Radius des Balls
            (x, y), radius = cv2.minEnclosingCircle(contour)
            radius = int(radius)
            
            # Überprüfe, ob der Radius größer als der Mindestradius ist
            if radius > self.MIN_RADIUS:
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
        return circles
    
    def process(self, frame, check_interval=20, consistency_threshold=0.2):
        self.frame = frame
        consistent_circles = []
        # Track circle detections for consistency check
        circle_history = {}

        for _ in range(check_interval):
            # Ball detection logic (assuming you have these functions)
            ball_circles = self.findCircles(
                self.getContours(self.applyColorMask(self.ball_lowerColor, self.ball_upperColor))
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

        # Print or utilize the detected consistent circles (consistent_circles list)
        if len(consistent_circles) > 0:
            print("Consistent circles found!")
        
        # Reset circle history for next frame
        circle_history = {}

        return consistent_circles

        

    def setModeToBall(self):
        self.mode = 0

    def setModeToTarget(self):
        self.mode = 1
    
    def getBallCoords(self):
        return self.findCircles(
            self.getContours(
                self.applyColorMask(self.ball_lowerColor, self.ball_upperColor)
            )
        )
    
    #Farbe für den Ball setzen
    def setBallColor(self, color): # Color string
        pass
    
    #Farbe für das Ziel setzen
    def setTargetColor(self, color):
        pass

    #die Koordinaten des Ziels ermitteln
    def getTargetCoords(self, frame):
        return
    
    #Array von Koordinaten zurückgeben, das die Daten der Hindernisse enthält
    def getObstacles(self, frame):
        return


img = ImageProcessing()