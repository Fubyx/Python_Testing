
#Farbe herausfiltern und darin die Circles erkennen

import cv2
import numpy as np


# Funktion zur Erkennung und Markierung des Balls in der angegebenen Farbe mit einem Kreis
def mark_ball_in_color(frame, lower_color, upper_color,min_radius, color_tolerance):
    # Konvertiere das Bild von BGR zu HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Erzeuge einen Maskenbereich für die angegebene Farbe
    mask = cv2.inRange(hsv, lower_color, upper_color)

    cv2.imshow("Farbe", mask)

    """
    #Apply Gradient
    ksize = 3
    gX = cv2.Sobel(mask, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=ksize)
    gY = cv2.Sobel(mask, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=ksize)
    gX = cv2.convertScaleAbs(gX)
    gY = cv2.convertScaleAbs(gY)
    combined = cv2.addWeighted(gX, 0.5, gY, 0.5, 0)
    cv2.imshow("Combined", combined)
    
    

    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 50, param1=90, param2=30, minRadius=10, maxRadius=300)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles: 
            if r > 10:
                cv2.circle(frame, (x, y), r, (0, 0, 255), 2)
    """
    edges = cv2.Canny(mask, 50, 150, apertureSize=3)
    cv2.imshow("Canny", edges)

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

    return frame

# Hauptfunktion
def main():
    # Öffne die Webcam
    cap = cv2.VideoCapture(0)
    
    # Überprüfe, ob die Webcam geöffnet wurde
    if not cap.isOpened():
        print("Error: Unable to open webcam.")
        return
    
    # Wähle die Farbgrenzen für den zu erkennenden Ball
    lower_color = np.array([100, 50, 50])  # Niedrige Grenzwerte für die Farbe (HSV)
    upper_color = np.array([140, 255, 255])  # Hohe Grenzwerte für die Farbe (HSV)

    min_radius = 15
    color_tolerance = 35        #darf nicht kleiner als 35 sein

    
    # Schleife zum Lesen und Verarbeiten der Bilder von der Webcam
    while True:
        # Lese ein Bild von der Webcam
        ret, frame = cap.read()
        if not ret:
            break
        
        # Markiere den Ball in der angegebenen Farbe mit einem Kreis
        marked_frame = mark_ball_in_color(frame, lower_color, upper_color, min_radius, color_tolerance)
        
        # Zeige das markierte Bild an
        cv2.imshow('Marked Ball', marked_frame)
        
        # Überprüfe auf Tastatureingaben (Beende die Schleife, wenn 'q' gedrückt wird)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Freigabe der Ressourcen
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
