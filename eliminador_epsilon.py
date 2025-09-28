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
        print(f"\n=== {titulo} ===")
        for nt in sorted(self.producciones.keys()):
            cuerpos = " | ".join(self.producciones[nt])
            print(f"{nt} → {cuerpos}")


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

        # Mostrar estadísticas iniciales
        total_prod = sum(len(cuerpos) for cuerpos in self.gramatica_original.producciones.values())
        prod_epsilon = sum(1 for cuerpos in self.gramatica_original.producciones.values()
                           for cuerpo in cuerpos if cuerpo == 'ε')

        print(f"\nEstadísticas iniciales:")
        print(f"  Total de producciones: {total_prod}")
        print(f"  Producciones-ε: {prod_epsilon}")

        self.encontrar_anulables()
        self.generar_nuevas_producciones()
        self.limpiar_epsilon()

        return self.nueva_gramatica

    def encontrar_anulables(self):
        print(f"\n--- PASO 1: Encontrar símbolos anulables ---")

        # Paso 1: Encontrar símbolos que producen ε directamente
        for nt, cuerpos in self.gramatica_original.producciones.items():
            if 'ε' in cuerpos:
                self.anulables.add(nt)
                self.epsilon_directos.add(nt)
                print(f"  {nt} → ε (anulable directo)")

        print(f"Anulables directos: {sorted(self.anulables)}")

        # Paso 2: Encontrar símbolos anulables indirectamente
        cambio = True
        iteracion = 1

        while cambio:
            cambio = False
            anulables_antes = len(self.anulables)
            nuevos_anulables = set()

            print(f"\nIteración {iteracion}:")

            for nt, cuerpos in self.gramatica_original.producciones.items():
                if nt not in self.anulables:
                    for cuerpo in cuerpos:
                        if cuerpo != 'ε' and self.es_cadena_anulable(cuerpo):
                            nuevos_anulables.add(nt)
                            print(f"  {nt} es anulable (produce '{cuerpo}' que es anulable)")
                            break

            # Agregar los nuevos anulables
            if nuevos_anulables:
                self.anulables.update(nuevos_anulables)
                cambio = True
                print(f"  Nuevos anulables en iteración {iteracion}: {sorted(nuevos_anulables)}")
            else:
                print(f"  No hay nuevos símbolos anulables")

            iteracion += 1

            # Prevenir bucles infinitos
            if iteracion > 10:
                print("  ⚠️  Deteniendo después de 10 iteraciones")
                break

        print(f"\n✓ Símbolos anulables finales: {sorted(self.anulables)}")
        print(f"✓ Símbolos con ε directo: {sorted(self.epsilon_directos)}")

    def es_cadena_anulable(self, cadena):
        if cadena == 'ε':
            return True
        return all(simbolo in self.anulables for simbolo in cadena)

    def generar_nuevas_producciones(self):
        print(f"\n--- PASO 2: Generar nuevas producciones ---")

        total_nuevas = 0

        for nt, cuerpos in self.gramatica_original.producciones.items():
            print(f"\nProcesando {nt}:")
            nuevos_cuerpos = set()

            for i, cuerpo in enumerate(cuerpos):
                print(f"  Producción {i + 1}: {nt} → {cuerpo}")

                if cuerpo == 'ε':
                    nuevos_cuerpos.add('ε')
                    print(f"    Manteniendo ε temporalmente")
                    continue

                # Encontrar posiciones de símbolos anulables
                posiciones_anulables = []
                for j, simbolo in enumerate(cuerpo):
                    if simbolo in self.anulables:
                        posiciones_anulables.append(j)

                if not posiciones_anulables:
                    nuevos_cuerpos.add(cuerpo)
                    print(f"    Sin símbolos anulables: '{cuerpo}'")
                else:
                    num_anulables = len(posiciones_anulables)
                    print(f"    Símbolos anulables en posiciones {posiciones_anulables}")
                    print(f"    Generando 2^{num_anulables} = {2 ** num_anulables} combinaciones:")

                    # Generar todas las combinaciones
                    combinaciones_generadas = 0
                    for r in range(num_anulables + 1):
                        for combo in combinations(posiciones_anulables, r):
                            nuevo_cuerpo = ""
                            for k, simbolo in enumerate(cuerpo):
                                if k not in combo:
                                    nuevo_cuerpo += simbolo

                            if nuevo_cuerpo == "":
                                nuevo_cuerpo = "ε"

                            nuevos_cuerpos.add(nuevo_cuerpo)
                            combinaciones_generadas += 1

                            if combo:
                                eliminados = [f"{cuerpo[p]}" for p in combo]
                                print(f"      Eliminando {eliminados}: '{nuevo_cuerpo}'")
                            else:
                                print(f"      Sin eliminaciones: '{nuevo_cuerpo}'")

                    print(f"    Total combinaciones generadas: {combinaciones_generadas}")

            # Agregar todas las nuevas producciones
            for nuevo_cuerpo in nuevos_cuerpos:
                self.nueva_gramatica.agregar_produccion(nt, nuevo_cuerpo)
                total_nuevas += 1

            print(f"  Total producciones para {nt}: {len(nuevos_cuerpos)}")

        print(f"\n✓ Total de producciones generadas: {total_nuevas}")
        self.nueva_gramatica.mostrar("Gramática con Nuevas Producciones")

    def limpiar_epsilon(self):
        print(f"\n--- PASO 3: Limpiar producciones ε ---")

        gramatica_limpia = Gramatica()
        gramatica_limpia.simbolo_inicial = self.nueva_gramatica.simbolo_inicial

        epsilon_removidas = 0
        epsilon_mantenidas = 0

        for nt, cuerpos in self.nueva_gramatica.producciones.items():
            for cuerpo in cuerpos:
                if cuerpo == 'ε':
                    # Solo mantener ε si es el símbolo inicial Y produce ε directamente
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

        print(f"\nResultado de limpieza:")
        print(f"  Producciones ε removidas: {epsilon_removidas}")
        if epsilon_mantenidas > 0:
            print(f"  Producciones ε mantenidas: {epsilon_mantenidas}")

        self.nueva_gramatica = gramatica_limpia
        self.nueva_gramatica.mostrar("Gramática Final Sin ε-Producciones")


def cargar_gramatica_desde_archivo(nombre_archivo):
    import os

    if not os.path.exists(nombre_archivo):
        raise FileNotFoundError(f"El archivo '{nombre_archivo}' no existe")

    gramatica = Gramatica()

    print(f"Cargando gramática desde: {nombre_archivo}")

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
                        print(f"  Línea {linea_num}: {no_terminal} → {cuerpo}")
                else:
                    print(f"  Error en línea {linea_num}: formato incorrecto")
            else:
                print(f"  Error en línea {linea_num}: falta flecha →")

    return gramatica
