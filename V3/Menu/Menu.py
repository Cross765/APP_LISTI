import customtkinter as ctk
from datetime import datetime
import calendar
import os
import sys
from tkinter import messagebox
from FuncMenu import cargar_icono
import FuncMenu as db
from tkinter import simpledialog
import tkinter as tk
from tkinter import colorchooser
import pygame

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

ventana = ctk.CTk()
ventana.geometry("1366x700")
ventana.title("Listi")

base_dir = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2 or not sys.argv[1].strip():
    messagebox.showerror("Error", "No se recibió el nombre de usuario. Inicie sesión nuevamente.")
    sys.exit(1)

nombre_usuario = sys.argv[1].strip()

usuario_id = db.obtener_usuario(nombre_usuario)

if usuario_id is None:
    messagebox.showerror("Error", f"Usuario '{nombre_usuario}' no encontrado en la base de datos.")
    sys.exit(1)

ventana.grid_rowconfigure(0, weight=1)
ventana.grid_columnconfigure(0, weight=0)
ventana.grid_columnconfigure(1, weight=1)
ventana.grid_columnconfigure(2, weight=0)

# PANEL IZQUIERDO
sidebar = ctk.CTkFrame(ventana, width=250, corner_radius=0, fg_color="white")
sidebar.grid(row=0, column=0, sticky="ns")

img_titulo = cargar_icono(os.path.join(base_dir, "Imgs", "Imagenes", "titulo.png"))
if img_titulo:
    img_titulo.configure(size=(120, 120))

titulo_sidebar = ctk.CTkLabel(sidebar, image=img_titulo, text="", font=ctk.CTkFont(size=20, weight="bold"), text_color="#333333")
titulo_sidebar.pack(pady=(10, 5))

scroll_secciones = ctk.CTkScrollableFrame(
    sidebar,
    width=220,
    fg_color="transparent",
    scrollbar_button_color="#DADADA",
    scrollbar_button_hover_color="#CCCCCC"
)
scroll_secciones.pack(fill="both", expand=True, padx=5, pady=(10, 5))

colores_secciones = ["#FFC107", "#4CAF50", "#F44336", "#9C27B0", "#03A9F4", "#FF9800", "#E91E63", "#673AB7"]

notas_widgets = {} 
frame_editor = None
text_nota = None
nota_actual_id = None

def agregar_nota_db(titulo):
    try:
        return db.crear_note(usuario_id, titulo)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear la nota.\n{e}")
        return None

def cargar_notas():
    for widget in scroll_secciones.winfo_children():
        widget.destroy()
    notas_widgets.clear()

    try:
        notas = db.listar_notas(usuario_id)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar las notas.\n{e}")
        return

    for idx, (nid, titulo) in enumerate(notas):
        color = colores_secciones[idx % len(colores_secciones)]
        frame = ctk.CTkFrame(scroll_secciones, fg_color="transparent")
        frame.pack(fill="x", pady=2, padx=5)

        icono = ctk.CTkLabel(frame, text="▎", text_color=color, font=ctk.CTkFont(size=20))
        icono.pack(side="left", padx=(5, 8))

        btn_nota = ctk.CTkButton(
            frame,
            text=titulo,
            text_color="#333333",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color="#E0D4EF",
            anchor="w",
            command=lambda n=nid: mostrar_nota(n)
        )
        btn_nota.pack(side="left", pady=2, fill="x", expand=True)

        # BOTÓN DE 3 PUNTITOS 
        def abrir_menu(nota_id, parent):
            menu = ctk.CTkToplevel(parent)
            menu.overrideredirect(True)  # sin borde/ventana
            menu.geometry(f"+{parent.winfo_rootx()+parent.winfo_width()}+{parent.winfo_rooty()}")  # al lado del botón
            menu.configure(fg_color="white")

            def modificar():
                menu.destroy()
                nuevo_titulo = simpledialog.askstring("Modificar", "Nuevo título:")
                if nuevo_titulo:
                    try:
                        db.renombrar_note(nota_id, nuevo_titulo.strip())
                        cargar_notas()
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo modificar.\n{e}")

            def borrar():
                menu.destroy()
                if messagebox.askyesno("Confirmar", "¿Eliminar esta nota?"):
                    try:
                        db.borrar_note(nota_id)
                        cargar_notas()
                        if frame_editor:
                            frame_editor.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo borrar.\n{e}")

            # opciones del menú
            ctk.CTkButton(menu, text="✏️ Modificar", fg_color="transparent", text_color="#333333", anchor="w", command=modificar).pack(fill="x", padx=5, pady=2)
            ctk.CTkButton(menu, text="🗑️ Borrar", fg_color="transparent", text_color="#333333", anchor="w", command=borrar).pack(fill="x", padx=5, pady=2)
            ctk.CTkButton(menu, text="📂 Mover", fg_color="transparent", text_color="#333333", anchor="w").pack(fill="x", padx=5, pady=2)

            # cerrar si clic afuera
            menu.bind("<FocusOut>", lambda e: menu.destroy())
            menu.focus_force()

        btn_menu = ctk.CTkButton(
            frame,
            text="⋮",
            width=25,
            fg_color="transparent",
            text_color="#666666",
            hover_color="#D1B6F1",
            command=lambda n=nid, p=frame: abrir_menu(n, p)
        )
        btn_menu.pack(side="right", padx=5)

        notas_widgets[nid] = (frame, btn_nota, btn_menu)

