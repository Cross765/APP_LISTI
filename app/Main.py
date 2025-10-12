import customtkinter as ctk 
from PIL import Image
import subprocess
import os
import sys
from FuncMain import registrar_usuario, login, verificar_codigo
from FuncMain import cargar_sesion

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Crear ventana principal
ventana_login = ctk.CTk()
ventana_login.title("Inicio de Sesión")
ventana_login.geometry("1000x600")
ventana_login.configure(fg_color="#B99AD9")

base_dir=os.path.dirname(os.path.abspath(__file__))

def cargar_icono(ruta):
    try:
        return ctk.CTkImage(Image.open(ruta), size=(20, 20))
    except:
        return None

frame = ctk.CTkFrame(ventana_login, width=950, height=550, corner_radius=25, fg_color="#F2F2F2")
frame.place(relx=0.5, rely=0.5, anchor="center")

img_fondo= cargar_icono(os.path.join(base_dir, "Imagenes", "fondo.png"))
img_fondo.configure(size=(550, 350))
imagen_label = ctk.CTkLabel(frame, image=img_fondo, text="")
imagen_label.place(relx=0.3, rely=0.5, anchor="center")

# Entradas globales
entry_user = None
entry_pass = None
entry_nuevo_usuario = None
entry_nueva_contra = None
entry_email = None
entry_codigo = None 

def abrir_menu(usuario=None):
    ventana_login.destroy()
    ruta = os.path.join(os.path.dirname(__file__), "./Menu/Menu.py")
    subprocess.Popen([sys.executable, ruta, usuario or ""])

def limpiar_frame():
    for widget in frame.winfo_children():
        if widget != imagen_label:
            widget.destroy()

ojo_abierto = cargar_icono(os.path.join(base_dir, "Imagenes", "ojo_abierto.png"))
ojo_abierto.configure(size=(25, 25))
ojo_cerrado = cargar_icono(os.path.join(base_dir, "Imagenes", "ojo_cerrado.png"))
ojo_cerrado.configure(size=(25, 25))

def toggle_contraseña(entry, boton):
    if entry.cget("show")=="*":
        entry.configure(show="")
        boton.configure(image=ojo_cerrado)
    else:
        entry.configure(show="*")
        boton.configure(image=ojo_abierto)

# Muestra la pantalla de login
def mostrar_login():
    global entry_user, entry_pass, btn_toggle_pass
    limpiar_frame()

    # Título
    ctk.CTkLabel(frame, text="INICIAR SESION", font=("Segoe UI", 24, "bold"), text_color="#8343C2").place(relx=0.7, rely=0.15, anchor="center")

    # Usuario
    ctk.CTkLabel(frame, text="Usuario:", width=200, anchor="center").place(relx=0.65, rely=0.30, anchor="center")
    entry_user = ctk.CTkEntry(frame, width=280, placeholder_text="Escribí tu nombre de usuario")
    entry_user.place(relx=0.7, rely=0.37, anchor="center")

    # Contraseña
    ctk.CTkLabel(frame, text="Contraseña:", width=200, anchor="center").place(relx=0.65, rely=0.47, anchor="center")
    entry_pass = ctk.CTkEntry(frame, show="*", width=280, placeholder_text="Tu contraseña secreta")
    entry_pass.place(relx=0.7, rely=0.54, anchor="center")

    btn_toggle_pass= ctk.CTkButton(frame, width=30, height=30, text="", image=ojo_abierto, fg_color="transparent", hover_color="#EBF2B6",command=lambda: toggle_contraseña(entry_pass, btn_toggle_pass))
    btn_toggle_pass.place(x=820, y=282)

    # Botón ingresar
    ctk.CTkButton(frame, text="Ingresar", command=lambda: login(entry_user.get(), entry_pass.get(), abrir_menu), width=300, corner_radius=15, fg_color="#A07BEF", hover_color="#8A5DD9", text_color="white").place(relx=0.7, rely=0.65, anchor="center")

    # Botón para ir a registro
    ctk.CTkLabel(frame, text="🐇 ¿No tenés cuenta?", font=("Segoe UI", 12), text_color="#999").place(relx=0.7, rely=0.75, anchor="center")
    ctk.CTkButton(frame, text="Registrate", command=mostrar_registro, width=150, fg_color="#8343C2", hover_color="#8A5DD9", text_color="white").place(relx=0.7, rely=0.82, anchor="center")

    # Checkbox para mantener la sesión
    check_recordar = ctk.CTkCheckBox(frame, text="Mantener sesión iniciada")
    check_recordar.place(relx=0.7, rely=0.60, anchor="center")

    # Botón ingresar
    ctk.CTkButton(
        frame,
        text="Ingresar",
        command=lambda: login(entry_user.get(), entry_pass.get(), abrir_menu, check_recordar.get()),
        width=300,
        corner_radius=15,
        fg_color="#A07BEF",
        hover_color="#8A5DD9",
        text_color="white"
    ).place(relx=0.7, rely=0.65, anchor="center")

