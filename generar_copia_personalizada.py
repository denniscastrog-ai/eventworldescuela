#!/usr/bin/env python3
"""
Genera una copia personalizada y protegida del ebook "La Biblia del
Parrillero Peruano" para un cliente de Carnes Delivery Premium.

Qué hace, por cada venta:
  1. Toma el PDF maestro (biblia-del-parrillero-peruano.pdf) ya generado
     desde el HTML fuente.
  2. Le agrega una marca de agua discreta en cada página con el nombre
     del comprador, para que la copia quede identificable como suya.
  3. La protege con una contraseña ÚNICA generada para esa venta
     (cifrado AES-256, el estándar real que usan Adobe Reader, Vista
     previa de macOS, etc. — no es una pantalla de "login" simulada).
  4. Guarda un registro local (entregas/registro_contrasenas.csv) con
     quién recibió qué copia y con qué contraseña, para que puedas
     reenviarla si el cliente la pierde.

No protege el .html ni el .epub: esos formatos no tienen un mecanismo
de cifrado por contraseña ampliamente soportado (a diferencia del PDF,
que sí lo tiene como parte del estándar). Por eso el archivo que se
entrega al cliente final debe ser el PDF que genera este script, no el
.html/.epub "maestro" del repositorio.

Requisitos (una sola vez):
    python3 -m pip install -r requirements-generador.txt

Uso:
    python3 generar_copia_personalizada.py --nombre "Ana Torres" --email ana@correo.com

Opcional:
    --origen   ruta al PDF maestro (por defecto biblia-del-parrillero-peruano.pdf)
    --salida   carpeta de salida para el PDF generado (por defecto entregas/)
"""

import argparse
import csv
import datetime
import os
import secrets
import sys
import unicodedata

try:
    from pypdf import PdfReader, PdfWriter
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
except ImportError:
    print(
        "Faltan dependencias. Instálalas con:\n"
        "    python3 -m pip install -r requirements-generador.txt",
        file=sys.stderr,
    )
    sys.exit(1)

PALABRAS_CLAVE = [
    "PICANA", "TOMAHAWK", "ENTRANA", "COWBOY", "PARRILLERO",
    "BRASA", "ASADO", "CARBON", "COSTILLA", "CHIMICHURRI",
]


def generar_password() -> str:
    palabra = secrets.choice(PALABRAS_CLAVE)
    numero = secrets.randbelow(9000) + 1000  # 4 dígitos, 1000-9999
    return f"{palabra}{numero}"


def slug(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = texto.lower().strip()
    out = []
    for ch in texto:
        if ch.isalnum():
            out.append(ch)
        elif ch in (" ", "-", "_"):
            out.append("-")
    slug_resultado = "".join(out)
    while "--" in slug_resultado:
        slug_resultado = slug_resultado.replace("--", "-")
    return slug_resultado.strip("-") or "cliente"


def crear_marca_de_agua(page_width: float, page_height: float, nombre: str) -> "canvas.Canvas":
    import io
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(page_width, page_height))
    c.saveState()
    c.setFillColorRGB(0.79, 0.64, 0.15)  # dorado, igual al --gold del diseño
    c.setFillAlpha(0.55)
    c.setFont("Helvetica", 7)
    texto = f"Ejemplar personal de {nombre} · Carnes Delivery Premium · no autorizado para redistribución"
    c.translate(page_width / 2, 14)
    c.drawCentredString(0, 0, texto)
    c.restoreState()
    c.showPage()
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--nombre", required=True, help="Nombre completo del comprador")
    parser.add_argument("--email", default="", help="Correo del comprador (opcional, solo para el registro)")
    parser.add_argument("--origen", default="biblia-del-parrillero-peruano.pdf", help="PDF maestro de origen")
    parser.add_argument("--salida", default="entregas", help="Carpeta donde guardar la copia generada")
    args = parser.parse_args()

    if not os.path.isfile(args.origen):
        print(f"No encuentro el PDF maestro: {args.origen}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.salida, exist_ok=True)

    reader = PdfReader(args.origen)
    writer = PdfWriter()

    for page in reader.pages:
        box = page.mediabox
        watermark_page = crear_marca_de_agua(float(box.width), float(box.height), args.nombre)
        page.merge_page(watermark_page)
        writer.add_page(page)

    writer.add_metadata({
        "/Title": "La Biblia del Parrillero Peruano",
        "/Author": "Dennis Castro — Carnes Delivery Premium",
        "/Subject": f"Ejemplar personal de {args.nombre}",
    })

    password = generar_password()
    writer.encrypt(user_password=password, owner_password=secrets.token_hex(8), algorithm="AES-256")

    nombre_archivo = f"biblia-del-parrillero-peruano_{slug(args.nombre)}.pdf"
    ruta_salida = os.path.join(args.salida, nombre_archivo)
    with open(ruta_salida, "wb") as f:
        writer.write(f)

    registro = os.path.join(args.salida, "registro_contrasenas.csv")
    existe = os.path.isfile(registro)
    with open(registro, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not existe:
            w.writerow(["fecha", "nombre", "email", "contraseña", "archivo"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"), args.nombre, args.email, password, nombre_archivo])

    print(f"Copia generada: {ruta_salida}")
    print(f"Contraseña única: {password}")
    print(f"Registro actualizado en: {registro}")
    print("\nRecomendación: envía el archivo y la contraseña por canales distintos")
    print("(por ejemplo, el PDF por correo y la contraseña por WhatsApp).")


if __name__ == "__main__":
    main()
