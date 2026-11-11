#!/usr/bin/env python3
"""Construye el prototipo estático de Banditas Chile en ./sitio a partir de catalogo.csv.
Uso: python3 construir.py
"""
import csv, pathlib, html, re
from urllib.parse import quote

AQUI = pathlib.Path(__file__).parent
SITIO = AQUI.parent / 'pagina'
CATALOGO = AQUI / 'catalogo.csv'
WSP = '56949670353'
WSP_VISIBLE = '+56 9 4967 0353'

FOTOS_CSV = AQUI / 'fotos.csv'

def fotos_de(handle):
    import csv as _csv
    try:
        return [r['archivo_web'] for r in _csv.DictReader(open(FOTOS_CSV, encoding='utf-8')) if r['handle'] == handle]
    except FileNotFoundError:
        return []

CATEGORIAS_BASE = ['Vestidos', 'Enteritos', 'Camisas y blusas', 'Poleras y polerones', 'Jeans y pantalones', 'Faldas y bermudas', 'Chaquetas y chalecos', 'Accesorios']
CATEGORIAS = CATEGORIAS_BASE[:-1]   # se recalcula en main(): solo las categorías con productos publicables
FOTO_CATEGORIA = {'Vestidos': 'tile-vestidos-1.jpg', 'Enteritos': 'tile-enteritos-1.jpg', 'Camisas y blusas': 'tile-camisas-1.jpg', 'Poleras y polerones': 'tile-poleras-1.jpg',
                  'Jeans y pantalones': 'tile-jeans-1.jpg', 'Faldas y bermudas': 'tile-faldas-1.jpg', 'Accesorios': 'tile-accesorios-1.jpg', 'Chaquetas y chalecos': 'tile-chaquetas-1.jpg'}

def e(s): return html.escape(str(s), quote=True)

def slug(s):
    import unicodedata, re
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

def clp(v):
    return '$' + f'{int(float(v)):,}'.replace(',', '.') if v else ''

def stock_por_talla(p):
    return {k: int(v) for k, v in (x.split(':') for x in (p.get('stock') or '').split('|') if ':' in x)}

ORDEN_TALLAS = ['XS', 'S', 'M', 'L', 'XL', 'TU']
ETIQUETA_TALLA = {'S': 'S (36)', 'M': 'M (38)', 'TU': 'Talla única'}
UNIR_COLOR = {'Rosa': 'Rosado', 'Jeans claro': 'Jeans', 'Café claro': 'Café', 'Calipso': 'Celeste'}

def tallas_disponibles(p):
    st = stock_por_talla(p)
    if not st: return ['TU'] if (p.get('tallas') or '').strip() == 'TU' else []
    return [t for t, n in st.items() if n > 0]

def colores_de(p):
    """'Blanco / Celeste' o 'Café claro y celeste' -> ['Blanco', 'Celeste']; para el filtro de color de /todo."""
    out = []
    for x in re.split(r'/| y |,', p.get('colores') or ''):
        x = x.strip().capitalize()
        if x and x != 'Varios colores': x = UNIR_COLOR.get(x, x); out += [x] if x not in out else []
    return out

def tallas_texto(p):
    st = stock_por_talla(p)
    if not st: return 'Talla única' if (p.get('tallas') or '').strip() == 'TU' else 'Tallas por confirmar'
    if sum(st.values()) == 0: return 'Agotado'
    if list(st) == ['TU']:
        n = st['TU']
        if n > 3: return 'Talla única'
        return f"Talla única · {'queda 1' if n == 1 else f'quedan {n}'}"
    con = [t for t, n in st.items() if n > 0]
    return ('Talla ' if len(con) == 1 else 'Tallas ') + ', '.join(con)

def leer_catalogo():
    filas = list(csv.DictReader(open(CATALOGO, encoding='utf-8')))
    filas = [f for f in filas if f.get('precio_clp') and f.get('estado') != 'incompleto']   # sin precio o sin stock definido no se publica (accesorios a medio llenar)
    for f in filas: f['fotos'] = [x for x in (f.get('imagenes') or '').split(',') if x]
    return [f for f in filas if f['fotos']]   # sin foto no se muestra (Mintaka, Mirach, Aros Circle): nada de 'foto pendiente' a la vista

ICONO_LUPA = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
ICONO_WSP = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20l1.3-3.8A8 8 0 1 1 8 19.1z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 1a4 4 0 0 1-2-2l1-1-1-2z"/></svg>'
# Vitrina (15-10): mientras Banditas no decida vender online, la página muestra y el pedido se cierra por WhatsApp.
# Para volver a modo tienda (bolsa y carro, p. ej. al pasar a Shopify) basta con poner VITRINA = False.
VITRINA = True
ICONO_BOLSA = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8h12l-1 12H7z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>'
ICONO_IG = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="4.5"/><circle cx="12" cy="12" r="3.6"/><circle cx="16.9" cy="7.1" r=".6"/></svg>'
ICONO_MENU = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
DOMINIO = 'https://www.banditas.cl'
CINTA = ''.join(f'<span>{t}</span>' for t in ['Boho-chic con una vena rock', 'Lino, algodón y jeans', 'Diseñado en Marsella, hecho en Italia', 'Pocas unidades por modelo', 'Tallas XS a XL y talla única', 'Envío a todo Chile'])
ANILLO = '<svg class="anillo" viewBox="0 0 100 100" aria-hidden="true"><circle class="a2" cx="50" cy="50" r="38"/><circle class="a1" cx="50" cy="50" r="48"/></svg>'

