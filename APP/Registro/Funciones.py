import psycopg2
import smtplib
import random
import re
import os
import hmac
import hashlib
import binascii
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import messagebox

DB_HOST = "dpg-d2qr6g15pdvs738hp4k0-a.oregon-postgres.render.com"
DB_PORT = "5432"
DB_NAME = "listi_if8a"
DB_USER = "listi_if8a_user"
DB_PASS = "zDvjad3QM9gLJn1zE8OqIkOr35K6MX5u"

EMAIL_EMISOR = "facundohotmailcarabajal@gmail.com"
EMAIL_PASSWORD = "kadfpjtyecevcplr"

# Datos temporales durante el registro (antes de verificar código)
usuario_temporal = {}

# Formato de la contraseña
def validar_password(password: str):
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Za-z]", password):
        return False, "La contraseña debe contener al menos una letra."
    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un número."
    if not re.fullmatch(r"[A-Za-z0-9]+", password):
        return False, "La contraseña solo puede tener letras y números (sin caracteres especiales)."
    return True, ""

# Formato del email
def validar_email(email: str):
    if not re.fullmatch(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", email or ""):
        return False, "El correo no tiene un formato válido (ejemplo: usuario@dominio.com)."
    return True, ""

# Hash seguro con PBKDF2
def hash_password(password: str, iterations: int = 600_000) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${binascii.hexlify(salt).decode()}${binascii.hexlify(dk).decode()}"

def verificar_password(password: str, almacenado: str) -> bool:
    try:
        algoritmo, iter_str, salt_hex, hash_hex = almacenado.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        iterations = int(iter_str)
        salt = binascii.unhexlify(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(binascii.hexlify(dk).decode(), hash_hex)
    except Exception:
        return False


def enviar_correo(destinatario, codigo, nombre_usuario):
    asunto = "Código de verificación - Registro"
    mensaje = f"""
Hola {nombre_usuario},

Tu código de verificación es: {codigo}

Ingresalo en la aplicación para completar tu registro.

¡Gracias por unirte! 🐰
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL_EMISOR
    msg["To"] = destinatario
    msg["Subject"] = asunto
    msg.attach(MIMEText(mensaje, "plain"))

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(EMAIL_EMISOR, EMAIL_PASSWORD)
        servidor.send_message(msg)
        servidor.quit()
    except Exception:
        messagebox.showerror("Error", "No se pudo enviar el correo de verificación. Intentá de nuevo.")


def registrar_usuario(nombre, contraseña, email, callback_mostrar_verificacion):
    nombre = (nombre or "").strip()
    contraseña = (contraseña or "").strip()
    email = (email or "").strip()

    if not nombre or not contraseña or not email:
        messagebox.showwarning("Atención", "No dejes campos vacíos.")
        return

    ok_pass, msg_pass = validar_password(contraseña)
    if not ok_pass:
        messagebox.showerror("Contraseña inválida", msg_pass)
        return

    ok_mail, msg_mail = validar_email(email)
    if not ok_mail:
        messagebox.showerror("Correo inválido", msg_mail)
        return

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS, sslmode="require"
        )
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM usuarios WHERE nombre_usuario = %s", (nombre,))
        if cur.fetchone():
            messagebox.showerror("Error", "Ese usuario ya existe.")
            return

        cur.execute("SELECT 1 FROM usuarios WHERE correo_electronico = %s", (email,))
        if cur.fetchone():
            messagebox.showerror("Error", "Ese correo ya está registrado.")
            return

        # Generamos código y hash
        codigo = str(random.randint(100000, 999999))
        contraseña_hash = hash_password(contraseña)

        # Guardamos temporalmente hasta que verifique el código
        usuario_temporal.clear()
        usuario_temporal.update({
            "usuario": nombre,
            "password_hash": contraseña_hash,
            "email": email,
            "codigo": codigo
        })

        enviar_correo(email, codigo, nombre)
        callback_mostrar_verificacion()

    except Exception:
        messagebox.showerror("Error", "Ocurrió un error al registrar. Revisá tu conexión e intentá nuevamente.")
    finally:
        if cur: cur.close()
        if conn: conn.close()

def verificar_codigo(codigo_ingresado, callback_exito):
    if (codigo_ingresado or "").strip() == usuario_temporal.get("codigo"):
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(
                host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS, sslmode="require"
            )
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO usuarios (nombre_usuario, correo_electronico, contraseña)
                VALUES (%s, %s, %s);
            """, (
                usuario_temporal["usuario"],
                usuario_temporal["email"],
                usuario_temporal["password_hash"]
            ))
            conn.commit()

            messagebox.showinfo("¡Registro completo!", "Tu cuenta fue verificada exitosamente.")
            callback_exito() 
        except Exception:
            messagebox.showerror("Error", "No se pudo completar el registro. Intentá nuevamente.")
        finally:
            if cur: cur.close()
            if conn: conn.close()
    else:
        messagebox.showerror("Código incorrecto", "El código no coincide. Revisá tu correo e intentá otra vez.")

def login(nombre, contraseña, callback_exito):
    nombre = (nombre or "").strip()
    contraseña = (contraseña or "").strip()

    if not nombre or not contraseña:
        messagebox.showwarning("Atención", "Ingresá usuario y contraseña.")
        return

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS, sslmode="require"
        )
        cur = conn.cursor()

        cur.execute("SELECT contraseña FROM usuarios WHERE nombre_usuario = %s", (nombre,))
        fila = cur.fetchone()

        if fila and verificar_password(contraseña, fila[0]):
            callback_exito(nombre)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")
    except Exception:
        messagebox.showerror("Error", "No se pudo conectar a la base de datos.")
    finally:
        if cur: cur.close()
        if conn: conn.close()