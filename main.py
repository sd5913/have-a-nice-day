import cv2

# 打开电脑自带摄像头
cap = cv2.VideoCapture(0)

print("正在启动摄像头，按键盘上的 'q' 键可以退出...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("无法读取摄像头画面")
        break

    # 在画面上加一行文字提示
    cv2.putText(frame, "Have a Nice Day - Test Window", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # 实时展示窗口
    cv2.imshow('Cat Game Prototype', frame)

    # 按下 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()