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


print("Session 12 design comparison reference system")
print("Use the existing robot to compare possible Smart Warehouse designs.")
print("System stages: camera -> vision -> decision -> serial -> robot output")
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

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        target_mask = cv2.inRange(hsv, TARGET_LOWER, TARGET_UPPER)
        obstacle_mask = cv2.inRange(hsv, OBSTACLE_LOWER_1, OBSTACLE_UPPER_1)
        obstacle_mask |= cv2.inRange(hsv, OBSTACLE_LOWER_2, OBSTACLE_UPPER_2)

        command = "s"
        state = "WAIT"
        capability_note = "No strong target or obstacle detected."
        design_note = "Designs need a camera view, safe stopping, and clear hardware placement."

        obstacle_contours, _ = cv2.findContours(
            obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        if obstacle_contours:
            obstacle = max(obstacle_contours, key=cv2.contourArea)
            obstacle_area = cv2.contourArea(obstacle)
            if obstacle_area > 2500:
                x, y, w, h = cv2.boundingRect(obstacle)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                state = "OBSTACLE PRIORITY"
                capability_note = "The existing robot can detect a red obstacle and stop."
                design_note = (
                    "A safer concept keeps the camera view clear and gives the robot space "
                    "to stop before a collision."
                )
        else:
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
                        capability_note = "The existing robot stops when the target fills most of the view."
                        design_note = (
                            "A front camera and stable mounting help the robot judge when to stop."
                        )
                    elif cx < frame_center - 60:
                        state = "FOLLOW LEFT"
                        command = "l"
                        capability_note = "The existing robot can turn left to keep a target in view."
                        design_note = (
                            "Concepts with better camera placement may track targets more consistently."
                        )
                    elif cx > frame_center + 60:
                        state = "FOLLOW RIGHT"
                        command = "r"
                        capability_note = "The existing robot can turn right to keep a target in view."
                        design_note = (
                            "Concepts with better camera placement may track targets more consistently."
                        )
                    else:
                        state = "FOLLOW FORWARD"
                        command = "f"
                        capability_note = "The existing robot can move forward when the target is centred."
                        design_note = (
                            "Concepts with balanced component placement may move more reliably in a straight line."
                        )

        if command != last_command:
            ser.write((command + "\n").encode())
            last_command = command

        if state != last_state:
            print("camera: frame captured")
            print("vision:", state)
            print("decision: command", command)
            print("serial: sent", repr(command + "\n"))
            print("robot output:", capability_note)
            print("design comparison note:", design_note)
            print("limitation: current behaviour depends on colour detection and a clear camera view\n")
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
            f"COMMAND: {command}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        cv2.putText(
            frame,
            "Compare concepts: component placement, safety, limits, reliability",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            2,
        )

        cv2.imshow("session12_reference_system", frame)
        cv2.imshow("session12_target_mask", target_mask)
        cv2.imshow("session12_obstacle_mask", obstacle_mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    ser.write(b"s\n")
    close_camera(camera_handle)
    cv2.destroyAllWindows()
