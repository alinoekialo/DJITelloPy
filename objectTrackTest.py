# import the necessary packages
from collections import deque
from imutils.video import VideoStream
import numpy as np
import cv2
import imutils
import time
from datetime import datetime, timedelta

def most_common(lst):
    cleared = [elem for elem in lst if elem != '']
    if not len(cleared) > 0:
        return ''
    return max(set(cleared), key=lst.count)

BUFFER_SIZE = 32

# define the lower and upper boundaries of the "green"
# ball in the HSV color space
greenLower = (157, 82, 89)
greenUpper = (173, 190, 225)

# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=BUFFER_SIZE)
directions = deque()
counter = 0
(dX, dY) = (0, 0)
direction = ""
final_direction = ""

previous_timestamp = datetime.now()

vs = VideoStream(src=0).start()

# allow the camera or video file to warm up
time.sleep(2.0)
# keep looping
while True:
    frame = vs.read()
    if frame is None:
        break

    frame = cv2.flip(frame, 1)
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, greenLower, greenUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours in the mask and initialize the current
    # (x, y) center of the ball
    cnts = cv2.findContours(
        mask.copy(),
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )
    cnts = imutils.grab_contours(cnts)
    center = None
    if len(cnts) > 0:
        # find the largest contour in the mask
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size
        if radius > 20:
            # draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(
                frame,
                (int(x), int(y)),
                int(radius),
                (0, 255, 255),
                2
            )
            cv2.circle(frame, center, 5, (0, 0, 255), -1)
            pts.appendleft(center)
    # loop over the set of tracked points
    for i in np.arange(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # check to see if enough points have been accumulated in
        # the buffer
        if counter >= 10 and i == 1 and len(pts) >= 10 and pts[-10] is not None:
            # compute the difference between the x and y
            # coordinates and re-initialize the direction
            # text variables
            dX = pts[-10][0] - pts[i][0]
            dY = pts[-10][1] - pts[i][1]
            (dirX, dirY) = ("", "")

            # ensure there is significant movement in the
            # x-direction
            if np.abs(dX) > 20:
                dirX = "East" if np.sign(dX) == 1 else "West"

            # ensure there is significant movement in the
            # y-direction
            if np.abs(dY) > 20:
                dirY = "North" if np.sign(dY) == 1 else "South"

            # handle when both directions are non-empty
            if dirX != "" and dirY != "":
                direction = "{}-{}".format(dirY, dirX)

            # otherwise, only one direction is non-empty
            else:
                direction = dirX if dirX != "" else dirY
            
            for elem in direction.split('-'):
                directions.appendleft(elem)
        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(BUFFER_SIZE / float(i + 1)) * 2.5)
        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)

    current_timestamp = datetime.now()
    if current_timestamp - previous_timestamp > timedelta(seconds=1):
        previous_timestamp = current_timestamp
        if {'North', 'East', 'West', 'South'}.issubset(set(directions)):
            final_direction = 'Circle'
        else:
            final_direction = most_common(directions)
        directions.clear()

        # show the movement deltas and the direction of movement on
    # the frame
    cv2.putText(
        frame,
        final_direction,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (0, 0, 255),
        3
    )
    cv2.putText(
        frame,
        "dx: {}, dy: {}".format(dX, dY),
        (10, frame.shape[0] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.35,
        (0, 0, 255),
        1
    )
    

    # show the frame to our screen and increment the frame counter
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    counter += 1

    # if the 'q' key is pressed, stop the loop
    if key == ord("q"):
        break

vs.release()
cv2.destroyAllWindows()