def cabecera(actual=''):
    def nav(href, texto, extra=''):
        cur = ' aria-current="page"' if href == actual else ''
        return f'<a href="{href}"{cur}{extra}>{texto}</a>'
    enlaces = [nav('/todo', 'Lo nuevo', ' class="destacado"')]
    enlaces += [nav('/todo#' + slug(c), c) for c in CATEGORIAS]
    enlaces.append(nav('/showroom', 'Showroom'))
    return f'''
<div class="aviso" aria-label="Avisos"><div class="aviso-pista"><span>Traído de Marsella <b>·</b> stock en Chile</span><span>Showroom en Santiago <b>·</b> próxima fecha pronto</span><span>Atención por WhatsApp <b>·</b> {WSP_VISIBLE}</span><span aria-hidden="true">Traído de Marsella <b>·</b> stock en Chile</span></div></div>
<header class="cabecera">
  <div class="wrap cabecera-fila">
    <details class="menu">
      <summary><span class="icono" aria-label="Menú">{ICONO_MENU}</span></summary>
    </details>
    <nav class="nav" aria-label="Categorías">{''.join(enlaces)}</nav>
    <a class="logo" href="/" aria-label="Banditas Chile, from Marseilles · inicio">
      <img class="logo-anillos" src="/img/logo-anillos.png" alt="" width="785" height="600">
      <img class="logo-texto" src="/img/logo-texto.png" alt="Banditas Chile, from Marseilles" width="785" height="600">
      <img class="logo-calavera" src="/img/logo-calavera.png" alt="" width="785" height="600">
    </a>
    <div class="iconos">
      <button class="icono" type="button" aria-label="Buscar">{ICONO_LUPA}</button>
      <a class="icono" href="https://www.instagram.com/banditaschile/" aria-label="Instagram @banditaschile">{ICONO_IG}</a>
      <a class="icono" href="https://wa.me/{WSP}" aria-label="WhatsApp">{ICONO_WSP}</a>
      {'' if VITRINA else f'<a class="icono" href="#" aria-label="Bolsa" id="bolsa">{ICONO_BOLSA}<span class="cuenta" id="bolsa-cuenta" hidden>0</span></a>'}
    </div>
  </div>
</header>'''

PIE = f'''
<footer class="pie">
  <div class="wrap">
    <div class="cols">
      <div><h3>Ayuda</h3><ul><li><a href="/ayuda#cambios">Cambios y devoluciones</a></li><li><a href="/ayuda#despacho">Despacho y retiro</a></li><li><a href="/ayuda#tallas">Guía de tallas</a></li><li><a href="/ayuda#contacto">Contacto</a></li></ul></div>
      <div><h3>Tienda</h3><ul>{''.join(f'<li><a href="/todo#{slug(c)}">{c}</a></li>' for c in CATEGORIAS)}</ul></div>
      <div><h3>Banditas</h3><ul><li><a href="/nosotras">Nosotras</a></li><li><a href="/showroom">Showroom</a></li><li><a href="https://www.instagram.com/banditaschile/">Instagram @banditaschile</a></li><li>WhatsApp {WSP_VISIBLE}</li><li><a href="mailto:banditaschile@gmail.com">banditaschile@gmail.com</a></li></ul></div>
      <div><h3>Legal</h3><ul><li><a href="/ayuda#privacidad">Privacidad</a></li><li><a href="/ayuda#terminos">Términos</a></li></ul></div>
    </div>
    <div class="legal"><span><b>Banditas Chile</b> · desde Marsella</span><span>Precios en pesos chilenos, IVA incluido</span><span>© 2026 Banditas Chile</span></div>
  </div>
</footer>
<script src="/sitio.js" defer></script>'''

# Contador de visitas: en Cloudflare se activa desde el panel (Web Analytics), sin tocar este programa.
def documento(titulo, cuerpo, actual='', descripcion='', clase=''):
    return f'''<!doctype html>
<html lang="es-CL">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(titulo)}</title>
<meta name="description" content="{e(descripcion)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Banditas Chile">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descripcion)}">
<meta property="og:image" content="{DOMINIO}/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="es_CL">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;500&family=Lora:ital,wght@1,400&display=swap">
<link rel="stylesheet" href="/estilos.css">
<script>window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};</script>
</head>
<body class="{clase}">
{cabecera(actual)}
<main>
{cuerpo}
</main>
{PIE}
</body>
</html>
'''

def tarjeta(p, lazy=True):
    fotos = p.get('fotos') or []
    nombre = e(p['nombre_web'])
    if fotos:
        foto = f'<img src="/img/{fotos[0]}" alt="{nombre}" width="675" height="900"{" loading=\"lazy\"" if lazy else ""}>'
        if len(fotos) > 1:
            foto += f'<img class="alt" src="/img/{fotos[1]}" alt="" width="675" height="900" loading="lazy">'
    else:
        foto = '<span class="pendiente">Foto pendiente</span>'
    precio = f'<span class="precio">{clp(p["precio_clp"])}</span>' if p['precio_clp'] else '<span class="precio por-confirmar">Precio por confirmar</span>'
    detalle = tallas_texto(p)
    if p.get('colores') and '/' in p['colores'] and detalle.startswith('Talla'): detalle += ' · ' + e(p['colores'])
    href = '/producto/' + p['handle']
    return f'''<a class="ficha revela" href="{href}" data-categoria="{e(p['categoria_web'])}" data-tallas="{' '.join(tallas_disponibles(p))}" data-colores="{e('|'.join(colores_de(p)))}" data-precio="{p['precio_clp'] or 0}">
  <div class="ficha-foto">{foto}</div>
  <span class="ficha-tipo">{e(p['categoria_web'])}</span><h3>{nombre}</h3>
  {precio}<span class="tallas">{detalle}</span>
</a>'''

