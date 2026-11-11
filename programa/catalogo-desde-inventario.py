#!/usr/bin/env python3
"""Construye catalogo.csv (la planilla neutra de la tienda) desde el Excel de Michelle del 9-10-2026:
hoja "Catalogo ok" (68 productos, nombre del proveedor, nota, precio, tallas) + hoja "Inventario" (stock por talla).
Los nombres web, categorías y descripciones están curados a mano abajo; las notas de Michelle son internas y no van a la web.
Uso: python3 catalogo-desde-inventario.py
"""
import csv, pathlib, re, unicodedata, openpyxl
from collections import OrderedDict

AQUI = pathlib.Path(__file__).parent
XLSX = AQUI / 'catalogo-michelle-2026-10-09.xlsx'            # nombres del proveedor, notas, precios
XLSX_VENTAS = AQUI / 'control-ventas-michelle-2026-10-27.xlsx'  # costo de importación y stock actual (tras el showroom de octubre)
FOTOS_CSV = AQUI / 'prototipo' / 'fotos.csv'
SALIDA = AQUI / 'catalogo.csv'

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')

# código RB → (nombre web, categoría, descripción para la web, colores, clave de fotos en prototipo/fotos.csv)
# Las descripciones salen de las notas de Michelle y del catálogo de WhatsApp. "" en descripción = por redactar.
P = OrderedDict([
 ('RB001', ('Bermuda de jeans Blanket', 'Faldas y bermudas', 'Bermuda de jeans liviano y versátil, ideal primavera-verano.', '', 'bermuda-de-jeans-blanket')),
 ('RB002', ('Bermuda de jeans Edgewater', 'Faldas y bermudas', 'Bermuda de jeans claro, corte recto bajo la rodilla.', '', 'bermuda-de-jeans-edgewater')),
 ('RB003', ('Bermuda de jeans Posillipo', 'Faldas y bermudas', 'Bermuda de jeans liviano, bajo la rodilla, con bordado.', '', 'bermuda-de-jeans-posillipo')),
 ('RB004', ('Camisa escocesa Adda', 'Camisas y blusas', 'Camisa escocesa en dos tonos, liviana, con degradé.', '', 'camisa-escocesa-adda')),
 ('RB005', ('Camisa de lino Ágata', 'Camisas y blusas', 'Camisa 100% lino. En celeste o verde.', 'Celeste / Verde', 'camisa-de-lino-agata')),
 ('RB006', ('Camisa estampada Cameron', 'Camisas y blusas', 'Camisa estampada en tonos vivos, tela liviana.', 'Naranjo', 'camisa-estampada-cameron')),   # 15-10: Michelle dejó solo el naranjo
 ('RB007', ('Camisa a rayas Opener', 'Camisas y blusas', 'Camisa a rayas azul y blanco con bordado.', '', 'blusa-a-rayas-opener')),
 ('RB008', ('Enterito de jeans Rase Top', 'Enteritos', 'Enterito de jeans delgado con dobleces de color en las mangas. En amarillo o calipso.', 'Amarillo / Calipso', 'enterito-de-jeans-rase-top')),
 ('RB009', ('Enterito animal print Sisine', 'Enteritos', 'Enterito con estampado leopardo, cómodo y versátil.', '', 'enterito-animal-print-sisine')),
 ('RB010', ('Enterito de jeans Spinne', 'Enteritos', 'Enterito de jeans negro, delgado y de calce perfecto.', 'Negro', 'enterito-de-jeans-spinne')),
 ('RB011', ('Chaleco de jeans Labiciano', 'Chaquetas y chalecos', 'Chaleco de jeans sin mangas, delgado, con cierre y bolsillos.', '', 'chaleco-de-jeans-labiciano')),
 ('RB012', ('Chaleco de lana Rita', 'Chaquetas y chalecos', 'Chaleco grueso de lana con estampado en la espalda.', '', 'chaleco-de-lana-rita')),
 ('RB013', ('Chaleco Sangiovese', 'Chaquetas y chalecos', 'Chaqueta gris sin mangas, oversize.', 'Gris', 'chaleco-oversize-sangiovese')),
 ('RB014', ('Jeans Bagnoli', 'Jeans y pantalones', 'Jeans livianos, de corte único, con un corazón en el bolsillo.', '', 'jeans-bomber-bagnoli')),
 ('RB015', ('Falda de jeans Collatino', 'Faldas y bermudas', 'Falda de jeans bajo la rodilla con detalle naranjo.', '', 'falda-de-jeans-collatino')),
 ('RB016', ('Jeans Hamal', 'Jeans y pantalones', 'Jeans con detalle de cinturón.', '', 'jeans-hamal')),
 ('RB017', ('Pantalón de buzo Marble', 'Jeans y pantalones', 'Pantalón tipo buzo del conjunto Marble. En verde o beige.', 'Verde / Beige', 'pantalon-de-buzo-marble')),
 ('RB019', ('Jeans pescador Larch', 'Jeans y pantalones', 'Jeans negros de calce pescador.', 'Negro', 'jeans-pescador-larch')),
 ('RB020', ('Chaqueta kimono Chilled', 'Chaquetas y chalecos', 'Chaqueta tipo kimono, liviana y estampada, para entretiempo. En verde o café.', 'Verde / Café', 'chaqueta-kimono')),
 ('RB021', ('Chaqueta tejida Pallide', 'Chaquetas y chalecos', 'Chaqueta tipo camisa, tejida, con cuadros pequeños en verde oscuro y blanco.', 'Verde / Blanco', 'chaqueta-tejida-pallide')),
 ('RB022', ('Pantalón de lino Chester', 'Jeans y pantalones', 'Pantalón de lino ancho, jaspeado. Hace conjunto con la chaqueta Marvel.', '', 'pantalon-de-lino-chester')),
 ('RB023', ('Pantalón leopardo Chopping', 'Jeans y pantalones', 'Pantalón ultra delgado con estampado leopardo. Hace conjunto con la chaqueta Peeler.', '', 'pantalon-leopardo-chopping')),
 ('RB024', ('Pantalón de jeans Delphine', 'Jeans y pantalones', 'Pantalón de jeans con estampado leopardo.', '', 'pantalon-de-jeans-delphine')),
 ('RB025', ('Chaleco con flecos Divina', 'Chaquetas y chalecos', 'Chaleco con flecos.', '', 'chaleco-con-flecos-divina')),
 ('RB026', ('Pantalón de buzo Fever', 'Jeans y pantalones', 'Pantalón tipo buzo, 100% algodón, verde. Hace conjunto con la chaqueta Rodi.', 'Verde', 'pantalon-de-buzo-fever')),
 ('RB027', ('Pantalón militar Fiffidi', 'Jeans y pantalones', 'Pantalón del conjunto militar. Hace conjunto con la chaqueta Casperino.', '', 'pantalon-militar-fiffidi')),
 ('RB028', ('Pantalón de buzo Homan', 'Jeans y pantalones', 'Pantalón casual estilo buzo con estampado, en gris o celeste.', 'Gris / Celeste', 'pantalon-de-buzo-homan')),
 ('RB029', ('Chaleco Lía', 'Chaquetas y chalecos', 'Chaleco delgado, rojo, con estampado "Yes you can".', 'Rojo', 'chaleco-lia')),
 ('RB030', ('Chaleco Tai', 'Chaquetas y chalecos', 'Chaleco delgado con estampado "Good things are coming".', '', 'chaleco-tai')),
 ('RB031', ('Pantalón vintage Ventura', 'Jeans y pantalones', 'Pantalón calipso con líneas blancas laterales. Delgado, cómodo y veraniego.', 'Calipso', 'pantalon-vintage-ventura')),
 ('RB032', ('Vestido teñido Decumani', 'Vestidos', 'Vestido largo de algodón, teñido en degradé rosado.', 'Rosado', 'vestido-decumani')),
 ('RB033', ('Vestido teñido Fidene', 'Vestidos', 'Vestido largo teñido a mano. En blanco o rosado.', 'Blanco / Rosado', 'vestido-tenido')),
 ('RB034', ('Vestido túnica Iron Fist', 'Vestidos', 'Vestido túnica delgado, versátil y cómodo. En negro o blanco.', 'Negro / Blanco', 'vestido-primaveral-iron-fist')),
 ('RB035', ('Vestido largo Monclaire', 'Vestidos', 'Vestido lila, largo y suelto, con estampado en la espalda.', 'Lila', 'vestido-largo-monclaire')),
 ('RB036', ('Vestido estampado Namrek', 'Vestidos', 'Vestido largo con estampado floral, amplio y liviano. En azul o naranjo.', 'Azul / Naranjo', 'vestido-estampado-namrek')),
 ('RB037', ('Vestido de jeans Parione', 'Vestidos', 'Vestido de jeans oversize con estampado en la espalda.', 'Jeans', 'vestido-de-jeans-imprime')),
 ('RB038', ('Vestido túnica Sirio', 'Vestidos', 'Vestido túnica café con estampado en la espalda.', 'Café', 'vestido-sirio')),
 ('RB039', ('Vestido canguro Terrano', 'Vestidos', 'Vestido canguro oversize, con capucha y bolsillo. En crudo, verde o negro.', 'Crudo / Verde / Negro', 'vestido-canguro-terrano')),
 ('RB040', ('Jardinera de jeans Materdei', 'Enteritos', 'Jardinera de jeans delgado con desgaste y parches.', 'Jeans', 'jardinera-de-jeans-materdai')),
 ('RB041', ('Polerón Basilea', 'Poleras y polerones', 'Polerón crudo con estampado LOVE rosado en la espalda.', 'Crudo', 'poleron-basilea')),
 ('RB042', ('Polerón Birch', 'Poleras y polerones', 'Polerón con capucha y estampado "Level 1". En gris o crudo.', 'Gris / Crudo', 'poleron-birch')),
 ('RB043', ('Polerón Mintaka', 'Poleras y polerones', '', '', '')),
 ('RB044', ('Polerón Mirach', 'Poleras y polerones', 'Polerón liviano. En verde o celeste.', 'Verde / Celeste', 'poleron-mirach')),
 ('RB045', ('Camisa de jeans Biene', 'Camisas y blusas', 'Camisa de jeans con estampado en la espalda.', 'Jeans', 'camisa-de-jeans-biene')),
 ('RB046', ('Polera cuello V Bolzano', 'Poleras y polerones', 'Polera cuello V, 100% algodón, en colores pastel.', 'Rosa / Fucsia / Celeste / Naranjo', 'polera-bolzano')),
 ('RB047', ('Polera Paradise Caketin', 'Poleras y polerones', 'Polera cuello V, 100% algodón, estampado Paradise. En rosado, verde o blanco.', 'Rosado / Verde / Blanco', 'polera-cuello-v-paradise')),
 ('RB048', ('Polera Circle', 'Poleras y polerones', 'Polera 100% algodón. En celeste, terracota o mostaza.', 'Celeste / Terracota / Mostaza', 'polera-circle')),
 ('RB049', ('Polera a rayas Clavel', 'Poleras y polerones', 'Polera a rayas blanco y negro.', 'Blanco / Negro', 'polera-a-rayas-clavel')),
 ('RB050', ('Polera Deneb', 'Poleras y polerones', 'Polera 100% algodón, corte boyfriend, con el estampado "No boyfriend, no migraine".', '', 'polera-estrella')),
 ('RB050A', ('Polera Deneb Star', 'Poleras y polerones', 'Polera 100% algodón, corte boyfriend, con estrella.', '', 'polera-deneb-star')),
 ('RB050B', ('Polera Deneb Beach', 'Poleras y polerones', 'Polera blanca 100% algodón, con estampado naranjo en la espalda.', 'Blanco', 'polera-deneb-beach')),
 ('RB051', ('Polera Doctor Strange', 'Poleras y polerones', 'Polera con estampado "Sorry, give me your password".', '', 'polera-doctor-strange')),
 ('RB051A', ('Polera Strange Love', 'Poleras y polerones', 'Polera con estampado LOVE en la espalda, en amarillo y naranjo.', '', 'polera-strange-love')),
 ('RB052', ('Polera de encaje Englewood', 'Poleras y polerones', 'Polera cuello V de encaje crudo, semitransparente, manga corta.', 'Crudo', 'polera-de-encaje-englewood')),
 ('RB053', ('Polera Love Gaiola', 'Poleras y polerones', 'Polera 100% algodón con estampado LOVE. En blanco, rosado o azul.', 'Blanco / Rosado / Azul', 'polera-love')),
 ('RB054', ('Polera Love Logetta', 'Poleras y polerones', 'Polera blanca con estampado LOVE en azul o negro.', 'Blanco', 'polera-love-logetta')),
 ('RB055', ('Polera Ridge', 'Poleras y polerones', 'Polera oversize 100% algodón con estampado en la espalda: "Good coffee, relaxed workspaces, fine music".', 'Varios colores', 'polera-anticons')),
 ('RB056', ('Polera Ridge Cons', 'Poleras y polerones', 'Polera oversize 100% algodón con estampado "Anti cons".', '', 'polera-ridge-cons')),
 ('RB057', ('Polera Thor', 'Poleras y polerones', 'Polera de conjunto. En beige o verde.', 'Beige / Verde', 'polera-thor')),
 ('RB059', ('Blusa de encaje Torrone', 'Camisas y blusas', 'Blusa de viscosa con encaje café y detalles semitransparentes.', 'Café', 'blusa-de-encaje-torrone')),
 ('RB060', ('Chaqueta cuadrillé Asparago', 'Chaquetas y chalecos', 'Chaqueta a cuadros azul, tipo blazer.', 'Azul', 'chaqueta-cuadrille-asparago')),
 ('RB061', ('Chaqueta de jeans Belle', 'Chaquetas y chalecos', 'Chaqueta de jeans oversize. En negro o azul.', 'Negro / Azul', 'chaqueta-de-jeans-belle')),
 ('RB062', ('Chaqueta militar Casperino', 'Chaquetas y chalecos', 'Chaqueta del conjunto militar, para un look relajado o elegante. Hace conjunto con el pantalón Fiffidi.', '', 'chaqueta-militar-casperino')),
 ('RB063', ('Chaqueta de lino Marvel', 'Chaquetas y chalecos', 'Chaqueta de lino cruzada, tipo blazer, jaspeada. Hace conjunto con el pantalón Chester.', '', 'chaqueta-de-lino-marvel')),
 ('RB064', ('Chaqueta de jeans Monte Sacro', 'Chaquetas y chalecos', 'Chaqueta de jeans claro, sin mangas, con botones.', 'Jeans claro', 'chaqueta-de-jeans-montesacro')),
 ('RB065', ('Chaqueta leopardo Peeler', 'Chaquetas y chalecos', 'Chaqueta delgada y liviana con estampado leopardo. Hace conjunto con el pantalón Chopping.', '', 'chaqueta-leopardo-chopping')),
 ('RB066', ('Chaqueta jaspeada Porter', 'Chaquetas y chalecos', 'Chaqueta jaspeada azul.', 'Azul', 'chaqueta-jaspeada-porter')),
 ('RB067', ('Chaqueta Rodi', 'Chaquetas y chalecos', 'Chaqueta del conjunto verde. Hace conjunto con el pantalón de buzo Fever.', 'Verde', 'chaqueta-rodi')),
 ('RB068', ('Chaqueta Solana', 'Chaquetas y chalecos', 'Chaqueta gris con vuelo, liviana, para look formal o informal.', 'Gris', 'chaqueta-veraniega-solana')),
 ('RB069', ('Chaqueta polerón de jeans Ciop', 'Chaquetas y chalecos', 'Chaqueta tipo polerón canguro, de jeans, con capucha y cordón grueso. En azul o negro.', 'Azul / Negro', 'chaqueta-poleron-ciop')),
 # 16-10: segundo pedido (RB070–RB078). Sin foto no se publican; las descripciones salen de las notas de Michelle.
 ('RB070', ('Blazer Merini Hola', 'Chaquetas y chalecos', 'Blazer Merini, modelo Hola.', '', 'blazer-merini-hola')),
 ('RB071', ('Blazer Merini Art', 'Chaquetas y chalecos', 'Blazer Merini, modelo Art, en rojo.', 'Rojo', 'blazer-merini-art')),
 ('RB072', ('Bermuda leopardo Portaromana', 'Faldas y bermudas', 'Bermuda con estampado leopardo.', '', 'bermuda-leopardo-portaromana')),
 ('RB073', ('Chaqueta de jeans Roland', 'Chaquetas y chalecos', 'Chaqueta de jeans en café claro con celeste. Hace conjunto con los jeans Delight.', 'Café claro / Celeste', 'chaqueta-de-jeans-roland')),
 ('RB074', ('Jeans Delight', 'Jeans y pantalones', 'Jeans de corte amplio en café claro. Hace conjunto con la chaqueta Roland.', 'Café claro', 'pantalon-delight')),   # 17-10: Michelle lo renombró JEANS DELIGHT
 ('RB075', ('Blazer Santa Trinita', 'Chaquetas y chalecos', 'Blazer oversize con letras rojas.', '', 'blazer-santa-trinita')),
 ('RB076', ('Camisa de jeans San Lorenzo', 'Camisas y blusas', 'Camisa de jeans.', '', 'camisa-de-jeans-san-lorenzo')),
 ('RB077', ('Camisa Puccini', 'Camisas y blusas', 'Camisa con botones hasta la mitad. En blanco o celeste.', 'Blanco / Celeste', 'camisa-puccini')),
 ('RB078', ('Camisa Borgo Pinti', 'Camisas y blusas', 'Camisa liviana de manga larga, abotonada entera. En blanco o celeste.', 'Blanco / Celeste', 'camisa-borgo-pinti')),
])
# filas del Excel que son el mismo producto en otro color: se suman a la fila principal
FUSIONES = {'RB018': 'RB017', 'RB058': 'RB057'}   # RB056 dejó de fusionarse con RB055 el 14-10: Michelle lo separó como 'Ridge Cons'
# correcciones de stock que Michelle avisó por WhatsApp y todavía no están en su Excel (código → stock por talla)
AJUSTES_STOCK = {}   # 19-10: Michelle borró la fila vieja RB056; Ridge Cons sale directo de su Inventario
ORDEN_TALLAS = ['XS', 'S', 'M', 'L', 'XL', 'TU']

