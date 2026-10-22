index.html

## La Biblia del Parrillero Peruano

Ebook de Carnes Delivery Premium (Dennis Castro), incluido en este repositorio:

- `biblia-del-parrillero-peruano.html` — fuente editable (diseño premium, para ver en navegador o re-exportar). **Este es el archivo maestro: edítalo a él, no a los PDF/EPUB directamente.**
- `biblia-del-parrillero-peruano.pdf` — versión maestra sin proteger, para revisión interna. **No es la que se entrega al cliente final.**
- `biblia-del-parrillero-peruano.epub` — versión para Apple Books y otros lectores EPUB (sin contraseña: el formato EPUB no tiene un cifrado estándar ampliamente soportado, a diferencia del PDF).

Cada capítulo incluye al final un bloque de **"Repaso del capítulo"**: un checklist de lo esencial más 3-4 preguntas abiertas con espacio para escribir a mano, pensado para que el cliente imprima el libro y lo use como cuaderno de trabajo junto a la parrilla.

### Entregar una copia personalizada y protegida a un cliente

El PDF maestro **no** tiene contraseña. Para cada venta, genera una copia individual, con marca de agua y contraseña propia, usando el script incluido:

```bash
python3 -m pip install -r requirements-generador.txt   # una sola vez
python3 generar_copia_personalizada.py --nombre "Nombre del cliente" --email "correo@cliente.com"
```

Esto crea, dentro de `entregas/` (carpeta ignorada por git — nunca se sube al repo):
- `biblia-del-parrillero-peruano_<nombre-del-cliente>.pdf` — el PDF a entregar, con una marca de agua discreta con el nombre del comprador en cada página y cifrado AES-256 real (lo pide cualquier lector de PDF al abrirlo, no es una pantalla simulada).
- `registro_contrasenas.csv` — registro local de qué cliente recibió qué contraseña, para poder reenviarla si la pierde.

Envía el PDF y la contraseña por canales separados (por ejemplo, el archivo por correo y la contraseña por WhatsApp).

Para regenerar el `.pdf`/`.epub` maestros tras editar el `.html`, ver los comandos usados en el historial de commits de este archivo (Chromium headless `--print-to-pdf` y `pandoc ... -t epub3`).
