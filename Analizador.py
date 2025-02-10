#-----------------------------------------------------Dependencias-----------------------------------------------------------
import tkinter
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from Sintactico import Sintactico
from Semantico import analisis_semantico
from Tres_Direcciones import codigo_3_direcciones, limpiar_codigo_3_direcciones
import re
import os

#-----------------------------------------------------Clase Analizador-----------------------------------------------------------
# Proyecto 1 - fase 1
# Desarrolladores :
# 1- Lorenzo Antonio López Tahuico – 202140289
# 2- Daimler´ss Hamiltón Ivánn Castro Aguilar - 202146856
# Compiladores 2
# Ing. Karen

class Analizador:
    """
    Inicializa la ventana principal y configura los elementos del interfaz de usuario.
    """
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana_nueva = None
        self.ventana.geometry('1024x720')
        self.ventana.title('Analizador Léxico')
        # self.ventana.maxsize(1024, 720)
        # self.ventana.minsize(1024, 720)
        self.ventana['padx'] = 20
        self.ventana['pady'] = 20
        self.ventana_secundaria_ref = {'Tablas': None}
        self.palabras_reservadas = [
            ['int', 'TipoDato'],
            ['double', 'TipoDato'],
            ['char', 'TipoDato'],
            ['string', 'TipoDato'],
            ['private', 'ModificadorAcceso'],
            ['public', 'ModificadorAcceso'],
            ['if', 'CondicionalIf'],
            ['while', 'BucleWhile'],
            ['main', 'Main'],
            ['then', 'rw'],
            ['print', 'Imprimir'],
            ['this', 'Referencia'],
        ]

        self.palabrasReservadas = [palabra[0] for palabra in self.palabras_reservadas]

        self.tokens = []
        self.signos = [
            [';', 'End'],
            [',', 'Separador'],
            ['=', 'Igualdad'],
            ['>', 'Mayor'],
            ['<', 'Menor'],
            ['+', 'Suma'],
            ['-', 'Resta'],
            ['(', 'ParentesisAbierto'],
            [')', 'ParentesisCerrado'],
            ['{', 'LlavesAbierto'],
            ['}', 'LlavesCerrado'],
        ]

        self.crear_menu()
        self.crear_widgets()
        self.texto = []
        # Crear tags para colores 
        self.crear_tags()

    def crear_tags(self):
        self.salida_text.tag_configure('Error', foreground='red')

#-----------------------------------------------------Métodos para buscar los tokens-----------------------------------------------------------
    def token(self):
        """
        Analiza el texto de entrada y extrae los tokens.
        """
        self.tokens = []
        codigo = self.entrada_text.get('1.0', 'end')
        bloque_comentario = False
        linea_comentario = False

        error_comentario = False
        error = False

        regExr_numeros = re.compile(r'^[-+]?[0-9]*\.?[0-9]+$')
        regExr_identificadores = re.compile(r'\b[a-zA-Z]+[0-9a-zA-Z_]*\b')
        self.regExr_numeros_error = re.compile(r'^[0-9]+[a-zA-Z_]+$|^[.#,][0-9]+$|^[0-9]+[.#,]+$')
        self.regExr_identificadores_error = re.compile(r'^\d+[a-zA-Z_0-9]+[a-zA-Z]+$|^[a-zA-Z_]+[#$%&]+[a-zA-Z_]+$')
        simbolos = []

        lineas = codigo.strip().splitlines()
        self.texto = lineas
        for numero_linea, linea in enumerate(lineas, start=1):
            lineaCompleta = linea
            linea_codigo = []

            palabras = re.findall(r'(?:[.,]\d+)|(?:\d+[.,]$)|(?:\d+[.,#]\d+)|<--|-->|<-|->|\(|\)|\{|\}|;|=|,|\+|-|\*|>|<|\b\w+\d*[/_#"”\'’$%&!¡]*\w*\d*', linea)
            for token in palabras:
                numero_columna = linea.find(token) + 1

                error_mensaje = self.manejo_errores(token, lineaCompleta)
                if error_mensaje is not None:
                    error = True
                    self.imprimir_error(error_mensaje, numero_linea, numero_columna)
                    break

                rw = self.buscar_palabras_reservadas(token)
                if rw:
                    linea_codigo.append([rw[1], rw[0], numero_linea, numero_columna])
                
                signo = self.buscar_signos_operadores(token)
                if signo:
                    linea_codigo.append([signo, token, numero_linea, numero_columna])
                
                if rw is None and signo is None:
                    numero = regExr_numeros.findall(token) or None
                    if numero:
                        linea_codigo.append(['Valor', token, numero_linea, numero_columna])
                    identificador = regExr_identificadores.findall(token) or None
                    if identificador:
                        linea_codigo.append(['Id', token, numero_linea, numero_columna])
                espacios = ' ' * len(token)
                linea = linea.replace(token, espacios, 1)
            else:
                if linea_codigo:
                    self.tokens.append(linea_codigo)
                continue
            break
        # print(self.tokens, "tokens")
        if not error:
            self.salida_text.config(state='normal')
            self.salida_text.delete(1.0, 'end')
            tokens_str = '\n'.join(''.join(f'<{tipo_token} {token} {linea} {posicion}>' for tipo_token, token, linea, posicion in line) for line in self.tokens)
            self.salida_text.insert(tkinter.END, tokens_str)
            self.salida_text.config(state='disabled')

            self.guardar_resultado_lexico()
            self.abrir_ventana_sintactico()
        elif linea_comentario:
            self.salida_text.config(state='normal')
            self.salida_text.delete(1.0, 'end')
            self.salida_text.insert(tkinter.END, 'Error sintáctico de comentario')
            self.salida_text.config(state='disabled')

    def buscar_palabras_reservadas(self, palabra):
        for lista in self.palabras_reservadas:
            if palabra in lista:
                return lista

    def buscar_signos_operadores(self, signo):
        for lista in self.signos:
            if signo in lista:
                return lista[1]
            