def main():
    wb = openpyxl.load_workbook(XLSX, data_only=True)
    cat = {}
    for r in wb['Catalogo ok'].iter_rows(min_row=7, values_only=True):
        if not r[0]: continue
        cod = r[0].split('·')[0].strip()
        cat[cod] = {'proveedor': r[1], 'nota': r[2], 'precio': r[3], 'tallas_nota': r[4]}
    wv = openpyxl.load_workbook(XLSX_VENTAS, data_only=True)
    costo = {}
    for r in wv['Catalogo'].iter_rows(min_row=4, values_only=True):
        if r[0] and str(r[0]).startswith('RB'):
            cod = r[0].split('·')[0].strip(); costo[cod] = round(r[5] or 0)
            cat.setdefault(cod, {'proveedor': r[1], 'nota': r[2], 'precio': r[3], 'tallas_nota': r[4]})   # productos agregados después (RB069)
            cat[cod]['desc_excel'] = (r[2] or '').strip()
            if r[3]: cat[cod]['precio'] = int(round(float(r[3])))   # el precio vigente es el del control de ventas (Michelle lo cambia ahí; 14-10 subió poleras)
            cat[cod]['desc2'] = (r[8] or '').strip() if len(r) > 8 else ''   # columna "Descipcion 2.0" (Michelle, 11-10): si tiene texto, manda sobre la descripción del script
    inv = {}
    for r in wv['Inventario'].iter_rows(min_row=5, values_only=True):
        if not r[0] or not str(r[0]).startswith('RB'): continue
        cod = r[0].split('·')[0].strip(); cod = FUSIONES.get(cod, cod)
        talla = str(r[1]).strip().upper()
        d = inv.setdefault(cod, {})
        d[talla] = max(0, d.get(talla, 0) + int(r[4] or 0))   # stock actual (ya descontadas las ventas confirmadas); nunca negativo (Logetta venía en -1)
    for cod, ajuste in AJUSTES_STOCK.items(): inv[cod] = dict(ajuste)
    # productos nuevos que Michelle todavía no pasa a Inventario: se usa el stock que anotó en Catálogo ('3TU') hasta que exista la fila
    import re as _re
    for cod in P:
        if cod not in inv and cod in cat:
            m = _re.fullmatch(r'\s*(\d+)\s*TU\s*', str(cat[cod].get('tallas_nota') or ''))
            if m: inv[cod] = {'TU': int(m.group(1))}
    fotos = {}
    if FOTOS_CSV.exists():
        for r in csv.DictReader(open(FOTOS_CSV, encoding='utf-8')):
            fotos.setdefault(r['handle'], []).append(r['archivo_web'])
    filas = []
    for cod, (nombre, categoria, desc, colores, foto_key) in P.items():
        c = cat[cod]
        stock = inv.get(cod, {})
        tallas = [t for t in ORDEN_TALLAS if t in stock]
        skus = cod + ('+' + ','.join(k for k, v in FUSIONES.items() if v == cod) if cod in FUSIONES.values() else '')
        # la columna Descripción del Excel son apuntes de inventario ("2 rosadas, 2 verdes"); no se usa en la web. Si Michelle la reescribe, se revisa y se copia aquí.
        if c.get('desc2'): desc = c['desc2']
        pend = []
        if not desc: pend.append('descripción')
        if not tallas: pend.append('tallas')
        filas.append({
            'handle': slug(nombre), 'sku': skus, 'nombre_web': nombre, 'nombre_proveedor': c['proveedor'],
            'categoria_web': categoria, 'tipo': nombre.split(' ')[0],
            'descripcion': desc, 'tallas': ', '.join(tallas), 'colores': colores,
            'precio_clp': c['precio'] or '', 'costo_clp': costo.get(cod, ''),
            'stock': '|'.join(f'{t}:{stock[t]}' for t in tallas), 'stock_total': sum(stock.values()),
            'imagenes': ','.join(fotos.get(foto_key, [])) if foto_key else '',
            'estado': 'activo' if (c['precio'] and tallas) else 'incompleto',
            'nota_interna': c['nota'] or '', 'pendiente': '; '.join(pend),
        })
    # accesorios: lista maestra en accesorios.csv (hoja "Catálogo tienda (vista)" de Javier + precios del Excel de Michelle).
    # Entran a la tienda solo cuando tienen precio y stock; mientras tanto quedan como 'incompleto' en catalogo.csv.
    # 17-10: Michelle ya tiene los accesorios (AC…) en Catálogo e Inventario. Se cruzan por nombre, no por código,
    # porque ella repite algunos códigos (AC29, AC31). Precio y stock salen de su Excel; el costo, solo si no es el
    # $2.500 de relleno. Lo que no está en su Excel sigue con lo de accesorios.csv.
    def _n(t):
        t = unicodedata.normalize('NFKD', str(t)).encode('ascii', 'ignore').decode().lower()
        return re.sub(r'[^a-z0-9]+', ' ', t).strip()
    ALIAS_ACC = {'Aro Hoja doré': 'aros hoja dore', 'Aro Hoja black': 'aros hoja black', 'Botón de camisa Tiger': 'boton tiger',
                 'Earcuff Diamonds': 'earcuff diamonds', 'Earcuff Stars': 'earcuff star', 'Prendedor Abejitas mini': 'prendedor mini abejitas',
                 'Prendedor Gold XXL': 'prendedor gold xl', 'Prendedor Planta': 'prendedor plants dore', 'Prendedor Plumas': 'prendor plumas'}
    wb_v = openpyxl.load_workbook(XLSX_VENTAS, data_only=True)
    cat_ac, inv_ac = {}, {}
    for row in wb_v['Catalogo'].iter_rows(values_only=True):
        if row[0] and str(row[0]).strip().startswith('AC') and '·' in str(row[0]):
            k = _n(str(row[0]).split('·', 1)[1]); k = ' '.join(dict.fromkeys(k.split()))   # 'EARCUFF DIAMONDS\n\nEARCUFF DIAMONDS'
            cat_ac[k] = row
    for row in wb_v['Inventario'].iter_rows(values_only=True):
        if row[0] and str(row[0]).strip().startswith('AC') and '·' in str(row[0]):
            k = _n(str(row[0]).split('·', 1)[1]); inv_ac[' '.join(dict.fromkeys(k.split()))] = row
    def _buscar(tabla, nombre):
        for k in (_n(nombre), ALIAS_ACC.get(nombre)):
            if k and k in tabla: return tabla[k]
    RETIRADOS_ACC = {'Botón de camisa Tiger'}   # 20-10: Michelle lo borró de su Excel. 27-10: el Collar Ají volvió (AC45) y se muestra de nuevo
    ACC = AQUI / 'accesorios.csv'
    if ACC.exists():
        for r in csv.DictReader(open(ACC, encoding='utf-8')):
            nombre = r['nombre'].strip(); h = slug(nombre); key = 'acc-' + h
            if nombre in RETIRADOS_ACC: continue
            st = int(r['stock_tu']) if (r.get('stock_tu') or '').strip().isdigit() else None   # None = stock por confirmar
            precio = (r.get('precio_clp') or '').strip()
            c_ex, i_ex = _buscar(cat_ac, nombre), _buscar(inv_ac, nombre)
            if c_ex and isinstance(c_ex[3], (int, float)) and c_ex[3]: precio = str(int(round(c_ex[3])))
            if c_ex and isinstance(c_ex[5], (int, float)) and c_ex[5] and round(c_ex[5]) != 2500: r['costo_clp'] = str(int(round(c_ex[5])))
            if i_ex and isinstance(i_ex[4], (int, float)): st = max(0, int(i_ex[4]))
            if c_ex: r['codigo'] = str(c_ex[0]).split('·')[0].strip()   # 18-10: el código vigente es el del Catálogo de Michelle (ella los renumeró)
            pend = [x for x, falta in (('precio', not precio), ('stock', st is None), ('costo', not (r.get('costo_clp') or '').strip())) if falta]
            filas.append({
                'handle': h, 'sku': r['codigo'], 'nombre_web': nombre, 'nombre_proveedor': nombre.upper(),
                'categoria_web': 'Accesorios', 'tipo': nombre.split(' ')[0],
                'descripcion': r.get('descripcion', ''), 'tallas': 'TU', 'colores': r.get('colores', ''),
                'precio_clp': precio, 'costo_clp': (r.get('costo_clp') or '').strip(),
                'stock': f'TU:{st}' if st is not None else '', 'stock_total': st or 0,
                'imagenes': ','.join(fotos.get(key, [])),
                'estado': ('activo' if st is not None else 'sin stock') if precio else 'incompleto',   # 'sin stock' = se muestra en la web, va como borrador a Shopify
                'nota_interna': r.get('origen', ''), 'pendiente': '; '.join(pend),
            })
    with open(SALIDA, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys())); w.writeheader(); w.writerows(filas)
    con_foto = sum(1 for f in filas if f['imagenes']); agot = sum(1 for f in filas if f['stock_total'] == 0)
    print(f'{len(filas)} productos · {con_foto} con foto · {agot} agotados · stock total {sum(f["stock_total"] for f in filas)}')

if __name__ == '__main__':
    main()
