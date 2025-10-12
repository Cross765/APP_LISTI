import customtkinter as ctk
from PIL import Image
import psycopg2

def cargar_icono(ruta):
    try:
        return ctk.CTkImage(Image.open(ruta), size=(20, 20))
    except:
        return None

DB_HOST = "dpg-d3elbeer433s73eppof0-a.oregon-postgres.render.com"
DB_PORT = "5432"
DB_NAME = "listi_7mwu"
DB_USER = "listi_7mwu_user"
DB_PASS = "cPEEWPBRxx4R0jnyfym6FebpEVGgRWhB"

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        sslmode="require",
    )

def obtener_usuario(nombre_usuario: str):
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id FROM usuarios WHERE nombre_usuario = %s;", (nombre_usuario,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        if cur: cur.close()
        if conn: conn.close()

##### notas #####
def crear_note(usuario_id: int, titulo: str) -> int:
    sql = """
    INSERT INTO notas (usuario_id, titulo, contenido)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (usuario_id, titulo, ""))
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        if cur: cur.close()
        if conn: conn.close()

def listar_notas(usuario_id: int):
    sql = """
    SELECT id, titulo
    FROM notas
    WHERE usuario_id = %s AND carpeta_id IS NULL
    ORDER BY fecha_modificacion DESC, id DESC;
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (usuario_id,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def listar_notas_en_carpeta(carpeta_id: int):
    sql = """
    SELECT id, titulo
    FROM notas
    WHERE carpeta_id = %s
    ORDER BY fecha_modificacion DESC, id DESC;
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (carpeta_id,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def traer_nota(nota_id: int):
    sql = "SELECT titulo, contenido FROM notas WHERE id = %s;"
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (nota_id,))
        row = cur.fetchone()
        return (row[0], row[1]) if row else None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def actualizar_nota(nota_id: int, contenido: str):
    sql = """
    UPDATE notas
    SET contenido = %s, fecha_modificacion = NOW()
    WHERE id = %s;
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (contenido, nota_id))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def renombrar_note(nota_id: int, nuevo_titulo: str):
    sql = """
    UPDATE notas
    SET titulo = %s, fecha_modificacion = NOW()
    WHERE id = %s;
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (nuevo_titulo, nota_id))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def borrar_note(nota_id: int):
    sql = "DELETE FROM notas WHERE id = %s;"
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (nota_id,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def mover_nota(nota_id: int, carpeta_id: int):
    sql = """
    UPDATE notas
    SET carpeta_id = %s, fecha_modificacion = NOW()
    WHERE id = %s;
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (carpeta_id, nota_id))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def quitar_de_carpeta(nota_id: int):
    sql = """
    UPDATE notas
    SET carpeta_id = NULL, fecha_modificacion = NOW()
    WHERE id = %s;
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (nota_id,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

##### carpetas #####
def crear_carpeta(usuario_id: int, nombre: str) -> int:
    sql = """
    INSERT INTO carpetas (usuario_id, nombre)
    VALUES (%s, %s)
    RETURNING id;
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (usuario_id, nombre))
        new_id = cur.fetchone()[0]
        conn.commit()
        return new_id
    finally:
        if cur: cur.close()
        if conn: conn.close()

def listar_carpetas(usuario_id: int):
    sql = """
    SELECT id, nombre
    FROM carpetas
    WHERE usuario_id = %s
    ORDER BY fecha_creacion DESC, id DESC;
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (usuario_id,))
        return cur.fetchall()
    finally:
        if cur: cur.close()
        if conn: conn.close()   

def traer_carpeta(carpeta_id: int):
    sql = "SELECT nombre, fecha_creacion FROM carpetas WHERE id = %s;"
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (carpeta_id,))
        row = cur.fetchone()
        return (row[0], row[1]) if row else None
    finally:
        if cur: cur.close()
        if conn: conn.close()

def renombrar_carpeta(carpeta_id: int, nuevo_nombre: str):
    sql = """
    UPDATE carpetas
    SET nombre = %s
    WHERE id = %s;
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (nuevo_nombre, carpeta_id))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()

def borrar_carpeta(carpeta_id: int):
    sql = "DELETE FROM carpetas WHERE id = %s;"
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(sql, (carpeta_id,))
        conn.commit()
    finally:
        if cur: cur.close()
        if conn: conn.close()