# Muestra la pantalla de registro
def mostrar_registro():
    global entry_nuevo_usuario, entry_nueva_contra, entry_email, btn_toggle_nueva
    limpiar_frame()

    # Título
    ctk.CTkLabel(frame, text="CREAR CUENTA", font=("Segoe UI", 24, "bold"), text_color="#8343C2").place(relx=0.7, rely=0.15, anchor="center")

    # Usuario
    ctk.CTkLabel(frame, text="Nuevo usuario:", anchor="w", width=200).place(relx=0.55, rely=0.28, anchor="center")
    entry_nuevo_usuario = ctk.CTkEntry(frame, width=280, placeholder_text="Elegí un nombre de usuario")
    entry_nuevo_usuario.place(relx=0.7, rely=0.33, anchor="center")

    # Contraseña
    ctk.CTkLabel(frame, text="Contraseña:", anchor="w", width=200).place(relx=0.55, rely=0.43, anchor="center")
    entry_nueva_contra = ctk.CTkEntry(frame, show="*", width=280, placeholder_text="Creá tu contraseña")
    entry_nueva_contra.place(relx=0.7, rely=0.48, anchor="center")

    btn_toggle_nueva= ctk.CTkButton(frame, width=30, height=30, text="", fg_color="transparent", hover_color="#EBF2B6",image=ojo_cerrado, command=lambda: toggle_contraseña(entry_nueva_contra, btn_toggle_nueva))
    btn_toggle_nueva.place(x=820, y=248)

    # Email
    ctk.CTkLabel(frame, text="Email:", anchor="w", width=200).place(relx=0.55, rely=0.58, anchor="center")
    entry_email = ctk.CTkEntry(frame, width=280, placeholder_text="ejemplo@email.com")
    entry_email.place(relx=0.7, rely=0.63, anchor="center")

    # Botón registrar
    ctk.CTkButton(frame, text="Registrar", command=lambda: registrar_usuario(entry_nuevo_usuario.get(), entry_nueva_contra.get(), entry_email.get(), mostrar_verificacion_registro), width=200, corner_radius=15, fg_color="#A07BEF", hover_color="#8A5DD9", text_color="white" ).place(relx=0.7, rely=0.73, anchor="center")

    # Botón para volver a login
    ctk.CTkLabel(frame, text="🐰 ¿Ya tenés cuenta?", font=("Segoe UI", 12), text_color="#999").place(relx=0.7, rely=0.80, anchor="center")
    ctk.CTkButton(frame, text="Iniciar Sesión", command=mostrar_login, width=150, fg_color="#8343C2", hover_color="#8A5DD9", text_color="white").place(relx=0.7, rely=0.87, anchor="center")

def mostrar_verificacion_registro():
    global entry_codigo
    limpiar_frame()

    ctk.CTkLabel(frame, text="VERIFICAR REGISTRO", font=("Segoe UI", 24, "bold"), text_color="#8343C2").place(relx=0.7, rely=0.15, anchor="center")
    ctk.CTkLabel(frame, text="Ingresá el código que enviamos a tu email", font=("Segoe UI", 14), text_color="#444").place(relx=0.7, rely=0.25, anchor="center")

    entry_codigo = ctk.CTkEntry(frame, width=250, placeholder_text="Código de verificación")
    entry_codigo.place(relx=0.7, rely=0.37, anchor="center")

    ctk.CTkButton(frame, text="Verificar", width=200, corner_radius=15, fg_color="#A07BEF", hover_color="#8A5DD9", text_color="white",command=lambda: verificar_codigo(entry_codigo.get(), mostrar_login)).place(relx=0.7, rely=0.50, anchor="center")

    ctk.CTkButton(frame, text="← Volver", width=150, fg_color="#E0D4F7", hover_color="#D0BFF3", text_color="#4B2B7F",corner_radius=20, command=mostrar_registro).place(relx=0.7, rely=0.65, anchor="center")

usuario_guardado = cargar_sesion()

if usuario_guardado:
    abrir_menu(usuario_guardado)
else:
    mostrar_login()
    ventana_login.mainloop()