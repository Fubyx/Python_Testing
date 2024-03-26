import cv2
import numpy as np

# Load the video capture device (i.e., the webcam)
cap = cv2.VideoCapture(0)

# Define the template for the ball
template = cv2.imread("balltemplate.png", cv2.IMREAD_GRAYSCALE)

# Define the size of the ball in the template
template_size = (template.shape[1], template.shape[0])

# Define the maximum size of the ball in the frame
max_size = (300, 300)

# Define the scale factor
scale_factor = 1.05

# Define the search region for the ball
search_region = (100, 100, 400, 400)

# Create a template scaled up to the maximum size
max_template = cv2.resize(template, max_size, interpolation=cv2.INTER_CUBIC)

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()

    # Resize the template to match the scale of the frame
    scale_percent = (search_region[2] / template_size[0]) * 100
    resize_width = int(template_size[0] * scale_percent / 100)
    resize_height = int(template_size[1] * scale_percent / 100)
    template_resized = cv2.resize(template, (resize_width, resize_height))

    # Convert the resized template to CV_8U
    resized_template_8u = np.uint8(template_resized)

    # Define the search region in the frame
    search_region_frame = frame[search_region[1]:search_region[1] + search_region[3], search_region[0]:search_region[0] + search_region[2]]

    # Resize the search region to match the scale of the template
    search_region_resized = cv2.resize(search_region_frame, template_size, interpolation=cv2.INTER_AREA)

    # Binary threshold the search region
    ret, search_region_resized = cv2.threshold(search_region_resized, 1, 255, cv2.THRESH_BINARY_INV)

    # Perform template matching
    result = cv2.matchTemplate(search_region_resized, resized_template_8u, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Find the top-left corner of the ball
    top_left = (max_loc[0] + search_region[0], max_loc[1] + search_region[1])

    # Draw the ball's location on the frame
    cv2.rectangle(frame, top_left, (top_left[0] + template_size[0], top_left[1] + template_size[1]), (0, 255, 0), 2)

    # Show the resulting frame
    cv2.imshow("Frame", frame)

    # Exit the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()