def nueva_nota():
    global frame_editor
    if frame_editor:
        frame_editor.destroy()

    frame_editor = ctk.CTkFrame(contenido, fg_color="#FAFAFA", corner_radius=12)
    frame_editor.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

    # Título
    titulo = ctk.CTkLabel(
        frame_editor,
        text="📒 Nueva Nota",
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#4A148C"
    )
    titulo.pack(pady=(10, 8))

    # Entrada de texto
    entrada = ctk.CTkEntry(
        frame_editor,
        width=400,
        placeholder_text="Escribe el título de tu nota..."
    )
    entrada.pack(pady=10, padx=10)
    entrada.focus()

    # Separador
    ctk.CTkFrame(frame_editor, height=1, fg_color="#DDDDDD").pack(fill="x", padx=20, pady=10)

    # Botones
    botones = ctk.CTkFrame(frame_editor, fg_color="transparent")
    botones.pack(pady=10)

    btn_crear = ctk.CTkButton(
        botones, text="✔ Crear", fg_color="#B99AD9", text_color="white",
        corner_radius=8, width=100
    )
    btn_crear.pack(side="left", padx=10)

    btn_cancelar = ctk.CTkButton(
        botones, text="✖ Cancelar", fg_color="#F44336", text_color="white",
        corner_radius=8, width=100
    )
    btn_cancelar.pack(side="left", padx=10)

    # Funciones
    def guardar():
        titulo = entrada.get().strip()
        if not titulo:
            messagebox.showwarning("Atención", "El título no puede estar vacío.")
            return
        nid = agregar_nota_db(titulo)
        if nid:
            frame_editor.destroy()
            cargar_notas()
            mostrar_nota(nid)

    def cancelar():
        frame_editor.destroy()

    btn_crear.configure(command=guardar)
    btn_cancelar.configure(command=cancelar)

