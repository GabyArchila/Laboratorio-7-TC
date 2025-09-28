import re
import sys
import os

from preprocesamiento import infix_to_postfix
from thompson import Thompson
from subconjuntos import Subconjuntos


class ValidadorGramaticas:
    def __init__(self):
        self.regex_produccion = r'^[A-Z]\s*→\s*(ε|([A-Za-z0-9]+(\s*\|\s*[A-Za-z0-9]+)*))$'
        self.patron = re.compile(self.regex_produccion)
        self.construir_automata_validacion()

    def construir_automata_validacion(self):

        print("Construyendo autómata para validación usando Proyecto 1...")
        regex_simple = "[A-Z]→[A-Za-z0-9|]*"

        try:
            postfix = infix_to_postfix(regex_simple)
            thompson = Thompson()
            afn = thompson.construir_desde_postfix(postfix)
            subconjuntos = Subconjuntos(afn)
            self.afd_validador = subconjuntos.convertir()

            print("Autómata de validación construido exitosamente")

        except Exception as e:
            print(f"Error construyendo autómata: {e}")
            self.afd_validador = None

    def validar_linea(self, linea):
        linea = linea.strip()

        if not linea or linea.startswith('#'):
            return True, "Línea vacía o comentario"

        print(f"Validando línea: '{linea}'")

        if self.patron.match(linea):
            print("✓ Validación con regex: VÁLIDA")
            linea_sin_espacios = linea.replace(' ', '')
            print(f"  Línea sin espacios: '{linea_sin_espacios}'")
            self.analizar_produccion(linea)

            return True, "Producción válida"
        else:
            print("✗ Validación con regex: INVÁLIDA")
            return False, "Formato de producción inválido"

    def analizar_produccion(self, linea):
        partes = linea.split('→')
        if len(partes) != 2:
            return

        no_terminal = partes[0].strip()
        cuerpo = partes[1].strip()

        print(f"  No-terminal: {no_terminal}")
        print(f"  Cuerpo: {cuerpo}")

        if '|' in cuerpo:
            alternativas = [alt.strip() for alt in cuerpo.split('|')]
            print(f"  Alternativas: {alternativas}")
        else:
            print(f"  Producción única: {cuerpo}")

    def validar_archivo(self, nombre_archivo):
        if not os.path.exists(nombre_archivo):
            return False, [f"El archivo '{nombre_archivo}' no existe"]

        errores = []
        linea_num = 0
        producciones_validas = []

        print(f"\n=== VALIDANDO ARCHIVO: {nombre_archivo} ===")

        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                linea_num += 1
                linea_original = linea.rstrip('\n\r')

                es_valida, mensaje = self.validar_linea(linea_original)

                if not es_valida and linea_original.strip() and not linea_original.strip().startswith('#'):
                    error = f"Línea {linea_num}: {mensaje} - '{linea_original}'"
                    errores.append(error)
                    print(f"ERROR línea {linea_num}: {error}")
                elif es_valida and linea_original.strip() and not linea_original.strip().startswith('#'):
                    producciones_validas.append((linea_num, linea_original.strip()))
                    print(f"OK línea {linea_num}: Válida")

        print(f"\n--- Resumen ---")
        print(f"Total líneas procesadas: {linea_num}")
        print(f"Producciones válidas: {len(producciones_validas)}")
        print(f"Errores encontrados: {len(errores)}")

        if producciones_validas:
            print("\nProducciones válidas encontradas:")
            for num, prod in producciones_validas:
                print(f"  Línea {num}: {prod}")

        return len(errores) == 0, errores