#-----------------------------------------------------Métodos para crear el menú y widgets-----------------------------------------------------------

    def crear_menu(self):
        """
        Crea el menú de la aplicación y los comandos asociados.
        """
        menu = tkinter.Menu(self.ventana)

        menu_archivo = tkinter.Menu(menu, tearoff=0)
        menu_archivo.add_command(label='Guardar', command=self.guardar_archivos)
        menu_archivo.add_separator()
        menu_archivo.add_command(label='Abrir archivo', command=self.buscador_de_archivos)

        menu.add_cascade(label='Archivo', menu=menu_archivo)
        menu.add_command(label='Analizar', command=self.token)
        menu.add_command(label='Código 3 direcciones', command=self.mostrar_resultado)
        menu.add_command(label='Limpiar', command=self.limpiar)
        
        self.ventana.config(menu=menu)
#-----------------------------------------------------Manejo de errores-----------------------------------------------------------
    def manejo_errores(self, token, linea):
        """
        Maneja errores en los tokens identificados.
        """
        regExr_palabrasReservadas_error = re.compile(r'\b(?:' + '|'.join(self.palabrasReservadas) + r')+\s+(?:' + '|'.join(self.palabrasReservadas) + r')+')

        palabraReservado_error = regExr_palabrasReservadas_error.findall(linea) or None
        if palabraReservado_error:
            return f'Error: El identificador "{palabraReservado_error[0]}" tiene el nombre de una palabra reservada'

        numero_error = self.regExr_numeros_error.search(token) or None
        if numero_error:
            return f'Error: "{numero_error.group()}" no es un valor permitido'
        
        identificador_error = self.regExr_identificadores_error.search(token) or None
        if identificador_error:
            return f'Error: "{identificador_error.group()}" no es un identificador permitido'

    def imprimir_error(self, mensaje, linea, columna):
        self.salida_text.config(state='normal')
        self.salida_text.delete(1.0, 'end')
        self.salida_text.insert(tkinter.END, f'🔴 En línea {linea}, columna {columna}: {mensaje}\n', 'Error')
        self.salida_text.config(state='disabled')


    def imprimir(self, texto):
        self.salida_text.config(state='normal')
        self.salida_text.insert(tkinter.END, texto)
        self.salida_text.config(state='disabled')