def mostrar_nota(nota_id):
    global frame_editor, text_nota, nota_actual_id
    nota_actual_id = nota_id

    if frame_editor:
        frame_editor.destroy()

    frame_editor = ctk.CTkFrame(contenido, fg_color="white")
    frame_editor.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    try:
        row = db.traer_nota(nota_id)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la nota.\n{e}")
        return

    if not row:
        messagebox.showerror("Error", "La nota no existe.")
        return

    titulo, contenido_txt = row

    header = ctk.CTkFrame(frame_editor, fg_color="transparent")
    header.pack(fill="x", pady=(5, 6), padx=10)

    titulo_entry = ctk.CTkEntry(header, width=500)
    titulo_entry.insert(0, titulo)
    titulo_entry.pack(side="left", padx=(0, 8))

    def renombrar():
        nuevo = titulo_entry.get().strip()
        if not nuevo:
            messagebox.showwarning("Atención", "El título no puede estar vacío.")
            return
        try:
            db.renombrar_note(nota_id, nuevo)
            cargar_notas()
            messagebox.showinfo("OK", "Título actualizado.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el título.\n{e}")

    ctk.CTkButton(header, text="Renombrar", command=renombrar, fg_color="#A07BEF", text_color="white").pack(side="left")

    # ------------------ BARRA DE HERRAMIENTAS FORMATO ------------------
    toolbar = ctk.CTkFrame(frame_editor, fg_color="transparent")
    toolbar.pack(fill="x", padx=10, pady=(0,5))

    # ------------------ TEXT BOX CON FORMATO ------------------
    text_nota = tk.Text(frame_editor, wrap="word", font=("Arial", 14))
    text_nota.pack(fill="both", expand=True, padx=10, pady=5)
    text_nota.insert("1.0", contenido_txt or "")


    # Configurar tags
    text_nota.tag_configure("bold", font=("Arial", 14, "bold"))
    text_nota.tag_configure("italic", font=("Arial", 14, "italic"))
    text_nota.tag_configure("underline", font=("Arial", 14, "underline"))

    # Funciones de formato
    def toggle_tag(tag):
        try:
            current_tags = text_nota.tag_names("sel.first")
            if tag in current_tags:
                text_nota.tag_remove(tag, "sel.first", "sel.last")
            else:
                text_nota.tag_add(tag, "sel.first", "sel.last")
        except tk.TclError:
            messagebox.showinfo("Info", "Selecciona texto primero")

    def cambiar_color():
        color = colorchooser.askcolor()[1]
        if color:
            try:
                text_nota.tag_add(color, "sel.first", "sel.last")
                text_nota.tag_configure(color, foreground=color)
            except tk.TclError:
                messagebox.showinfo("Info", "Selecciona texto primero")

    # Botones de formato
    ctk.CTkButton(toolbar, text="B", width=30, command=lambda: toggle_tag("bold")).pack(side="left", padx=2)
    ctk.CTkButton(toolbar, text="I", width=30, command=lambda: toggle_tag("italic")).pack(side="left", padx=2)
    ctk.CTkButton(toolbar, text="U", width=30, command=lambda: toggle_tag("underline")).pack(side="left", padx=2)
    ctk.CTkButton(toolbar, text="Color", width=50, command=cambiar_color).pack(side="left", padx=2)

    # ------------------ BOTONES GUARDAR / ELIMINAR / CERRAR ------------------
    botones_frame = ctk.CTkFrame(frame_editor, fg_color="transparent")
    botones_frame.pack(pady=10)

    def guardar_contenido():
        contenido_guardado = text_nota.get("1.0", "end").strip()
        try:
            db.actualizar_nota(nota_id, contenido_guardado)
            cargar_notas()
            messagebox.showinfo("Guardado", "La nota se guardó correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la nota.\n{e}")

    def eliminar_nota():
        if messagebox.askyesno("Confirmar", "¿Eliminar esta nota?"):
            try:
                db.borrar_note(nota_id)
                cerrar_editor()
                cargar_notas()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar la nota.\n{e}")

    def cerrar_editor():
        if frame_editor:
            frame_editor.destroy()

    ctk.CTkButton(botones_frame, text="Guardar", fg_color="#B99AD9", text_color="white", command=guardar_contenido).pack(side="left", padx=5)
    ctk.CTkButton(botones_frame, text="Eliminar", fg_color="#F44336", text_color="white", command=eliminar_nota).pack(side="left", padx=5)
    ctk.CTkButton(botones_frame, text="Cerrar", fg_color="#9E9E9E", text_color="white", command=cerrar_editor).pack(side="left", padx=5)

### carpetas ###
carpetas_widgets = {}

def agregar_carpeta_db(nombre):
    try:
        return db.crear_carpeta(usuario_id, nombre)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear la carpeta.\n{e}")
        return None

