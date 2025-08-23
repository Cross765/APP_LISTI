import customtkinter as ctk
from PIL import Image
from datetime import datetime
import calendar

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

ventana = ctk.CTk()
ventana.geometry("1366x700")
ventana.title("Listi")

# Configuración de la grilla principal
ventana.grid_rowconfigure(0, weight=1)
ventana.grid_columnconfigure(0, weight=0)
ventana.grid_columnconfigure(1, weight=1)
ventana.grid_columnconfigure(2, weight=0)

# PANEL IZQUIERDO 
sidebar = ctk.CTkFrame(ventana, width=250, corner_radius=0, fg_color="white")
sidebar.grid(row=0, column=0, sticky="ns")

titulo = ctk.CTkLabel(
    sidebar,
    text="LISTI",
    font=ctk.CTkFont(size=30, weight="bold", family="Comic Sans MS"),
    text_color="#B99AD9")
titulo.pack(pady=(20, 10))

def cargar_icono(ruta):
    try:
        return ctk.CTkImage(Image.open(ruta), size=(20, 20))
    except:
        return None

iconos = {
    "Tablero": cargar_icono("Iconos del menu/diseño_base/tablero.png"),
    "Mis Notas": cargar_icono("Iconos del menu/diseño_base/mis_notas.png"),
    "Carpetas": cargar_icono("Iconos del menu/diseño_base/carpeta.png"),
    "Papelera": cargar_icono("Iconos del menu/diseño_base/papelera.png")
}

botones = {}
nombres = ["Tablero", "Mis Notas", "Carpetas", "Papelera"]

def seleccionar_boton(nombre_boton):
    for nombre, boton in botones.items():
        if nombre == nombre_boton:
            boton.configure(fg_color="#B99AD9", text_color="white")
        else:
            boton.configure(fg_color="transparent", text_color="#4C4C4C")

fuente_botones = ctk.CTkFont(size=20, family="Pacifico")
for nombre in nombres:
    boton = ctk.CTkButton(
        sidebar,
        text=nombre,
        image=iconos[nombre],
        anchor="w",
        width=180,
        height=40,
        fg_color="transparent",
        hover_color="#B99AD9",
        text_color="#4C4C4C",
        font=fuente_botones,
        command=lambda n=nombre: seleccionar_boton(n))
    boton.pack(pady=5, padx=10)
    botones[nombre] = boton


# PANEL DERECHO
sidebar_derecho = ctk.CTkFrame(ventana, width=250, corner_radius=0, fg_color="white")
sidebar_derecho.grid(row=0, column=2, sticky="ns")

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
        global mes_actual, anio_actual
        mes_actual += delta
        if mes_actual < 1:
            mes_actual = 12
            anio_actual -= 1
        elif mes_actual > 12:
            mes_actual = 1
            anio_actual += 1
        dibujar_calendario(frame, mes_actual, anio_actual)

    encabezado = ctk.CTkFrame(frame, fg_color="transparent")
    encabezado.grid(row=0, column=0, columnspan=7, pady=(8, 4))

    btn_izq = ctk.CTkButton(encabezado, text="←", width=20, height=20, fg_color="transparent", text_color="#B99AD9", hover_color="#E0D4EF", command=lambda: cambiar_mes(-1))
    btn_izq.pack(side="left")

    nombre_mes = datetime(anio, mes, 1).strftime("%B %Y").capitalize()
    lbl_mes = ctk.CTkLabel(encabezado, text=nombre_mes, font=ctk.CTkFont(size=14, weight="bold"), text_color="#333333")
    lbl_mes.pack(side="left", padx=6)

    btn_der = ctk.CTkButton(
        encabezado, text="→", width=20, height=20, fg_color="transparent", text_color="#B99AD9", hover_color="#E0D4EF", command=lambda: cambiar_mes(1))
    btn_der.pack(side="left")

    dias_semana= ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"]
    for i, dia in enumerate(dias_semana):
        lbl_dia= ctk.CTkLabel(frame, text=dia, width=20, height=20, text_color="#666666", font=ctk.CTkFont(size=10))
        lbl_dia.grid(row=1, column=i, padx=1, pady=1)

    cal = calendar.Calendar(firstweekday=6)  # Domingo como inicio
    semanas = cal.monthdayscalendar(anio, mes)

    for fila_idx, semana in enumerate(semanas, start=2):
        for col_idx, dia in enumerate(semana):
            texto= str(dia) if dia != 0 else ""
            es_hoy= (
                dia == fecha_actual.day and
                mes == fecha_actual.month and
                anio == fecha_actual.year)
            color_fondo= "#B99AD9" if es_hoy else "transparent"
            color_texto= "white" if es_hoy else "#333333"

            lbl_dia= ctk.CTkLabel(frame, text=texto, width=20, height=20, corner_radius=20, fg_color=color_fondo, text_color=color_texto, font=ctk.CTkFont(size=10))
            lbl_dia.grid(row=fila_idx, column=col_idx, padx=1, pady=1)
dibujar_calendario(calendario_frame, mes_actual, anio_actual)

titulo_temporizador = ctk.CTkLabel(sidebar_derecho, text="Temporizador", font=ctk.CTkFont(size=18, weight="bold", family="Comic Sans MS"), text_color="#333333")
titulo_temporizador.pack(pady=(10, 0))

