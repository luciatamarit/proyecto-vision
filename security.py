import cv2
import numpy as np
from collections import defaultdict

# HSV RANGES
ORANGE_LOW = np.array([5, 120, 120])
ORANGE_HIGH = np.array([20, 255, 255])

RED_LOW1 = np.array([0, 120, 120])
RED_HIGH1 = np.array([10, 255, 255])
RED_LOW2 = np.array([170, 120, 120])
RED_HIGH2 = np.array([180, 255, 255])

WHITE_LOW = np.array([0, 0, 200])
WHITE_HIGH = np.array([180, 60, 255])

BLUE_LOW = np.array([95, 80, 50])
BLUE_HIGH = np.array([130, 255, 255])

# DETECTORS
def detect_orange_ball(hsv_frame, min_area=800):
    mask = cv2.inRange(hsv_frame, ORANGE_LOW, ORANGE_HIGH)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False, None

    c = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(c)
    if area < min_area:
        return False, None

    return True, area

def detect_white_ball(hsv_frame, orange_area=None, min_area=800):
    mask = cv2.inRange(hsv_frame, WHITE_LOW, WHITE_HIGH)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False

    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        if orange_area is not None and abs(area - orange_area) < 0.4 * orange_area:
            continue

        return True

    return False


# def detect_red_ball(hsv_frame, orange_area=None, min_area=800):
#     mask1 = cv2.inRange(hsv_frame, RED_LOW1, RED_HIGH1)
#     mask2 = cv2.inRange(hsv_frame, RED_LOW2, RED_HIGH2)
#     mask = mask1 | mask2

#     kernel = np.ones((5, 5), np.uint8)
#     mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
#     mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     if not contours:
#         return False

#     for c in contours:
#         area = cv2.contourArea(c)
#         if area < min_area:
#             continue

#         if orange_area is not None and abs(area - orange_area) < 0.4 * orange_area:
#             continue

#         return True

#     return False


def detect_basket(hsv):
    blue_mask = cv2.inRange(hsv, BLUE_LOW, BLUE_HIGH)
    blue_mask = cv2.medianBlur(blue_mask, 5)

    blue_conts, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for b in blue_conts:
        if cv2.contourArea(b) < 4000:
            continue

        x, y, w, h = cv2.boundingRect(b)
        board_bottom = y + h

        red_mask1 = cv2.inRange(hsv, RED_LOW1, RED_HIGH1)
        red_mask2 = cv2.inRange(hsv, RED_LOW2, RED_HIGH2)
        red_mask = cv2.medianBlur(red_mask1 | red_mask2, 5)

        red_conts, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for r in red_conts:
            area_r = cv2.contourArea(r)
            if 800 < area_r < 5000:
                xr, yr, wr, hr = cv2.boundingRect(r)
                if yr > board_bottom - 10:
                    return True
    return False


def detect_scoreboard(gray, frame):
    _, th = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
    conts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    h, w = gray.shape[:2]

    for c in conts:
        if cv2.contourArea(c) > 15000:
            approx = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
            if len(approx) == 4:
                x, y, cw, ch = cv2.boundingRect(c)
                if cw < 0.95 * w and ch < 0.95 * h:
                    roi = frame[y:y+ch, x:x+cw]
                    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
                    red_pixels = cv2.inRange(hsv_roi, RED_LOW1, RED_HIGH1)
                    if cv2.countNonZero(red_pixels) > 300:
                        return True
    return False




# SECURITY LOGIC
SEQUENCE_GOAL = ["BASKET", "ORANGE", "WHITE", "SCORE"]
STABLE_FRAMES = 8

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Camera error")
        return

    stable_counter = defaultdict(int)
    sequence = []

    print("SECURITY MODE ACTIVE")
    print("Expected:", SEQUENCE_GOAL)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        orange_detected, orange_area = detect_orange_ball(hsv)
        white_detected = detect_white_ball(hsv, orange_area)


        raw = {
            "BASKET": detect_basket(hsv),
            "ORANGE": orange_detected,
            "WHITE": white_detected,
            "SCORE": detect_scoreboard(gray, frame)
        }

        # DETECTED (SIN ORDEN)
        detected_now = [k for k, v in raw.items() if v]
        cv2.putText(frame, f"Detected: {detected_now}",
                    (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                    (255, 255, 255), 2)

        # SECUENCIA DE SEGURIDAD (PRESENCIA CONTINUA)
        sequence = []

        for obj in SEQUENCE_GOAL:
            if raw[obj]:
                sequence.append(obj)
            else:
                break


        cv2.putText(frame, f"Security sequence: {sequence}",
                    (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                    (200, 200, 200), 2)

        # OK FINAL
        if sequence == SEQUENCE_GOAL:
            cv2.putText(frame, "SECURITY OK",
                        (30, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2,
                        (0, 255, 0), 3)
            cv2.imshow("SECURITY", frame)
            cv2.waitKey(800)
            cap.release()
            cv2.destroyAllWindows()
            return True
       

        cv2.imshow("SECURITY", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


    cap.release()
    cv2.destroyAllWindows()
    return False


if __name__ == "__main__":
    main()