def cargar_carpetas():
    for widget in scroll_secciones.winfo_children():
        widget.destroy()
    carpetas_widgets.clear()

    try:
        carpetas = db.listar_carpetas(usuario_id) 
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar las carpetas.\n{e}")
        return

    for idx, (cid, nombre) in enumerate(carpetas):
        color = colores_secciones[idx % len(colores_secciones)]
        frame = ctk.CTkFrame(scroll_secciones, fg_color="transparent")
        frame.pack(fill="x", pady=2, padx=5)

        icono = ctk.CTkLabel(frame, text="📂", text_color=color, font=ctk.CTkFont(size=20))
        icono.pack(side="left", padx=(5, 8))

        btn_carpeta = ctk.CTkButton(
            frame,
            text=nombre,
            text_color="#333333",
            fg_color="#FFFFFF", hover_color="#B8B8B8",
            font=ctk.CTkFont(size=14),
            command=lambda c=cid: mostrar_carpeta(c) 
        )
        btn_carpeta.pack(side="left", pady=2, fill="x", expand=True)

        # --- Menú contextual ---
        def abrir_menu(carpeta_id, parent):
            menu = ctk.CTkToplevel(parent)
            menu.overrideredirect(True)
            menu.geometry(f"+{parent.winfo_rootx()+parent.winfo_width()}+{parent.winfo_rooty()}")
            menu.configure(fg_color="white")

            def editar():
                menu.destroy()
                nuevo_nombre = simpledialog.askstring("Editar carpeta", "Nuevo nombre:")
                if nuevo_nombre:
                    try:
                        db.renombrar_carpeta(carpeta_id, nuevo_nombre.strip())
                        cargar_carpetas()
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo editar la carpeta.\n{e}")

            def borrar():
                menu.destroy()
                if messagebox.askyesno("Confirmar", "¿Eliminar esta carpeta?"):
                    try:
                        db.borrar_carpeta(carpeta_id)
                        cargar_carpetas()
                        if frame_editor:
                            frame_editor.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"No se pudo eliminar la carpeta.\n{e}")

            ctk.CTkButton(menu, text="✏️ Editar", fg_color="transparent", text_color="#333333",
                          anchor="w", command=editar).pack(fill="x", padx=5, pady=2)
            ctk.CTkButton(menu, text="🗑️ Borrar", fg_color="transparent", text_color="#333333",
                          anchor="w", command=borrar).pack(fill="x", padx=5, pady=2)

            menu.bind("<FocusOut>", lambda e: menu.destroy())
            menu.focus_force()

        btn_menu = ctk.CTkButton(
            frame,
            text="⋮",
            width=25,
            fg_color="transparent",
            text_color="#666666",
            hover_color="#E0D4EF",
            command=lambda c=cid, p=frame: abrir_menu(c, p)
        )
        btn_menu.pack(side="right", padx=5)

        carpetas_widgets[cid] = (frame, btn_carpeta, btn_menu)

def nueva_carpeta():
    global frame_editor
    if frame_editor:
        frame_editor.destroy()

    frame_editor = ctk.CTkFrame(contenido, fg_color="white")
    frame_editor.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    ctk.CTkLabel(frame_editor, text="Nombre de la carpeta:", font=ctk.CTkFont(size=14)).pack(pady=(12, 6))
    entrada = ctk.CTkEntry(frame_editor, width=400)
    entrada.pack(pady=5)

    def guardar_nombre():
        nombre = entrada.get().strip()
        if not nombre:
            messagebox.showwarning("Atención", "El nombre no puede estar vacío.")
            return
        cid = agregar_carpeta_db(nombre)
        if cid:
            cargar_carpetas()
            mostrar_carpeta(cid)  # abre la carpeta recién creada

    botones = ctk.CTkFrame(frame_editor, fg_color="transparent")
    botones.pack(pady=10)

    ctk.CTkButton(botones, text="Crear", command=guardar_nombre,
                  fg_color="#B99AD9", text_color="white").pack(side="left", padx=5)
    ctk.CTkButton(botones, text="Cancelar",
                  command=lambda: frame_editor.destroy(),
                  fg_color="#F44336", text_color="white").pack(side="left", padx=5)

def mostrar_carpeta(carpeta_id):
    global frame_editor
    if frame_editor:
        frame_editor.destroy()

    frame_editor = ctk.CTkFrame(contenido, fg_color="white")
    frame_editor.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    try:
        row = db.traer_carpeta(carpeta_id)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la carpeta.\n{e}")
        return

    if not row:
        messagebox.showerror("Error", "La carpeta no existe.")
        return

    nombre, contenido_txt = row

    titulo = ctk.CTkLabel(frame_editor, text=f"📂 {nombre}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#333333")
    titulo.pack(pady=10)

# ---------- PANEL DERECHO (calendario, temporizador, sonidos) ----------
sidebar_derecho = ctk.CTkFrame(ventana, width=250, corner_radius=0, fg_color="white")
sidebar_derecho.grid(row=0, column=2, sticky="ns")

# calendario
titulo_calendario = ctk.CTkLabel(sidebar_derecho, text="Calendario", font=ctk.CTkFont(size=20, weight="bold", family="Comic Sans MS"), text_color="#333333")
titulo_calendario.pack(pady=(20, 10))

calendario_frame = ctk.CTkFrame(sidebar_derecho, fg_color="#EBF2B6", corner_radius=15)
calendario_frame.pack(padx=5, pady=1)

fecha_actual = datetime.today()
mes_actual = fecha_actual.month
anio_actual = fecha_actual.year

