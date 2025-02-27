import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import networkx as nx
import math
import os

TIPOS_PERMITIDOS = ["Accesorios", "Almuerzos", "Comida Rapida", "Snacks - Paquetes"]

class Chaza:
    def __init__(self, nombre, posicion, tipo="Sin especificar"):
        self.nombre = nombre
        self.posicion = posicion
        self.tipo = tipo
        self.calificaciones = []

    def agregar_calificacion(self, puntaje, comentario=""):
        self.calificaciones.append((puntaje, comentario))

    def obtener_promedio(self):
        if not self.calificaciones:
            return 0
        return sum(puntaje for puntaje, _ in self.calificaciones) / len(self.calificaciones)

    def ultimas_tres(self):
        return self.calificaciones[-3:]

class CalificacionChazasApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calificación de Chazas - Universidad Nacional de Colombia")
        self.geometry("800x600")
        
        self.modo = "explorador"
        self.grafo_chazas = nx.Graph()
        self.lista_chazas = []
        self.chazas_visibles = None
        
        # Cargar imagen
        ruta_imagen = os.path.join(os.path.dirname(__file__), "Imagenes", "Campus.jpg")
        
        try:
            self.imagen_mapa = Image.open(ruta_imagen).resize((800,600))
            self.foto_mapa = ImageTk.PhotoImage(self.imagen_mapa)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
            self.destroy()
            return
        
        # Configurar interfaz
        self.canvas = tk.Canvas(self, width=800, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_image(0, 0, image=self.foto_mapa, anchor="nw")
        self.canvas.bind("<Button-1>", self.procesar_click_canvas)
        
        # Configurar botones con efecto de cursor
        self.btn_añadir = tk.Button(self, text="Añadir Chaza", command=self.activar_modo_añadir, cursor="hand2")
        self.btn_añadir.place(x=10, y=10)
        self.btn_filtrar = tk.Button(self, text="Filtrar por Tipo", command=self.filtrar_por_tipo, cursor="hand2")
        self.btn_filtrar.place(x=120, y=10)
        self.btn_top5 = tk.Button(self, text="Top 5 Chazas", command=self.mostrar_top_5, cursor="hand2")
        self.btn_top5.place(x=240, y=10)

    def procesar_click_canvas(self, event):
        if self.modo == "añadir":
            self.agregar_chaza(event)
        else:
            self.seleccionar_chaza(event)
            self.config(cursor="arrow")  # Restaurar cursor después de click

    def seleccionar_chaza(self, event):
        self.config(cursor="hand2")  # Cambiar cursor al seleccionar
        umbral = 10
        chazas = self.lista_chazas if self.chazas_visibles is None else self.chazas_visibles
        for chaza in chazas:
            x, y = chaza.posicion
            if math.hypot(event.x - x, event.y - y) <= umbral:
                self.mostrar_menu_chaza(chaza)
                return
        self.config(cursor="arrow")  # Restaurar cursor si no hay chaza

    def filtrar_por_tipo(self):
        top = tk.Toplevel(self)
        top.title("Filtrar por Tipo")
        top.geometry("300x150")
        
        tk.Label(top, text="Seleccione el tipo de chaza:").pack(pady=10)
        
        tipo_var = tk.StringVar()
        tipos = TIPOS_PERMITIDOS + ["Todas las chazas"]
        combo = ttk.Combobox(top, textvariable=tipo_var, values=tipos, state="readonly")
        combo.current(0)
        combo.pack(pady=10)
        
        def aplicar_filtro():
            tipo_seleccionado = tipo_var.get()
            if tipo_seleccionado == "Todas las chazas":
                self.chazas_visibles = None
            else:
                self.chazas_visibles = [c for c in self.lista_chazas if c.tipo == tipo_seleccionado]
            self.redibujar()
            top.destroy()
        
        btn_aplicar = tk.Button(top, text="Aplicar", command=aplicar_filtro, cursor="hand2")
        btn_aplicar.pack(pady=5)

    def redibujar(self):
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, image=self.foto_mapa, anchor="nw")
        
        chazas_a_mostrar = self.lista_chazas if self.chazas_visibles is None else self.chazas_visibles
        
        # Dibujar conexiones
        for nodo1, nodo2 in self.grafo_chazas.edges():
            if any(c.nombre == nodo1 and c in chazas_a_mostrar for c in self.lista_chazas):
                pos1 = self.grafo_chazas.nodes[nodo1]["pos"]
                pos2 = self.grafo_chazas.nodes[nodo2]["pos"]
                self.canvas.create_line(pos1[0], pos1[1], pos2[0], pos2[1], fill="yellow", width=2)
        
        # Dibujar chazas con efecto de cursor
        for chaza in chazas_a_mostrar:
            x, y = chaza.posicion
            color = self.obtener_color(chaza.obtener_promedio()) if chaza.calificaciones else "#0000ff"
            self.canvas.create_oval(x-6, y-6, x+6, y+6, fill=color, outline="black", tags="chaza")
            self.canvas.create_text(x, y-10, text=chaza.nombre, fill="white", font=("Arial", 8))
        
        # Configurar cursor para las chazas
        self.canvas.tag_bind("chaza", "<Enter>", lambda e: self.config(cursor="hand2"))
        self.canvas.tag_bind("chaza", "<Leave>", lambda e: self.config(cursor="arrow"))

    # Resto de métodos se mantienen igual que en la versión anterior
    def activar_modo_añadir(self):
        self.modo = "añadir"
        self.config(cursor="cross")  # Cambiar cursor a cruz en modo añadir
        messagebox.showinfo("Modo Añadir", "Haga clic en el mapa para agregar una chaza.")

    def dialogo_calificacion(self, chaza):
        datos = {"puntaje": None, "comentario": ""}
        top = tk.Toplevel(self)
        top.title(f"Nueva Calificación para {chaza.nombre}")
        
        tk.Label(top, text="Ingrese el puntaje (0-5):").pack(pady=5)
        entrada_puntaje = tk.Entry(top, width=10)
        entrada_puntaje.pack(pady=5)
        
        tk.Label(top, text="Ingrese un comentario (opcional):").pack(pady=5)
        entrada_comentario = tk.Entry(top, width=40)
        entrada_comentario.pack(pady=5)
        
        def confirmar():
            try:
                puntaje = float(entrada_puntaje.get())
            except ValueError:
                messagebox.showerror("Error", "Debe ingresar un puntaje válido (número).")
                return
            if puntaje < 0 or puntaje > 5:
                messagebox.showerror("Error", "El puntaje debe estar entre 0 y 5.")
                return
            datos["puntaje"] = puntaje
            datos["comentario"] = entrada_comentario.get().strip()
            top.destroy()
        
        def cancelar():
            top.destroy()
        
        btn_confirmar = tk.Button(top, text="Aceptar", command=confirmar)
        btn_confirmar.pack(side="left", padx=10, pady=10)
        btn_cancelar = tk.Button(top, text="Cancelar", command=cancelar)
        btn_cancelar.pack(side="right", padx=10, pady=10)
        
        top.grab_set()
        self.wait_window(top)
        return datos["puntaje"], datos["comentario"]

    def agregar_calificacion(self, chaza):
        puntaje, comentario = self.dialogo_calificacion(chaza)
        if puntaje is None:
            return
        chaza.agregar_calificacion(puntaje, comentario)
        self.grafo_chazas.nodes[chaza.nombre]["calif"] = chaza.obtener_promedio()
        self.redibujar()

    def agregar_chaza(self, event):
        nombre, tipo = self.dialogo_datos_chaza()
        if not nombre or not tipo:
            return
        posicion = (event.x, event.y)
        nueva_chaza = Chaza(nombre, posicion, tipo)
        self.lista_chazas.append(nueva_chaza)
        self.grafo_chazas.add_node(nombre, pos=posicion, tipo=tipo, calif=0)
        self.redibujar()
        self.modo = "explorador"
        messagebox.showinfo("Modo Explorador", "Chaza agregada. Ahora en modo explorador.")

    def dialogo_datos_chaza(self):
        datos = {"nombre": None, "tipo": None}
        top = tk.Toplevel(self)
        top.title("Nueva Chaza")
        
        tk.Label(top, text="Nombre de la chaza:").pack(pady=5)
        entrada_nombre = tk.Entry(top, width=30)
        entrada_nombre.pack(pady=5)
        
        tk.Label(top, text="Tipo de Chaza:").pack(pady=5)
        tipo_var = tk.StringVar(top)
        tipo_var.set(TIPOS_PERMITIDOS[0])
        combo_tipo = ttk.Combobox(top, textvariable=tipo_var, values=TIPOS_PERMITIDOS, state="readonly")
        combo_tipo.pack(pady=5)
        
        def confirmar():
            nombre_ingresado = entrada_nombre.get().strip()
            if not nombre_ingresado:
                messagebox.showerror("Error", "Debe ingresar un nombre.")
                return
            datos["nombre"] = nombre_ingresado
            datos["tipo"] = tipo_var.get()
            top.destroy()
        
        def cancelar():
            top.destroy()
        
        tk.Button(top, text="Aceptar", command=confirmar).pack(side="left", padx=20, pady=10)
        tk.Button(top, text="Cancelar", command=cancelar).pack(side="right", padx=20, pady=10)
        
        top.grab_set()
        self.wait_window(top)
        return datos["nombre"], datos["tipo"]

    def mostrar_menu_chaza(self, chaza):
        promedio = chaza.obtener_promedio()
        if not chaza.calificaciones:
            info_calif = "Todavía no ha sido calificada."
        else:
            ultimas = chaza.ultimas_tres()
            info_calif = "\n".join([
                f"{cal} estrellas. Comentario: {comentario}" if comentario else f"{cal} estrellas"
                for cal, comentario in ultimas
            ])
        mensaje = (f"Chaza: {chaza.nombre}\nTipo: {chaza.tipo}\nPromedio: {promedio:.2f}\n\n"
                   f"Últimas calificaciones:\n{info_calif}")
        respuesta = messagebox.askyesno("Información Chaza", mensaje + "\n\n¿Desea agregar una nueva calificación?")
        if respuesta:
            self.agregar_calificacion(chaza)

    def obtener_color(self, calificacion):
        ratio = calificacion / 5.0 if calificacion <= 5 else 1
        r = int(255 * (1 - ratio))
        g = int(255 * ratio)
        b = 0
        return f"#{r:02x}{g:02x}{b:02x}"

    def mostrar_top_5(self):
        if not self.lista_chazas:
            messagebox.showinfo("Top 5 Chazas", "No hay chazas registradas.")
            return
        chazas_ordenadas = sorted(self.lista_chazas, key=lambda c: c.obtener_promedio(), reverse=True)
        top_5 = chazas_ordenadas[:5]
        info = "Top 5 Chazas (por promedio):\n\n"
        for i, chaza in enumerate(top_5, start=1):
            info += f"{i}. {chaza.nombre} ({chaza.tipo}): Promedio = {chaza.obtener_promedio():.2f}\n"
        messagebox.showinfo("Top 5 Chazas", info)

def main():
    app = CalificacionChazasApp()
    app.mainloop()

if __name__ == "__main__":
    main()