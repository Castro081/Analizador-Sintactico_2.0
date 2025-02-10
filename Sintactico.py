#-----------------------------------------------------Dependencias-----------------------------------------------------------
import tkinter
from tkinter import ttk, messagebox
import os
import re

#-----------------------------------------------------Clase Sintactico-----------------------------------------------------------
class Sintactico:
    def __init__(self, root, actual):
        if actual:
            actual.destroy()
        self.nueva_ventana = tkinter.Toplevel(root)
        self.nueva_ventana.geometry('1024x720')
        self.nueva_ventana.title('Analizador Sintáctico')
        self.nueva_ventana.maxsize(1024, 720)
        self.nueva_ventana.minsize(1024, 720)
        
        self.paned = ttk.Panedwindow(self.nueva_ventana, orient='horizontal')
        self.paned.pack(fill=tkinter.BOTH, expand=True)

        self.reglas_sintacticas = [
            '<TipoDato><Id><End>',
            '<TipoDato><Id><Igualdad><Valor><End>',
            '<TipoDato><Id><Separador><Id><End>',
            '<CondicionalIf><ParentesisAbierto><Id><ParentesisCerrado>',
            '<BucleWhile><ParentesisAbierto><Id><ParentesisCerrado>',
            '<CondicionalIf><ParentesisAbierto><Id><Igualdad><Id><ParentesisCerrado>',
            '<CondicionalIf><ParentesisAbierto><Id><Igualdad><Valor><ParentesisCerrado>',
            '<CondicionalIf><ParentesisAbierto><Valor><Igualdad><Id><ParentesisCerrado>',
            '<BucleWhile><ParentesisAbierto><Id><Igualdad><Id><ParentesisCerrado>',
            '<BucleWhile><ParentesisAbierto><Id><Igualdad><Valor><ParentesisCerrado>',
            '<BucleWhile><ParentesisAbierto><Valor><Igualdad><Id><ParentesisCerrado>',
            '<TipoDato><Id><Igualdad><Valor><Separador><Id><Igualdad><Valor><End>',
            '<TipoDato><Id><Igualdad><Valor><Separador><Id><End>',
            '<TipoDato><Id><Separador><Id><Igualdad><Valor><End>',
            '<TipoDato><Id><Igualdad><Id><End>',
        ]
        
        self.tamaño_de_datos = {
            'int': 4,
            'string': 12,
            'double': 8,
            'char': 1,
        }

        self.tabla_simbolos = {}
        self.lineas = []
        self.crear_widgets()
        self.pintar()

    def crear_tags(self):
        """
        Define los estilos para errores, advertencias y confirmaciones
        en el área de texto de salida sintáctica.
        """
        self.salida_sintactico.tag_configure('Error', foreground='red')
        self.salida_sintactico.tag_configure('Advertencia', foreground='orange')
        self.salida_sintactico.tag_configure('Bien', foreground='green')

    def abrir_resultado_lexico(self):
        archivo = None
        try:
            ruta_archivo = os.path.join(os.path.dirname(__file__), 'resultado.lex')
            if not os.path.exists(ruta_archivo):
                raise FileNotFoundError("El archivo resultado.lex no existe.")
                
            with open(ruta_archivo, 'r') as file:
                archivo = file.read()
        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al abrir el archivo: {e}")
        return archivo or ""

    def extraer_tipo_ids(self, linea):
        """
        Extrae el tipo de dato y los identificadores de una línea dada.
        :param linea: Línea de texto a analizar.
        :return: Tupla con el tipo de dato y una lista de identificadores.
        """
        partes = linea.split("<Id")
        tipo_partes = partes[0].split()
        tipo_dato = tipo_partes[1] if len(tipo_partes) > 1 else None
        ids = []
        for parte in partes[1:]:
            id_partes = parte.split()
            id = id_partes[0] if len(id_partes) > 0 else None
            if id:
                ids.append(id)
        return tipo_dato, ids

    def tomar_informacion(self):
        contenido = self.abrir_resultado_lexico().strip().splitlines()
        if not contenido:
            return []

        self.lineas = contenido
        instruccion_de_linea = []
        for instruccion in contenido:
            primera_palabra_tk = r'<(\w+)'
            instruccion_formateado = re.findall(primera_palabra_tk, instruccion)
            instruccion_formateado = ''.join(f'<{tipo}>' for tipo in instruccion_formateado)
            instruccion_de_linea.append(instruccion_formateado)
            tipo, ids = self.extraer_tipo_ids(instruccion)
            if tipo and ids:
                for id in ids:
                    self.tabla_simbolos[id] = tipo
        print(instruccion_de_linea)
        return instruccion_de_linea

    def aceptacion_de_instrucciones(self):
        """
        Valida las instrucciones de acuerdo con las reglas sintácticas.
        :return: Lista de resultados con indicaciones de aceptación o errores.
        """
        informacion = self.tomar_informacion()
        resultado = []
        for info in informacion:
            if info in self.reglas_sintacticas:
                resultado.append(f'{info} ✓')
            else:
                resultado.append(f'{info} Error de Sintaxis')
        return resultado

    def guardar_resultados(self):
        resultados = self.aceptacion_de_instrucciones()
        if not resultados:
            return

        archivo_resultado = "resultado_sintactico.txt"

        if os.path.exists(archivo_resultado):
            with open(archivo_resultado, 'r', encoding='utf-8') as f_resultado:
                lineas = f_resultado.readlines()

                ids = [int(linea.split(':')[0].strip()) for linea in lineas if linea.split(':')[0].strip().isdigit()]
                next_id = max(ids) + 1 if ids else 1
        else:
            next_id = 1

        with open(archivo_resultado, 'a', encoding='utf-8') as f_resultado:
            if os.path.getsize(archivo_resultado) == 0 or not lineas[-1].startswith("--- Análisis Sintáctico ---"):
                f_resultado.write("--- Análisis Sintáctico ---\n")

                for i, (linea, resultado) in enumerate(zip(self.lineas, resultados), start=next_id):
                    f_resultado.write(f"{i}: {linea} ------------> {resultado}\n")

    def crear_widgets(self):
        """
        Crea y configura los widgets de la interfaz gráfica, incluyendo
        áreas de texto para la entrada y salida, y botones de control.
        """
        frame_entrada = ttk.Frame(self.paned)
        frame_salida = ttk.Frame(self.paned)
        self.paned.add(frame_entrada, weight=1)
        self.paned.add(frame_salida, weight=1)
        
        # Entrada Léxica
        entrada_label = ttk.Label(frame_entrada, text='Entrada Léxica', font=('Arial', 12, 'bold'))
        entrada_label.pack(pady=10)

        self.entrada_lexico = tkinter.Text(frame_entrada, height=20, state='disabled', bg='#E8E8E8', wrap='none')
        self.entrada_lexico.pack(fill=tkinter.BOTH, expand=True, padx=10, pady=10)

        # Salida Sintáctica
        salida_label = ttk.Label(frame_salida, text='Salida Sintáctica', font=('Arial', 12, 'bold'))
        salida_label.pack(pady=10)

        self.salida_sintactico = tkinter.Text(frame_salida, height=20, state='disabled', bg='#D8D8D8', wrap='none')
        self.salida_sintactico.pack(fill=tkinter.BOTH, expand=True, padx=10, pady=10)

        button_frame = ttk.Frame(frame_salida)
        button_frame.pack(pady=10)

        refrescar_btn = ttk.Button(button_frame, text="Refrescar", command=self.pintar)
        refrescar_btn.pack(side=tkinter.LEFT, padx=5)

        self.crear_tags()

    def pintar(self):
        """
        Actualiza el contenido de los widgets de entrada y salida,
        mostrando el resultado del análisis sintáctico.
        """
        self.entrada_lexico.config(state='normal')
        self.entrada_lexico.delete(1.0, 'end')
        contenido = self.abrir_resultado_lexico().strip().splitlines()
        if contenido:
            self.entrada_lexico.insert(tkinter.END, '\n'.join(contenido))
        self.entrada_lexico.config(state='disabled')

        self.salida_sintactico.config(state='normal')
        self.salida_sintactico.delete(1.0, 'end')
        instrucciones = self.aceptacion_de_instrucciones()
        if instrucciones:
            for instruccion in instrucciones:
                if "✓" in instruccion:
                    self.salida_sintactico.insert(tkinter.END, f'{instruccion}\n', 'Bien')
                elif "Error" in instruccion:
                    self.salida_sintactico.insert(tkinter.END, f'{instruccion}\n', 'Error')
                else:
                    self.salida_sintactico.insert(tkinter.END, f'{instruccion}\n', 'Advertencia')
        self.salida_sintactico.config(state='disabled')
        self.guardar_resultados()

    def retornar_ventana(self):
        return self.nueva_ventana

    def mostrar_ventana(self):
        self.nueva_ventana.deiconify()

    def ocultar_ventana(self):
        self.nueva_ventana.withdraw()

if __name__ == "__main__":
    root = tkinter.Tk()
    app = Sintactico(root, None)
    root.mainloop()
