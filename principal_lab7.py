import os
import re
from itertools import combinations


class Gramatica:
    def __init__(self):
        self.producciones = {}
        self.no_terminales = set()
        self.terminales = set()
        self.simbolo_inicial = None

    def agregar_produccion(self, no_terminal, cuerpo):
        if no_terminal not in self.producciones:
            self.producciones[no_terminal] = []

        self.producciones[no_terminal].append(cuerpo)
        self.no_terminales.add(no_terminal)

        for char in cuerpo:
            if char.islower() or char.isdigit():
                self.terminales.add(char)

        if self.simbolo_inicial is None:
            self.simbolo_inicial = no_terminal

    def mostrar(self, titulo="Gramática"):
        print(f"\n=== {titulo} ===")
        for nt in sorted(self.producciones.keys()):
            cuerpos = " | ".join(self.producciones[nt])
            print(f"{nt} → {cuerpos}")


class ValidadorGramaticas:
    def __init__(self):
        # Regex corregida para aceptar epsilon
        self.regex_produccion = r'^[A-Z]\s*→\s*(ε|[A-Za-z0-9]+(\s*\|\s*([A-Za-z0-9]+|ε))*)$'
        self.patron = re.compile(self.regex_produccion)

    def validar_archivo(self, nombre_archivo):
        if not os.path.exists(nombre_archivo):
            return False, [f"El archivo '{nombre_archivo}' no existe"]

        errores = []

        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            for linea_num, linea in enumerate(archivo, 1):
                linea = linea.strip()

                if not linea or linea.startswith('#'):
                    continue

                if not self.patron.match(linea):
                    errores.append(f"Línea {linea_num}: Formato inválido - '{linea}'")

        return len(errores) == 0, errores


class EliminadorEpsilon:
    def __init__(self, gramatica):
        self.gramatica_original = gramatica
        self.anulables = set()
        self.nueva_gramatica = Gramatica()
        self.nueva_gramatica.simbolo_inicial = gramatica.simbolo_inicial
        # Guardar qué símbolos producen epsilon DIRECTAMENTE
        self.epsilon_directos = set()

    def eliminar_producciones_epsilon(self):
        print("\n" + "=" * 50)
        print(" Eliminación de producciones ε")
        print("=" * 50)

        self.gramatica_original.mostrar("Gramática Original")
        self.encontrar_anulables()
        self.generar_nuevas_producciones()
        self.limpiar_epsilon()

        return self.nueva_gramatica

    def encontrar_anulables(self):
        print("\n--- Encontrando símbolos anulables ---")

        for nt, cuerpos in self.gramatica_original.producciones.items():
            if 'ε' in cuerpos:
                self.anulables.add(nt)
                self.epsilon_directos.add(nt)
                print(f"  {nt} produce ε directamente")

        cambio = True
        iteracion = 1

        while cambio:
            cambio = False
            anulables_antes = len(self.anulables)

            for nt, cuerpos in self.gramatica_original.producciones.items():
                if nt not in self.anulables:
                    for cuerpo in cuerpos:
                        if cuerpo != 'ε' and self.es_cadena_anulable(cuerpo):
                            self.anulables.add(nt)
                            print(f"  {nt} es anulable (produce '{cuerpo}' que es anulable)")
                            cambio = True
                            break

            if len(self.anulables) > anulables_antes:
                print(f"  Iteración {iteracion}: {len(self.anulables) - anulables_antes} nuevos símbolos anulables")

            iteracion += 1

        print(f"Símbolos anulables finales: {sorted(self.anulables)}")
        print(f"Símbolos con ε directo: {sorted(self.epsilon_directos)}")

    def es_cadena_anulable(self, cadena):
        if cadena == 'ε':
            return True
        return all(simbolo in self.anulables for simbolo in cadena)

    def generar_nuevas_producciones(self):
        print("\n--- Generando nuevas producciones ---")

        for nt, cuerpos in self.gramatica_original.producciones.items():
            nuevos_cuerpos = set()

            for cuerpo in cuerpos:
                if cuerpo == 'ε':
                    nuevos_cuerpos.add('ε')
                    continue

                posiciones_anulables = []
                for i, simbolo in enumerate(cuerpo):
                    if simbolo in self.anulables:
                        posiciones_anulables.append(i)

                if not posiciones_anulables:
                    nuevos_cuerpos.add(cuerpo)
                else:
                    num_anulables = len(posiciones_anulables)
                    print(f"  Procesando {nt} → {cuerpo} (tiene {num_anulables} símbolos anulables)")

                    for r in range(num_anulables + 1):
                        for combo in combinations(posiciones_anulables, r):
                            nuevo_cuerpo = ""
                            for i, simbolo in enumerate(cuerpo):
                                if i not in combo:
                                    nuevo_cuerpo += simbolo

                            if nuevo_cuerpo == "":
                                nuevo_cuerpo = "ε"

                            nuevos_cuerpos.add(nuevo_cuerpo)
                            if nuevo_cuerpo != cuerpo:
                                eliminar_pos = [f"{cuerpo[p]}" for p in combo] if combo else ["ninguno"]
                                print(f"    Eliminando {eliminar_pos}: '{nuevo_cuerpo}'")

            for nuevo_cuerpo in nuevos_cuerpos:
                self.nueva_gramatica.agregar_produccion(nt, nuevo_cuerpo)

    def limpiar_epsilon(self):
        print("\n--- Limpiando producciones ε ---")

        gramatica_limpia = Gramatica()
        gramatica_limpia.simbolo_inicial = self.nueva_gramatica.simbolo_inicial

        epsilon_removidas = 0
        epsilon_mantenidas = 0

        for nt, cuerpos in self.nueva_gramatica.producciones.items():
            for cuerpo in cuerpos:
                if cuerpo == 'ε':
                    if (nt == self.nueva_gramatica.simbolo_inicial and
                            nt in self.epsilon_directos):
                        gramatica_limpia.agregar_produccion(nt, cuerpo)
                        epsilon_mantenidas += 1
                        print(f"  Manteniendo {nt} → ε (símbolo inicial con ε directo)")
                    else:
                        epsilon_removidas += 1
                        print(f"  Removiendo {nt} → ε")
                else:
                    gramatica_limpia.agregar_produccion(nt, cuerpo)

        print(f"Producciones ε removidas: {epsilon_removidas}")
        if epsilon_mantenidas > 0:
            print(f"Producciones ε mantenidas: {epsilon_mantenidas}")

        self.nueva_gramatica = gramatica_limpia
        self.nueva_gramatica.mostrar("Gramática Final Sin ε-Producciones")


def cargar_gramatica_desde_archivo(nombre_archivo):
    gramatica = Gramatica()

    print(f"Cargando gramática desde: {nombre_archivo}")

    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        for linea_num, linea in enumerate(archivo, 1):
            linea = linea.strip()

            if not linea or linea.startswith('#'):
                continue

            if '→' in linea:
                partes = linea.split('→')
                if len(partes) == 2:
                    no_terminal = partes[0].strip()
                    cuerpo_completo = partes[1].strip()

                    if '|' in cuerpo_completo:
                        cuerpos = [c.strip() for c in cuerpo_completo.split('|')]
                    else:
                        cuerpos = [cuerpo_completo]

                    for cuerpo in cuerpos:
                        gramatica.agregar_produccion(no_terminal, cuerpo)
                        print(f"  Línea {linea_num}: {no_terminal} → {cuerpo}")

    return gramatica


def main():

    while True:
        print("\nOpciones:")
        print("1. Procesar archivo")
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

            print(" Archivo válido")

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