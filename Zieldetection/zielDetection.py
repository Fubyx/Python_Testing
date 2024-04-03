import cv2
import numpy as np
from matplotlib import pyplot as plt


def find_rectangle_and_hole(image, color_lower, color_upper, min_area = 50, max_area = 300000, max_area_ratio = 2.0):
    # Laden des Bildes
    image = image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #cv2.imshow("OriginalZielbild", image)

    """
    ksize = 3
    gX = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=ksize)
    gY = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=ksize)
    # the gradient magnitude images are now of the floating point data
    # type, so we need to take care to convert them back a to unsigned
    # 8-bit integer representation so other OpenCV functions can operate
    # on them and visualize them
    gX = cv2.convertScaleAbs(gX)
    gY = cv2.convertScaleAbs(gY)
    # combine the gradient representations into a single image
    edges = cv2.addWeighted(gX, 0.5, gY, 0.5, 0)
    """

    # Kantenerkennung mit Canny
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    
    #"""
    cv2.imshow("Edges", edges)
    # Konturen finden
    contours, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # Rechtecke suchen und markieren
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
        if len(approx) >= 4 and len(approx) <= 6:
            area = cv2.contourArea(contour)
            print(area)
            #cv2.drawContours(image, [contour], -1, (0, 255, 0), 3)

            if area > min_area and area < max_area:
                x,y,w,h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                area_ratio = float(max(w,h)) / min(w,h)
                if aspect_ratio >= 0.8 and aspect_ratio <= 1.2 and area_ratio <= max_area_ratio:
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