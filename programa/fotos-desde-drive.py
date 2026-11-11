"""Lee el orden de fotos desde los nombres que Michelle pone en el Drive (modelo + número; 1 = principal).
Entrada: un JSON con el listado de imágenes del Drive (search_files: title, fileSize, id, parentId).
Salida: orden-drive.json = {handle: [{'title','size','id'}...]} en el orden de Michelle, solo carpetas vigentes de "Catalogo web y wsp".
Uso: python3 fotos-desde-drive.py listado.json"""
import json, re, sys, unicodedata, pathlib, collections
AQUI = pathlib.Path(__file__).parent
CARPETAS = {'1O6XHkAlbZpFL8QCy3kxHRoN8Vh2BqIhy': 'Enteritos', '1qxJD9MWokdC5AlR_w2xQzKFV7TiRLLEf': 'jeans', '1JXI98YhREAcVI8LiIF3CKtpKy6n0i15p': 'chaquetas',
            '1Rww-kkgpMj2RbKdD7YGXQGtLimnfjIYP': 'blusas - camisas', '1AQolb26Xv4HTZNYDWWAqZPguRAehUzca': 'vestidos', '1Su8jqrcRg18xxrVampRpCrz_6KhWO3wC': 'Polerones y chalecos',
            '1CLYNsh9zO3_lRTlxxpKu5hb-JuwNPqQq': 'Pantalones', '1oMgI-1L4E7RSMUWv8NFRNJ76ioDNOztr': 'poleras'}
# palabra del modelo (como la escribe Michelle) → handle de la foto. El orden importa: lo más específico primero.
MODELOS = [
    ('borgo pinti', 'camisa-borgo-pinti'), ('borgopinti', 'camisa-borgo-pinti'), ('puccini', 'camisa-puccini'), ('san lorenzo', 'camisa-de-jeans-san-lorenzo'),
    ('santa trinita', 'blazer-santa-trinita'), ('merini hola', 'blazer-merini-hola'), ('merini art', 'blazer-merini-art'), ('portaromana', 'bermuda-leopardo-portaromana'), ('bermudas de leopardo', 'bermuda-leopardo-portaromana'),
    ('roland', 'chaqueta-de-jeans-roland'), ('delight', 'pantalon-delight'),
    ('deneb beach', 'polera-deneb-beach'), ('ridge beach', 'polera-deneb-beach'), ('deneb star', 'polera-deneb-star'), ('deneb', 'polera-estrella'),
    ('strange love', 'polera-strange-love'), ('strange', 'polera-doctor-strange'), ('gaiola', 'polera-love'), ('logetta', 'polera-love-logetta'),
    ('ridge cons', 'polera-ridge-cons'), ('ridge relax', 'polera-anticons'), ('thor', 'polera-thor'), ('englewood', 'polera-de-encaje-englewood'),
    ('clavel', 'polera-a-rayas-clavel'), ('caketin', 'polera-cuello-v-paradise'), ('bolzano', 'polera-bolzano'), ('circle', 'polera-circle'), ('circel', 'polera-circle'),
    ('blanket', 'bermuda-de-jeans-blanket'), ('edgewater', 'bermuda-de-jeans-edgewater'), ('posillipo', 'bermuda-de-jeans-posillipo'),
    ('collatino', 'falda-de-jeans-collatino'), ('labiciano', 'chaleco-de-jeans-labiciano'), ('materdai', 'jardinera-de-jeans-materdai'),
    ('delphine', 'pantalon-de-jeans-delphine'), ('bagnoli', 'jeans-bomber-bagnoli'), ('hamal', 'jeans-hamal'), ('larch', 'jeans-pescador-larch'),
    ('ciop', 'chaqueta-poleron-ciop'), ('montesacro', 'chaqueta-de-jeans-montesacro'),
    ('chester', 'pantalon-de-lino-chester'), ('chopping', 'pantalon-leopardo-chopping'), ('fever', 'pantalon-de-buzo-fever'), ('homan', 'pantalon-de-buzo-homan'),
    ('marbel', 'pantalon-de-buzo-marble'), ('marble', 'pantalon-de-buzo-marble'), ('ventura', 'pantalon-vintage-ventura'), ('fiffidi', 'pantalon-militar-fiffidi'),
    ('asparago', 'chaqueta-cuadrille-asparago'), ('belle', 'chaqueta-de-jeans-belle'), ('biene', 'camisa-de-jeans-biene'), ('casperino', 'chaqueta-militar-casperino'),
    ('kimono', 'chaqueta-kimono'), ('marvel', 'chaqueta-de-lino-marvel'), ('pallide', 'chaqueta-tejida-pallide'), ('peeler', 'chaqueta-leopardo-chopping'),
    ('porter', 'chaqueta-jaspeada-porter'), ('rodi', 'chaqueta-rodi'), ('solana', 'chaqueta-veraniega-solana'), ('sangiovese', 'chaleco-oversize-sangiovese'),
    ('cameron', 'camisa-estampada-cameron'), ('torrone', 'blusa-de-encaje-torrone'), ('adda', 'camisa-escocesa-adda'), ('agatha', 'camisa-de-lino-agata'),
    ('agata', 'camisa-de-lino-agata'), ('opener', 'blusa-a-rayas-opener'),
    ('rase', 'enterito-de-jeans-rase-top'), ('sisine', 'enterito-animal-print-sisine'), ('spinne', 'enterito-de-jeans-spinne'),
    ('divina', 'chaleco-con-flecos-divina'), ('lia', 'chaleco-lia'), ('rita', 'chaleco-de-lana-rita'), ('tai', 'chaleco-tai'),
    ('basilea', 'poleron-basilea'), ('birch', 'poleron-birch'), ('mintaka', 'poleron-mintaka'), ('mirach', 'poleron-mirach'),
    ('decumani', 'vestido-decumani'), ('fidene', 'vestido-tenido'), ('imprime', 'vestido-de-jeans-imprime'), ('parione', 'vestido-de-jeans-imprime'),
    ('iron', 'vestido-primaveral-iron-fist'), ('monclaire', 'vestido-largo-monclaire'), ('namrek', 'vestido-estampado-namrek'),
    ('sirio', 'vestido-sirio'), ('terrano', 'vestido-canguro-terrano'),
]
# 20-10: ajustes por id del Drive. 'ignorar' = copia repetida; 'despues' = va al final, tras las fotos que Michelle numeró.
AJUSTES = {'1r1sfm4QgNtOGu4zh10_34hWVJBhl-G20': 'ignorar', '1Uf7Li52_NQhyygaBhxXiQH6IBYx7Mncr': 'ignorar', '1JKXksxS_06q1z8GlwNVDgTdupz429sgu': 'ignorar',   # Blazer Santa Trinita PNG = Veste Santa Trinita 1-3
           '1fjZJrkdRrlFJUtd9HX1bkBxtaSDDa4Si': 'ignorar', '1RPDgTqACIunRSF2_vk2eUw8H4jmEmCsr': 'ignorar',   # 23-10: Deneb Star naranja, agotada (Michelle)
           '1JdicOJpJt5y-7JjyaZ2x1M---rOP3xBD': 'despues', '1-qEnc_UhQfwSVM7CrNU_-2u10-tw4hHS': 'despues', '14jhrp8khChoIhLoBetituas6ZMlnKdfk': 'despues'}   # San Lorenzo PNG: después de las 1-4 nuevas
