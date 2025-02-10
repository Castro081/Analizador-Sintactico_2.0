#-----------------------------------------------------Dependencias-----------------------------------------------------------
import tkinter as tk
from tkinter import ttk

#-----------------------------------------------------Clase VentanaSecundaria-----------------------------------------------------------
class VentanaSecundaria(tk.Toplevel):
    """
    Clase para crear una ventana secundaria que muestra tablas de símbolos y tokens.
    Hereda de tk.Toplevel para crear una ventana adicional sobre la ventana principal.
    """
    def __init__(self, master, data, tokens):
        """
        Inicializa la ventana secundaria con las tablas de símbolos y tokens.
        :param master: Ventana principal que contiene esta ventana secundaria.
        :param data: Datos para la tabla de símbolos.
        :param tokens: Datos para la tabla de tokens.
        """
        super().__init__(master)
        self.title("Tablas")
        self.geometry("800x600")  

        paned = ttk.Panedwindow(self, orient="vertical")
        paned.pack(fill="both", expand=True)

        frame_simbolos = ttk.Frame(paned)
        frame_tokens = ttk.Frame(paned)

        paned.add(frame_simbolos, weight=1)  
        paned.add(frame_tokens, weight=1)

        self.crear_tabla(frame_simbolos, ["ID", "Valor"], data, "Tabla de Símbolos")
        self.crear_tabla(frame_tokens, ["Token", "Descripción"], tokens, "Tabla de Tokens")

    def crear_tabla(self, frame, columnas, datos, titulo):
        etiqueta = tk.Label(frame, text=titulo, font=('Arial', 10, 'bold'))
        etiqueta.pack(pady=5)

        tabla = ttk.Treeview(frame, columns=columnas, show="headings")
        tabla.pack(padx=10, pady=10, fill="both", expand=True)

        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, anchor="center", stretch=True)  
        
        for fila in datos:
            tabla.insert("", "end", values=fila)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tabla.yview)
        tabla.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")


#-----------------------------------------------------Funciones para manejar ventanas secundarias-----------------------------------------------------------
def abrir_ventana_secundaria(master, simbolos, tokens, ventana_secundaria_ref):
    
    if ventana_secundaria_ref['Tablas'] is None or not tk.Toplevel.winfo_exists(ventana_secundaria_ref['Tablas']):
        ventana_secundaria = VentanaSecundaria(master, simbolos, tokens)
        ventana_secundaria_ref['Tablas'] = ventana_secundaria
    else:
        ventana_secundaria_ref['Tablas'].focus()  

def cerrar_ventana_secundaria(ventana):
    ventana.destroy()
