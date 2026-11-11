#!/usr/bin/env python3
"""Genera catalogo-shopify.csv y catalogo-jumpseller.csv desde catalogo.csv (planilla neutra).
Uso: python3 generar-csv.py [--base-imagenes https://host/fotos/]
No inventa datos: sin talla ni precio, el producto sale como borrador / no disponible.
"""
import csv, sys, re, pathlib
here = pathlib.Path(__file__).parent
base_img = 'https://www.banditas.cl/img/'   # Shopify y Jumpseller necesitan URL directa; la vitrina las sirve (19-10: dominio propio)
if '--base-imagenes' in sys.argv:
    base_img = sys.argv[sys.argv.index('--base-imagenes') + 1].rstrip('/') + '/'

TALLAS_EU = {'XS': '34', 'S': '36', 'M': '38', 'L': '40', 'XL': '42'}

def stock_por_talla(r):
    return {k: int(v) for k, v in (x.split(':') for x in (r.get('stock') or '').split('|') if ':' in x)}

def tallas(s, r=None):
    st = stock_por_talla(r) if r else {}
    if st: return [] if list(st) == ['TU'] else list(st)   # talla única = producto sin variantes
    s = (s or '').strip()
    if not s or s.upper() == 'TU': return []
    return [x.strip().upper() for x in s.split(',')]

def colores(s):
    return [c.strip() for c in (s or '').split('/') if c.strip()]

def dims(ts, cs):
    d = []
    if ts: d.append(('Talla', ts))
    if len(cs) > 1: d.append(('Color', cs))
    return d

def sku_var(sku, t, c):
    def k(x): return re.sub(r'[^A-Z0-9]+', '', x.upper().replace('Ú', 'U'))[:6] if x else ''
    return '-'.join(p for p in [sku, k(t), k(c)] if p)

rows = list(csv.DictReader(open(here / 'catalogo.csv', encoding='utf-8')))
rows = [r for r in rows if r.get('precio_clp')]   # sin precio no se importa; sin stock va como borrador (draft / not-available)
for r in rows:   # los colores disponibles van al final de la descripción
    if r.get('colores') and '/' in r['colores'] and 'Colores:' not in r['descripcion']:
        r['descripcion'] = (r['descripcion'] + ' Colores: ' + r['colores'] + '.').strip()

# ---------- Shopify ----------
sh_cols = ['Title', 'URL handle', 'Description', 'Vendor', 'Product category', 'Type', 'Tags',
           'Published on online store', 'Status', 'SKU', 'Option1 name', 'Option1 value',
           'Option2 name', 'Option2 value', 'Price', 'Compare-at price', 'Cost per item',
           'Charge tax', 'Inventory tracker', 'Inventory quantity', 'Continue selling when out of stock',
           'Requires shipping', 'Product image URL', 'Image position', 'Image alt text',
           'SEO title', 'SEO description']
sh = []
for r in rows:
    ts, cs = tallas(r['tallas'], r), []           # los colores van en la descripción: el inventario no separa stock por color
    st = stock_por_talla(r)
    listo = bool(r['precio_clp']) and bool(st) and bool(r['imagenes'].strip())   # sin foto va como borrador
    imgs = [i.strip() for i in r['imagenes'].split(',') if i.strip()]
    d = dims(ts, cs)
    combos = [(t, c) for t in (ts or ['']) for c in (cs if len(cs) > 1 else [''])]
    first = True
    for t, c in combos:
        vals = [t, c] if ts else [c, '']
        row = {k: '' for k in sh_cols}
        row['URL handle'] = r['handle']
        if first:
            row.update({'Title': r['nombre_web'], 'Description': r['descripcion'],
                        'Vendor': 'Banditas Chile', 'Type': r['categoria_web'],
                        'Tags': r['tipo'], 'Published on online store': 'TRUE' if listo else 'FALSE',
                        'Status': 'active' if listo else 'draft',
                        'SEO title': f"{r['nombre_web']} | Banditas Chile",
                        'SEO description': r['descripcion'][:155]})
            if imgs:
                row['Product image URL'] = base_img + imgs[0]; row['Image position'] = '1'
                row['Image alt text'] = r['nombre_web']
        row.update({'SKU': sku_var(r['sku'], t, c),
                    'Option1 name': d[0][0] if d else 'Title',
                    'Option1 value': vals[0] if d else 'Default Title',
                    'Option2 name': d[1][0] if len(d) > 1 else '',
                    'Option2 value': vals[1] if len(d) > 1 else '',
                    'Price': r['precio_clp'], 'Cost per item': r['costo_clp'],
                    'Charge tax': 'TRUE', 'Inventory tracker': 'shopify',
                    'Inventory quantity': str(st.get(t, st.get('TU', 0))),
                    'Continue selling when out of stock': 'FALSE', 'Requires shipping': 'TRUE'})
        sh.append(row); first = False
    for i, img in enumerate(imgs[1:], start=2):
        sh.append({**{k: '' for k in sh_cols}, 'URL handle': r['handle'],
                   'Product image URL': base_img + img, 'Image position': str(i),
                   'Image alt text': r['nombre_web']})
