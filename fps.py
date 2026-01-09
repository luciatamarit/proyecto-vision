import cv2
import time

cap = cv2.VideoCapture(0)
prev = time.time()

while True:
    ret, frame = cap.read()
    now = time.time()
    fps = 1 / (now - prev)
    prev = now

    cv2.putText(frame, f"FPS: {fps:.1f}", (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

    cv2.imshow("FPS test", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