#-----------------------------------------------------Métodos para cargar los estilos y funciones de limpieza.-----------------------------------------------------------
    def mostrar_resultado(self):
        limpiar_codigo_3_direcciones()
        expresion = self.entrada_text.get("1.0", tkinter.END).strip()
        resultado_codigo = codigo_3_direcciones(expresion)
        self.salida_text.config(state=tkinter.NORMAL)
        self.salida_text.delete("1.0", tkinter.END)
        self.salida_text.insert(tkinter.END, resultado_codigo)
        self.salida_text.config(state=tkinter.DISABLED)

    
    def crear_widgets(self):
        """
        Crea y configura los widgets de la interfaz gráfica.
        """
        frame = tkinter.Frame(master=self.ventana, bg='#333333') 
        frame.pack(fill=tkinter.BOTH, expand=True)
        
        # Crear scrollbar
        scrollbar = tkinter.Scrollbar(frame)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # Estilo para el scrollbar
        style = ttk.Style()
        style.configure("Vertical.TScrollbar",
                        background="#555555",  
                        troughcolor="#333333",  
                        arrowcolor="#FFFFFF",  
                        gripcount=0,
                        borderwidth=0,
                        relief="flat")

        self.lineas_text = tkinter.Text(frame, width=4, padx=5, takefocus=0, border=0, state='disabled') 
        self.lineas_text.pack(side=tkinter.LEFT, fill=tkinter.Y)

        self.entrada_text = tkinter.Text(frame, undo=True, yscrollcommand=self.sync_scroll) 
        self.entrada_text.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)


        scrollbar.config(command=self.scroll_textos)
        self.entrada_text.config(yscrollcommand=scrollbar.set)
        self.lineas_text.config(yscrollcommand=scrollbar.set)

        self.entrada_text.bind('<KeyRelease>', self.actualizar_numeros_lineas)
        self.entrada_text.bind('<MouseWheel>', self.actualizar_numeros_lineas)
        self.entrada_text.bind('<Button-1>', self.actualizar_numeros_lineas)
        self.entrada_text.bind('<Return>', self.actualizar_numeros_lineas)
        self.entrada_text.bind('<BackSpace>', self.actualizar_numeros_lineas)

        # Etiqueta de salida
        salida_label = tkinter.Label(self.ventana, text='Salida', font=('Courier', 12))  
        salida_label.pack(pady=(10, 0))

        # Text para la salida
        self.salida_text = tkinter.Text(self.ventana, height=100, state='disabled')
        self.salida_text.pack(fill=tkinter.BOTH, expand=True, pady=(0, 10))
        self.ventana.update_idletasks()
        self.ventana.minsize(self.ventana.winfo_width(), self.ventana.winfo_height())
    
    def limpiar(self):
        self.entrada_text.delete(1.0, 'end')
        self.salida_text.config(state='normal')
        self.salida_text.delete(1.0, 'end')
        self.salida_text.config(state='disabled')
        self.limpiar_numeros_lineas()  
        self.actualizar_numeros_lineas()  

    def limpiar_salida(self):
        self.salida_text.config(state='normal')
        self.salida_text.delete(1.0, 'end')
        self.salida_text.config(state='disabled')

    def limpiar_numeros_lineas(self):
        self.lineas_text.config(state='normal')
        self.lineas_text.delete('1.0', 'end')
        self.lineas_text.config(state='disabled')

    def scroll_textos(self, *args):
        # Sincroniza el scroll de los widgets de texto.
        self.lineas_text.yview(*args)
        self.entrada_text.yview(*args)

    def sync_scroll(self, *args):
        # Función para sincronizar el scroll del área de texto y la barra de desplazamiento.
        self.scroll_textos('moveto', args[0])
        self.actualizar_numeros_lineas()

    def actualizar_numeros_lineas(self, event=None):
        # Actualiza los números de línea en el Text de números.
        self.lineas_text.config(state='normal')
        self.lineas_text.delete('1.0', 'end')

        num_lineas = int(self.entrada_text.index('end-1c').split('.')[0])

        linea_numeros = "\n".join(str(i) for i in range(1, num_lineas + 1))
        self.lineas_text.insert('1.0', linea_numeros)
        self.lineas_text.config(state='disabled')

        self.scroll_textos('moveto', self.entrada_text.yview()[0])

    def buscador_de_archivos(self):
        ruta_archivo = filedialog.askopenfilename(
            title='Seleccionar archivo',
            filetypes=[['Archivo de texto', '*.lalt']]
        )

        if ruta_archivo:
            with open(ruta_archivo, 'r', encoding='utf-8') as file:
                contenido = file.read()
                self.entrada_text.delete(1.0, tkinter.END)
                self.entrada_text.insert(tkinter.END, contenido.strip())
            messagebox.showinfo('Notificación', 'Archivo seleccionado')
            
#-----------------------------------------------------Métodos para guardar y cargar la ventana.-----------------------------------------------------------
    def guardar_archivos(self):
        contenido = self.entrada_text.get('1.0', tkinter.END)

        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension='.lalt',
            filetypes=[['Archivo de texto', '*.lalt']]
        )

        if ruta_archivo:
            with open(ruta_archivo, 'w', encoding='utf-8') as file:
                file.write(contenido)
            messagebox.showinfo('Notificación', 'Archivo guardado satisfactoriamente')

    def abrir_ventana_sintactico(self):
        sin = Sintactico(self.ventana, self.ventana_nueva)
        # sin.ocultar_ventana()
        self.ventana_nueva = sin.retornar_ventana()
        analisis_semantico(sin, self)

    def guardar_resultado_lexico(self):
        ubicacion_script = os.path.dirname(os.path.abspath(__file__))
        contenido = self.salida_text.get('1.0', tkinter.END)
        ruta_archivo = os.path.join(ubicacion_script, 'resultado.lex')

        with open(ruta_archivo, 'w') as file:
            file.write(contenido)
        messagebox.showinfo('Notificación', 'Resultado Léxico guardado')

if __name__ == '__main__':
    ventana = tkinter.Tk()
    analizador = Analizador(ventana)
    ventana.mainloop()
