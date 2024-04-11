#ball mit houghCircles suchen und Canny


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

    #Detect circles using Hough transform
    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 50, param1=90, param2=30, minRadius=0, maxRadius=75)
    
    #"""
    
    #If circles are detected, draw a red circle around the largest one 
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            if r > 10: # ignore small circles that are not likely to be a ball
                # Draw the circle on the frame
                cv2.circle(frame, (x, y), r, (0,250,0), 2)
    """
    
    # Define thresholds
    color_threshold = 15  # Maximum allowable difference in BGR values
    min_consecutive_frames = 6  # Minimum frames to consider a circle initially
    max_missed_frames = 0  # Maximum allowed missed frames before discarding a circle

    # Initialize variables for tracking
    consecutive_frames = {}  # Dictionary to store frame counts and missed frames
    tracked_circles = set()  # Set to store circles currently being tracked

    # Update tracking information (pre-color check)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            if r > 10:  # Ignore small circles
                circle_key = (x, y, r)

                # Check if circle is newly detected or already tracked
                if circle_key not in tracked_circles:
                    consecutive_frames[circle_key] = 1
                    tracked_circles.add(circle_key)
                else:
                    consecutive_frames[circle_key] = min(consecutive_frames[circle_key] + 1, min_consecutive_frames)

    
    # Filter circles based on consecutive detection and missed frames
    valid_circles = []
    for circle_key in tracked_circles.copy():
        # Check if circle has been consistently detected or missed too many frames
        if consecutive_frames.get(circle_key, 0) >= min_consecutive_frames or \
                consecutive_frames.get(circle_key, 0) <= 0:
            tracked_circles.remove(circle_key)
            consecutive_frames.pop(circle_key, None)
        else:
            consecutive_frames[circle_key] -= 1  # Decrement missed frames counter
            valid_circles.append(circle_key)  # Unpack circle info

    # Apply color consistency check only to valid circles
    
    if valid_circles:
        for (x, y, r) in valid_circles:
            # Create a mask for the circle area
            mask = np.zeros_like(frame[:, :, 0], dtype="uint8")
            cv2.circle(mask, (x, y), r, 255, -1)

            # Apply the mask to extract color information within the circle
            masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

            # Check color consistency using standard deviation
            color_variance = np.std(masked_frame.reshape(-1, 3), axis=0)
            if np.all(color_variance < color_threshold):
                # Draw the circle if color is consistent
                cv2.circle(frame, (x, y), r, (0,255,0), 2)
    """
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
    #Licht
    #Rosa
    #lower_color = np.array([320/2, 30*255/100, 50*255/100])  # Niedrige Grenzwerte für die Farbe (HSV)
    #upper_color = np.array([330/2, 50*255/100, 90*255/100])  # Hohe Grenzwerte für die Farbe (HSV)
    #Blau
    #lower_color = np.array([210/2, 30*255/100, 30*255/100])
    #upper_color = np.array([235/2, 100*255/100, 60*255/100])
    #rot
    lower_color = np.array([345/2, 20*255/100, 40*255/100])
    upper_color = np.array([359/2, 50*255/100, 80*255/100])
    #gelb
    lower_color = np.array([65/2, 40*255/100, 60*255/100])
    upper_color = np.array([80/2, 90*255/100, 90*255/100])

    #Dunkel
    #Rosa
    lower_color = np.array([290/2, 20*255/100, 0*255/100])  # Niedrige Grenzwerte für die Farbe (HSV)
    upper_color = np.array([320/2, 100*255/100, 100*255/100])  # Hohe Grenzwerte für die Farbe (HSV)
    #Blau
    lower_color = np.array([210/2, 30*255/100, 0*255/100])
    upper_color = np.array([240/2, 100*255/100, 100*255/100])
    #oranged
    #lower_color = np.array([0/2, 40*255/100, 60*255/100])
    #upper_color = np.array([30/2, 100*255/100, 100*255/100])
    #rot
    #lower_color = np.array([320/2, 20*255/100, 10*255/100])
    #upper_color = np.array([359/2, 80*255/100, 80*255/100])
    #gelb
    lower_color = np.array([65/2, 10*255/100, 60*255/100])
    upper_color = np.array([80/2, 98*255/100, 100*255/100])

    #Test rot für Ziel
    #lower_color = np.array([340/2, 60*255/100, 40*255/100])
    #upper_color = np.array([359/2, 80*255/100, 100*255/100])


    #lower_color = np.array([320/2, 20*255/100, 20*255/100])
    #upper_color = np.array([359/2, 80*255/100, 80*255/100])

    #blau hell
    lower_color = np.array([210/2, 30*255/100, 30*255/100])
    upper_color = np.array([235/2, 90*255/100, 60*255/100])
    
    min_radius = 15
    color_tolerance = 50        #darf nicht kleiner als 35 sein

    
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