def norm(t):
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    t = re.sub(r'\.(jpe?g|png|jfif|webp)$', '', t); t = re.sub(r'png$', '', t)
    return re.sub(r'[_\s]+', ' ', t).strip()
def leer(listado):
    grupos = collections.defaultdict(list); sin = []
    for f in listado:
        if f.get('parentId') not in CARPETAS or not f.get('mimeType', 'image/').startswith('image/') or AJUSTES.get(f['id']) == 'ignorar': continue
        n = norm(f['title'])
        # 18-10: un look con dos modelos ("Chaqueta Roland y Bermuda Posillipo-1") va a los dos productos, después de sus fotos propias
        hits, usados_h = [], set()
        for k, h in MODELOS:
            mk = re.search(r'(?<![a-z])' + k + r'(?![a-z])', n)
            if mk and h not in usados_h and not any(a < mk.end() and mk.start() < b for a, b, _, _ in hits):
                hits.append((mk.start(), mk.end(), k, h)); usados_h.add(h)
        if not hits: sin.append(f['title']); continue
        combo = len(hits) > 1
        for a, b, k, h in hits:
            resto = n[b:]
            m = re.search(r'\d+', resto)
            num = int(m.group()) if m else None
            variante = resto[:m.start()].strip(' ()') if m else resto.strip(' ()')
            if combo: variante = ''
            if AJUSTES.get(f['id']) == 'despues' and num is not None: num += 100
            grupos[h].append({'title': f['title'], 'size': int(f.get('fileSize') or 0), 'id': f['id'], 'num': num, 'var': variante, 'combo': combo})
    orden = {}
    for h, fs in grupos.items():
        usados = {f['num'] for f in fs if f['num'] is not None and not f['combo']}
        libre = (i for i in range(1, 100) if i not in usados)
        for f in sorted([f for f in fs if f['num'] is None], key=lambda f: f['title'].lower()): f['num'] = next(libre)   # sin número: el primer número que falte
        orden[h] = [{'title': f['title'], 'size': f['size'], 'id': f['id']} for f in sorted(fs, key=lambda f: (f['combo'], f['num'], f['var'], f['title'].lower()))]
    return orden, sin
if __name__ == '__main__':
    orden, sin = leer(json.load(open(sys.argv[1], encoding='utf-8')))
    json.dump(orden, open(AQUI / 'orden-drive.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(orden), 'productos,', sum(len(v) for v in orden.values()), 'fotos; sin modelo reconocido:', sin)
