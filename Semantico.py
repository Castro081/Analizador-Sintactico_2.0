from Sintactico import Sintactico
from tabla import abrir_ventana_secundaria, cerrar_ventana_secundaria
from tkinter import filedialog
import re, os

analizador = None

def analisis_semantico(sintactico_instancia, analizador_instancia):
    lineas = sintactico_instancia.lineas
    tokens = analizador_instancia.tokens
    texto = analizador_instancia.texto
    ventana_tabla = None

    letra = 'A'
    numero = 1
    
    simbolos = []
    tabla_simbolos = []
    tabla_de_simbolos = ""

    if ventana_tabla is not None:
        cerrar_ventana_secundaria(ventana_tabla)

    for linea in lineas:

        if 'LlavesAbierto' in linea:
            siguiente_letra = chr(ord(letra) + 1)
            letra = siguiente_letra
    
        if 'LlavesCerrado' in linea:
            anterior_letra = chr(ord(letra) - 1)
            numero = mayor_numero_scope(anterior_letra, simbolos) + 1
            letra = anterior_letra

        if 'TipoDato' in linea:
            tipo_dato = linea.split()[1]
            if 'Id' in linea:
                idd = linea.split()[4]
                if 'Igualdad' in linea:
                    if 'Valor' in linea:
                        indice_valor = linea.index('Valor')
                        valor = linea[indice_valor + len('Valor') + 1:].split()[0]
                        buscar = buscar_valor_variables(letra, numero, simbolos, idd)
                        if buscar is None:
                            tabla_de_simbolos += f"{idd} {valor}\n"
                            tabla_simbolos.append([idd, valor])
                            simbolos.append([idd, tipo_dato, f'{letra}{numero}', valor])
                        else:
                            # print('Variable ya declarada')
                            analizador_instancia.limpiar_salida()
                            analizador_instancia.imprimir(f'Variable {idd} ya declarada')

                else:
                    print(letra, numero, simbolos, idd)
                    buscar = buscar_valor_variables(letra, numero, simbolos, idd)
                    if buscar is None:
                        simbolos.append([idd, tipo_dato, f'{letra}{numero}','No inicializado'])
                    else:
                        print('Variable ya declarada')
                        analizador_instancia.limpiar_salida()
                        analizador_instancia.imprimir(f'Variable {idd} ya declarada')
        else:
            if 'Id' and 'Igualdad' and 'Valor' in linea and not 'Referencia' in linea:
                indice_valor = linea.index('Valor')
                valor = linea[indice_valor + len('Valor') + 1:].split()[0]
                indice_id = linea.index('Id') 
                variable = linea[indice_id + len('Id') + 1:].split()[0]
                print(valor, variable, f'{letra}{numero}')
                estado = cambiar_valor_variable(letra, numero, simbolos, variable, valor)
                if estado is None: 
                    # print('Variable no declarada') 
                    # analizador_instancia.imprimir(f'Variable no declarada')
                    pass

        if all(x in linea for x in ['Igualdad', 'Id']):
            indice_id = linea.index('Id') 
            variable = linea[indice_id + len('Id') + 1:].split()[0]
            if buscar_valor_variables(letra, numero, simbolos, variable) is None:
                # analizador_instancia.imprimir('Variable no inicializada')
                pass

        if all(x in linea for x in ['Referencia', 'Id', 'Igualdad', 'Valor']):
                indice_valor = linea.index('Valor')
                valor = linea[indice_valor + len('Valor') + 1:].split()[0]
                indice_id = linea.index('Id') 
                variable = linea[indice_id + len('Id') + 1:].split()[0]
                letra_actual = 'A'
                numero_actual = 1
                # print(valor, variable, f'{letra}{numero_actual}')
                estado = cambiar_valor_variable(letra_actual, numero_actual, simbolos, variable, valor)

        if 'Imprimir' in linea:
            if 'Id' in linea:
                indice_id = linea.index('Id') 
                variable = linea[indice_id + len('Id') + 1:].split()[0]
                numero_actual = mayor_numero_scope(letra, simbolos)
                imprimir = buscar_valor_variables(letra, numero_actual, simbolos, variable)
                if imprimir is None:
                    # print('Variable no declarada')
                    # analizador_instancia.imprimir(f'Variable no declarada')
                    pass
                else:
                    # print(imprimir)
                    # analizador_instancia.imprimir(f'{imprimir}')
                    pass
                    
    # if no_utilizado(simbolos) is not None:
        # analizador_instancia.imprimir(f'{no_utilizado(simbolos)}')
    guardar_tabla_simbolos(tabla_de_simbolos)
    tabla_tokens = tokensTabla(tokens)
    print(tabla_tokens)
    ventana_tabla = abrir_ventana(tabla_simbolos, tabla_tokens, analizador_instancia)

def tokensTabla(tokens):
    lista_tokens = []
    for linea in tokens:
        for tipo_token, token, numero, posicion in linea:
            if tipo_token != "Id":
                lista_tokens.append([token, tipo_token])
    return lista_tokens

def mayor_numero_scope(letra, simbolos):
    max_num = 1

    for sublist in simbolos:
        if sublist[2].startswith(letra):
            num = int(sublist[2][1:])
            max_num = max(max_num, num)
    return max_num

def buscar_valor_variables(letra, numero_actual, simbolos, variable):
    for sublist in simbolos:
        if f'{letra}{numero_actual}' in sublist:
            if variable in sublist:
                return sublist[3]
    return None

def cambiar_valor_variable(letra, numero_actual, simbolos, variable, valor):
    for sublist in simbolos:
        if f'{letra}{numero_actual}' in sublist:
            if variable in sublist:
                sublist[3] = valor
                return sublist[3]
    return None

def abrir_ventana(data, tabla_tokens, analizador_instancia):
        data = data
        abrir_ventana_secundaria(analizador, data, tabla_tokens, analizador_instancia.ventana_secundaria_ref)

def verificar_variable(variable, simbolos):
    for sublist in simbolos:
        if 'No inicializado' in sublist:
            return 'Variable no inicializado'
    
def no_utilizado(simbolos):
    for sublist in simbolos:
        if 'No inicializado' in sublist:
            return 'Variable no utilizada'

#-----------------------------------------------------Métodos para guardar.-----------------------------------------------------------


def guardar_tabla_simbolos(simbolos):
    ubicacion_script = os.path.dirname(os.path.abspath(__file__))
    ruta_archivo = os.path.join(ubicacion_script, 'TablaSimbolos.txt')

    with open(ruta_archivo, 'w') as file:
        file.write(simbolos)