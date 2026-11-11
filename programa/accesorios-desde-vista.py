"""Rearma accesorios.csv desde la exportación CSV de la hoja "Catálogo tienda (vista)" (carpeta Tienda en el Drive).
Uso: exportar la hoja como CSV (Archivo → Descargar → CSV) a vista-AAAA-MM-DD.csv y correr: python3 accesorios-desde-vista.py vista-AAAA-MM-DD.csv
Conserva precio/costo/stock ya puestos en accesorios.csv si la hoja viene vacía en esa celda, y mantiene las fotos asignadas."""
import csv, sys, pathlib
AQUI = pathlib.Path(__file__).parent
vista = sys.argv[1] if len(sys.argv) > 1 else sorted(AQUI.glob('vista-*.csv'))[-1]
viejo = {r['codigo']: r for r in csv.DictReader(open(AQUI / 'accesorios.csv', encoding='utf-8'))} if (AQUI / 'accesorios.csv').exists() else {}
campos = ['codigo', 'nombre', 'categoria', 'descripcion', 'colores', 'precio_clp', 'costo_clp', 'stock_tu', 'fotos', 'origen']
filas = []
for r in csv.DictReader(open(vista, encoding='utf-8')):
    if r.get('Categoría') != 'Accesorios': continue
    cod = r['Código']; v = viejo.get(cod, {})
    def num(x):   # '14990', '$14.990', '1391,11' (coma decimal) → entero en pesos
        x = (x or '').strip().replace('$', '').replace(' ', '')
        if ',' in x: x = x.replace('.', '').replace(',', '.')
        elif x.count('.') >= 1 and len(x.split('.')[-1]) == 3: x = x.replace('.', '')
        try: return str(int(round(float(x)))) if x else ''
        except ValueError: return ''
    stock = num(r.get('Stock total')) or num((r.get('Stock por talla') or '').replace('TU:', ''))
    filas.append({'codigo': cod, 'nombre': (r['Nombre en la tienda'] or v.get('nombre', '')).strip(), 'categoria': 'Accesorios',
                  'descripcion': (r.get('Descripción') or v.get('descripcion', '')).strip(), 'colores': (r.get('Colores') or v.get('colores', '')).strip(),
                  'precio_clp': num(r.get('Precio CLP')) or v.get('precio_clp', ''), 'costo_clp': num(r.get('Costo CLP')) or v.get('costo_clp', ''),
                  'stock_tu': stock or v.get('stock_tu', ''), 'fotos': v.get('fotos', ''), 'origen': 'vista ' + pathlib.Path(vista).stem})
for cod, v in viejo.items():   # filas que están en accesorios.csv y no en la hoja (p. ej. Aros Circle) se conservan
    if cod not in {f['codigo'] for f in filas}: filas.append(v)
filas.sort(key=lambda f: f['codigo'])
with open(AQUI / 'accesorios.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=campos); w.writeheader(); w.writerows(filas)
print(len(filas), 'accesorios;', sum(1 for f in filas if f['precio_clp'] and f['stock_tu']), 'con precio y stock')
