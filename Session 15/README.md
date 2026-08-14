# Session 15

## Session Overview

- investigation objective: organise the approved Session 14 prototype into simple autonomous behaviours with clear priorities and a fail-safe
- connection to previous session: this is the integrated Session 14 prototype with its existing decision logic organised into clearer autonomous behaviours, without changing the camera, vision, or communication architecture
- expected behaviour: the robot uses `SEARCH`, `FOLLOW`, and `STOP` states, tests conflicting conditions, and applies a predictable fail-safe

## Equipment

- Raspberry Pi 4B
- Pi Camera Module 3
- computer
- Python
- OpenCV
- NumPy
- PySerial
- micro:bit
- Maqueen robot
- integrated Session 14 prototype
- coloured target object
- coloured obstacle object

## Existing Session 14 Code Reused

- [code_activities_v1/session14/lecturer_solution.py](/Users/robbozinoz/Documents/nmtafe/Robotics/robotics-systems-design-cluster/Sessions/code_activities_v1/session14/lecturer_solution.py)
- [code_activities_v1/session14/student_starter.py](/Users/robbozinoz/Documents/nmtafe/Robotics/robotics-systems-design-cluster/Sessions/code_activities_v1/session14/student_starter.py)
- inherited system components:
  - canonical `open_camera()`, `read_frame()`, `close_camera()`
  - existing blur + HSV pipeline
  - existing target and obstacle masks
  - corrected obstacle-priority logic
  - existing serial commands `f`, `l`, `r`, `s`
  - Raspberry Pi -> micro:bit -> Maqueen command flow

## Verified Libraries

- canonical camera path: `open_camera()`, `read_frame()`, `close_camera()` from `code_activities_v1/Pi Camera Library/pi_camera.py`
- OpenCV path: `cv2.GaussianBlur()`, `cv2.cvtColor()`, `cv2.inRange()`, `cv2.findContours()`, `cv2.boundingRect()`, `cv2.putText()`, `cv2.imshow()`
- serial path: `serial.Serial()`, `ser.write()`
- existing robot command path: single-character `f`, `l`, `r`, `s` commands sent from Raspberry Pi to micro:bit to Maqueen

## Session 15 Additions

- explicit `SEARCH`, `FOLLOW`, and `STOP` state names
- behaviour transitions between those states
- priority logic where unsafe conditions override normal task behaviour
- target-loss tracking
- simple fail-safe stop
- controlled behaviour comparison before and after one small change if needed

## Student Focus

```text
IDENTIFY STATE
      ↓
TEST TRANSITION
      ↓
CHECK PRIORITY
      ↓
TEST FAIL-SAFE
      ↓
CHANGE ONE VALUE IF REQUIRED
      ↓
COMPARE BEFORE / AFTER
```

This file should be treated as the Session 14 prototype with a clearer behaviour layer, not as a completely new program.

## Existing Inputs Used

- camera target detection
- camera obstacle detection
- target-loss frame count as an existing system condition

This is a simple introductory example of combining information for autonomous behaviour.
The current decision uses:
- camera target detection
- camera obstacle detection
- target-loss count

A later system could combine camera, distance, LiDAR, IMU, or other sensors, but no new hardware is introduced here.

## Controlled Refinement Values

- `SEARCH_COMMAND`
- `FAILSAFE_LOST_FRAME_LIMIT`
- `CENTRE_TOLERANCE`

These remain small existing behaviour values that can be changed one at a time during testing.
`FAILSAFE_LOST_FRAME_LIMIT` is a testable engineering parameter, not a guaranteed universal safety setting.

## Practical Alignment

- supports Investigation 1 by making `SEARCH`, `FOLLOW`, and `STOP` visible as explicit states
- supports Investigation 2 by testing priorities when target and obstacle conditions compete
- supports Investigation 3 by using more than one existing input in the decision stage
- supports Investigation 4 by implementing a simple observable fail-safe stop
- supports Investigation 5 by allowing before/after comparison under the same test conditions

## Assessment Preparation

- prepares students to explain behaviour organisation and transitions
- prepares students to justify safety priorities and fail-safe behaviour
- prepares students to compare system behaviour before and after refinement
- does not create a new architecture or provide an assessment solution
