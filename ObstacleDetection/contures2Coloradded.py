#erkennt hindernisse, nachdem alles entfernt wurde, was weiß oder baiche ist
#funktioniert nicht gut

import cv2
import numpy as np

# Funktion zur Konturerkennung und Markierung mit Rechtecken
def detect_objects(frame, min_area=500):
    # Konvertiere das Bild in den HSV-Farbraum
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Definiere den Farbbereich für weiß bis beige
    lower_color = np.array([0, 0, 180])
    upper_color = np.array([30, 30, 255])
    
    # Erzeuge eine Maske für den Farbbereich
    mask = cv2.inRange(hsv, lower_color, upper_color)
    cv2.imshow("mask", mask)
    
        
    # Wende die inverse Maske auf das Bild an
    result = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow("after baiche away", result)
    
    # Konvertiere das Ergebnis in Graustufen
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
    
    # Wende den Kantendetektor an
    edges = cv2.Canny(gray, 50, 150)
    
    
    # Finde Konturen im Bild
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Durchlaufe alle gefundenen Konturen
    for contour in contours:
        # Berechne das umgebende Rechteck um die Kontur
        x, y, w, h = cv2.boundingRect(contour)
        
        # Überprüfe, ob das Rechteck die Mindestgröße hat
        if w * h < min_area:
            continue
        
        # Überprüfe, ob das Rechteck von einem anderen Rechteck umgeben ist
        surrounded = False
        for other_contour in contours:
            if other_contour is not contour:
                other_x, other_y, other_w, other_h = cv2.boundingRect(other_contour)
                if x > other_x and y > other_y and x + w < other_x + other_w and y + h < other_y + other_h:
                    surrounded = True
                    break
        
        if surrounded:
            continue
        
        # Zeichne ein Rechteck um die Kontur
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    return frame

# Hauptfunktion
def main():
    # Öffne die Kamera
    cap = cv2.VideoCapture(0)
    
    while True:
        # Lies ein Frame von der Kamera
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Erkenne Objekte und markiere sie mit Rechtecken
        frame_with_boxes = detect_objects(frame)
        
        # Zeige das Bild mit den markierten Objekten an
        cv2.imshow('Objects Detection', frame_with_boxes)
        
        # Warte auf eine Taste zum Beenden des Programms
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Freigabe der Ressourcen
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
