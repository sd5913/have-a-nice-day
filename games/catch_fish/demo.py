"""几何图形占位版：合作接小鱼（Catch Together）核心玩法原型。"""

from __future__ import annotations

from dataclasses import dataclass
from random import uniform
import cv2
import numpy as np


@dataclass
class FishToy:
    x: float  # 归一化横坐标 [0.1, 0.9]
    y: float  # 归一化纵坐标 [0.0, 1.0]
    speed: float
    caught: bool = False
    missed: bool = False


class CatchTogetherGame:
    """用简单几何图形跑通接小鱼、落点提示、失误不扣分、跟踪丢失暂停与鼠标备用。"""

    def __init__(self, target_count: int = 8) -> None:
        self.target_count = target_count
        self.caught_count = 0
        self.missed_count = 0  # 仅作统计，不扣分、不减进度
        self.completed = False

        # 篮子状态（归一化 X 坐标，Y 固定在底部区域）
        self.basket_x = 0.5
        self.basket_y = 0.86
        self.basket_half_w = 0.09
        self.basket_half_h = 0.03

        # 顶部架子与猫咪提示状态
        self.shelf_y = 0.16
        self.cat_x = 0.5
        self.hint_target_x = 0.5
        self.paw_raised = False
        self.spawn_cooldown = 0.45  # 距离下一条小鱼拨下的提示/冷却秒数

        # 当前下落的小鱼列表（每次先专注一条或少量，手感更清爽）
        self.fish_list: list[FishToy] = []

        # 鼠标备用状态
        self.mouse_x: float | None = None
        self.mouse_active = False

    def set_mouse_position(self, norm_x: float) -> None:
        self.mouse_x = max(0.08, min(0.92, norm_x))
        self.mouse_active = True

    def _schedule_next_fish(self) -> None:
        """猫咪先用目光和抬爪提示下一个落点，短暂延迟后再拨下小鱼。"""
        self.hint_target_x = uniform(0.14, 0.86)
        self.paw_raised = True
        self.spawn_cooldown = 0.55

    def _spawn_fish(self) -> None:
        speed = uniform(0.24, 0.34)
        self.fish_list.append(
            FishToy(
                x=self.hint_target_x,
                y=self.shelf_y + 0.03,
                speed=speed,
            )
        )
        self.paw_raised = False

    def reset(self) -> None:
        self.__init__(target_count=self.target_count)

    def update(
        self,
        dt: float,
        hand_x: float | None,
        hand_tracked: bool,
    ) -> dict[str, object]:
        """更新游戏逻辑。

        参数:
            dt: 距离上一帧经过的秒数
            hand_x: 手部归一化横坐标 [0, 1]，未检测到手时可为 None
            hand_tracked: 是否成功追踪到手部
        返回:
            状态字典，方便外部/测试查看当前事件
        """
        dt = max(0.0, min(dt, 0.1))

        # 识别不到手时暂停玩法；若用户移动过鼠标，则启用鼠标备用控制
        active_x: float | None = None
        paused_no_hand = False

        if hand_tracked and hand_x is not None:
            active_x = max(0.08, min(0.92, hand_x))
        elif self.mouse_active and self.mouse_x is not None:
            active_x = self.mouse_x
        else:
            paused_no_hand = True

        if self.completed:
            return {
                "paused": False,
                "completed": True,
                "caught": self.caught_count,
                "missed": self.missed_count,
            }

        if paused_no_hand:
            return {
                "paused": True,
                "reason": "no_hand_detected",
                "caught": self.caught_count,
                "missed": self.missed_count,
            }

        # 平滑移动篮子与猫咪朝向
        assert active_x is not None
        self.basket_x += (active_x - self.basket_x) * min(1.0, dt * 16.0)
        self.cat_x += (self.hint_target_x - self.cat_x) * min(1.0, dt * 8.0)

        # 如果场上没有活跃小鱼，安排猫咪提示并拨出下一条
        if not self.fish_list:
            if not self.paw_raised and self.spawn_cooldown <= 0:
                self._schedule_next_fish()
            else:
                self.spawn_cooldown -= dt
                if self.spawn_cooldown <= 0 and self.paw_raised:
                    self._spawn_fish()

        # 更新下落小鱼与碰撞判定
        remaining_fish: list[FishToy] = []
        for fish in self.fish_list:
            fish.y += fish.speed * dt

            in_x = abs(fish.x - self.basket_x) <= (self.basket_half_w + 0.025)
            in_y = abs(fish.y - self.basket_y) <= (self.basket_half_h + 0.025)

            if in_x and in_y:
                fish.caught = True
                self.caught_count += 1
                if self.caught_count >= self.target_count:
                    self.completed = True
            elif fish.y >= 0.96:
                fish.missed = True
                self.missed_count += 1  # 失误不扣分、不减计数
            else:
                remaining_fish.append(fish)

        self.fish_list = remaining_fish

        return {
            "paused": False,
            "completed": self.completed,
            "caught": self.caught_count,
            "missed": self.missed_count,
        }

    def render(self, frame: np.ndarray, paused: bool = False) -> np.ndarray:
        """用简单圆形、矩形、线条绘制占位画面。"""
        h, w, _ = frame.shape
        canvas = frame.copy()

        # 柔和浅底遮罩，突出几何占位元素
        overlay = np.full_like(canvas, (245, 240, 232))
        canvas = cv2.addWeighted(overlay, 0.72, canvas, 0.28, 0)

        # 1. 顶部架子（矩形横梁）
        shelf_px_y = int(self.shelf_y * h)
        cv2.rectangle(
            canvas,
            (int(0.08 * w), shelf_px_y - 8),
            (int(0.92 * w), shelf_px_y + 8),
            (130, 145, 165),
            -1,
        )

        # 2. 猫咪占位（圆形身体 + 圆形头 + 目光连线 + 抬爪示意）
        cat_px_x = int(self.cat_x * w)
        cat_px_y = shelf_px_y - 26
        target_px_x = int(self.hint_target_x * w)

        # 目光朝向虚线/细线与落点圆圈提示
        cv2.line(canvas, (cat_px_x, cat_px_y), (target_px_x, shelf_px_y + 6), (120, 170, 220), 2)
        cv2.circle(canvas, (target_px_x, shelf_px_y + 18), 8, (90, 150, 230), 2)

        # 猫咪身体与头部（圆形）
        cv2.circle(canvas, (cat_px_x, cat_px_y + 8), 18, (110, 165, 235), -1)
        cv2.circle(canvas, (cat_px_x, cat_px_y - 14), 14, (125, 180, 245), -1)

        # 抬爪提示（线条/小圆）
        if self.paw_raised:
            paw_px_x = cat_px_x + (18 if target_px_x >= cat_px_x else -18)
            paw_px_y = cat_px_y - 24
            cv2.line(canvas, (cat_px_x, cat_px_y - 6), (paw_px_x, paw_px_y), (80, 130, 210), 4)
            cv2.circle(canvas, (paw_px_x, paw_px_y), 6, (80, 130, 210), -1)

        # 3. 下落小鱼占位（椭圆 + 小三角尾巴）
        for fish in self.fish_list:
            fx = int(fish.x * w)
            fy = int(fish.y * h)
            cv2.ellipse(canvas, (fx, fy), (18, 10), 0, 0, 360, (220, 150, 80), -1)
            tail = np.array([[fx + 16, fy], [fx + 26, fy - 8], [fx + 26, fy + 8]], np.int32)
            cv2.fillPoly(canvas, [tail], (220, 150, 80))

        # 4. 底部篮子（矩形框）
        bx1 = int((self.basket_x - self.basket_half_w) * w)
        bx2 = int((self.basket_x + self.basket_half_w) * w)
        by1 = int((self.basket_y - self.basket_half_h) * h)
        by2 = int((self.basket_y + self.basket_half_h) * h)
        cv2.rectangle(canvas, (bx1, by1), (bx2, by2), (70, 140, 95), -1)
        cv2.rectangle(canvas, (bx1, by1), (bx2, by2), (45, 95, 65), 3)

        # 5. 状态文字（不扣分、目标进度、暂停/完成提示）
        cv2.putText(
            canvas,
            f"Caught: {self.caught_count}/{self.target_count}  Missed (no penalty): {self.missed_count}",
            (24, 36),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (50, 50, 50),
            2,
        )

        if paused:
            cv2.putText(
                canvas,
                "Paused: No hand detected (move mouse or show hand)",
                (24, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.72,
                (40, 60, 190),
                2,
            )

        if self.completed:
            cv2.putText(
                canvas,
                "Goal reached! Press R to replay or Q to quit",
                (24, h // 2 + 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (50, 140, 60),
                2,
            )

        return canvas


def run_standalone_demo() -> None:
    """独立运行测试窗口：支持鼠标移动备用控制，按 R 重置，按 Q 退出。"""
    game = CatchTogetherGame(target_count=8)
    cap = cv2.VideoCapture(0)
    win_name = "Catch Together (Placeholder)"
    cv2.namedWindow(win_name)

    def on_mouse(event: int, x: int, y: int, flags: int, param: object) -> None:
        if event == cv2.EVENT_MOUSEMOVE:
            w = max(1, int(param)) if isinstance(param, int) else 640
            game.set_mouse_position(x / w)

    prev_tick = cv2.getTickCount()
    freq = cv2.getTickFrequency()

    while True:
        now_tick = cv2.getTickCount()
        dt = (now_tick - prev_tick) / freq
        prev_tick = now_tick

        if cap.isOpened():
            ok, frame = cap.read()
            if not ok or frame is None:
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

        frame = cv2.flip(frame, 1)
        fh, fw, _ = frame.shape
        cv2.setMouseCallback(win_name, on_mouse, fw)

        # 占位阶段先用 hand_tracked=False 演示“未检测到手时暂停 + 鼠标备用控制”
        status = game.update(dt=dt, hand_x=None, hand_tracked=False)
        out = game.render(frame, paused=bool(status.get("paused", False)))
        cv2.imshow(win_name, out)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q")):
            break
        if key in (ord("r"), ord("R")):
            game.reset()

    if cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_standalone_demo()