# ---------------- portada ----------------
def portada(productos):
    por_handle = {p['handle']: p for p in productos}
    destacados = ['vestido-de-jeans-parione', 'chaqueta-solana', 'polera-ridge', 'vestido-largo-monclaire',
                  'jardinera-de-jeans-materdei', 'camisa-a-rayas-opener', 'falda-de-jeans-collatino', 'vestido-tunica-iron-fist']
    tiles = ''
    for c in CATEGORIAS:
        f = FOTO_CATEGORIA.get(c)
        img = f'<img src="/img/{f}" alt="" width="675" height="900" loading="lazy">' if f else '<span class="pendiente">foto por elegir</span>'
        tiles += f'<a class="tile revela" href="/todo#{slug(c)}">{img}<span class="tile-nombre">{c}</span></a>'
    cuerpo = f'''
  <section class="wrap hero" aria-labelledby="titulo">
    <div class="hero-foto hero-pila" aria-label="Fotos de la colección">
      <img src="/img/hero-1-1.jpg" alt="Polera French y jeans anchos, saludando" width="900" height="1200" fetchpriority="high">
      <img src="/img/hero-2-1.jpg" alt="Musculosa de lino y bermudas de jeans con crochet" width="900" height="1200" loading="lazy">
      <img src="/img/hero-3-1.jpg" alt="Jardinera de jeans, sentada en un tarro de zinc" width="900" height="1200" loading="lazy">
      <img src="/img/hero-4-1.jpg" alt="Polera con estrella, en estudio" width="900" height="1200" loading="lazy">
    </div>
    <div class="hero-texto">
      {ANILLO}
      <p class="rotulo">Diseñado en Marsella · Hecho en Italia</p>
      <h1 id="titulo">Básicas con estilo. Básicas con actitud.</h1>
      <p>Lino, algodón y color para todos los días. Una marca que solo se vende en Europa y que nosotras trajimos a Chile: pocas unidades por modelo, auténticas y exclusivas para ti.</p>
      <a class="btn" href="/todo">Ver la colección</a>
    </div>
  </section>
  <div class="cinta" aria-hidden="true"><div class="cinta-pista">{CINTA}{CINTA}</div></div>
  <section class="wrap seccion" id="recien" aria-labelledby="t-recien">
    <div class="cabeza-seccion"><h2 id="t-recien">Lo nuevo</h2><a href="/todo">Ver los {len(productos)} productos</a></div>
    <div class="grilla">{''.join(tarjeta(por_handle[h]) for h in destacados)}</div>
  </section>
  <section class="wrap seccion" id="categorias" aria-labelledby="t-cat">
    <div class="cabeza-seccion"><h2 id="t-cat">¿Qué buscas?</h2><a href="/todo">Ver todo</a></div>
    <div class="tiles tiles-tira">{tiles}</div>
  </section>
  <section class="confianza revela" aria-label="Cómo compramos">
    <ul class="wrap">
      <li><strong>Traído de Marsella</strong><span>Stock en Chile, sin esperas de aduana.</span></li>
      <li><strong>Entrega a todo Chile</strong><span>Retiro en el showroom o envío, por WhatsApp.</span></li>
      <li><strong>Cambio por talla</strong><span>Plazo por confirmar.</span></li>
      <li><strong>{'Pedidos por WhatsApp' if VITRINA else 'Atención por WhatsApp'}</strong><span>{WSP_VISIBLE}</span></li>
    </ul>
  </section>
  <section class="wrap seccion" id="showroom" aria-labelledby="t-show">
    <div class="showroom revela">
      <div class="showroom-foto showroom-video">
        <video poster="/img/showroom-video.jpg" muted loop playsinline autoplay preload="metadata" aria-label="Las dos amigas de Banditas riéndose en el showroom de octubre"><source src="/video/showroom.mp4" type="video/mp4"></video>
      </div>
      <div class="showroom-texto">
        <p class="rotulo">Showroom</p>
        <h2 id="t-show">Próximo showroom</h2>
        <p><strong>Jueves 5 y viernes 6 de noviembre</strong> en The Beauty Place, Paseo La Cruz, Lo Barnechea. Jueves de 17:00 a 22:00 y viernes de 11:00 a 20:00. Para probarse las prendas y llevárselas al tiro.</p>
        <a class="btn btn-linea" href="/showroom">Ver dirección y horario</a>
      </div>
    </div>
  </section>
  <section class="wrap seccion nosotras revela" aria-labelledby="t-nos">
    <p class="rotulo" id="t-nos">Nosotras</p>
    <p class="frase">Dos amigas de la vida que se enamoraron de una marca de Marsella: su calidad, su tela y su calce. Banditas vende en Europa; en Chile la encuentras a través de Banditas Chile.</p>
    <a class="enlace" href="/nosotras">Conocer a Banditas</a>
  </section>
  {boletin()}'''
    return documento('Banditas Chile · ropa femenina desde Marsella', cuerpo, '/', 'Ropa femenina básica, con estilo y pocas unidades por modelo. Traída de Marsella, con stock en Chile. Online y en showrooms.', clase='inicio')

def boletin(titulo='Enterarme de lo nuevo', texto='Lo que llega de Marsella y la fecha del próximo showroom. Un correo al mes, nada más.', boton='Quiero enterarme', gracias='Listo. Te escribimos cuando llegue lo nuevo.'):
    return f'''
  <section class="wrap seccion boletin revela" id="boletin" aria-labelledby="t-bol">
    <h2 id="t-bol">{titulo}</h2>
    <p>{texto}</p>
    <form id="form-boletin">
      <label for="correo">Tu correo<input id="correo" type="email" name="correo" required autocomplete="email" placeholder="nombre@correo.cl"></label>
      <label class="consentir"><input type="checkbox" name="consentimiento" required> Acepto que Banditas Chile guarde mi correo para mandarme estos avisos.</label>
      <button class="btn" type="submit">{boton}</button>
    </form>
    <p class="nota">Usamos tu correo solo para estos avisos. Te puedes salir con un clic en cualquier correo. <a class="enlace" href="/ayuda#privacidad" style="text-transform:none;letter-spacing:0;font-size:inherit">Cómo cuidamos tus datos</a>.</p>
    <p class="gracias" id="gracias" hidden>{gracias}</p>
  </section>'''

# ---------------- categoría / todo ----------------
def pagina_todo(productos):
    chips = '<a class="chip" href="/todo" aria-current="true">Todo</a>' + ''.join(f'<a class="chip" href="/todo#{slug(c)}" data-cat="{e(c)}">{c}</a>' for c in CATEGORIAS)
    filtros_cat = ''.join(f'<label><input type="checkbox" name="cat" value="{e(c)}"> {c}</label>' for c in CATEGORIAS)
    # 20-10: talla y color salen de los productos publicados (antes eran opciones fijas sin efecto)
    hay_t = {t for p in productos for t in tallas_disponibles(p)}
    filtros_talla = ''.join(f'<label><input type="checkbox" name="talla" value="{t}"> {ETIQUETA_TALLA.get(t, t)}</label>' for t in ORDEN_TALLAS if t in hay_t)
    cuenta_c = {}
    for p in productos:
        for c in colores_de(p): cuenta_c[c] = cuenta_c.get(c, 0) + 1
    filtros_color = ''.join(f'<label><input type="checkbox" name="color" value="{e(c)}"> {c}</label>' for c, n in sorted(cuenta_c.items(), key=lambda x: (-x[1], x[0])) if n >= 2)
    cuerpo = f'''
  <div class="wrap">
    <nav class="migas" aria-label="Estás en"><a href="/">Inicio</a><span>/</span><span aria-current="page">Todo</span></nav>
    <div class="cat-cabeza"><h1 id="cat-titulo">Todo</h1><span class="nota" id="cat-cuenta">{len(productos)} productos</span></div>
    <div class="chips" id="chips">{chips}</div>
    <div class="herramientas">
      <details class="filtro"><summary>Talla</summary><div class="filtro-panel">{filtros_talla}</div></details>
      <details class="filtro"><summary>Color</summary><div class="filtro-panel">{filtros_color}</div></details>
      <details class="filtro"><summary>Categoría</summary><div class="filtro-panel">{filtros_cat}</div></details>
      <label class="orden">Ordenar <select id="orden"><option value="nuevo">Lo nuevo primero</option><option value="menor">Precio: menor a mayor</option><option value="mayor">Precio: mayor a menor</option></select></label>
    </div>
    <div class="grilla" id="grilla">{''.join(tarjeta(p) for p in productos)}</div>
    <p class="nota" id="vacio" hidden style="padding-block:32px">No hay productos con esos filtros. Prueba quitando alguno.</p>
  </div>
  {boletin()}'''
    return documento('Todo · Banditas Chile', cuerpo, '/todo', f'Los {len(productos)} productos de Banditas Chile: vestidos, enteritos, camisas, poleras, jeans, faldas y chaquetas.')

