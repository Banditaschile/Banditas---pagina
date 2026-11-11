# Banditas Chile: página www.banditas.cl

Entrega del 9 de noviembre de 2026. Aquí está todo lo necesario para que la página quede en sus cuentas.

## Qué hay en esta carpeta

| Carpeta o archivo | Qué es |
|---|---|
| `pagina/` | La página completa, lista para publicar tal cual: 137 productos, fotos, video del showroom y las páginas Nosotras, Showroom y Ayuda. |
| `programa/` | El programa en Python que arma `pagina/` a partir del catálogo (`catalogo.csv`, `accesorios.csv`, `fotos.csv`). |
| `catalogos/` | El catálogo en el formato de Shopify (moderno y clásico) y de Jumpseller, por si algún día venden en línea. |
| `informe-final-banditas-2026-11-06.pdf` | El informe de lo hecho: Instagram, página, publicidad y showroom. |

## Publicar en Cloudflare (una sola vez)

1. En Cloudflare, entrar a **Workers y Pages → Crear → Pages → Subir recursos** (Upload assets).
2. Ponerle un nombre al proyecto (por ejemplo `banditas`) y arrastrar la carpeta `pagina` completa.
3. Revisar que la página se vea bien en la dirección de prueba que da Cloudflare (termina en `.pages.dev`).
4. En el proyecto, ir a **Dominios personalizados** y agregar `www.banditas.cl` y `banditas.cl`.
5. Cloudflare pide agregar el dominio a la cuenta y entrega dos servidores de nombre (nameservers).
6. En **NIC Chile**, con la cuenta de The Blond SPA, cambiar los servidores de nombre de banditas.cl por los dos que dio Cloudflare. El cambio tarda entre minutos y algunas horas.
7. Cuando www.banditas.cl ya se vea desde Cloudflare, avisarle a Javier para que saque el dominio de su cuenta de Vercel.

Hasta el paso 7 la página sigue funcionando desde la cuenta de Javier, así que no se cae en ningún momento.

**Contador de visitas:** en Cloudflare se activa desde el panel, en **Web Analytics**. No hay que tocar la página.

## Cambiar algo de la página

- **Cambios chicos** (un precio, un texto, un producto agotado): se pueden hacer directo en los archivos de `pagina/`. Cada producto es un archivo en `pagina/producto/`. Después se vuelve a subir la carpeta en Cloudflare, en **Crear nueva implementación**.
- **Cambios de catálogo** (productos nuevos, fotos nuevas, stock): se editan `programa/catalogo.csv` y `programa/fotos.csv`, se ponen las fotos en `pagina/img/` y se corre:

  ```
  cd programa
  python3 construir.py
  ```

  Eso rearma toda la carpeta `pagina/`. Necesita Python 3, que viene en los Mac.

- **Ojo:** dos programas buscan sus archivos en lugares fijos. `catalogo-desde-inventario.py` (pasa el Excel de control de ventas a `catalogo.csv`) busca el Excel con un nombre fijo en su misma carpeta. `preparar-fotos.py` y `fotos-desde-drive.py` (recortan y nombran las fotos) buscan las fotos en carpetas de descarga del computador donde se hicieron. Para usarlos hay que cambiar esos nombres y rutas por los de ustedes. Su Claude lo puede hacer si le pasan esta carpeta y le explican dónde quedan el Excel y las fotos.

## Datos que conviene tener a mano

- WhatsApp de la página: +56 9 4967 0353 (está en `programa/construir.py`, variable `WSP`).
- Dominio: banditas.cl, registrado en NIC Chile a nombre de The Blond SPA, pagado hasta el 12-10-2028.
- La página está en **modo vitrina**: cada prenda se pide por WhatsApp. Para volver al modo tienda con carro, se cambia `VITRINA = True` por `VITRINA = False` en `programa/construir.py`.

## Correos del boletín

El formulario "Enterarme de lo nuevo" guarda los correos en una planilla de Google, en la pestaña **Suscriptoras** (fecha, correo y página desde donde se inscribió). No guarda correos repetidos.

- El código que recibe los correos está en `programa/boletin-google-sheets.gs` y va pegado en la planilla (**Extensiones → Apps Script**).
- La dirección de esa aplicación web está en `programa/construir.py`, en la variable `BOLETIN_URL`, y también en `pagina/sitio.js`, en `DESTINO_BOLETIN`.
- Si esa dirección queda vacía, el formulario solo muestra el mensaje de gracias y no guarda nada.