with open(here / 'catalogo-shopify.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=sh_cols); w.writeheader(); w.writerows(sh)

# ---------- Shopify, formato clásico (Handle / Body (HTML) / Variant ...) por si el importador rechaza el nuevo ----------
cl_cols = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Product Category', 'Type', 'Tags', 'Published',
           'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value',
           'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy',
           'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping',
           'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card',
           'SEO Title', 'SEO Description', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per item', 'Status']
cl = []
for r in sh:
    row = {k: '' for k in cl_cols}
    row.update({'Handle': r['URL handle'], 'Title': r['Title'], 'Body (HTML)': ('<p>' + r['Description'] + '</p>') if r['Description'] else '',
                'Vendor': r['Vendor'], 'Type': r['Type'], 'Tags': r['Tags'], 'Published': r['Published on online store'],
                'Option1 Name': r['Option1 name'], 'Option1 Value': r['Option1 value'], 'Option2 Name': r['Option2 name'], 'Option2 Value': r['Option2 value'],
                'Variant SKU': r['SKU'], 'Variant Price': r['Price'], 'Cost per item': r['Cost per item'],
                'Image Src': r['Product image URL'], 'Image Position': r['Image position'], 'Image Alt Text': r['Image alt text'],
                'SEO Title': r['SEO title'], 'SEO Description': r['SEO description'], 'Status': r['Status']})
    if r['SKU']:
        row.update({'Variant Grams': '0', 'Variant Inventory Tracker': 'shopify', 'Variant Inventory Qty': r['Inventory quantity'],
                    'Variant Inventory Policy': 'deny', 'Variant Fulfillment Service': 'manual', 'Variant Requires Shipping': 'TRUE',
                    'Variant Taxable': 'TRUE', 'Variant Weight Unit': 'g'})
    if r['Title']: row['Gift Card'] = 'FALSE'
    cl.append(row)
with open(here / 'catalogo-shopify-clasico.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cl_cols); w.writeheader(); w.writerows(cl)

# ---------- Jumpseller ----------
js_cols = ['Permalink', 'Name', 'Description', 'Meta Title', 'Meta Description', 'Width', 'Length',
           'Height', 'Brand', 'Barcode', 'Categories', 'Images', 'Digital', 'Featured', 'Status',
           'SKU', 'Weight', 'Cost per item', 'Compare at price', 'Stock', 'Stock Unlimited',
           'Stock Notification', 'Stock Threshold', 'Price', 'Quotable', 'Minimum Quantity',
           'Maximum Quantity', 'Variant Image', 'Variant 1 Option Name', 'Variant 1 Option Type',
           'Variant 1 Option Value', 'Variant 1 Option Custom', 'Variant 2 Option Name',
           'Variant 2 Option Type', 'Variant 2 Option Value', 'Variant 2 Option Custom']
js = []
for r in rows:
    ts, cs = tallas(r['tallas'], r), []
    st = stock_por_talla(r)
    listo = bool(r['precio_clp']) and bool(st) and sum(st.values()) > 0 and bool(r['imagenes'].strip())
    imgs = [base_img + i.strip() for i in r['imagenes'].split(',') if i.strip()]
    head = {k: '' for k in js_cols}
    head.update({'Permalink': '',  # vacío: Jumpseller lo crea desde el nombre
                 'Name': r['nombre_web'], 'Description': r['descripcion'],
                 'Meta Title': f"{r['nombre_web']} | Banditas Chile",
                 'Meta Description': r['descripcion'][:155], 'Brand': 'Banditas Chile',
                 'Categories': r['categoria_web'], 'Images': ','.join(imgs), 'Digital': 'NO',
                 'Featured': 'NO', 'Status': 'available' if listo else 'not-available',
                 'Stock Unlimited': 'NO', 'Quotable': 'NO'})
    d = dims(ts, cs)
    combos = [(t, c) for t in (ts or ['']) for c in (cs if len(cs) > 1 else [''])]
    if not d:  # sin variantes: una sola fila
        head.update({'SKU': r['sku'], 'Stock': str(st.get('TU', 0)), 'Price': r['precio_clp'] or '0',
                     'Cost per item': r['costo_clp']})
        js.append(head); continue
    head.update({'Stock': '0', 'Price': '0'}); js.append(head)   # fila madre, exige Stock y Price
    for t, c in combos:
        v = {k: '' for k in js_cols}
        vals = [t, c] if ts else [c, '']
        v.update({'Permalink': r['handle'], 'SKU': sku_var(r['sku'], t, c),
                  'Stock': str(st.get(t, 0)), 'Price': r['precio_clp'] or '0',
                  'Cost per item': r['costo_clp'], 'Stock Unlimited': 'NO',
                  'Variant 1 Option Name': d[0][0], 'Variant 1 Option Type': 'option',
                  'Variant 1 Option Value': vals[0]})
        if len(d) > 1:
            v.update({'Variant 2 Option Name': d[1][0], 'Variant 2 Option Type': 'option',
                      'Variant 2 Option Value': vals[1]})
        js.append(v)
with open(here / 'catalogo-jumpseller.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=js_cols); w.writeheader(); w.writerows(js)

print(f"Shopify: {len(sh)} filas · Jumpseller: {len(js)} filas · productos: {len(rows)}")
print("Nota: en la fila madre de Jumpseller el Permalink va vacío al crear; las filas de variante "
      "llevan el handle para agruparse. Tras la primera importación, usar el permalink real.")
