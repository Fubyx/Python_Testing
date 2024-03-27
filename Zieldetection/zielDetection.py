import cv2
import numpy as np
from matplotlib import pyplot as plt


def find_rectangle_and_hole(image, color_lower, color_upper, min_area = 1000):
    # Laden des Bildes
    image = image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #cv2.imshow("OriginalZielbild", image)

    # Kantenerkennung mit Canny
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    cv2.imshow("Edges", edges)
    
    # Konturen finden
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Rechtecke suchen und markieren
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:
            area = cv2.contourArea(contour)
            if area > min_area:
                cv2.drawContours(image, [contour], -1, (0, 255, 0), 2)
    
    
    # Anzeigen des Ergebnisbildes
    cv2.imshow("Rectangles and Holes Detection", image)
    #cv2.waitKey(0)


# Load the video capture device (i.e., the webcam)
cap = cv2.VideoCapture(0)

# Pfad zum Bild einstellen
image_path = 'Zieldetection/Zielprobe.jpg'

# Definieren der Farbgrenzen für das Rechteck (hier: blau)
color_lower = np.array([100, 100, 100])
color_upper = np.array([140, 255, 255])

# Rechteck und Loch erkennen
while True:
    # Capture a frame from the webcam
    ret,frame = cap.read()
    find_rectangle_and_hole(frame, color_lower, color_upper)
    # Exit the loop if the user presses 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()