# ---------------- ficha ----------------
def pagina_producto(p, productos):
    """Ficha de una prenda: todas sus fotos, descripción, colores y tallas con su stock. Una página por producto en /producto/<handle>."""
    nombre = e(p['nombre_web']); cat = p['categoria_web']; es_acc = cat == 'Accesorios'
    fotos = p['fotos']; st = stock_por_talla(p); total = sum(st.values()) if st else None
    agotado = total == 0
    figuras = ''.join(
        f'<figure id="foto-{i}"><img src="/img/{f}" alt="{nombre}, foto {i} de {len(fotos)}" width="675" height="900"'
        f'{" fetchpriority=\"high\"" if i == 1 else " loading=\"lazy\""}><figcaption>Foto {i}</figcaption></figure>'
        for i, f in enumerate(fotos, 1))
    minis = '' if len(fotos) < 2 else '<div class="miniaturas" aria-label="Fotos">' + ''.join(
        f'<a href="#foto-{i}"><img src="/img/{f}" alt="Ver foto {i}" width="56" height="75" loading="lazy"></a>' for i, f in enumerate(fotos, 1)) + '</div>'
    # tallas: una opción por talla del inventario; las que están en 0 se ven tachadas y no se pueden elegir
    tallas = list(st) if st else ['TU']
    primera = next((t for t in tallas if st.get(t, 1) > 0), None) if st else 'TU'
    opciones = ''
    for t in tallas:
        n = st.get(t) if st else None
        sin = n == 0
        etiqueta = 'Talla única' if t == 'TU' else t
        pista = '<small>agotada</small>' if sin else ('<small>corte oversize</small>' if t == 'TU' and not es_acc else '')
        opciones += (f'<label class="swatch talla"><input type="radio" name="talla" value="{t}"'
                     f'{" checked" if t == primera else ""}{" disabled" if sin else ""}>{etiqueta}{pista}</label>')
    quedan = ''
    if total and total <= 3:
        quedan = f'<p class="nota">{"Queda 1 unidad" if total == 1 else f"Quedan {total} unidades"}.</p>'
    colores = [c.strip() for c in (p.get('colores') or '').split('/') if c.strip()]
    linea_colores = f'<p class="nota">{"Colores" if len(colores) > 1 else "Color"}: {e(", ".join(colores))}.</p>' if colores else ''
    msg = e(f'Hola, quiero preguntar por {p["nombre_web"]} ({p["sku"]})')
    if VITRINA:
        # el botón principal abre WhatsApp con el pedido escrito; el JS le agrega la talla elegida
        base = f'Hola, quiero pedir {p["nombre_web"]} ({p["sku"]}), {clp(p["precio_clp"])}.'
        t0 = '' if not primera else (' Talla: ' + ('única' if primera == 'TU' else primera) + '.')
        if agotado:
            boton = f'<a class="btn btn-ancho" href="https://wa.me/{WSP}?text={quote("Hola, me avisan si vuelve " + p["nombre_web"] + " (" + p["sku"] + ")?")}">{ICONO_WSP} Avisarme si vuelve</a>'
        else:
            boton = (f'<a class="btn btn-ancho pedir" id="pedir" data-base="{e(base)}" href="https://wa.me/{WSP}?text={quote(base + t0)}">'
                     f'{ICONO_WSP} Pedir por WhatsApp</a>')
        texto_wsp = ''
    else:
        boton = ('<button class="btn btn-ancho" type="button" disabled>Agotado</button>' if agotado
                 else '<button class="btn btn-ancho" type="submit">Agregar a la bolsa</button>')
        texto_wsp = 'Preguntar si vuelve' if agotado else 'Preguntar por WhatsApp'
    guia = '' if es_acc else '<a href="/ayuda#tallas">Guía de tallas</a>'
    # 16-10 (reunión con Valerie): sin 'Composición y cuidado'; las etiquetas no traen la composición
    otros = [x for x in productos if x['categoria_web'] == cat and x['handle'] != p['handle']]
    otros.sort(key=lambda x: (sum(stock_por_talla(x).values()) == 0 if stock_por_talla(x) else False))
    relacionados = otros[:4]
    rel = '' if not relacionados else f'''
  <section class="wrap seccion" aria-labelledby="t-rel">
    <div class="cabeza-seccion"><h2 id="t-rel">También te puede gustar</h2><a href="/todo#{slug(cat)}">Más {e(cat.lower())}</a></div>
    <div class="grilla">{''.join(tarjeta(x) for x in relacionados)}</div>
  </section>'''
    cuerpo = f'''
  <div class="wrap">
    <nav class="migas" aria-label="Estás en"><a href="/">Inicio</a><span>/</span><a href="/todo#{slug(cat)}">{e(cat)}</a><span>/</span><span aria-current="page">{nombre}</span></nav>
    <article class="producto">
      <div>
        <div class="galeria" id="galeria">{figuras}</div>
        {minis}
      </div>
      <form class="compra" id="form-compra">
        <div>
          <p class="rotulo">{e(cat)} · {e(p['sku'])}</p>
          <h1>{nombre}</h1>
        </div>
        <p class="precio-grande">{ANILLO}{clp(p['precio_clp'])}<small>IVA incluido</small></p>
        {linea_colores}
        <fieldset class="opcion" style="border:0;padding:0;margin:0">
          <div class="opcion-cabeza"><legend class="rotulo">Talla</legend>{guia}</div>
          <div class="swatches">{opciones}</div>
          {quedan}
        </fieldset>
        <div class="acciones">
          {boton}
          {f'<a class="wsp" href="https://wa.me/{WSP}?text={msg}">{ICONO_WSP} {texto_wsp}</a>' if texto_wsp else '<p class="nota">Te respondemos por WhatsApp para confirmar stock y coordinar la entrega de tu producto.</p>'}
        </div>
        <p class="descripcion">{e(p['descripcion'])}</p>
        <div class="plegables">
          <details><summary>Entrega</summary><div class="cuerpo"><p>Coordinamos la entrega por WhatsApp: retiro en el showroom o envío a todo Chile. El costo y el plazo del envío te los confirmamos al coordinar.</p></div></details>
          <details><summary>Cambios</summary><div class="cuerpo"><p>Cambio por talla o color, sujeto a stock, con la prenda sin uso y con etiquetas. Plazo por confirmar. <a href="/ayuda#cambios">Ver la política completa</a>.</p></div></details>
        </div>
      </form>
    </article>
  </div>
  <dialog class="luz" id="luz" aria-label="Foto ampliada"><button class="cerrar" type="button" aria-label="Cerrar" id="luz-cerrar">×</button><img id="luz-img" alt="" width="675" height="900"></dialog>{rel}'''
    desc = f"{p['descripcion']} {clp(p['precio_clp'])}, IVA incluido."
    return documento(f'{p["nombre_web"]} · Banditas Chile', cuerpo, '', desc)

