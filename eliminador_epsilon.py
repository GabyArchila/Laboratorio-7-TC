from itertools import combinations


class Gramatica:
    def __init__(self):
        self.producciones = {}  # {no_terminal: [lista_de_cuerpos]}
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
        print(f"\n ------- {titulo} --------")
        for nt in sorted(self.producciones.keys()):
            cuerpos = " | ".join(self.producciones[nt])
            print(f"{nt} → {cuerpos}")

        print(f"No-terminales: {sorted(self.no_terminales)}")
        print(f"Terminales: {sorted(self.terminales)}")
        print(f"Símbolo inicial: {self.simbolo_inicial}")


class EliminadorEpsilon:
    def __init__(self, gramatica):
        self.gramatica_original = gramatica
        self.anulables = set()
        self.nueva_gramatica = Gramatica()
        self.nueva_gramatica.simbolo_inicial = gramatica.simbolo_inicial

    def eliminar_producciones_epsilon(self):
        print("------------ Eliminación de Producciones ε ------------")
        self.gramatica_original.mostrar("Gramática Original")
        self.encontrar_anulables()
        self.generar_nuevas_producciones()
        self.limpiar_epsilon()

        return self.nueva_gramatica

    def encontrar_anulables(self):

        print("\n--- PASO 1: Encontrar símbolos anulables ---")
        for nt, cuerpos in self.gramatica_original.producciones.items():
            if 'ε' in cuerpos:
                self.anulables.add(nt)
                print(f"'{nt}' es anulable (produce ε directamente)")

        cambio = True
        iteracion = 1

        while cambio:
            print(f"\nIteración {iteracion}:")
            cambio = False
            anulables_antes = self.anulables.copy()

            for nt, cuerpos in self.gramatica_original.producciones.items():
                if nt not in self.anulables:
                    for cuerpo in cuerpos:
                        if cuerpo != 'ε' and self.es_cadena_anulable(cuerpo):
                            self.anulables.add(nt)
                            cambio = True
                            print(f"  '{nt}' es anulable (produce '{cuerpo}' que es anulable)")
                            break

            if not cambio:
                print(f"  No hay nuevos símbolos anulables")

            iteracion += 1

        print(f"\nSímbolos anulables finales: {sorted(self.anulables)}")

    def es_cadena_anulable(self, cadena):
        if cadena == 'ε':
            return True

        return all(simbolo in self.anulables for simbolo in cadena)

    def generar_nuevas_producciones(self):

        print("\n--- PASO 2: Generar Nuevas Producciones ---")

        for nt, cuerpos in self.gramatica_original.producciones.items():
            print(f"\nProcesando producciones de {nt}:")

            nuevos_cuerpos = set()

            for cuerpo in cuerpos:
                print(f"  Analizando: {nt} → {cuerpo}")

                if cuerpo == 'ε':
                    print(f"    Saltando producción ε")
                    continue

                posiciones_anulables = []
                for i, simbolo in enumerate(cuerpo):
                    if simbolo in self.anulables:
                        posiciones_anulables.append(i)

                print(f"    Símbolos anulables en posiciones: {posiciones_anulables}")

                if not posiciones_anulables:
                    nuevos_cuerpos.add(cuerpo)
                    print(f"    Sin cambios: {cuerpo}")
                else:
                    num_anulables = len(posiciones_anulables)
                    print(f"    Generando 2^{num_anulables} = {2 ** num_anulables} combinaciones")

                    for r in range(num_anulables + 1):
                        for combo in combinations(posiciones_anulables, r):
                            nuevo_cuerpo = ""
                            for i, simbolo in enumerate(cuerpo):
                                if i not in combo:
                                    nuevo_cuerpo += simbolo

                            if nuevo_cuerpo == "":
                                nuevo_cuerpo = "ε"

                            nuevos_cuerpos.add(nuevo_cuerpo)
                            print(f"      Eliminando posiciones {combo}: '{nuevo_cuerpo}'")

            for nuevo_cuerpo in nuevos_cuerpos:
                self.nueva_gramatica.agregar_produccion(nt, nuevo_cuerpo)

        self.nueva_gramatica.mostrar("Gramática con Nuevas Producciones")

    def limpiar_epsilon(self):

        print("\n--- PASO 3: Limpiar Producciones ε ---")

        gramatica_limpia = Gramatica()
        gramatica_limpia.simbolo_inicial = self.nueva_gramatica.simbolo_inicial

        epsilon_removidas = 0

        for nt, cuerpos in self.nueva_gramatica.producciones.items():
            for cuerpo in cuerpos:
                if cuerpo == 'ε':
                    if nt == self.nueva_gramatica.simbolo_inicial and nt in self.anulables:
                        gramatica_limpia.agregar_produccion(nt, cuerpo)
                        print(f"Manteniendo {nt} → ε (símbolo inicial anulable)")
                    else:
                        epsilon_removidas += 1
                        print(f"Removiendo {nt} → ε")
                else:
                    gramatica_limpia.agregar_produccion(nt, cuerpo)

        print(f"\nTotal de producciones ε removidas: {epsilon_removidas}")

        self.nueva_gramatica = gramatica_limpia
        self.nueva_gramatica.mostrar("Gramática Final Sin ε-Producciones")


def cargar_gramatica_desde_archivo(nombre_archivo):
    import os

    if not os.path.exists(nombre_archivo):
        raise FileNotFoundError(f"El archivo '{nombre_archivo}' no existe")

    gramatica = Gramatica()

    print(f"\nCargando gramática desde: {nombre_archivo}")

    with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
        for linea_num, linea in enumerate(archivo, 1):
            linea = linea.strip()

            # Saltar líneas vacías y comentarios
            if not linea or linea.startswith('#'):
                continue

            # Parsear producción
            if '→' in linea:
                partes = linea.split('→')
                if len(partes) == 2:
                    no_terminal = partes[0].strip()
                    cuerpo_completo = partes[1].strip()

                    # Manejar alternativas (|)
                    if '|' in cuerpo_completo:
                        cuerpos = [c.strip() for c in cuerpo_completo.split('|')]
                    else:
                        cuerpos = [cuerpo_completo]

                    # Agregar cada cuerpo como producción separada
                    for cuerpo in cuerpos:
                        gramatica.agregar_produccion(no_terminal, cuerpo)
                        print(f"  Agregada: {no_terminal} → {cuerpo}")
                else:
                    print(f"  Error en línea {linea_num}: formato incorrecto")
            else:
                print(f"  Error en línea {linea_num}: falta flecha →")

    return gramatica