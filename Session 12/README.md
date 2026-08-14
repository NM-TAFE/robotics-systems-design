# Session 12

## Session Overview

- Investigation objective: use the existing integrated robot as a reference system while comparing and selecting Smart Warehouse design concepts.
- Robotics concept: component placement, concept comparison, design trade-offs, and evidence-based recommendation.
- Expected behaviour: students observe how the current system works, then use those observations to compare Concept A, Concept B, and Concept C against the design brief.

## Equipment Required

- Session 11 design brief
- computer
- Raspberry Pi with Pi Camera or a development machine with a webcam fallback
- Python
- OpenCV
- NumPy
- PySerial
- micro:bit
- Maqueen robot
- coloured target object
- coloured obstacle object

## Library Functions Used

- Canonical camera path: `open_camera()`, `read_frame()`, `close_camera()` from `code_activities_v1/Pi Camera Library/pi_camera.py`
- OpenCV path: `cv2.cvtColor()`, `cv2.inRange()`, `cv2.findContours()`, `cv2.boundingRect()`, `cv2.putText()`, `cv2.imshow()`
- Serial path: `serial.Serial()`, `ser.write()`
- Existing robot command path: single-character `f`, `l`, `r`, `s` commands sent from Raspberry Pi to micro:bit to Maqueen

## Student Tasks

- RUN the existing integrated reference system
- OBSERVE the camera, vision, decision, serial, and robot-output stages
- IDENTIFY which robot jobs from the design brief are already demonstrated
- COMPARE how Concept A, Concept B, and Concept C would place and support the existing components
- IDENTIFY strengths, weaknesses, and trade-offs for each concept
- SELECT the concept that best fits the client problem, project limits, safety needs, and reliability needs
- JUSTIFY the recommended design using observed behaviour from the reference system

## Evidence Collection

- notes that support the worksheet sections on design brief review, concept comparison, recommendation, and trade-offs

## Practical Alignment

- supports Investigation 1 by reconnecting students with the design brief through visible robot jobs
- supports Investigation 2 by giving a real reference system students can use when sketching Concept A, B, and C
- supports Investigation 3 by helping students compare designs against observed subsystem needs and project limits
- supports Investigation 4 by giving concrete evidence students can use when recommending the best concept
- supports Investigation 5 by showing real trade-offs around placement, safety, visibility, and reliability

## Assessment Preparation

- prepares students to compare design options using evidence
- prepares students to justify component placement and subsystem reuse
- prepares students to recommend a practical prototype direction before building begins
- does not provide a completed Smart Warehouse assessment solution
