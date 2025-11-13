import customtkinter as ctk
from PIL import Image
import psycopg2

def cargar_icono(ruta):
    try:
        return ctk.CTkImage(Image.open(ruta), size=(20, 20))
    except:
        return None

DB_HOST = "dpg-d49lmf1r0fns738l7vkg-a.oregon-postgres.render.com"
DB_PORT = "5432"
DB_NAME = "listi_6ntc"
DB_USER = "listi_6ntc_user"
DB_PASS = "1nCSIvXNljC0oVn48OXJMQUMsCwVlQBv"

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        sslmode="require"
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
    sql = """INSERT INTO notas (usuario_id, titulo, contenido) VALUES (%s, %s, %s) RETURNING id; """
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
    sql = """ SELECT id, titulo FROM notas WHERE usuario_id = %s AND carpeta_id IS NULL ORDER BY fecha_modificacion DESC, id DESC; """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (usuario_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def listar_notas_en_carpeta(carpeta_id: int):
    sql = """
    SELECT id, titulo
    FROM notas
    WHERE carpeta_id = %s
    ORDER BY fecha_modificacion DESC, id DESC;
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (carpeta_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def traer_nota(nota_id: int):
    sql = "SELECT titulo, contenido FROM notas WHERE id = %s;"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (nota_id,))
    row = cur.fetchone()
    cur.execute("UPDATE notas SET fecha_uso = NOW() WHERE id = %s;", (nota_id,))
    conn.commit()
    cur.close()
    conn.close()
    return (row[0], row[1]) if row else None

def actualizar_nota(nota_id: int, contenido: str):
    sql = """
    UPDATE notas
    SET contenido = %s, fecha_modificacion = NOW()
    WHERE id = %s;
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (contenido, nota_id))
    conn.commit()
    cur.close()
    conn.close()

def renombrar_note(nota_id: int, nuevo_titulo: str):
    sql = """
    UPDATE notas
    SET titulo = %s, fecha_modificacion = NOW()
    WHERE id = %s;
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (nuevo_titulo, nota_id))
    conn.commit()
    cur.close()
    conn.close()

def borrar_note(nota_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM notas WHERE id = %s;", (nota_id,))
    conn.commit()
    cur.close()
    conn.close()

def mover_nota(nota_id: int, carpeta_id: int):
    sql = """
    UPDATE notas
    SET carpeta_id = %s, fecha_modificacion = NOW()
    WHERE id = %s;
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (carpeta_id, nota_id))
    conn.commit()
    cur.close()
    conn.close()

def quitar_de_carpeta(nota_id: int):
    sql = """
    UPDATE notas
    SET carpeta_id = NULL, fecha_modificacion = NOW()
    WHERE id = %s;
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (nota_id,))
    conn.commit()
    cur.close()
    conn.close()

##### carpetas #####
def crear_carpeta(usuario_id: int, nombre: str) -> int:
    sql = """
    INSERT INTO carpetas (usuario_id, nombre)
    VALUES (%s, %s)
    RETURNING id;
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (usuario_id, nombre))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return new_id

def listar_carpetas(usuario_id: int):
    sql = """
    SELECT id, nombre
    FROM carpetas
    WHERE usuario_id = %s
    ORDER BY fecha_creacion DESC, id DESC;
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (usuario_id,))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def traer_carpeta(carpeta_id: int):
    sql = "SELECT nombre, fecha_creacion FROM carpetas WHERE id = %s;"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (carpeta_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return (row[0], row[1]) if row else None

def renombrar_carpeta(carpeta_id: int, nuevo_nombre: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE carpetas SET nombre = %s WHERE id = %s;", (nuevo_nombre, carpeta_id))
    conn.commit()
    cur.close()
    conn.close()

def borrar_carpeta(carpeta_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM carpetas WHERE id = %s;", (carpeta_id,))
    conn.commit()
    cur.close()
    conn.close()

##### dashboard #####
def obtener_ultimas_notas_creadas(usuario_id: int, limite: int = 4):
    sql = """
    SELECT id, titulo, fecha_creacion
    FROM notas
    WHERE usuario_id = %s
    ORDER BY fecha_creacion DESC
    LIMIT %s;
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (usuario_id, limite))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def obtener_ultimas_carpetas_creadas(usuario_id: int, limite: int = 4):
    sql = """
    SELECT id, nombre, fecha_creacion
    FROM carpetas
    WHERE usuario_id = %s
    ORDER BY fecha_creacion DESC
    LIMIT %s;
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (usuario_id, limite))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

def obtener_ultimas_notas_modificadas(usuario_id: int, limite: int = 4):
    sql = """
    SELECT id, titulo, fecha_modificacion
    FROM notas
    WHERE usuario_id = %s
    ORDER BY fecha_modificacion DESC
    LIMIT %s;
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, (usuario_id, limite))
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data