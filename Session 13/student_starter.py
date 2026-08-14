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

# Session 13 student scaffold.
# Use this existing robot system as an investigation harness for vision reliability.
# Students run it, change one physical condition, observe the result, and record evidence.

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
camera_handle = open_camera()
last_command = None

print("Session 13 reliability investigation")
print("Run the existing robot system and observe the live views.")
print("Worksheet prompts:")
print("- How does the image change when the robot is stationary, moving slowly, or moving faster?")
print("- Which lighting condition produces the most noise?")
print("- How does the blurred image compare with the original image?")
print("- Does the binary image make the object stand out clearly from the background?")
print("- Which environment produces the poorest result, and what evidence supports that conclusion?")
print("- Is the vision system ready for prototype construction yet?\n")

try:
    while True:
        frame = read_frame(camera_handle)
        if frame is None:
            print("No frame received from camera.")
            break

        # CAMERA / INPUT STAGE
        # This is the live image from the Pi Camera.

        # VISION PROCESSING STAGE
        # The program applies blur, colour masking, and thresholding for investigation.
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

        # DECISION STAGE
        # The program chooses one robot command from the processed image.
        obstacle_contours, _ = cv2.findContours(
            obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        obstacle_detected = False
        if obstacle_contours:
            obstacle = max(obstacle_contours, key=cv2.contourArea)
            if cv2.contourArea(obstacle) > 2500:
                obstacle_detected = True
                state = "OBSTACLE PRIORITY"
                command = "s"

        if not obstacle_detected:
            target_contours, _ = cv2.findContours(
                target_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            if target_contours:
                target = max(target_contours, key=cv2.contourArea)
                if cv2.contourArea(target) > 600:
                    x, y, w, h = cv2.boundingRect(target)
                    cx = x + w // 2
                    frame_center = frame.shape[1] // 2
                    if cv2.contourArea(target) > 18000:
                        state = "TARGET TOO CLOSE"
                        command = "s"
                    elif cx < frame_center - 60:
                        state = "FOLLOW LEFT"
                        command = "l"
                    elif cx > frame_center + 60:
                        state = "FOLLOW RIGHT"
                        command = "r"
                    else:
                        state = "FOLLOW FORWARD"
                        command = "f"

        # SERIAL COMMUNICATION STAGE
        # The Raspberry Pi sends one short command to the micro:bit.
        if command != last_command:
            ser.write((command + "\n").encode())
            print("state:", state, "command:", command)
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
            "Investigate reliability: motion, noise, thresholding, environment",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.imshow("session13_student_frame", frame)
        cv2.imshow("session13_blurred", blurred)
        cv2.imshow("session13_target_mask", target_mask)
        cv2.imshow("session13_binary", binary)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    ser.write(b"s\n")
    close_camera(camera_handle)
    cv2.destroyAllWindows()
