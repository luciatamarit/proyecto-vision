# Proyecto de Visión Artificial – Sistema de Seguridad y Tracking

## Descripción del proyecto  
Este proyecto implementa un **sistema de visión artificial** dividido en dos fases principales:

---

## 1. Fase SECURITY (`security.py`)

El sistema desbloquea el acceso solo cuando la cámara detecta **cuatro objetos físicos en un orden concreto**:

1. **Aro de baloncesto (naranja)**
2. **Pelota de baloncesto (naranja)**
3. **Marcador cuadrado**
4. **Objeto rojo**

### ✔ Normas de la secuencia
- Cada objeto debe aparecer **en el orden correcto**.  
- Los objetos ya detectados deben **permanecer visibles** en todo momento.  
- Si un objeto confirmado desaparece → **RESET total**.  
- Cuando los cuatro están visibles **a la vez**, aparece un mensaje verde:  
  **"SECUENCIA COMPLETA - ACCESO PERMITIDO"**  
- Tras esto, `security.py` ejecuta automáticamente **`tracking.py`**.

---

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
