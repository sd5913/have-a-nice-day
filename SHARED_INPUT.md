# Shared hand input

Shared hand tracking for the four mini-games. Detects hand position, pinching and release, with smoothing and recovery when tracking is lost. Each game can use these inputs for its own controls, such as dragging ingredients, moving covers or steering a basket.

## Setup

Use Python 3.11 with uv. From the repository root:

```bash
uv venv --python 3.11
uv pip install -r requirements-shared.txt
uv run --no-project python download_model.py
uv run --no-project python shared_input_demo.py
```

The demo starts in mouse mode. H enables the webcam, M returns to mouse, Q quits.
Open your hand once before pinching after startup or tracking recovery.
Camera index defaults to 0; use `--camera 1` to select a different device.
Allow camera access if prompted. Frames are processed locally, not recorded/uploaded.
Model file: `hand_landmarker.task` in the repository root; not bundled in this change.
Official model/setup: https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker/python

The existing main.py can continue using GestureTracker(model_path), update(frame), close().
Flip the frame horizontally before update, as main.py already does; do not flip coordinates again.
This change does not wire a game into main.py or replace another member's runner.

## Contract

Keep one camera/tracker in the main loop and send the same frame's HandInput to the active game:

```python
hand = tracker.update(frame)
game.update(hand)  # Each team member implements their own game update method.
```

- tracked: hand exists; x/y: smoothed palm position in [0,1], origin at top-left.
- pinched: held state; pressed/released: one-frame transitions.
- cancelled: tracking lost during hold; NOT a successful release/drop.
- ready: player has opened hand since startup/recovery; prevents accidental reacquisition grabs.
- points: original 21 normalized keypoints; index fingertip is points[8].
- source: hand or mouse. InputFilter also supports normalized mouse input.

Existing HandInput fields and positional order are preserved; new fields have defaults.
Tracking loss resets position smoothing and requires an open hand before another press.

## Per-game helpers

DragObject handles pinch/drag/release and returns to the pre-grab position on tracking loss.
CircleStir accumulates consistent circular motion, rejecting small back-and-forth oscillations.
The chef-specific five-finger classifier belongs in the chef game, not this shared tracker.
basket_position follows x without requiring pinch and holds its position if tracking is lost.
Visuals is optional: loads transparent PNG files and draws fallback placeholders; no game rules.
Each game owns its hit regions, scoring, stages, animations and completion conditions.

## Checks and limitations

```bash
uv run --no-project python -m unittest discover -s tests -p 'test_input.py' -v
uv run --no-project python -m unittest discover -s tests -p 'test_visuals.py' -v
```

8 automated tests pass locally: transitions, cancellation/recovery, drag rollback, circular
motion, pinch hysteresis, paused basket, alpha compositing and missing/corrupt image fallback.
Test environment: Python 3.11, OpenCV 4.11.0, MediaPipe 0.10.21, NumPy 1.26.4.
The student reported successful food pinch/drag in the separate chef prototype. A fresh-checkout
camera run and other machines/lighting are not verified. The agent's restricted execution
could not initialize the macOS graphics service; this is not proof of the student's runtime failure.
Ask teammates to test the shared demo and record actual machine/camera observations.

## Credits

Based on the team’s existing GestureTracker by Cshushs1, with coding assistance from Codex.
