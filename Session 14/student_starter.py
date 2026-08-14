import sys
import time
from pathlib import Path

import cv2
import numpy as np
import serial

LIBRARY_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(LIBRARY_ROOT / "Pi Camera Library"))

from pi_camera import close_camera, open_camera, read_frame


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

# Session 14 student scaffold.
# Use the approved Session 13 system as the prototype integration baseline.
# Verify each subsystem first. If a problem is found, change one existing value, retest, and document it.

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
camera_handle = open_camera()
last_command = None

print("Session 14 prototype integration")
print("Run the approved integrated system and verify each subsystem.")
print("Worksheet prompts:")
print("- Does the prototype match the approved design and Session 13 recommendations?")
print("- Which subsystem required the most adjustment: vision, processing, communication, or drive?")
print("- What single fault was discovered during verification?")
print("- Which one existing value, if any, needed a controlled change?")
print("- Did the change improve the integrated robot after retesting?")
print("- What engineering decision must be documented before Session 15?\n")

try:
    while True:
        frame = read_frame(camera_handle)
        if frame is None:
            print("No frame received from camera.")
            break

        # CAMERA / INPUT STAGE
        # This is the live image from the Pi Camera in the assembled prototype.

        # VISION / PROCESSING STAGE
        # The approved Session 13 blur and HSV pipeline is reused directly.
        blurred = cv2.GaussianBlur(frame, BLUR_KERNEL, 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        target_mask = cv2.inRange(hsv, TARGET_LOWER, TARGET_UPPER)
        obstacle_mask = cv2.inRange(hsv, OBSTACLE_LOWER_1, OBSTACLE_UPPER_1)
        obstacle_mask |= cv2.inRange(hsv, OBSTACLE_LOWER_2, OBSTACLE_UPPER_2)

        command = "s"
        state = "WAIT"

        # DECISION STAGE
        # The approved obstacle-priority logic is preserved.
        obstacle_contours, _ = cv2.findContours(
            obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        obstacle_detected = False
        if obstacle_contours:
            obstacle = max(obstacle_contours, key=cv2.contourArea)
            if cv2.contourArea(obstacle) > OBSTACLE_MIN_AREA:
                obstacle_detected = True
                state = "OBSTACLE PRIORITY"
                command = "s"

        if not obstacle_detected:
            target_contours, _ = cv2.findContours(
                target_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            if target_contours:
                target = max(target_contours, key=cv2.contourArea)
                if cv2.contourArea(target) > TARGET_MIN_AREA:
                    x, y, w, h = cv2.boundingRect(target)
                    cx = x + w // 2
                    frame_center = frame.shape[1] // 2
                    if cv2.contourArea(target) > 18000:
                        state = "TARGET TOO CLOSE"
                        command = "s"
                    elif cx < frame_center - CENTRE_TOLERANCE:
                        state = "FOLLOW LEFT"
                        command = "l"
                    elif cx > frame_center + CENTRE_TOLERANCE:
                        state = "FOLLOW RIGHT"
                        command = "r"
                    else:
                        state = "FOLLOW FORWARD"
                        command = "f"

        # SERIAL COMMUNICATION STAGE
        # The Raspberry Pi sends the same single-character commands to the micro:bit.
        if command != last_command:
            ser.write((command + "\n").encode())
            print("camera frame:", "RECEIVED")
            print("vision state:", state)
            print("command sent:", command)
            print(
                "record if changed:",
                "blur", BLUR_KERNEL,
                "target_min_area", TARGET_MIN_AREA,
                "obstacle_min_area", OBSTACLE_MIN_AREA,
                "centre_tolerance", CENTRE_TOLERANCE,
            )
            last_command = command

        # ROBOT OUTPUT STAGE
        # f = forward, l = left, r = right, s = stop

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
            f"CMD: {command}  TOL: {CENTRE_TOLERANCE}  AREA: {TARGET_MIN_AREA}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            "Verify subsystems, change one value only if needed, then retest",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.imshow("session14_student_frame", frame)
        cv2.imshow("session14_target_mask", target_mask)
        cv2.imshow("session14_obstacle_mask", obstacle_mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    ser.write(b"s\n")
    close_camera(camera_handle)
    cv2.destroyAllWindows()
