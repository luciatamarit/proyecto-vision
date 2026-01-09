import security
import tracking

def main():
    print("=== PROYECTO COMPUTER VISION ===")
    print("Iniciando SECURITY...\n")

    security_ok = security.main()

    if not security_ok:
        print("SECURITY abortado. Saliendo del programa.")
        return

    print("\nSECURITY OK")
    print("Iniciando TRACKING...\n")

    tracking.main()

    print("\nTRACKING finalizado.")
    print("Programa terminado correctamente.")

if __name__ == "__main__":
    main()
