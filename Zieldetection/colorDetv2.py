import cv2
import numpy as np

# Function to detect and mark objects in the specified color
def mark_objects_in_color(frame, lower_color, upper_color):
    # Convert image from BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Generate mask for the specified color
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Mark detected objects with rectangles
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if (w < 40 or h < 40):
            continue
        #print(f"{w} * {h}")

        # Extract ROI around the colored box
        roi = frame[y:y + h, x:x + w]

        # Detect and mark hole in the ROI (call the separate function)
        detect_and_mark_hole(roi)

        # Draw green rectangle around the colored box (optional)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    return frame

# Function to detect and mark the hole in the colored box
def detect_and_mark_hole(roi):
    # Convert to grayscale
    #gray_image = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    #cv2.imshow('Gray', gray_image)
    # Apply thresholding
    #_, thresh = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)

    #cv2.imshow('thresh', thresh)

    # Morphological operations for noise removal and hole refinement
    #kernel = np.ones((3, 3), np.uint8)
    #opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    #closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)

    #cv2.imshow('morph', closing)

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    #bounds for Black
    lower_bound = np.array([0.0, 0.0, 0.0])
    upper_bound = np.array([360/2, 255*255/100, 10*255/100])
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) > 0:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        print(f"w: {w} h: {h}")
        cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 0, 255), 2)


# Define color thresholds for the colored box
lower_color = np.array([175/2, 80*255/100, 30*255/100]) # Lower HSV limits for the color
upper_color = np.array([230/2, 100*255/100, 100*255/100]) # Upper HSV limits for the color

# Main function
def main():
    # Open webcam
    cap = cv2.VideoCapture(1)

    # Check if webcam is opened
    if not cap.isOpened():
        print("Error: Unable to open webcam.")
        return

    # Loop for reading and processing webcam frames
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Mark objects in the specified color
        marked_frame = mark_objects_in_color(frame, lower_color, upper_color)

        # Display the marked frame
        cv2.imshow('Marked Objects', marked_frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()