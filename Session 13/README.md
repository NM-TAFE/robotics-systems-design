# Session 13

## Session Overview

- Investigation objective: use the existing integrated robot as a controlled reliability investigation harness before prototype construction.
- Robotics concept: motion effects, image noise, preprocessing, thresholding, environmental testing, failure investigation, and repeatability.
- Expected behaviour: students run the same vision system, change one physical condition at a time, observe the result, and record engineering evidence.

## Equipment Required

- Raspberry Pi 4B
- Pi Camera Module 3
- computer
- Python
- OpenCV
- NumPy
- PySerial
- micro:bit
- Maqueen robot
- coloured target object
- coloured obstacle object
- varied lighting and background conditions for testing

## Library Functions Used

- Canonical camera path: `open_camera()`, `read_frame()`, `close_camera()` from `code_activities_v1/Pi Camera Library/pi_camera.py`
- OpenCV path: `cv2.GaussianBlur()`, `cv2.cvtColor()`, `cv2.threshold()`, `cv2.inRange()`, `cv2.findContours()`, `cv2.boundingRect()`, `cv2.putText()`, `cv2.imshow()`
- Serial path: `serial.Serial()`, `ser.write()`
- Existing robot command path: single-character `f`, `l`, `r`, `s` commands sent from Raspberry Pi to micro:bit to Maqueen

### Image View Clarification

- `session13_target_mask` is the HSV colour mask used by the existing target-detection logic.
- `session13_binary` is a separate grayscale black/white threshold view used only to investigate binary image behaviour.

## Student Tasks

- RUN the existing integrated reference system
- OBSERVE the raw frame, blurred frame, HSV target mask, and grayscale binary threshold image
- CHANGE one physical condition only, such as movement, lighting, distance, background, or reflection
- RECORD what changed in detection quality and robot behaviour
- IDENTIFY one likely cause for any failure before changing anything else
- REPEAT tests to judge reliability and prototype readiness

## Evidence Collection

- notes that support the worksheet sections on motion effects, noise and preprocessing, thresholding and binary images, environmental testing, failure investigation, and reliability assessment

## Practical Alignment

- supports Investigation 1 by letting students compare image and behaviour quality during stationary, slow, and faster motion conditions
- supports Investigation 2 by showing how blur and lighting affect noise before object detection
- supports Investigation 3 by making the binary image visible so students can judge whether the object stands out from the background
- supports Investigation 4 by allowing environmental tests under different light, background, and reflection conditions
- supports Investigation 5 by giving students concrete failure evidence before they recommend any change
- supports Investigation 6 by allowing repeated runs of the same system to judge reliability before Session 14

## Assessment Preparation

- prepares students to justify reliability concerns with evidence
- prepares students to recommend physical and environmental improvements before prototype build
- prepares students to judge whether the current vision system is ready for Session 14 integration
- does not redesign the working robot architecture or provide an assessment solution
