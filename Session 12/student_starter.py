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

# Session 12 student scaffold.
# Use this existing robot system strictly as a reference while comparing design concepts.
# Students run it, observe it, and connect what they see to Concept A, B, and C.

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)
camera_handle = open_camera()
last_command = None

print("Session 12 reference system")
print("Run the program and compare possible Smart Warehouse robot designs.")
print("Worksheet prompts:")
print("- Which robot jobs from the design brief are visible in this reference system?")
print("- Which concept would place the camera, Raspberry Pi, battery, and robot parts most effectively?")
print("- Which concept would be easiest to build, safest, and most reliable?")
print("- What limitation of the current reference system should affect your design choice?")
print("- Which concept would you recommend, and why?\n")

try:
    while True:
        frame = read_frame(camera_handle)
        if frame is None:
            print("No frame received from camera.")
            break

        # CAMERA / INPUT STAGE
        # This frame is the robot's current input from the Pi Camera.

        # VISION PROCESSING STAGE
        # The program converts the frame and isolates target and obstacle colours.
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        target_mask = cv2.inRange(hsv, TARGET_LOWER, TARGET_UPPER)
        obstacle_mask = cv2.inRange(hsv, OBSTACLE_LOWER_1, OBSTACLE_UPPER_1)
        obstacle_mask |= cv2.inRange(hsv, OBSTACLE_LOWER_2, OBSTACLE_UPPER_2)

        command = "s"
        state = "WAIT"

        # DECISION STAGE
        # The program chooses one robot command from the visual result.
        obstacle_contours, _ = cv2.findContours(
            obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if obstacle_contours:
            obstacle = max(obstacle_contours, key=cv2.contourArea)
            if cv2.contourArea(obstacle) > 2500:
                state = "OBSTACLE PRIORITY"
                command = "s"
        else:
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
            "Compare concepts: placement, safety, limits, reliability",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.imshow("session12_student_reference", frame)
        cv2.imshow("session12_target_mask", target_mask)
        cv2.imshow("session12_obstacle_mask", obstacle_mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    ser.write(b"s\n")
    close_camera(camera_handle)
    cv2.destroyAllWindows()