temporizador_frame = ctk.CTkFrame(sidebar_derecho, fg_color="#EBF2B6", corner_radius=15, width=240, height=120)
temporizador_frame.pack(padx=5, pady=1)
temporizador_frame.pack_propagate(False)

reloj_label = ctk.CTkLabel(temporizador_frame, text="00:00", font=ctk.CTkFont(size=34, weight="bold"), text_color="#A3B044")
reloj_label.pack(pady=(8, 0))

mensaje_label = ctk.CTkLabel(temporizador_frame, text="¡Hora de enfocarse!", font=ctk.CTkFont(size=12), text_color="#333333")
mensaje_label.pack(pady=(0, 5))

botones_frame = ctk.CTkFrame(temporizador_frame, fg_color="transparent")
botones_frame.pack(pady=4)

btn_iniciar = ctk.CTkButton(botones_frame, text="Iniciar", width=75, height=28, fg_color="#B99AD9", text_color="white")
btn_iniciar.grid(row=0, column=0, padx=2)

btn_pausar = ctk.CTkButton(botones_frame, text="⏸", width=32, height=28, fg_color="#F4F4F4", text_color="#333333")
btn_pausar.grid(row=0, column=1, padx=2)

btn_reiniciar = ctk.CTkButton(botones_frame, text="↻", width=32, height=28, fg_color="#F4F4F4", text_color="#333333")
btn_reiniciar.grid(row=0, column=2, padx=2)

btn_configurar = ctk.CTkButton(botones_frame, text="⚙", width=32, height=28, fg_color="#F4F4F4", text_color="#333333")
btn_configurar.grid(row=0, column=3, padx=2)

# SONIDOS
titulo_sonidos = ctk.CTkLabel(sidebar_derecho, text="Sonidos Relajantes", font=ctk.CTkFont(size=16, weight="bold", family="Comic Sans MS"), text_color="#333333")
titulo_sonidos.pack(pady=(10, 0))

contenedor_sonidos = ctk.CTkFrame(sidebar_derecho, fg_color="transparent", height=110, width=200)
contenedor_sonidos.pack(padx=5, pady=(5, 10))

scroll_sonidos = ctk.CTkScrollableFrame(contenedor_sonidos, width=220, fg_color="transparent", scrollbar_button_color="#DADADA", scrollbar_button_hover_color="#CCCCCC")
scroll_sonidos.pack()

def agregar_sonido(nombre, color_fondo, color_icono):
    frame = ctk.CTkFrame(scroll_sonidos, fg_color=color_fondo, corner_radius=15)
    frame.pack(pady=5, fill="x", padx=5)

    icono = ctk.CTkLabel(frame, text="🎵", text_color=color_icono, font=ctk.CTkFont(size=16))
    icono.pack(side="left", padx=(10, 5), pady=5)

    nombre_lbl = ctk.CTkLabel(frame, text=nombre, text_color="#333333", font=ctk.CTkFont(size=13))
    nombre_lbl.pack(side="left", padx=(0, 5))

    btn_play = ctk.CTkButton(frame, text="▶", width=20, height=20, fg_color="transparent", text_color=color_icono, hover_color="#EEEEEE")
    btn_play.pack(side="right", padx=10)

agregar_sonido("Lluvia Suave", "#F6F2FF", "#B99AD9")
agregar_sonido("Olas del Mar", "#EBF2B6", "#A3B044")

# PANEL CENTRAL PARA ENCABEZADO Y CONTENIDO
panel_central = ctk.CTkFrame(ventana, fg_color="transparent")
panel_central.grid(row=0, column=1, sticky="nsew")
panel_central.grid_rowconfigure(0, weight=0)  # encabezado
panel_central.grid_rowconfigure(1, weight=1)  # contenido
panel_central.grid_columnconfigure(0, weight=1)

# PANEL SUPERIOR
encabezado= ctk.CTkFrame(panel_central, fg_color="#ebeaea", height=80, corner_radius=0)
encabezado.grid(row=0, column=0, sticky="ew")

titulo_mis_notas= ctk.CTkLabel(encabezado, text="Mis Notas", font=("Arial", 22, "bold"), text_color="#1a1a1a")
titulo_mis_notas.place(x=10, y=25)

barra_busqueda_frame= ctk.CTkFrame(encabezado, width=280, height=35, corner_radius=10, border_width=1.5, border_color="#000000", fg_color="#ffffff")
barra_busqueda_frame.place(x=300, y=25)

lupa_label= ctk.CTkLabel(barra_busqueda_frame, text="🔍", text_color="#b388eb", font=("Arial", 16))
lupa_label.place(x=8, y=2)

entry_busqueda= ctk.CTkEntry(barra_busqueda_frame, placeholder_text="Buscar notas...", width=220, height=25, border_width=0, fg_color="white", text_color="black", font=("Arial", 12))
entry_busqueda.place(x=35, y=5)

contenedor_perfil=ctk.CTkButton(encabezado, fg_color="#ebeaea",height=38, width=140, text="Ana", text_color="#000000")
contenedor_perfil.configure(fg_color="#B99AD9", hover_color="#B99AD9",text_color="white")
contenedor_perfil.place(x=750, y=20)

img_perfil=cargar_icono("perfil.png")
img_perfil.configure(size=(25, 25))

perfil_label = ctk.CTkLabel(contenedor_perfil, image=img_perfil, text="")
perfil_label.place(x=5, y=5)

ventana.mainloop()