def dibujar_calendario(frame, mes, anio):
    for widget in frame.winfo_children():
        widget.destroy()

    def cambiar_mes(delta):
        nonlocal mes, anio
        mes += delta
        if mes < 1:
            mes = 12
            anio -= 1
        elif mes > 12:
            mes = 1
            anio += 1
        dibujar_calendario(frame, mes, anio)

    encabezado = ctk.CTkFrame(frame, fg_color="transparent")
    encabezado.grid(row=0, column=0, columnspan=7, pady=(8, 4))

    ctk.CTkButton(encabezado, text="←", width=20, height=20, fg_color="transparent", text_color="#B99AD9", hover_color="#E0D4EF", command=lambda: cambiar_mes(-1)).pack(side="left")

    nombre_mes = datetime(anio, mes, 1).strftime("%B %Y").capitalize()
    ctk.CTkLabel(encabezado, text=nombre_mes, font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333").pack(side="left", padx=6)

    ctk.CTkButton(encabezado, text="→", width=20, height=20, fg_color="transparent", text_color="#B99AD9", hover_color="#E0D4EF", command=lambda: cambiar_mes(1)).pack(side="left")

    dias_semana = ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]
    for i, dia in enumerate(dias_semana):
        ctk.CTkLabel(frame, text=dia, width=20, height=20, text_color="#666666", font=ctk.CTkFont(size=10)).grid(row=1, column=i, padx=1, pady=1)

    cal = calendar.Calendar(firstweekday=6)
    semanas = cal.monthdayscalendar(anio, mes)

    for fila_idx, semana in enumerate(semanas, start=2):
        for col_idx, dia in enumerate(semana):
            texto = str(dia) if dia != 0 else ""
            es_hoy = (dia == fecha_actual.day and mes == fecha_actual.month and anio == fecha_actual.year)
            color_fondo = "#B99AD9" if es_hoy else "transparent"
            color_texto = "white" if es_hoy else "#333333"

            ctk.CTkLabel(frame, text=texto, width=20, height=20, corner_radius=20,
                         fg_color=color_fondo, text_color=color_texto,
                         font=ctk.CTkFont(size=10)).grid(row=fila_idx, column=col_idx, padx=1, pady=1)

dibujar_calendario(calendario_frame, mes_actual, anio_actual)

# temporizador (UI)
titulo_temporizador = ctk.CTkLabel(sidebar_derecho, text="Temporizador", font=ctk.CTkFont(size=18, weight="bold", family="Comic Sans MS"), text_color="#333333")
titulo_temporizador.pack(pady=(10, 0))

temporizador_frame = ctk.CTkFrame(sidebar_derecho, fg_color="#EBF2B6", corner_radius=15, width=240, height=120)
temporizador_frame.pack(padx=5, pady=1)
temporizador_frame.pack_propagate(False)

ctk.CTkLabel(temporizador_frame, text="00:00", font=ctk.CTkFont(size=34, weight="bold"), text_color="#A3B044").pack(pady=(8, 0))

ctk.CTkLabel(temporizador_frame, text="¡Hora de enfocarse!", font=ctk.CTkFont(size=12), text_color="#333333").pack(pady=(0, 5))

bf = ctk.CTkFrame(temporizador_frame, fg_color="transparent")
bf.pack(pady=4)
ctk.CTkButton(bf, text="Iniciar", width=75, height=28, fg_color="#B99AD9", text_color="white").grid(row=0, column=0, padx=2)
ctk.CTkButton(bf, text="⏸", width=32, height=28, fg_color="#F4F4F4", text_color="#333333").grid(row=0, column=1, padx=2)
ctk.CTkButton(bf, text="↻", width=32, height=28, fg_color="#F4F4F4", text_color="#333333").grid(row=0, column=2, padx=2)
ctk.CTkButton(bf, text="⚙", width=32, height=28, fg_color="#F4F4F4", text_color="#333333").grid(row=0, column=3, padx=2)

# sonidos (UI)
titulo_sonidos = ctk.CTkLabel(sidebar_derecho, text="Sonidos Relajantes", font=ctk.CTkFont(size=16, weight="bold", family="Comic Sans MS"), text_color="#333333")
titulo_sonidos.pack(pady=(10, 0))

contenedor_sonidos = ctk.CTkFrame(sidebar_derecho, fg_color="transparent", height=110, width=200)
contenedor_sonidos.pack(padx=5, pady=(5, 10))

