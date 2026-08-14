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
TARGET_LOWER = np.array([40, 70, 70])
TARGET_UPPER = np.array([80, 255, 255])
OBSTACLE_LOWER_1 = np.array([0, 120, 70])
OBSTACLE_UPPER_1 = np.array([10, 255, 255])
OBSTACLE_LOWER_2 = np.array([170, 120, 70])
OBSTACLE_UPPER_2 = np.array([179, 255, 255])


print("Session 13 reliable vision investigation")
print("Run the existing robot system and change one physical condition at a time.")
print("Suggested conditions: stationary, slow movement, faster movement, bright light, shadow, reflection.")
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
        # This is the live image from the Pi Camera.

        # VISION PROCESSING STAGE
        # The program applies blur, colour masking, and thresholding for reliability checks.
        # 'binary' is a simple grayscale black/white threshold view for investigation.
        # 'target_mask' is the HSV colour mask used by the robot's target-detection logic.
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
        target_mask = cv2.inRange(hsv, TARGET_LOWER, TARGET_UPPER)
        obstacle_mask = cv2.inRange(hsv, OBSTACLE_LOWER_1, OBSTACLE_UPPER_1)
        obstacle_mask |= cv2.inRange(hsv, OBSTACLE_LOWER_2, OBSTACLE_UPPER_2)

        command = "s"
        state = "WAIT"
        investigation_note = "Observe image clarity, noise, and the binary image before changing anything."

        # DECISION STAGE
        # The program chooses one command from the processed image.
        obstacle_contours, _ = cv2.findContours(
            obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        obstacle_detected = False
        if obstacle_contours:
            obstacle = max(obstacle_contours, key=cv2.contourArea)
            obstacle_area = cv2.contourArea(obstacle)
            if obstacle_area > 2500:
                obstacle_detected = True
                x, y, w, h = cv2.boundingRect(obstacle)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                state = "OBSTACLE PRIORITY"
                investigation_note = (
                    "If this state flickers, check reflections, lighting changes, and camera movement."
                )

        if not obstacle_detected:
            target_contours, _ = cv2.findContours(
                target_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            if target_contours:
                target = max(target_contours, key=cv2.contourArea)
                target_area = cv2.contourArea(target)
                if target_area > 600:
                    x, y, w, h = cv2.boundingRect(target)
                    cx = x + w // 2
                    frame_center = frame.shape[1] // 2
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(frame, (cx, y + h // 2), 6, (0, 0, 255), -1)
                    if target_area > 18000:
                        state = "TARGET TOO CLOSE"
                        investigation_note = (
                            "Large target area reached. Compare this result across different backgrounds and light."
                        )
                    elif cx < frame_center - 60:
                        state = "FOLLOW LEFT"
                        command = "l"
                        investigation_note = (
                            "Turn decisions depend on clear target edges and a stable image."
                        )
                    elif cx > frame_center + 60:
                        state = "FOLLOW RIGHT"
                        command = "r"
                        investigation_note = (
                            "Turn decisions depend on clear target edges and a stable image."
                        )
                    else:
                        state = "FOLLOW FORWARD"
                        command = "f"
                        investigation_note = (
                            "Forward decisions are strongest when the target mask clearly separates the object from the background."
                        )

        # SERIAL COMMUNICATION STAGE
        # The Raspberry Pi sends one short command to the micro:bit.
        if command != last_command:
            ser.write((command + "\n").encode())
            last_command = command

        # ROBOT OUTPUT STAGE
        # f = forward, l = left, r = right, s = stop
        if state != last_state:
            print("vision state:", state)
            print("command:", command)
            print("investigation note:", investigation_note)
            print("reliability reminder: change one physical condition, test again, and record the result.\n")
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
            "Investigate reliability: motion, noise, thresholding, environment",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.imshow("session13_reference_frame", frame)
        cv2.imshow("session13_blurred", blurred)
        cv2.imshow("session13_target_mask", target_mask)
        cv2.imshow("session13_binary", binary)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    ser.write(b"s\n")
    close_camera(camera_handle)
    cv2.destroyAllWindows()
