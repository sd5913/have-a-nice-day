"""Search three hiding spots by dragging their covers."""
from random import randrange

import cv2


class HideAndSeek:
    def __init__(self):
        self.hidden = randrange(3)
        self.covers = [[x, 0.56] for x in (0.19, 0.49, 0.79)]
        self.grabbed = None
        self.offset = (0, 0)
        self.found = False

    def update(self, x, y, held, pressed):
        if x is None or y is None or not held:
            self.grabbed = None
            return False
        if pressed:
            for index in reversed(range(len(self.covers))):
                left, top = self.covers[index]
                if abs(x - left) <= 0.105 and abs(y - top) <= 0.12:
                    self.grabbed = index
                    self.offset = (left - x, top - y)
                    break
        if self.grabbed is None:
            return False
        left = max(0.105, min(0.895, x + self.offset[0]))
        top = max(0.20, min(0.78, y + self.offset[1]))
        self.covers[self.grabbed] = [left, top]
        start = (0.19, 0.49, 0.79)[self.hidden]
        if self.grabbed == self.hidden and (abs(left - start) > 0.12 or abs(top - 0.56) > 0.15):
            self.found = True
            return True
        return False

    def draw(self, image):
        h, w = image.shape[:2]
        clue_x = int((0.19, 0.49, 0.79)[self.hidden] * w)
        cv2.putText(image, "...", (clue_x - 12, int(h * 0.40)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (45, 39, 33), 2, cv2.LINE_AA)
        for (x, y), name, color in zip(
            self.covers, ("Curtain", "Box", "Sofa"),
            ((174, 156, 105), (125, 157, 193), (157, 134, 171)),
        ):
            left, top = int((x - 0.105) * w), int((y - 0.12) * h)
            cv2.rectangle(image, (left, top), (int((x + 0.105) * w), int((y + 0.12) * h)), color, -1)
            cv2.putText(image, name, (left + 15, int(y * h)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.65, (45, 39, 33), 2, cv2.LINE_AA)
