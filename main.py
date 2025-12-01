import subprocess
import sys

def run_security():
    """
    Ejecuta el script de seguridad y espera a que termine.
    Security se encarga de mostrar cámara, validar la secuencia
    y cerrar su ventana cuando esté todo correcto.
    """
    print("\n>>> Iniciando SECURITY MODE...\n")

    # Llamamos al archivo security
    result = subprocess.call([sys.executable, "security_bueno.py"])

    # Si security termina correctamente, seguimos.
    print("\n>>> SECURITY COMPLETADO. Secuencia validada.\n")

def run_tracking():
    """
    Ejecuta el módulo de tracking.
    tracking.py se ejecuta en una ventana nueva y finaliza con 'q'.
    """
    print("\n>>> Iniciando TRACKING...\n")
    subprocess.call([sys.executable, "tracking.py"])
    print("\n>>> TRACKING finalizado.\n")

def main():
    print("=== SISTEMA COMPLETO DE VISIÓN INICIADO ===")

    # 1. EJECUTAR SECURITY
    run_security()

    # 2. CUANDO SECURITY ACABA: TRACKING
    run_tracking()

    print("=== SISTEMA FINALIZADO ===")

if __name__ == "__main__":
    main()
