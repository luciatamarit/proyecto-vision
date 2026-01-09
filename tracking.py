import cv2
import numpy as np
import time

# PARÁMETROS DE CALIBRACIÓN
# Matriz intrínseca 
K = np.array([
    [851.09792811,   0.        , 496.3082453 ],
    [  0.        , 824.72695001, 337.64549556],
    [  0.        ,   0.        ,   1.        ]
], dtype=np.float32)

# Coeficientes de distorsión (k1, k2, p1, p2, k3)
dist_coeffs = np.array([[
    -0.16626935, 0.82529379, 0.00386685, -0.06644165, -0.88137497
]], dtype=np.float32)

# RANGOS HSV (PELota NARANJA Y ARO AZUL)
ORANGE_LOW = np.array([5, 120, 120])
ORANGE_HIGH = np.array([20, 255, 255])

BLUE_LOW = np.array([90, 90, 60])
BLUE_HIGH = np.array([130, 255, 255])

RED_LOW1 = np.array([0, 80, 80])
RED_HIGH1 = np.array([10, 255, 255])
RED_LOW2 = np.array([160, 80, 80])
RED_HIGH2 = np.array([180, 255, 255])


# FUNCIONES DE DETECCIÓN
def detect_orange_ball(hsv_frame, min_area=800):
    """Devuelve (encontrada_bool, (x, y, r)) para la pelota naranja."""
    mask = cv2.inRange(hsv_frame, ORANGE_LOW, ORANGE_HIGH)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False, None

    # Elegimos el contorno más grande por área
    c = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(c)
    if area < min_area:
        return False, None

    (x, y), r = cv2.minEnclosingCircle(c)
    return True, (int(x), int(y), int(r))


# def detect_blue_hoop(hsv_frame, min_area=2000):
#     """Devuelve (encontrado_bool, (x, y, w, h)) para el aro azul."""
#     mask = cv2.inRange(hsv_frame, BLUE_LOW, BLUE_HIGH)
#     kernel = np.ones((5, 5), np.uint8)
#     mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
#     mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

#     contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     if not contours:
#         return False, None

#     # Elegimos el contorno más grande
#     c = max(contours, key=cv2.contourArea)
#     area = cv2.contourArea(c)
#     if area < min_area:
#         return False, None

#     x, y, w, h = cv2.boundingRect(c)
#     return True, (x, y, w, h)

def detect_red_hoop(hsv_frame, min_area=600):
    """Devuelve (encontrado_bool, (x, y, w, h)) para el aro rojo."""
    mask1 = cv2.inRange(hsv_frame, RED_LOW1, RED_HIGH1)
    mask2 = cv2.inRange(hsv_frame, RED_LOW2, RED_HIGH2)
    mask = mask1 | mask2

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False, None

    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue

        perimeter = cv2.arcLength(c, True)
        if perimeter == 0:
            continue

        circularity = 4 * np.pi * area / (perimeter * perimeter)

        # aro aprox circular
        if circularity > 0.55:
            x, y, w, h = cv2.boundingRect(c)
            return True, (x, y, w, h)

    return False, None



