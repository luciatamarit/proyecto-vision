import cv2
import numpy as np
import subprocess

# ------------ HSV ranges -------------
ORANGE_LOW = np.array([5, 120, 120])
ORANGE_HIGH = np.array([20, 255, 255])

RED_LOW1 = np.array([0, 120, 120])
RED_HIGH1 = np.array([10, 255, 255])
RED_LOW2 = np.array([170, 120, 120])
RED_HIGH2 = np.array([180, 255, 255])

BLUE_LOW = np.array([90, 90, 60])
BLUE_HIGH = np.array([130, 255, 255])

# ------------ Detection functions -------------
def detect_orange(frame_hsv):
    mask = cv2.inRange(frame_hsv, ORANGE_LOW, ORANGE_HIGH)
    return cv2.countNonZero(mask) > 1000

# def detect_red(frame_hsv):
#     mask1 = cv2.inRange(frame_hsv, RED_LOW1, RED_HIGH1)
#     mask2 = cv2.inRange(frame_hsv, RED_LOW2, RED_HIGH2)
#     mask = mask1 | mask2
#     return cv2.countNonZero(mask) > 1000

def detect_red(frame_hsv):
    # 1. Máscara de color rojo
    mask1 = cv2.inRange(frame_hsv, RED_LOW1, RED_HIGH1)
    mask2 = cv2.inRange(frame_hsv, RED_LOW2, RED_HIGH2)
    mask = cv2.medianBlur(mask1 | mask2, 5)

    # 2. Find contours
    conts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in conts:
        area = cv2.contourArea(c)

        # 3. Área mínima y máxima para una pelota roja
        if area < 1500 or area > 25000:
            continue

        # 4. Circularidad
        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue

        circularity = 4 * np.pi * (area / (perimeter * perimeter))

        # Circularidad perfecta = 1 | redonda ≈ 0.75–1.0
        if circularity > 0.70:
            return True

    return False


# Nuevo aro naranja
def detect_orange_hoop(frame_hsv):
    mask = cv2.inRange(frame_hsv, ORANGE_LOW, ORANGE_HIGH)
    mask = cv2.medianBlur(mask, 5)
    conts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in conts:
        area = cv2.contourArea(c)
        if 1500 < area < 8000:  # área típica del aro
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = w / float(h + 1)
            if aspect_ratio > 2.5:  # forma horizontal típica
                return True
    return False

# Detector de marcador
def detect_marker(frame_gray):
    _, th = cv2.threshold(frame_gray, 120, 255, cv2.THRESH_BINARY)
    conts, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    h, w = frame_gray.shape[:2]

    for c in conts:
        area = cv2.contourArea(c)
        if area > 5000:
            approx = cv2.approxPolyDP(c, 0.02 * cv2.arcLength(c, True), True)
            if len(approx) == 4:
                x, y, cw, ch = cv2.boundingRect(c)
                if cw < 0.95 * w and ch < 0.95 * h:
                    return True
    return False


# ------------ MAIN SECURITY SEQUENCE -------------
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Camera not found.")
        return

    window = "SECURITY MODE - Show patterns in correct order"
    cv2.namedWindow(window, cv2.WINDOW_NORMAL)

    sequence_goal = ["HOOP", "ORANGE", "RED", "MARKER"]
    sequence_current = []

    print("SECURITY MODE ACTIVE")
    print("Expected sequence:", sequence_goal)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # --- DETECCIONES ---
        detections = {
            "HOOP": detect_orange_hoop(hsv),
            "ORANGE": detect_orange(hsv),
            "MARKER": detect_marker(gray),
            "RED": detect_red(hsv)
        }

        # --- MOSTRAR ESTADO ---
        cv2.putText(frame, f"Sequence: {sequence_current}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        cv2.putText(frame, f"Detected: {[k for k,v in detections.items() if v]}", (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        # --- LÓGICA DE ORDEN + PERSISTENCIA ---
        reset_flag = False

        # 1. Si un objeto ya validado desaparece → reset
        for obj in sequence_current:
            if not detections[obj]:
                reset_flag = True
                break

        if reset_flag:
            sequence_current = []
            cv2.putText(frame, "Object lost → RESET", (30, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        else:
            # 2. Comprobar el siguiente paso del orden
            if len(sequence_current) < len(sequence_goal):
                expected_next = sequence_goal[len(sequence_current)]
                if detections[expected_next]:
                    sequence_current.append(expected_next)
                    cv2.putText(frame, f"{expected_next} OK", (30, 140),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        # 3. Secuencia completa y todos visibles → desbloquear
        if sequence_current == sequence_goal and all(detections[k] for k in sequence_goal):

            cv2.putText(frame, "SECUENCIA COMPLETA - ACCESO PERMITIDO",
                        (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 3)

            cv2.imshow(window, frame)
            cv2.waitKey(800)

            print("\nSEQUENCE CORRECT ✔ Unlocking TRACKING...\n")

            cap.release()
            cv2.destroyAllWindows()

            # Ejecutar tracking.py
            subprocess.Popen(["python", "tracking.py"])
            return

        # --- MOSTRAR FRAME ---
        cv2.imshow(window, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
