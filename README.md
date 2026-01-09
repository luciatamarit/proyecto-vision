# Proyecto de Visión por Ordenador – Sistema de Seguridad y Tracking
Proyecto Final – Visión por Ordenador I  
Grado en Ingeniería Matemática – ICAI, Universidad Pontificia Comillas
Lucía Tamarit e Irene Turrado

---

## Descripción del proyecto

Este proyecto implementa un **sistema completo de visión por ordenador clásico**, utilizando una cámara como única fuente de información.  
El sistema se divide en dos grandes bloques, tal y como se especifica en el enunciado del laboratorio:

1. **Calibración de cámara** (`calibracion.ipynb`)
2. **Sistema de Seguridad** (`security.py`)
3. **Sistema de Tracking** (`tracking.py`)

El control de ejecución del sistema se realiza desde `main.py`.

---

## Arquitectura general del sistema

La arquitectura del sistema sigue el siguiente flujo secuencial:

Captura de vídeo  
↓  
Calibración de cámara (offline)  
↓  
Sistema de Seguridad (detección y decodificación de patrones)  
↓ (si la secuencia es correcta)  
Sistema de Tracking y análisis  
↓  
Salida de vídeo en tiempo real + FPS

---

## 1. Fase de Calibración (`calibracion.ipynb`)

La calibración de la cámara se realiza **offline**, siguiendo el procedimiento visto en la práctica de calibración.

Este proceso permite obtener:
- Matriz intrínseca de la cámara
- Coeficientes de distorsión radial y tangencial
- Error RMS de la calibración

Los parámetros obtenidos se utilizan posteriormente en el sistema de tracking para aplicar **corrección de distorsión en tiempo real**, mejorando la precisión geométrica del sistema.

---

## 2. Sistema de Seguridad (`security.py`)

El sistema de seguridad implementa un mecanismo de **identificación visual mediante patrones**, cumpliendo los requisitos de detección de patrones y extracción de información.

### 2.1 Detección de patrones

La detección se basa en técnicas clásicas de visión por ordenador:
- Conversión de color BGR → HSV
- Segmentación por umbrales de color
- Operaciones morfológicas (opening y closing)
- Detección y análisis de contornos

Los patrones detectados son:
- Pelota naranja
- Pelota blanca
- Canasta (tablero + aro)
- Marcador

### 2.2 Decodificación de la secuencia

El sistema implementa un decodificador que valida la siguiente **secuencia ordenada de patrones visuales**:

["BASKET", "ORANGE", "WHITE", "SCORE"]

La lógica del sistema garantiza que:
- Los patrones deben aparecer **en el orden correcto**
- Cada patrón debe mantenerse visible de forma continua
- La secuencia se evalúa de forma estrictamente secuencial
- Si algún patrón no aparece, el sistema se bloquea y no permite avanzar

Solo cuando la secuencia completa es válida se concede el acceso al sistema de tracking.

El patrón "SCORE" se detecta mediante el análisis de regiones rectangulares de gran tamaño que contienen información de color rojo, lo que permite identificar el marcador del sistema de juego y completar la secuencia de seguridad.

---

## 3. Sistema de Tracking (`tracking.py`)

El sistema de tracking constituye el bloque principal del proyecto y se ejecuta tras superar el sistema de seguridad.

### 3.1 Corrección de distorsión

Cada frame capturado se corrige utilizando los parámetros obtenidos en la calibración, aplicando:
- `cv2.initUndistortRectifyMap`
- `cv2.remap`

Esto permite trabajar con imágenes geométricamente corregidas.

---

### 3.2 Detección del aro

El aro se detecta en los primeros frames del vídeo mediante:
- Segmentación por color en HSV
- Filtrado por área mínima
- Cálculo de circularidad
- Obtención de una bounding box fija

Una vez detectado, el aro se mantiene como referencia durante todo el tracking.

---

### 3.3 Tracking de la pelota

La pelota de baloncesto se detecta mediante:
- Segmentación por color naranja en HSV
- Selección del contorno de mayor área
- Cálculo del círculo mínimo envolvente

El tracking se realiza almacenando las posiciones recientes del centro de la pelota, lo que permite dibujar su trayectoria y analizar su movimiento.

---

### 3.4 Conteo automático de canastas

Se contabiliza una canasta cuando:
- La pelota cruza verticalmente el centro del aro
- El cruce se produce de arriba hacia abajo
- La posición horizontal está dentro del ancho del aro

Se implementa un tiempo de bloqueo (cooldown) para evitar dobles conteos.

---

## Flujo de procesamiento de imagen

Para cada frame capturado se realiza la siguiente secuencia:

1. Captura de imagen desde la cámara
2. Corrección de distorsión
3. Conversión a HSV
4. Segmentación por color
5. Operaciones morfológicas
6. Detección de contornos
7. Extracción de características geométricas
8. Tracking y análisis temporal
9. Visualización de resultados

---

## Salida de vídeo y rendimiento

El sistema:
- Funciona en tiempo real
- Muestra la tasa de refresco (FPS) en pantalla
- Presenta overlays de información (puntos, trayectoria, detecciones)

---

## Estructura del repositorio

├── main.py              # Control principal del sistema  
├── security.py          # Sistema de seguridad por patrones  
├── tracking.py          # Tracking y conteo de canastas  
├── calibracion.ipynb    # Calibración de cámara (offline)  
└── README.md  

---

## Ejecución del sistema

1. Conectar una cámara al sistema
2. Ejecutar el archivo principal:

python main.py

3. Introducir la secuencia correcta de patrones
4. Acceder automáticamente al sistema de tracking

Para salir del programa, pulsar la tecla `q`.

---

## Ampliaciones

Además de los módulos mínimos exigidos, el proyecto incluye:
- Conteo automático de canastas
- Visualización de trayectorias
- Corrección de distorsión en tiempo real
- Arquitectura modular y extensible

---

## Uso de herramientas de IA
Se ha utilizado un asistente de IA como apoyo para la revisión del código y la mejora de la documentación.  
El diseño, implementación y validación del sistema han sido realizados por el autor del proyecto.

---

## Conclusión

Este proyecto demuestra que, mediante técnicas clásicas de visión por ordenador, es posible implementar un sistema completo que integra seguridad visual, tracking y análisis temporal en tiempo real, cumpliendo todos los requisitos del laboratorio.
