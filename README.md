# Have a Nice Day

A virtual cat game controlled by hand gestures. Use your webcam to play short games with a cat and build a bond over time.

## Mini Games

| Game | How to play |
| --- | --- |
| **Little Cat Chef** | Pinch to pick up ingredients, stir them in a bowl, and serve the meal to the cat. |
| **Hide and Seek** | Pinch and drag objects to look for the cat. Watch for a moving tail or listen for a sound. |
| **Ball Rally** | Receive the ball, pinch to hold it, and release to roll it back to the cat. |
| **Catch Together** | Move your hand left and right to steer a basket and catch toy fish dropped by the cat. |

## How It Works

- **OpenCV** captures video from the webcam.
- **MediaPipe Hand Landmarker** detects hand landmarks.
- A shared gesture module turns those landmarks into game inputs, such as hand position, pinch, and release.

## Project Structure

- `main.py` — Starts the camera prototype.
- `utils/gesture_tracker.py` — Shared hand tracking module.
- `games/` — One folder for each mini game.
- `requirements.txt` — Python dependencies.

## Getting Started

From the repository root, install the dependencies and run the camera test:

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

Allow camera access when prompted. Press **Q** to close the test window.

## Development Status

- [x] Open the webcam and display a live preview.
- [ ] Integrate and test hand tracking, pinch, and release.
- [ ] Build **Catch Together** as the first playable game.
- [ ] Add the other three mini games and shared bond progression.

## Team

Chang Shu- Hide And Seek
Li Xinyang- Little Cat Chef
