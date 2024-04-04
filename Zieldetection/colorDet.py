#Erkennt das Ziel nur über die Farbe


import cv2
import numpy as np

# Funktion zur Erkennung und Markierung der Objekte in der angegebenen Farbe
def mark_objects_in_color(frame, lower_color, upper_color):
    # Konvertiere das Bild von BGR zu HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Erzeuge einen Maskenbereich für die angegebene Farbe
    mask = cv2.inRange(hsv, lower_color, upper_color)
    
    
    # Finde Konturen im Maskenbereich
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Markiere die gefundenen Objekte mit Rechtecken
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return frame

# Hauptfunktion
def main():
    # Öffne die Webcam
    cap = cv2.VideoCapture(0)
    
    # Überprüfe, ob die Webcam geöffnet wurde
    if not cap.isOpened():
        print("Error: Unable to open webcam.")
        return
    
    # Wähle die Farbgrenzen für die zu erkennende Farbe
    # Hier kannst du die Farbintervalle für die gewünschte Farbe anpassen
    lower_color = np.array([90, 100, 100])  # Niedrige Grenzwerte für die Farbe (HSV)
    upper_color = np.array([130, 255, 255])  # Hohe Grenzwerte für die Farbe (HSV)
    
    # Schleife zum Lesen und Verarbeiten der Bilder von der Webcam
    while True:
        # Lese ein Bild von der Webcam
        ret, frame = cap.read()
        if not ret:
            break
        
        # Markiere Objekte in der angegebenen Farbe
        marked_frame = mark_objects_in_color(frame, lower_color, upper_color)
        
        # Zeige das markierte Bild an
        cv2.imshow('Marked Objects', marked_frame)
        
        # Überprüfe auf Tastatureingaben (Beende die Schleife, wenn 'q' gedrückt wird)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Freigabe der Ressourcen
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
