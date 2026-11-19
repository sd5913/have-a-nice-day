import cv2
import numpy as np

if __package__:
    from .game import HideAndSeek
else:
    from game import HideAndSeek


def main():
    width, height = 800, 520
    window = "Hide and Seek"
    game = HideAndSeek()

    x = y = None
    held = False
    pressed = False

    def mouse(event, px, py, flags, data):
        nonlocal x, y, held, pressed

        x = px / width
        y = py / height

        if event == cv2.EVENT_LBUTTONDOWN:
            held = True
            pressed = True
        elif event == cv2.EVENT_LBUTTONUP:
            held = False
        elif event == cv2.EVENT_MOUSEMOVE:
            if not flags & cv2.EVENT_FLAG_LBUTTON:
                held = False

    cv2.namedWindow(window, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(window, mouse)

    try:
        while True:
            if not game.found:
                game.update(x, y, held, pressed)

            pressed = False
            screen = np.full(
                (height, width, 3),
                (229, 237, 246),
                dtype=np.uint8,
            )

            if game.found:
                title = "You found the cat!"
            else:
                title = "Find the dots. Click and drag the cover."
                game.draw(screen)

            cv2.putText(
                screen, title, (24, 52),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75, (50, 43, 35), 2, cv2.LINE_AA,
            )
            cv2.putText(
                screen, "R: new round   Q: quit", (24, 490),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (50, 43, 35), 2, cv2.LINE_AA,
            )

            cv2.imshow(window, screen)
            key = cv2.waitKey(16) & 0xFF

            if key in (ord("q"), 27):
                break
            if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
                break
            if key == ord("r"):
                game = HideAndSeek()
                held = False
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