scroll_sonidos = ctk.CTkScrollableFrame(contenedor_sonidos, width=220, fg_color="transparent", scrollbar_button_color="#DADADA", scrollbar_button_hover_color="#CCCCCC")
scroll_sonidos.pack()

def agregar_sonido(nombre, color_fondo, color_icono):
    frame = ctk.CTkFrame(scroll_sonidos, fg_color=color_fondo, corner_radius=15)
    frame.pack(pady=5, fill="x", padx=5)

    ctk.CTkLabel(frame, text="🎵", text_color=color_icono, font=ctk.CTkFont(size=16)).pack(side="left", padx=(10, 5), pady=5)
    ctk.CTkLabel(frame, text=nombre, text_color="#333333", font=ctk.CTkFont(size=13)).pack(side="left", padx=(0, 5))
    ctk.CTkButton(frame, text="▶", width=20, height=20, fg_color="transparent", text_color=color_icono, hover_color="#EEEEEE").pack(side="right", padx=10)

agregar_sonido("Lluvia Suave", "#F6F2FF", "#B99AD9")
agregar_sonido("Olas del Mar", "#EBF2B6", "#A3B044")

# PANEL CENTRAL
panel_central = ctk.CTkFrame(ventana, fg_color="transparent")
panel_central.grid(row=0, column=1, sticky="nsew")
panel_central.grid_rowconfigure(0, weight=0)
panel_central.grid_rowconfigure(1, weight=1)
panel_central.grid_columnconfigure(0, weight=1)

encabezado = ctk.CTkFrame(panel_central, fg_color="#f2f2f2", height=80, corner_radius=0)
encabezado.grid(row=0, column=0, sticky="ew")
encabezado.grid_rowconfigure(0, weight=1)

contenido = ctk.CTkFrame(panel_central, fg_color="white")
contenido.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
contenido.grid_rowconfigure(0, weight=1)
contenido.grid_rowconfigure(1, weight=0)
contenido.grid_columnconfigure(0, weight=1)

# BOTONES ENCABEZADO
iconos = {
    "Tablero": cargar_icono(os.path.join(base_dir,"Imgs","diseño_base", "tablero.png")),
    "Mis Notas": cargar_icono(os.path.join(base_dir,"Imgs","diseño_base", "mis_notas.png")),
    "Carpetas": cargar_icono(os.path.join(base_dir,"Imgs","diseño_base", "carpeta.png")),
    "Papelera": cargar_icono(os.path.join(base_dir,"Imgs","diseño_base", "papelera.png"))
}

botones = {}
nombres = ["Tablero", "Mis Notas", "Carpetas", "Papelera"]

btn_accion = ctk.CTkButton(
    sidebar,
    text="",
    fg_color="transparent",
    text_color="#B99AD9",
    hover_color="#EBF2B6",
    anchor="w",
    font=ctk.CTkFont(size=16, weight="bold"),
    command=nueva_nota
)

btn_accion.pack(fill="x", pady=10, padx=5)
btn_accion.pack_forget()

def seleccionar_boton(nombre_boton):
    for nombre, boton in botones.items():
        if nombre == nombre_boton:
            boton.configure(fg_color="#B99AD9", text_color="white")
        else:
            boton.configure(fg_color="transparent", text_color="#4C4C4C")

    if nombre_boton == "Mis Notas":
        btn_accion.pack(fill="x", pady=10, padx=5)
        btn_accion.configure(text="+ Agregar nota", command=nueva_nota)
        cargar_notas()

    elif nombre_boton == "Carpetas":
        btn_accion.pack(fill="x", pady=10, padx=5)
        btn_accion.configure(text="+ Agregar carpeta", command=nueva_carpeta)
        cargar_carpetas()

    else:
        btn_accion.pack_forget()
        for widget in scroll_secciones.winfo_children():
            widget.destroy()

for i in range(len(nombres)):
    encabezado.grid_columnconfigure(i, weight=1, uniform="col")

fuente_botones = ctk.CTkFont(size=20, family="Pacifico")
for i, nombre in enumerate(nombres):
    boton = ctk.CTkButton(
        encabezado,
        text=nombre,
        image=iconos[nombre],
        anchor="center",
        fg_color="transparent",
        hover_color="#B99AD9",
        text_color="#4C4C4C",
        font=fuente_botones,
        command=lambda n=nombre: seleccionar_boton(n)
    )
    boton.grid(row=0, column=i, padx=5, pady=20, sticky="nsew")
    botones[nombre] = boton

ventana.mainloop()