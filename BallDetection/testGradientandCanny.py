import cv2
import numpy as np
from matplotlib import pyplot as plt


# Load the video capture device (i.e., the webcam)
cap = cv2.VideoCapture(0)

# Define the color and thickness of the circle around the ball
circle_color = (0, 0, 255)  # red color
circle_thickness = 2

# Define thresholds
color_threshold = 30  # Maximum allowable difference in BGR values
min_consecutive_frames = 6  # Minimum frames to consider a circle initially
max_missed_frames = 0  # Maximum allowed missed frames before discarding a circle

# Initialize variables for tracking
consecutive_frames = {}  # Dictionary to store frame counts and missed frames
tracked_circles = set()  # Set to store circles currently being tracked

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    """
    

    # Convert the frame to grayscale and apply Gaussian blur
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect circles using Hough transform
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 50, param1=90, param2=30, minRadius=0, maxRadius=75)
    """
    #https://docs.opencv.org/4.x/d5/d0f/tutorial_py_gradients.html

    # Convert the frame to grayscale and apply Gaussian blur
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    """
    plt.subplot(2,2,1),plt.imshow(gray,cmap = 'gray')
    plt.title('Gray'), plt.xticks([]), plt.yticks([])

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    plt.subplot(2,2,2),plt.imshow(blurred,cmap = 'gray')
    plt.title('Blurred'), plt.xticks([]), plt.yticks([])

    laplacian = cv2.Laplacian(blurred, cv2.CV_64F)

    plt.subplot(2,2,3),plt.imshow(laplacian,cmap = 'gray')
    plt.title('Laplacian also Blurred'), plt.xticks([]), plt.yticks([])
    

    img = cv2.imread('BallDetection/balltemplate.jpg')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    assert img is not None, "file could not be read, check with os.path.exists()"
    
    laplacian = cv2.Laplacian(img,cv2.CV_64F)
    sobelx = cv2.Sobel(img,cv2.CV_64F,1,0,ksize=5)
    sobely = cv2.Sobel(img,cv2.CV_64F,0,1,ksize=5)
    
    plt.subplot(2,2,1),plt.imshow(img,cmap = 'gray')
    plt.title('Original'), plt.xticks([]), plt.yticks([])
    plt.subplot(2,2,2),plt.imshow(laplacian,cmap = 'gray')
    plt.title('Laplacian'), plt.xticks([]), plt.yticks([])
    plt.subplot(2,2,3),plt.imshow(sobelx,cmap = 'gray')
    plt.title('Sobel X'), plt.xticks([]), plt.yticks([])
    plt.subplot(2,2,4),plt.imshow(sobely,cmap = 'gray')
    plt.title('Sobel Y'), plt.xticks([]), plt.yticks([])

    """

    #https://pyimagesearch.com/2021/05/12/image-gradients-with-opencv-sobel-and-scharr/
    """
    # set the kernel size, depending on whether we are using the Sobel
    # operator of the Scharr operator, then compute the gradients along
    # the x and y axis, respectively
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
    combined = cv2.addWeighted(gX, 0.5, gY, 0.5, 0)
    # show our output images
    cv2.imshow("Sobel/Scharr X", gX)
    cv2.imshow("Sobel/Scharr Y", gY)
    cv2.imshow("Sobel/Scharr Combined", combined)
    #cv2.waitKey(0)
    plt.show()
    """

    
    # convert back to uint8 
    #laplacian = cv2.convertScaleAbs(laplacian)
    #laplacian = cv2.cvtColor(laplacian, cv2.COLOR_BGR2GRAY)

    # Detect circles using Hough transform

    # Setting parameter values 
    t_lower = 50  # Lower Threshold 
    t_upper = 150  # Upper threshold 
    aperture_size = 5  # Aperture size

    
    # Applying the Canny Edge filter
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    #Apply Gradient
    ksize = 3
    gX = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=ksize)
    gY = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=ksize)
    gX = cv2.convertScaleAbs(gX)
    gY = cv2.convertScaleAbs(gY)
    combined = cv2.addWeighted(gX, 0.5, gY, 0.5, 0)
    cv2.imshow("Combined", combined)


    frame1 = frame
    circles = cv2.HoughCircles(combined, cv2.HOUGH_GRADIENT, 1, 50, param1=90, param2=30, minRadius=0, maxRadius=75)


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
            mask = np.zeros_like(frame1[:, :, 0], dtype="uint8")
            cv2.circle(mask, (x, y), r, 255, -1)

            # Apply the mask to extract color information within the circle
            masked_frame = cv2.bitwise_and(frame1, frame1, mask=mask)

            # Check color consistency using standard deviation
            color_variance = np.std(masked_frame.reshape(-1, 3), axis=0)
            if np.all(color_variance < color_threshold):
                # Draw the circle if color is consistent
                cv2.circle(frame1, (x, y), r, circle_color, circle_thickness)
    

    #"""
    
    # Display the resulting frame
    cv2.imshow("Combined Gradient NO Canny", frame1)
    
    #edges = cv2.Canny(blurred, t_lower, t_upper, apertureSize= aperture_size) 
    #edges = cv2.Canny(np.uint8(combined), t_lower, t_upper)
    edges = cv2.Canny(gray, t_lower, t_upper)
    

    # Dilatation, um die Kantenlinien zu verdicken

    kernel = np.ones((5, 5), np.uint8)
    dilated_edges = cv2.dilate(edges, kernel, iterations=1)
    cv2.imshow("Canny Edge Detection", dilated_edges)
    
    circles = cv2.HoughCircles(dilated_edges, cv2.HOUGH_GRADIENT, 1, 50, param1=90, param2=30, minRadius=0, maxRadius=75)
    
    
    
    """
    #If circles are detected, draw a red circle around the largest one 
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            if r > 10: # ignore small circles that are not likely to be a ball
                # Draw the circle on the frame
                cv2.circle(frame, (x, y), r, circle_color, circle_thickness)
    """
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
                cv2.circle(frame, (x, y), r, circle_color, circle_thickness)
    

    #"""
    
    # Display the resulting frame
    cv2.imshow("Frame with Canny", frame)

    # Exit the loop if the user presses 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()