def pagina_producto_redirige():
    """/producto?p=<handle> (enlaces viejos, hoja vista) → /producto/<handle>."""
    cuerpo = '''
  <div class="wrap seccion">
    <p>Buscando la prenda… Si no carga, <a href="/todo">mira toda la colección</a>.</p>
  </div>
  <script>(function(){var h=new URLSearchParams(location.search).get('p');location.replace(h?'/producto/'+encodeURIComponent(h):'/todo');})();</script>'''
    return documento('Banditas Chile', cuerpo, '', 'Ropa femenina desde Marsella.')

# ---------------- páginas de texto ----------------
def pagina_nosotras():
    cuerpo = '''
  <div class="wrap">
    <nav class="migas" aria-label="Estás en"><a href="/">Inicio</a><span>/</span><span aria-current="page">Nosotras</span></nav>
    <div class="pagina">
      <div class="pagina-cuerpo">
        <p class="rotulo">Nosotras</p>
        <h1>Dos amigas y una marca de Marsella</h1>
        <p class="frase">Una ingeniera comercial y una relacionadora pública, con estilos parecidos y mucho amor por la moda.</p>
        <p>Conocimos Banditas y nos enamoramos de su tela, su calidad y su calce. Banditas vende en Europa; en Chile la encuentras a través de Banditas Chile.</p>
        <p>Vendemos online y, una vez al mes, en un showroom de tres días en algún lugar con onda de Santiago. Te pruebas todo y te lo llevas al tiro.</p>
        <h2>Sobre Banditas</h2>
        <p>Nació en Marsella en 2018. Diseño francés, confección italiana y una calavera como emblema. Su estilo es boho-chic con un toque de rock clásico: urbano, despreocupado y con un sello de elegancia. La colección se renueva cada pocas semanas.</p>
        <h2>Básicas con estilo. Básicas con actitud.</h2>
        <p>Cortes amplios y talla única, pensados para una caída fluida y la comodidad. Un oversize que queda bien en cualquier cuerpo: esa es la magia de la marca.</p>
        <h2 id="materiales">Sus telas</h2>
        <ul class="telas">
          <li><strong>Algodón:</strong> poleras y polerones.</li>
          <li><strong>Viscosa:</strong> vestidos largos, túnicas y blusas.</li>
          <li><strong>Lino:</strong> pantalones, camisas y chalecos de temporada cálida.</li>
          <li><strong>Punto y lana:</strong> cárdigans, chaquetas y suéteres de invierno.</li>
          <li><strong>Denim:</strong> jeans amplios y chaquetas.</li>
        </ul>
        <a class="btn btn-linea" href="/todo">Ver la colección</a>
      </div>
      <div class="pagina-foto"><img src="/img/nosotras-1.jpg" alt="Michelle y Valerie, de Banditas Chile, riéndose en un jardín con trajes de leopardo y verde" width="675" height="900"></div>
    </div>
  </div>'''
    return documento('Nosotras · Banditas Chile', cuerpo, '', 'Dos amigas traen a Chile Banditas from Marseille: marca francesa diseñada en Marsella y fabricada en Italia.')

# Próximo showroom: None mientras no haya fecha. Cuando Michelle la confirme, por ejemplo:
# PROXIMO = {'fecha': 'Jueves 6 al sábado 8 de noviembre', 'lugar': 'Nombre del lugar, Lo Barnechea', 'mapa': 'https://maps.google.com/?q=...',
#            'horario': '11:00 a 19:00', 'inicio': '20261106T140000Z', 'fin': '20261108T220000Z'}
# 23-10: confirmado por Michelle y Valerie. Hora de Chile en verano (UTC-3): jueves 17-22 y viernes 11-20.
PROXIMO = {'fecha': 'Jueves 5 y viernes 6 de noviembre', 'lugar': 'The Beauty Place · Paseo La Cruz, Los Trapenses 3200, local 8, Lo Barnechea',
           'mapa': 'https://www.google.com/maps/search/?api=1&query=' + quote('Camino Los Trapenses 3200, Lo Barnechea'),
           'horario': 'Jueves de 17:00 a 22:00 y viernes de 11:00 a 20:00', 'inicio': '20261105T200000Z', 'fin': '20261106T230000Z'}

def caja_proximo():
    aviso = 'https://wa.me/' + WSP + '?text=' + quote('Hola, quiero que me avisen del próximo showroom de Banditas.')
    if not PROXIMO:
        return f'''<section class="proximo" aria-labelledby="t-prox">
          <p class="rotulo" id="t-prox">Próximo showroom</p>
          <p class="proximo-fecha">Fecha por anunciar</p>
          <p>Se anuncia acá, en Instagram y a quienes piden aviso.</p>
          <div class="proximo-botones"><a class="btn" href="{aviso}">{ICONO_WSP} Avísame por WhatsApp</a><a class="btn btn-linea" href="#boletin">Avísame por correo</a></div>
        </section>'''
    cal = ('https://calendar.google.com/calendar/render?action=TEMPLATE&text=' + quote('Showroom Banditas Chile') +
           f"&dates={PROXIMO['inicio']}/{PROXIMO['fin']}&location=" + quote(PROXIMO['lugar']))
    return f'''<section class="proximo" aria-labelledby="t-prox">
          <p class="rotulo" id="t-prox">Próximo showroom</p>
          <p class="proximo-fecha">{e(PROXIMO['fecha'])}</p>
          <p><a class="enlace" href="{e(PROXIMO['mapa'])}">{e(PROXIMO['lugar'])}</a> · {e(PROXIMO['horario'])}</p>
          <div class="proximo-botones"><a class="btn" href="{cal}">Agregar al calendario</a><a class="btn btn-linea" href="{aviso}">{ICONO_WSP} Avísame por WhatsApp</a></div>
        </section>'''

