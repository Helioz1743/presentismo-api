import sqlite3

DB = "presentismo.db"

def crear_bd():

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencias (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nombre TEXT,
            fecha TEXT,
            hora TEXT,
            ubicacion TEXT,
            foto TEXT

        )
    """)

    conn.commit()
    conn.close()