# TRACKING + CONTEO DE CANASTAS
def main(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("ERROR: no se ha podido abrir la cámara.")
        return
    
    ret, frame = cap.read()
    if not ret:
        print("ERROR: no se ha podido leer un frame inicial.")
        cap.release()
        return

    h, w = frame.shape[:2]

    new_K, roi = cv2.getOptimalNewCameraMatrix(K, dist_coeffs, (w, h), 1, (w, h))
    map1, map2 = cv2.initUndistortRectifyMap(K, dist_coeffs, None, new_K, (w, h), cv2.CV_16SC2)

    window_name = "TRACKING - Pelota naranja y canastas"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    # DETECCIÓN INICIAL DEL ARO
    hoop_found = False
    hoop_rect = None
    max_hoop_search_frames = 60
    hoop_search_count = 0

    print("Buscando aro azul en los primeros frames...")

    while not hoop_found and hoop_search_count < max_hoop_search_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        undistorted = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR)
        hsv = cv2.cvtColor(undistorted, cv2.COLOR_BGR2HSV)

        # hoop_found, hoop_rect = detect_blue_hoop(hsv)
        hoop_found, hoop_rect = detect_red_hoop(hsv)

        hoop_search_count += 1

        if hoop_found:
            print("Aro detectado:", hoop_rect)
        cv2.putText(undistorted, "Buscando aro rojo...", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.imshow(window_name, undistorted)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return

    if not hoop_found:
        print("No se ha podido detectar el aro. Saliendo.")
        cap.release()
        cv2.destroyAllWindows()
        return

    # VARIABLES DE TRACKING
    trail_points = [] #puntos recientes de la trayectoria
    max_trail_len = 30
    score = 0
    last_time = time.time()
    fps = 0.0

    # Para lógica de canasta
    last_ball_center = None
    just_scored = False
    score_cooldown_frames = 0
    SCORE_COOLDOWN_MAX = 15  #frames durante los que no vuelve a contar otra canasta

    hoop_x, hoop_y, hoop_w, hoop_h = hoop_rect
    hoop_center_y = hoop_y + hoop_h // 2

    print("TRACKING iniciado. Pulsa 'q' para salir.")

    # BUCLE PRINCIPAL
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        # Aplicamos corrección de distorsión
        undistorted = cv2.remap(frame, map1, map2, interpolation=cv2.INTER_LINEAR)

        hsv = cv2.cvtColor(undistorted, cv2.COLOR_BGR2HSV)

        ball_ok, ball_params = detect_orange_ball(hsv)

        # Dibujo del aro
        cv2.rectangle(undistorted,
                      (hoop_x, hoop_y),
                      (hoop_x + hoop_w, hoop_y + hoop_h),
                      (0, 0, 255), 3)
        cv2.putText(undistorted, "ARO", (hoop_x, hoop_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 250), 2)

        current_center = None

        if ball_ok:
            x, y, r = ball_params
            current_center = (x, y)

            # Dibujamos la pelota
            cv2.circle(undistorted, (x, y), r, (0, 140, 255), 3)
            cv2.circle(undistorted, (x, y), 3, (0, 255, 255), -1)

            # Actualizamos la trayectoria
            trail_points.append(current_center)
            if len(trail_points) > max_trail_len:
                trail_points.pop(0)

            # Dibujar la trayectoria
            for i in range(1, len(trail_points)):
                if trail_points[i - 1] is None or trail_points[i] is None:
                    continue
                cv2.line(undistorted, trail_points[i - 1], trail_points[i], (0, 255, 0), 2)

            # LÓGICA DE CANASTA 
            if last_ball_center is not None and score_cooldown_frames == 0:
                last_x, last_y = last_ball_center
                cur_x, cur_y = current_center

                # Condiciones: la pelota cruza de arriba hacia abajo
                # la línea central del aro y está dentro del rango horizontal
                crosses_vertical = (last_y < hoop_center_y) and (cur_y > hoop_center_y)
                inside_x_range = (hoop_x < cur_x < hoop_x + hoop_w)

                if crosses_vertical and inside_x_range:
                    score += 1
                    just_scored = True
                    score_cooldown_frames = SCORE_COOLDOWN_MAX
                    print(f"CANASTA! Puntos: {score}")

            last_ball_center = current_center

        else:
            # Si no se ve la pelota, añadimos None a la trayectoria
            trail_points.append(None)
            if len(trail_points) > max_trail_len:
                trail_points.pop(0)

        # Disminuimos cooldown para evitar dobles conteos
        if score_cooldown_frames > 0:
            score_cooldown_frames -= 1

        # FPS
        now = time.time()
        dt = now - last_time
        if dt > 0:
            fps = 0.9 * fps + 0.1 * (1.0 / dt) if fps > 0 else 1.0 / dt
        last_time = now

        # OVERLAYS DE INFO
        cv2.putText(undistorted, f"Puntos: {score}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(undistorted, f"FPS: {fps:.1f}", (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        if just_scored:
            cv2.putText(undistorted, "CANASTA!", (w // 2 - 120, 80),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            # Solo mostramos el texto un frame; el efecto visual lo da el cooldown
            just_scored = False

        cv2.imshow(window_name, undistorted)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
