# Session 14

## Session Overview

- Investigation objective: integrate the approved Smart Warehouse prototype using the verified Session 13 software baseline and make only controlled refinements when verification shows they are needed.
- Robotics concept: subsystem verification, complete system integration, controlled refinement, retesting, and engineering documentation.
- Expected behaviour: students run the integrated system, verify subsystems one at a time, identify a specific fault if one appears, adjust one real value only if required, retest, and document the outcome.

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
- prototype mounts and routed cables
- approved prototype plan
- coloured target object
- coloured obstacle object

## Reused Session 13 Baseline

- canonical `open_camera()`, `read_frame()`, and `close_camera()` camera path
- existing `cv2.GaussianBlur()` plus HSV colour-mask pipeline
- existing obstacle-priority decision order
- existing single-character serial commands `f`, `l`, `r`, `s`
- existing Raspberry Pi -> micro:bit -> Maqueen command architecture

## Controlled Refinement Values

- `BLUR_KERNEL`
- `TARGET_MIN_AREA`
- `OBSTACLE_MIN_AREA`
- `CENTRE_TOLERANCE`

These are exposed because they are real values already present in the working implementation and can be changed one at a time during integration testing.

## Student Tasks

- RUN the approved integrated baseline from Session 13
- VERIFY the vision, processing, communication, and drive subsystems separately
- INTEGRATE the complete prototype and confirm the command chain works end to end
- IDENTIFY one specific fault or instability if testing shows a problem
- RECORD the original value before changing one controlled refinement value
- RETEST the system and decide whether to keep or reverse the change
- DOCUMENT the engineering decision and the improvement made

## Evidence Collection

- notes that support the worksheet sections on prototype construction, subsystem verification, complete system integration, and prototype review
- observable code evidence such as `camera frame: RECEIVED`, `vision state: ...`, and `command sent: ...`, which students use alongside robot behaviour to record subsystem pass or fail in the worksheet

## Practical Alignment

- supports Investigation 1 by using the existing code while students compare the built prototype against the approved plan
- supports Investigation 2 by making subsystem-by-subsystem verification possible before full integration
- supports Investigation 3 by preserving the full camera-to-Maqueen pathway for complete system integration testing
- supports Investigation 4 by exposing only small real values for controlled refinement after evidence is collected

## Diagnostic Evidence

- the code reports observable subsystem evidence only
- the code does not automatically declare subsystem success
- subsystem pass or fail remains a student observation recorded in the Practical Investigation Worksheet

## Assessment Preparation

- prepares students to collect implementation evidence for Assessment Task 3
- prepares students to document subsystem faults, corrective actions, and retest results
- prepares students to enter Session 15 with an integrated prototype rather than a redesigned application
- does not recreate the vision system or redesign the software architecture
