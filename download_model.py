"""Download the official MediaPipe Hand Landmarker model, not camera data."""
from pathlib import Path
from urllib.request import urlopen
URL='https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task'
if __name__=='__main__':
    target=Path(__file__).with_name('hand_landmarker.task')
    if target.exists():
        print(f'Already exists: {target}; not overwritten.')
    else:
        try:
            with urlopen(URL,timeout=60) as response: data=response.read()
            if len(data)<100000: raise ValueError('Unexpected model response')
            target.write_bytes(data)
            print(f'Saved {target}')
        except Exception as exc:
            raise SystemExit(f'Download failed: {exc}. Mouse mode still works.')
