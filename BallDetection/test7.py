import cv2
import numpy as np

cap=cv2.VideoCapture(0)


ret,frame=cap.read()
l_b=np.array([0,230,170])# lower hsv bound for red
u_b=np.array([255,255,220])# upper hsv bound to red

while ret==True:
    ret,frame=cap.read()

    hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask=cv2.inRange(hsv,l_b,u_b)

    contours,_= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    if not contours: 
        print("No contours detected")
        continue
    max_contour = contours[0]
    for contour in contours:
        if cv2.contourArea(contour)>cv2.contourArea(max_contour):
           max_contour=contour
        contour=max_contour
        approx=cv2.approxPolyDP(contour, 0.01*cv2.arcLength(contour,True),True)
        x,y,w,h=cv2.boundingRect(approx)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),4)

    cv2.imshow("frame",frame)

    cv2.imshow("mask",mask)
    # Exit the loop if the user presses 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture device and destroy all windows
cap.release()
cv2.destroyAllWindows()