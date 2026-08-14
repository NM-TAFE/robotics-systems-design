import sys
import time
from pathlib import Path

import cv2
import numpy as np
import serial

LIBRARY_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(LIBRARY_ROOT / "Pi Camera Library"))

from pi_camera import close_camera, open_camera, read_frame


# EXISTING SESSION 14 INFRASTRUCTURE:
# Camera, OpenCV, serial, and Maqueen communication remain unchanged.
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
# Blur kernel dimensions must be positive odd numbers,
# e.g. (5, 5) or (7, 7).
BLUR_KERNEL = (5, 5)
TARGET_LOWER = np.array([40, 70, 70])
TARGET_UPPER = np.array([80, 255, 255])
OBSTACLE_LOWER_1 = np.array([0, 120, 70])
OBSTACLE_UPPER_1 = np.array([10, 255, 255])
OBSTACLE_LOWER_2 = np.array([170, 120, 70])
OBSTACLE_UPPER_2 = np.array([179, 255, 255])
TARGET_MIN_AREA = 600
OBSTACLE_MIN_AREA = 2500
CENTRE_TOLERANCE = 60
# SESSION 15:
# Organise the existing Session 14 decisions into SEARCH / FOLLOW / STOP.
SEARCH_COMMAND = "l"
# SESSION 15:
# Keep target-loss fail-safe as a small testable engineering value.
FAILSAFE_LOST_FRAME_LIMIT = 15


print("Session 15 reliable autonomous behaviour")
print("Use the Session 14 integrated prototype as the autonomous behaviour baseline.")
print("This is not a new program.")
print("It is the Session 14 prototype with its existing decisions organised into clearer behaviours.")
print("States: SEARCH -> FOLLOW -> STOP")
print("Safety conditions should override normal task behaviour.")
print("Press q to quit.\n")

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
camera_handle = open_camera()
last_command = None
last_state = None
lost_target_frames = 0

try:
    while True:
        frame = read_frame(camera_handle)
        if frame is None:
            print("camera frame:", "MISSING")
            print("fail-safe state:", "STOP")
            print("command sent:", "s\n")
            ser.write(b"s\n")
            break

        # CAMERA / INPUT STAGE
        # The integrated prototype receives a live frame from the Pi Camera.

        # EXISTING SESSION 14 INFRASTRUCTURE
        # VISION / PROCESSING STAGE
        # The Session 14 blur and HSV pipeline is preserved.
        blurred = cv2.GaussianBlur(frame, BLUR_KERNEL, 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        target_mask = cv2.inRange(hsv, TARGET_LOWER, TARGET_UPPER)
        obstacle_mask = cv2.inRange(hsv, OBSTACLE_LOWER_1, OBSTACLE_UPPER_1)
        obstacle_mask |= cv2.inRange(hsv, OBSTACLE_LOWER_2, OBSTACLE_UPPER_2)

        target_detected = False
        obstacle_detected = False
        target_cx = None
        target_area = 0
        state = "SEARCH"
        command = SEARCH_COMMAND
        behaviour_note = "No target is currently visible, so the robot searches."

        obstacle_contours, _ = cv2.findContours(
            obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if obstacle_contours:
            obstacle = max(obstacle_contours, key=cv2.contourArea)
            obstacle_area = cv2.contourArea(obstacle)
            if obstacle_area > OBSTACLE_MIN_AREA:
                obstacle_detected = True
                x, y, w, h = cv2.boundingRect(obstacle)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        target_contours, _ = cv2.findContours(
            target_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if target_contours:
            target = max(target_contours, key=cv2.contourArea)
            target_area = cv2.contourArea(target)
            if target_area > TARGET_MIN_AREA:
                target_detected = True
                x, y, w, h = cv2.boundingRect(target)
                target_cx = x + w // 2
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(frame, (target_cx, y + h // 2), 6, (0, 0, 255), -1)

        if target_detected:
            lost_target_frames = 0
        else:
            lost_target_frames += 1

        # SESSION 15:
        # Combine multiple information sources into one behaviour decision.
        # The current sources are camera target detection, camera obstacle detection,
        # and the target-loss system condition.
        unsafe_condition = obstacle_detected or lost_target_frames >= FAILSAFE_LOST_FRAME_LIMIT

        # SESSION 15 BEHAVIOUR LOGIC
        # Organise the existing Session 14 decision logic into simple behaviour states.
        if unsafe_condition:
            state = "STOP"
            command = "s"
            if obstacle_detected:
                behaviour_note = "Obstacle detected, so safety overrides target following."
            else:
                behaviour_note = "Target has been lost for too long, so the fail-safe stop is active."
        elif target_detected and target_cx is not None:
            frame_center = frame.shape[1] // 2
            state = "FOLLOW"
            if target_area > 18000:
                command = "s"
                behaviour_note = "Target is very close, so the robot stops within FOLLOW behaviour."
            elif target_cx < frame_center - CENTRE_TOLERANCE:
                command = "l"
                behaviour_note = "Target is left of centre, so FOLLOW turns left."
            elif target_cx > frame_center + CENTRE_TOLERANCE:
                command = "r"
                behaviour_note = "Target is right of centre, so FOLLOW turns right."
            else:
                command = "f"
                behaviour_note = "Target is centred, so FOLLOW moves forward."

        # SERIAL COMMUNICATION STAGE
        # The Raspberry Pi sends the same single-character commands to the micro:bit.
        if command != last_command:
            ser.write((command + "\n").encode())
            last_command = command

        # ROBOT OUTPUT STAGE
        # The micro:bit and Maqueen respond to the selected behaviour command.
        if state != last_state:
            print("camera frame:", "RECEIVED")
            print("state:", state)
            print("target detected:", target_detected)
            print("obstacle detected:", obstacle_detected)
            print("lost target frames:", lost_target_frames)
            print("command sent:", command)
            print("behaviour note:", behaviour_note)
            print("decision inputs:", "camera target, camera obstacle, target-loss condition")
            print()
            last_state = state

        cv2.putText(
            frame,
            f"STATE: {state}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            f"CMD: {command}  LOST: {lost_target_frames}  SEARCH: {SEARCH_COMMAND}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            "Priority: unsafe -> STOP, target -> FOLLOW, else -> SEARCH",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.imshow("session15_autonomous_frame", frame)
        cv2.imshow("session15_target_mask", target_mask)
        cv2.imshow("session15_obstacle_mask", obstacle_mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    ser.write(b"s\n")
    close_camera(camera_handle)
    cv2.destroyAllWindows()