def pagina_showroom():
    espacio = 'https://wa.me/' + WSP + '?text=' + quote('Hola, tengo un espacio que podría servir para un showroom de Banditas.')
    cuerpo = f'''
  <div class="wrap">
    <nav class="migas" aria-label="Estás en"><a href="/">Inicio</a><span>/</span><span aria-current="page">Showroom</span></nav>
    <div class="pagina">
      <div class="pagina-cuerpo">
        <p class="rotulo">Showroom</p>
        <h1>Showroom Banditas</h1>
        <p class="frase">Dos días en The Beauty Place, en Lo Barnechea, con la colección para probarse.</p>
        {caja_proximo()}
        <h2>Cómo funciona</h2>
        <p>Llegas, te pruebas lo que quieras y te lo llevas al tiro. Se paga ahí mismo con tarjeta o transferencia. Si tu talla no está, pregúntanos por WhatsApp.</p>
        <h2>El de octubre</h2>
        <p>Tres días en Lo Barnechea. Lo que más nos preguntaron: cuándo es el próximo.</p>
      </div>
      <div class="pagina-foto"><img src="/img/showroom-amigas-1.jpg" alt="Las dos amigas de Banditas Chile en el showroom de octubre, entre los percheros" width="960" height="1280" fetchpriority="high"></div>
    </div>
    <div class="showroom-galeria">
      <video poster="/img/showroom-video.jpg" muted loop playsinline autoplay preload="metadata" aria-label="Las dos amigas riéndose en el showroom de octubre"><source src="/video/showroom.mp4" type="video/mp4"></video>
      <img src="/img/showroom-1.jpg" alt="Probándose una chaqueta en el showroom, entre los percheros" width="900" height="1200" loading="lazy">
    </div>
    <section class="espacio" aria-labelledby="t-esp">
      <h2 id="t-esp">¿Tienes un local o una casa para el próximo showroom?</h2>
      <p>Buscamos lugares con onda en Santiago para tres días. Escríbenos y lo conversamos.</p>
      <a class="btn btn-linea" href="{espacio}">{ICONO_WSP} Ofrecer un espacio</a>
    </section>
  </div>
  {boletin('Avísame del próximo showroom', 'Te escribimos con la fecha y el lugar antes que a nadie. Nada más.', 'Avisarme', 'Listo. Te avisamos apenas tengamos fecha.')}'''
    return documento('Showroom · Banditas Chile', cuerpo, '/showroom', 'El showroom de Banditas Chile: tres días para probarse la colección en Santiago. Pide aviso del próximo.')

def pagina_ayuda():
    cuerpo = f'''
  <div class="wrap">
    <nav class="migas" aria-label="Estás en"><a href="/">Inicio</a><span>/</span><span aria-current="page">Ayuda</span></nav>
    <div class="pagina-cuerpo" style="max-width:none">
      <h1>Ayuda</h1>
      <nav class="indice" aria-label="Secciones">{'<a href="#pedir">Cómo pedir</a>' if VITRINA else ''}<a href="#cambios">Cambios</a><a href="#retracto">Retracto</a><a href="#despacho">Despacho y retiro</a><a href="#tallas">Guía de tallas</a><a href="#contacto">Contacto</a><a href="#privacidad">Privacidad</a><a href="#terminos">Términos</a></nav>
    </div>
    <div class="pagina-cuerpo" style="padding-block:24px 64px">
      {'<h2 id="pedir">Cómo pedir</h2><p>Elige la prenda y tu talla, y toca <b>Pedir por WhatsApp</b>: se abre el chat con tu pedido escrito. Te confirmamos que esté disponible y coordinamos el pago y el despacho o el retiro. También puedes pasar por el showroom.</p>' if VITRINA else ''}
      <h2 id="cambios">Cambios y devoluciones</h2>
      <p>Puedes cambiar una prenda por otra talla o color, sujeto a stock, si está sin uso, con sus etiquetas y en su empaque. Escríbenos por WhatsApp con tu número de pedido y coordinamos el cambio.</p>
      <p>El plazo para pedir el cambio, la devolución de dinero y quién paga el despacho del cambio están por confirmar. Si una prenda viene con falla, aplica la garantía legal de 6 meses.</p>

      <h2 id="retracto">Derecho a retracto</h2>
      <p>En Chile, en las compras hechas por internet puedes retractarte dentro de los 10 días siguientes a recibir el producto, sin dar razones, mientras esté sin uso y con sus etiquetas (Ley 19.496, artículo 3 bis). La tienda puede excluir este derecho, pero solo si lo informa de forma destacada antes de la compra.</p>

      <h2 id="despacho">Despacho y retiro</h2>
      <p>Coordinamos la entrega por WhatsApp: puedes retirar en el showroom o pedir envío a todo Chile. El costo y el plazo del envío te los confirmamos al coordinar.</p>

      <h2 id="tallas">Guía de tallas</h2>
      <p>La mayoría de las prendas son de talla única, con corte amplio. Las que vienen por talla traen la talla europea; esta es la equivalencia.</p>
      <div class="tabla-scroll"><table>
        <thead><tr><th>Europa / Francia</th><th>Chile</th></tr></thead>
        <tbody>
          <tr><td>34</td><td>XS</td></tr>
          <tr><td>36</td><td>S</td></tr>
          <tr><td>38</td><td>M</td></tr>
          <tr><td>Por confirmar</td><td>L</td></tr>
          <tr><td>Por confirmar</td><td>XL</td></tr>
          <tr><td>Talla única</td><td>Única</td></tr>
        </tbody>
      </table></div>
      <p>Si dudas entre dos tallas, escríbenos: te decimos cómo calza esa prenda en particular.</p>

      <h2 id="contacto">Contacto</h2>
      <p>WhatsApp {WSP_VISIBLE} · Instagram <a href="https://www.instagram.com/banditaschile/">@banditaschile</a> · <a href="mailto:banditaschile@gmail.com">banditaschile@gmail.com</a></p>
      <p>Respondemos de lunes a viernes en horario de oficina; los fines de semana, cuando podemos.</p>

      <h2 id="privacidad">Privacidad</h2>
      <p>Usamos tu nombre, dirección, contacto y datos de pago solo para procesar y despachar tu compra y avisarte sobre tu pedido. No los vendemos ni los compartimos, salvo con quienes hacen posible la entrega y el pago. Puedes pedir ver o borrar tus datos escribiéndonos.</p>

      <h2 id="terminos">Términos</h2>
      <p>Precios en pesos chilenos con IVA incluido. La compra se confirma una vez aprobado el pago. Los plazos de despacho son referenciales. Las fotos son de las prendas reales; puede haber pequeñas diferencias de color según la pantalla. Promociones sujetas a stock.</p>
    </div>
  </div>'''
    return documento('Ayuda · Banditas Chile', cuerpo, '', 'Cambios, despacho, guía de tallas, contacto, privacidad y términos de Banditas Chile.')

