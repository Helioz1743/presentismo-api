from fastapi import FastAPI, UploadFile, File, Form
from openpyxl import Workbook, load_workbook
from openpyxl.drawing.image import Image
import os
from database import crear_bd
import sqlite3


app = FastAPI()
crear_bd()

ARCHIVO = "presentismo.xlsx"
CARPETA_FOTOS = "fotos"

os.makedirs(CARPETA_FOTOS, exist_ok=True)


def crear_excel():

    if not os.path.exists(ARCHIVO):

        wb = Workbook()
        ws = wb.active

        ws.append([
            "Nombre",
            "Fecha",
            "Hora",
            "Ubicacion",
            "NombreArchivo",
            "Foto"
        ])

        wb.save(ARCHIVO)


@app.post("/registrar")
async def registrar(
    nombre: str = Form(...),
    fecha: str = Form(...),
    hora: str = Form(...),
    ubicacion: str = Form(...),
    foto: UploadFile = File(...)
):

    crear_excel()

    nombre_archivo = foto.filename

    ruta_foto = os.path.join(
        CARPETA_FOTOS,
        nombre_archivo
    )

    contenido = await foto.read()

    with open(ruta_foto, "wb") as f:
        f.write(contenido)

    # ========= SQLITE =========

    conn = sqlite3.connect("presentismo.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO asistencias
        (
            nombre,
            fecha,
            hora,
            ubicacion,
            foto
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            nombre,
            fecha,
            hora,
            ubicacion,
            nombre_archivo
        )
    )

    conn.commit()
    conn.close()

    # ========= EXCEL =========

    wb = load_workbook(ARCHIVO)
    ws = wb.active

    ws.append([
        nombre,
        fecha,
        hora,
        ubicacion,
        nombre_archivo,
        ""
    ])

    fila_actual = ws.max_row

    try:

        img = Image(ruta_foto)

        img.width = 80
        img.height = 80

        ws.add_image(
            img,
            f"F{fila_actual}"
        )

        ws.row_dimensions[fila_actual].height = 65

    except Exception as e:

        print("Error al insertar imagen:")
        print(e)

    wb.save(ARCHIVO)

    return {
        "mensaje": "Registro guardado"
    }
@app.get("/historial")
def historial():

    crear_excel()

    wb = load_workbook(ARCHIVO)
    ws = wb.active

    registros = []

    for fila in ws.iter_rows(min_row=2, values_only=True):

        registros.append({
            "nombre": fila[0],
            "fecha": fila[1],
            "hora": fila[2],
            "ubicacion": fila[3],
            "foto": fila[4]
        })

    return registros