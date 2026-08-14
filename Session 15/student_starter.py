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

# Session 15 student scaffold.
# Use the approved Session 14 integrated prototype as the autonomous behaviour baseline.
# This is not a new program. It is the Session 14 prototype with clearer behaviour organisation.
# Keep the states simple and adjust only one behaviour rule or value at a time if testing shows it is needed.

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
camera_handle = open_camera()
last_command = None
lost_target_frames = 0

print("Session 15 reliable autonomous behaviour")
print("Run the integrated prototype and observe the active behaviour state.")
print("Worksheet prompts:")
print("- When does the robot enter SEARCH, FOLLOW, and STOP?")
print("- Which condition has the highest priority in your current system?")
print("- What happens when target detected and obstacle detected are both true?")
print("- Which second input is affecting the final decision?")
print("- When does the fail-safe stop activate?")
print("- Which one behaviour rule or value, if any, should be refined after testing?\n")

try:
    while True:
        frame = read_frame(camera_handle)
        if frame is None:
            print("camera frame:", "MISSING")
            print("state:", "STOP")
            print("command sent:", "s")
            ser.write(b"s\n")
            break

        # CAMERA / INPUT STAGE
        # This is the live image from the Pi Camera in the integrated prototype.

        # EXISTING SESSION 14 INFRASTRUCTURE
        # VISION / PROCESSING STAGE
        # The approved Session 14 blur and HSV pipeline is reused directly.
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

        obstacle_contours, _ = cv2.findContours(
            obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if obstacle_contours:
            obstacle = max(obstacle_contours, key=cv2.contourArea)
            if cv2.contourArea(obstacle) > OBSTACLE_MIN_AREA:
                obstacle_detected = True

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
        # Organise the existing Session 14 decision logic into SEARCH, FOLLOW, and STOP.
        if unsafe_condition:
            state = "STOP"
            command = "s"
        elif target_detected and target_cx is not None:
            frame_center = frame.shape[1] // 2
            state = "FOLLOW"
            if target_area > 18000:
                command = "s"
            elif target_cx < frame_center - CENTRE_TOLERANCE:
                command = "l"
            elif target_cx > frame_center + CENTRE_TOLERANCE:
                command = "r"
            else:
                command = "f"

        # SERIAL COMMUNICATION STAGE
        # The Raspberry Pi sends the same single-character commands to the micro:bit.
        if command != last_command:
            ser.write((command + "\n").encode())
            print("camera frame:", "RECEIVED")
            print("state:", state)
            print("target detected:", target_detected)
            print("obstacle detected:", obstacle_detected)
            print("lost target frames:", lost_target_frames)
            print("command sent:", command)
            print("decision inputs:", "camera target, camera obstacle, target-loss condition")
            print(
                "record if changed:",
                "search_command", SEARCH_COMMAND,
                "failsafe_lost_frame_limit", FAILSAFE_LOST_FRAME_LIMIT,
                "centre_tolerance", CENTRE_TOLERANCE,
            )
            last_command = command

        # ROBOT OUTPUT STAGE
        # The micro:bit and Maqueen respond to the selected behaviour command.

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

        cv2.imshow("session15_student_frame", frame)
        cv2.imshow("session15_target_mask", target_mask)
        cv2.imshow("session15_obstacle_mask", obstacle_mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    ser.write(b"s\n")
    close_camera(camera_handle)
    cv2.destroyAllWindows()