SCRIPT = r'''
// Mejoras con JavaScript. Todo el contenido funciona sin él.
(function(){
  document.documentElement.classList.add('js');
  // menú móvil: se cierra al elegir algo, al cambiar de sección o al tocar fuera
  var menu = document.querySelector('.menu');
  if (menu) {
    document.querySelectorAll('.nav a').forEach(function(a){ a.addEventListener('click', function(){ menu.open = false; }); });
    window.addEventListener('hashchange', function(){ menu.open = false; });
    document.addEventListener('click', function(ev){ if (menu.open && !menu.contains(ev.target) && !ev.target.closest('.nav')) menu.open = false; });
    window.addEventListener('pageshow', function(){ menu.open = false; });
  }
  // imágenes diferidas: fundido al cargar
  document.querySelectorAll('img[loading=lazy]').forEach(function(img){
    if (img.complete) { img.classList.add('cargada'); return; }
    img.addEventListener('load', function(){ img.classList.add('cargada'); }, {once:true});
    img.addEventListener('error', function(){ img.classList.add('cargada'); }, {once:true});
  });
  var bolsa = 0;
  try { bolsa = parseInt(localStorage.getItem('bolsa') || '0', 10) || 0; } catch (e) {}
  var cuenta = document.getElementById('bolsa-cuenta');
  function pintarBolsa(){ if (cuenta) { cuenta.textContent = bolsa; cuenta.hidden = bolsa === 0; } }
  pintarBolsa();

  // boletín
  var f = document.getElementById('form-boletin');
  if (f) f.addEventListener('submit', function(e){ e.preventDefault(); document.getElementById('gracias').hidden = false; f.hidden = true; });

  // ficha: color cambia la foto, agregar a la bolsa
  var compra = document.getElementById('form-compra');
  if (compra) {
    compra.querySelectorAll('input[name=color]').forEach(function(r){
      r.addEventListener('change', function(){
        document.getElementById('color-nombre').textContent = r.value;
        var fig = document.getElementById(r.dataset.foto);
        if (fig) fig.scrollIntoView({behavior:'smooth', block:'nearest', inline:'center'});
      });
    });
    var pedir = document.getElementById('pedir');
    if (pedir) {
      var alCambiar = function(){
        var t = compra.querySelector('input[name=talla]:checked');
        var texto = pedir.dataset.base + (t ? ' Talla: ' + (t.value === 'TU' ? 'única' : t.value) + '.' : '');
        pedir.href = pedir.href.split('?')[0] + '?text=' + encodeURIComponent(texto);
      };
      compra.querySelectorAll('input[name=talla]').forEach(function(r){ r.addEventListener('change', alCambiar); });
    }
    compra.addEventListener('submit', function(e){
      e.preventDefault();
      if (pedir) return;
      var talla = compra.querySelector('input[name=talla]:checked');
      if (!talla) { compra.querySelector('input[name=talla]').focus(); return; }
      bolsa += 1; try { localStorage.setItem('bolsa', String(bolsa)); } catch (err) {}
      pintarBolsa();
      var icono = document.getElementById('bolsa');
      if (icono) { icono.classList.remove('rebote'); void icono.offsetWidth; icono.classList.add('rebote'); }
      var viejo = document.querySelector('.aviso-carrito'); if (viejo) viejo.remove();
      var c = compra.querySelector('input[name=color]:checked'), color = c ? c.value : '';
      var aviso = document.createElement('div');
      aviso.className = 'aviso-carrito'; aviso.setAttribute('role', 'status');
      aviso.innerHTML = 'Agregado: ' + (talla.value === 'TU' ? 'talla única' : 'talla ' + talla.value) + (color ? ', ' + color.toLowerCase() : '') + '. <a href="#">Ver la bolsa</a>';
      document.body.appendChild(aviso);
      setTimeout(function(){ aviso.classList.add('irse'); setTimeout(function(){ aviso.remove(); }, 400); }, 4000);
    });

    // galería: lupa que sigue al cursor (escritorio) y lightbox al hacer clic
    var luz = document.getElementById('luz'), luzImg = document.getElementById('luz-img');
    document.querySelectorAll('.galeria figure').forEach(function(fig){
      var img = fig.querySelector('img');
      fig.addEventListener('mousemove', function(ev){
        if (!window.matchMedia('(hover:hover) and (min-width:900px)').matches) return;
        var r = fig.getBoundingClientRect();
        img.style.transformOrigin = ((ev.clientX - r.left) / r.width * 100) + '% ' + ((ev.clientY - r.top) / r.height * 100) + '%';
        fig.classList.add('lupa');
      });
      fig.addEventListener('mouseleave', function(){ fig.classList.remove('lupa'); img.style.transformOrigin = ''; });
      fig.addEventListener('click', function(){
        if (!luz || typeof luz.showModal !== 'function') return;
        luzImg.src = img.currentSrc || img.src; luzImg.alt = img.alt; luz.showModal();
      });
    });
    if (luz) {
      document.getElementById('luz-cerrar').addEventListener('click', function(){ luz.close(); });
      luz.addEventListener('click', function(ev){ if (ev.target === luz) luz.close(); });
    }
  }

  // categoría: chips, filtro de categoría y orden
  var grilla = document.getElementById('grilla');
  if (grilla) {
    var fichas = Array.prototype.slice.call(grilla.querySelectorAll('.ficha'));
    var titulo = document.getElementById('cat-titulo'), cuentaCat = document.getElementById('cat-cuenta'), vacio = document.getElementById('vacio');
    var chips = document.querySelectorAll('#chips .chip');
    function aplicar(){
      var cat = decodeURIComponent(location.hash.slice(1));
      var activa = null;
      chips.forEach(function(c){ var es = (c.dataset.cat && slug(c.dataset.cat) === cat); if (es) activa = c.dataset.cat; c.setAttribute('aria-current', es || (!cat && !c.dataset.cat) ? 'true' : 'false'); });
      function marcadasDe(n){ return Array.prototype.map.call(document.querySelectorAll('input[name=' + n + ']:checked'), function(i){ return i.value; }); }
      function cruza(lista, valores){ return !lista.length || valores.some(function(v){ return lista.indexOf(v) >= 0; }); }
      var marcadas = marcadasDe('cat'), tallas = marcadasDe('talla'), colores = marcadasDe('color');
      var n = 0;
      fichas.forEach(function(f){
        var ok = (!activa || f.dataset.categoria === activa) && (!marcadas.length || marcadas.indexOf(f.dataset.categoria) >= 0)
          && cruza(tallas, (f.dataset.tallas || '').split(' ')) && cruza(colores, (f.dataset.colores || '').split('|'));
        f.hidden = !ok; if (ok) n++;
      });
      if (titulo) titulo.textContent = activa || 'Todo';
      if (cuentaCat) cuentaCat.textContent = n + (n === 1 ? ' producto' : ' productos');
      if (vacio) vacio.hidden = n > 0;
    }
    function slug(s){ return s.normalize('NFKD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,''); }
    window.addEventListener('hashchange', aplicar);
    document.querySelectorAll('input[name=cat], input[name=talla], input[name=color]').forEach(function(i){ i.addEventListener('change', aplicar); });
    var orden = document.getElementById('orden');
    if (orden) orden.addEventListener('change', function(){
      var v = orden.value;
      var lista = fichas.slice();
      if (v !== 'nuevo') lista.sort(function(a,b){ var pa = +a.dataset.precio || Infinity, pb = +b.dataset.precio || Infinity; return v === 'menor' ? pa - pb : (pb === Infinity ? -1 : pa === Infinity ? 1 : pb - pa); });
      lista.forEach(function(f){ grilla.appendChild(f); });
    });
    aplicar();
  }
})();
'''

FAVICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="50" cy="50" r="40" fill="none" stroke="#cca300" stroke-width="7" stroke-linecap="round" stroke-dasharray="215 40" transform="rotate(-70 50 50)"/><text x="50" y="62" font-family="Jost,Helvetica,Arial,sans-serif" font-size="38" text-anchor="middle" fill="#2b2829">B</text></svg>'''

VERCEL = '''{
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [{ "source": "/img/(.*)", "headers": [{ "key": "Cache-Control", "value": "public, max-age=86400" }] }],
  "redirects": [
    { "source": "/", "has": [{ "type": "host", "value": "banditas-prototipo.vercel.app" }], "destination": "https://www.banditas.cl/", "permanent": true },
    { "source": "/(.*)", "has": [{ "type": "host", "value": "banditas-prototipo.vercel.app" }], "destination": "https://www.banditas.cl/$1", "permanent": true }
  ]
}
'''   # 19-10: la dirección vieja redirige a banditas.cl (dos reglas: "/:path*" no toma la raíz)

# 20-10: catálogo para Meta (Instagram y Facebook). Commerce Manager lo lee desde www.banditas.cl/meta-catalogo.csv
# y se actualiza solo cada vez que se publica la página. Un producto por fila; tallas y colores en la descripción.
def catalogo_meta(productos):
    import csv as _csv, io as _io
    campos = ['id', 'title', 'description', 'availability', 'condition', 'price', 'link', 'image_link',
              'additional_image_link', 'brand', 'product_type', 'color', 'size']
    buf = _io.StringIO(); w = _csv.DictWriter(buf, fieldnames=campos); w.writeheader()
    for x in productos:
        fotos = [f.strip() for f in x['imagenes'].split(',') if f.strip()]
        if not fotos or not x.get('precio_clp'): continue
        st = stock_por_talla(x)
        hay = sum(st.values()) > 0 if st else int(x.get('stock_total') or 0) > 0
        tallas_ok = [('Única' if t == 'TU' else t) for t, n in st.items() if n > 0] if st else []
        desc = (x.get('descripcion') or x['nombre_web']).strip()
        if tallas_ok: desc += ' Tallas disponibles: ' + ', '.join(tallas_ok) + '.'
        desc += ' Pedidos por WhatsApp en banditas.cl.'
        w.writerow({'id': x['handle'], 'title': x['nombre_web'], 'description': desc[:5000],
                    'availability': 'in stock' if hay else 'out of stock', 'condition': 'new',
                    'price': f"{int(float(x['precio_clp']))} CLP", 'link': f"{DOMINIO}/producto/{x['handle']}",
                    'image_link': f"{DOMINIO}/img/{fotos[0]}",
                    'additional_image_link': ','.join(f"{DOMINIO}/img/{f}" for f in fotos[1:10]),
                    'brand': 'Banditas', 'product_type': x['categoria_web'],
                    'color': (x.get('colores') or '').replace(' / ', ', ')[:100], 'size': ', '.join(tallas_ok)[:100]})
    return buf.getvalue()

def main():
    global CATEGORIAS
    productos = leer_catalogo()
    CATEGORIAS = [c for c in CATEGORIAS_BASE if any(p['categoria_web'] == c for p in productos)]
    SITIO.mkdir(exist_ok=True)
    paginas = {
        'index.html': portada(productos),
        'todo.html': pagina_todo(productos),
        'producto.html': pagina_producto_redirige(),
        'nosotras.html': pagina_nosotras(),
        'showroom.html': pagina_showroom(),
        'ayuda.html': pagina_ayuda(),
    }
    import re, hashlib
    def version(m):
        # ?v=<hash del archivo>: cuando cambia la foto cambia la URL y ni el navegador ni el CDN sirven la vieja
        ruta = SITIO / 'img' / m.group(1)
        if not ruta.exists(): return m.group(0)
        return f"/img/{m.group(1)}?v={hashlib.md5(ruta.read_bytes()).hexdigest()[:8]}"
    (SITIO / 'producto').mkdir(exist_ok=True)
    for x in productos: paginas[f"producto/{x['handle']}.html"] = pagina_producto(x, productos)
    for nombre, contenido in paginas.items():
        contenido = re.sub(r'/img/([A-Za-z0-9._-]+)', version, contenido)
        (SITIO / nombre).write_text(contenido, encoding='utf-8')
    (SITIO / 'sitio.js').write_text(SCRIPT, encoding='utf-8')
    (SITIO / 'favicon.svg').write_text(FAVICON, encoding='utf-8')
    (SITIO / '_headers').write_text('/img/*\n  Cache-Control: public, max-age=86400\n', encoding='utf-8')
    (SITIO / 'meta-catalogo.csv').write_text(catalogo_meta(productos), encoding='utf-8')
    print('páginas:', sum(1 for n in paginas if not n.startswith('producto/')), '+', sum(1 for n in paginas if n.startswith('producto/')), 'fichas · productos:', len(productos))

if __name__ == '__main__':
    main()
