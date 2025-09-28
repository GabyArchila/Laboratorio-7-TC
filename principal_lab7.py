import os
from validador_gramaticas import ValidadorGramaticas
from eliminador_epsilon import EliminadorEpsilon, cargar_gramatica_desde_archivo


def main():
    while True:
        print("\nOpciones:")
        print("1. Archivo")
        print("2. Salir")

        opcion = input("\nSeleccione (1-2): ").strip()

        if opcion == '1':
            archivo = input("Nombre del archivo: ").strip()

            if not os.path.exists(archivo):
                print(f"Error: El archivo '{archivo}' no existe")
                continue

            print(f"\nProcesando: {archivo}")

            print("\n--- VALIDACIÓN DE FORMATO ---")
            validador = ValidadorGramaticas()
            es_valido, errores = validador.validar_archivo(archivo)

            if not es_valido:
                print("ERROR: Archivo inválido:")
                for error in errores:
                    print(f"  {error}")
                continue

            print("Archivo válido")

            try:
                print("\n--- CARGA DE GRAMÁTICA ---")
                gramatica = cargar_gramatica_desde_archivo(archivo)

                print("\n--- ELIMINACIÓN DE PRODUCCIONES-ε ---")
                eliminador = EliminadorEpsilon(gramatica)
                resultado = eliminador.eliminar_producciones_epsilon()

                print("¡Procesamiento completado!")

            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()

        elif opcion == '2':
            print("¡Hasta luego!")
            break

        else:
            print("Opción inválida")


if __name__ == "__main__":
    main()
