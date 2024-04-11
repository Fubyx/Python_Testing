

import cv2
import numpy as np
#klasse ist dafür da, die Koordinaten von Ball und Ziel zu finden
class findObjects:

    #Farbe für den Ball setzen
    def setBallColor(self, lowerColor, upperColor):
        self.lowerColor = lowerColor
        self.upperColor = upperColor

        
    #gibt die x und y Kordinaten und den Radius des Balls zurück 
    def getBallCoords(self, frame, min_radius = 15, color_tolerance = 35):
        # Konvertiere das Bild von BGR zu HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Erzeuge einen Maskenbereich für die angegebene Farbe
        mask = cv2.inRange(hsv, self.lowerColor, self.upperColor)
        edges = cv2.Canny(mask, 50, 150, apertureSize=3)
        # Finde Konturen im Maskenbereich
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            # Berechne das Zentrum und den Radius des Balls
            (x, y), radius = cv2.minEnclosingCircle(contour)
            radius = int(radius)
            
            # Überprüfe, ob der Radius größer als der Mindestradius ist
            if radius > min_radius:
                # Erzeuge eine Maske für den Kreisbereich
                mask_circle = np.zeros_like(frame[:, :, 0], dtype="uint8")
                cv2.circle(mask_circle, (int(x), int(y)), radius, (255, 255, 255), -1)

                # Wende die Maske an, um die Farbinformationen innerhalb des Kreises zu extrahieren
                masked_frame = cv2.bitwise_and(frame, frame, mask=mask_circle)

                # Überprüfe die Farbkonsistenz anhand der Standardabweichung
                color_variance = np.std(masked_frame[mask_circle == 255], axis=0)
                if np.all(color_variance < color_tolerance):
                    # Zeichne den Kreis, wenn die Farbe konsistent ist
                    cv2.circle(frame, (int(x), int(y)), radius, (0, 255, 0), 2)
        #am Ende soll man hier dann die Coordinaten zurückgeben

        return frame
    
    #Farbe für das Ziel setzen
    def setGoalColor(self, lowerColor, upperColor):
        self.lowerColor = lowerColor
        self.upperColor = upperColor

    #die Koordinaten des Ziels ermitteln
    def getGoalCoords(self, frame):
        return
    
    #Array von Koordinaten zurückgeben, das die Daten der Hindernisse enthält
    def getObstacles(self, frame):
        return
    
find = findObjects()
find.setBallColor(np.array([100, 50, 50]), np.array([140, 255, 255]))
image = cv2.imread("Balldetection/balltemplate.jpg")
cv2.imshow("d", image)
markedFrame = find.getBallCoords(image)
cv2.imshow("Result", markedFrame)
cv2.waitKey(0)
cv2.destroyAllWindows()
