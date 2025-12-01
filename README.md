# Proyecto de Visión Artificial – Sistema de Seguridad y Tracking

## Descripción del proyecto  
Este proyecto implementa un **sistema completo de visión artificial** dividido en tres fases:

1. **Calibración de cámara (`calibracion.ipynb`)**
2. **Fase SECURITY (`security.py`)** → detección secuencial obligatoria  
3. **Fase TRACKING (`tracking.py`)** → seguimiento del balón en tiempo real  

---

## 1. Fase de Calibración (`calibracion.ipynb`)

Este archivo en formato Jupyter Notebook permite:

- Ajustar los rangos **HSV** para la detección de:
  - Aro naranja  
  - Pelota naranja  
  - Marcador  
  - Objeto rojo  
- Visualizar en tiempo real las máscaras de color.
- Ajustar manualmente los límites para obtener una detección más robusta según:
  - condiciones de luz,
  - color del entorno,
  - cámara utilizada.


Se recomienda ejecutar este notebook **antes del sistema de seguridad** para dejar calibrados los rangos HSV óptimos.


## 2. Fase TRACKING (`tracking.py`)

Tras validar la secuencia correcta, comienza un sistema de **seguimiento en tiempo real** del balón de baloncesto mediante:

- Detección por color (HSV)  
- Contornos  
- Cálculo de trayectoria  
- Visualización en la cámara en vivo  

---

## Arquitectura del proyecto
proyecto-vision

├── main.py → Controlador general del sistema

├── security.py → Fase 1: detección secuencial y desbloqueo

├── tracking.py → Fase 2: tracking del balón en tiempo real

├── README.md → Documentación del proyecto

└── assets/ → (Opcional) imágenes, marcador, recursos



## Instalación

Requisitos:
- Python **3.8 o superior**
- Librerías:
  - `opencv-python`
  - `numpy`

Instala las dependencias con:

```bash
pip install opencv-python numpy
