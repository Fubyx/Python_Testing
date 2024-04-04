import cv2

def main():
    # Webcam öffnen
    cap = cv2.VideoCapture(0)

    previous_rectangles = []

    while True:
        # Einzelbild von der Webcam abrufen
        ret, frame = cap.read()

        # Bild in Graustufen konvertieren
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Kanten mit dem Canny-Algorithmus erkennen
        edges = cv2.Canny(gray, 50, 150)

        # Konturen finden
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Liste für gültige Rechtecke
        valid_rectangles = []

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)

            # Nur Rechtecke mit ausreichender Größe berücksichtigen
            if area > 100:
                # Überprüfen, ob das Rechteck in einem anderen Rechteck liegt
                is_inside = False
                for rect in valid_rectangles:
                    rx, ry, rw, rh = rect
                    intersection = cv2.intersectConvexPolygons(contour, rect)
                    if intersection is not None and cv2.contourArea(intersection) > 0:
                        is_inside = True
                        break

                if not is_inside:
                    valid_rectangles.append((x, y, w, h))

        for rectangle in valid_rectangles:
            x, y, w, h = rectangle

             # Gefiltertes Rechteck zur Liste hinzufügen
            previous_rectangles.append(rectangle)

        # Rechtecke um die gültigen Konturen zeichnen
        for rect in valid_rectangles:
            x, y, w, h = rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Bild anzeigen
        cv2.imshow('Webcam', frame)
        # Programm beenden, wenn 'q' gedrückt wird
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Programm beenden, wenn
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()