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


print("Session 14 prototype integration")
print("Use the approved Session 13 system as the prototype reference.")
print("Verify subsystems first, then integrate the complete robot.")
print("Adjust one existing parameter only if testing shows it is required.")
print("Press q to quit.\n")

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
camera_handle = open_camera()
last_command = None
last_state = None

try:
    while True:
        frame = read_frame(camera_handle)
        if frame is None:
            print("No frame received from camera.")
            break

        # CAMERA / INPUT STAGE
        # The integrated prototype receives a live frame from the Pi Camera.

        # VISION / PROCESSING STAGE
        # The existing blur and HSV pipeline is reused directly from Session 13.
        blurred = cv2.GaussianBlur(frame, BLUR_KERNEL, 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        target_mask = cv2.inRange(hsv, TARGET_LOWER, TARGET_UPPER)
        obstacle_mask = cv2.inRange(hsv, OBSTACLE_LOWER_1, OBSTACLE_UPPER_1)
        obstacle_mask |= cv2.inRange(hsv, OBSTACLE_LOWER_2, OBSTACLE_UPPER_2)

        command = "s"
        state = "WAIT"
        refinement_note = "Verify the prototype matches the approved design before changing any value."

        # DECISION STAGE
        # The existing obstacle-priority logic is preserved.
        obstacle_contours, _ = cv2.findContours(
            obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        obstacle_detected = False
        if obstacle_contours:
            obstacle = max(obstacle_contours, key=cv2.contourArea)
            obstacle_area = cv2.contourArea(obstacle)
            if obstacle_area > OBSTACLE_MIN_AREA:
                obstacle_detected = True
                x, y, w, h = cv2.boundingRect(obstacle)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                state = "OBSTACLE PRIORITY"
                refinement_note = (
                    "If obstacle behaviour is unreliable, inspect lighting, mounting, and "
                    "only then consider a small obstacle-area change."
                )

        if not obstacle_detected:
            target_contours, _ = cv2.findContours(
                target_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            if target_contours:
                target = max(target_contours, key=cv2.contourArea)
                target_area = cv2.contourArea(target)
                if target_area > TARGET_MIN_AREA:
                    x, y, w, h = cv2.boundingRect(target)
                    cx = x + w // 2
                    frame_center = frame.shape[1] // 2
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(frame, (cx, y + h // 2), 6, (0, 0, 255), -1)
                    if target_area > 18000:
                        state = "TARGET TOO CLOSE"
                        refinement_note = (
                            "The target stop condition works. Check mount stability and stopping space."
                        )
                    elif cx < frame_center - CENTRE_TOLERANCE:
                        state = "FOLLOW LEFT"
                        command = "l"
                        refinement_note = (
                            "If steering oscillates, check camera alignment before changing centre tolerance."
                        )
                    elif cx > frame_center + CENTRE_TOLERANCE:
                        state = "FOLLOW RIGHT"
                        command = "r"
                        refinement_note = (
                            "If steering oscillates, check camera alignment before changing centre tolerance."
                        )
                    else:
                        state = "FOLLOW FORWARD"
                        command = "f"
                        refinement_note = (
                            "Forward tracking is active. Retest after any single controlled adjustment."
                        )

        # SERIAL COMMUNICATION STAGE
        # The Raspberry Pi sends the same single-character commands used in earlier sessions.
        if command != last_command:
            ser.write((command + "\n").encode())
            last_command = command

        # ROBOT OUTPUT STAGE
        # The micro:bit and Maqueen respond to f, l, r, and s.
        if state != last_state:
            print("camera frame:", "RECEIVED")
            print("vision state:", state)
            print("command sent:", command)
            print("refinement note:", refinement_note)
            print(
                "current values:",
                "blur", BLUR_KERNEL,
                "target_min_area", TARGET_MIN_AREA,
                "obstacle_min_area", OBSTACLE_MIN_AREA,
                "centre_tolerance", CENTRE_TOLERANCE,
            )
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
            f"CMD: {command}  TOL: {CENTRE_TOLERANCE}  AREA: {TARGET_MIN_AREA}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            "Integrate -> verify -> change one item -> retest -> document",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.imshow("session14_integrated_frame", frame)
        cv2.imshow("session14_target_mask", target_mask)
        cv2.imshow("session14_obstacle_mask", obstacle_mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    ser.write(b"s\n")
    close_camera(camera_handle)
    cv2.destroyAllWindows()
