from pathlib import Path

import cv2

from utils.gesture_tracker import GestureTracker


# 模型文件放在 main.py 同一层。
model_path = Path(__file__).with_name("hand_landmarker.task")
tracker = GestureTracker(model_path)

cap = cv2.VideoCapture(0)

try:
    if not cap.isOpened():
        raise RuntimeError("无法打开摄像头，请检查摄像头权限。")

    print("请将一只手放入画面，按 q 退出。")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("无法读取摄像头画面")
            break

        # 先镜像再识别，让手部坐标和预览画面一致。
        frame = cv2.flip(frame, 1)
        hand = tracker.update(frame)
        height, width = frame.shape[:2]

        status = "Show one hand"
        color = (0, 180, 255)

        if hand.tracked:
            status = "Pinched" if hand.pinched else "Released"
            color = (0, 220, 100) if hand.pinched else (255, 200, 80)

            for x, y in hand.points:
                cv2.circle(frame, (int(x * width), int(y * height)), 4, color, -1)

        cv2.putText(
            frame,
            f"Have a Nice Day | {status} | Q: quit",
            (16, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            color,
            2,
        )

        cv2.imshow("Cat Game Prototype", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    tracker.close()
    cv2.destroyAllWindows()
