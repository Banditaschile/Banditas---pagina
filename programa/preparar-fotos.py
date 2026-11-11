#!/usr/bin/env python3
"""Toma las fotos elegidas de "Catalogo Octubre 2026" (zip del Drive de Michelle, descomprimido en
~/Downloads) y las deja listas para la web en sitio/img, recortadas 3:4 y nombradas por producto.
También escribe fotos.csv (handle → archivos de origen) y rellena la columna imagenes de catalogo.csv.
"""
import csv, pathlib, io
from PIL import Image, ImageFilter, ImageOps

ORIGEN = pathlib.Path.home() / 'Downloads' / 'Catalogo Octubre 2026'
AQUI = pathlib.Path(__file__).parent
IMG = AQUI / 'sitio' / 'img'
CATALOGO = AQUI.parent / 'catalogo.csv'
PORTADA = AQUI.parent.parent.parent / 'contexto' / 'fotos-portada'   # fotos que mandó Michelle para la portada
DRIVE = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-10'
DRIVE16 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-11-01'  # 1-11: fotos de los 9 accesorios que faltaban (subidas al Drive el 28-10) en accesorios/
DRIVE15 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-27'  # 27-10: 20 fotos de accesorios nuevos (AC33-AC58) en accesorios/
DRIVE14 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-23'  # 23-10: Circle 1 y 3 y Englewood 1 editadas por Michelle, fotos de Michelle y Valerie
DRIVE13 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-21'  # 21-10: Camisa Puccini 1-5, Polerón Mirach 1, Borgo Pinti 3 jpeg, Merini Art 3 jpg
DRIVE12 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-20'  # 20-10: Merini Hola y Art, Santa Trinita en jpeg, San Lorenzo 1-4, Aros Circle, carta corazón
DRIVE11 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-19'  # 19-10: Dr Strange 4 y 5
DRIVE10 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-18'  # 18-10: Santa Trinita, San Lorenzo, look Roland + Posillipo
DRIVE9 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-17'   # 17-10: Roland/Delight, Portaromana, Borgo Pinti 1-3 (bajadas por la API del Drive)
DRIVE8 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-16'   # 16-10: Ridge Relax 1 y blanca 2, Camisa Borgo Pinti
DRIVE7 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-15b'  # 15-10 tarde: Thor, Gaiola, Strange, Casperino y el prendedor
DRIVE6 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-15'   # 15-10: fotos que faltaban tras el renombre de Michelle
DRIVE5 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-14'   # 14-10: fotos nuevas que subió Michelle al numerar
DRIVE4 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-12'   # 12-10: PNG editados con IA por Michelle + carpeta accesorios/ (39 fotos)
DRIVE3 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-11b'  # barrido completo del Drive, 11-10 tarde (29+7 archivos que faltaban)
DRIVE2 = pathlib.Path.home() / 'Downloads' / 'Drive Banditas 2026-10-11'   # vestidos, polerones y lo que renombró Michelle el 11-10   # fotos con nombre que subió Michelle al Drive el 10-10 (bajadas con Chrome)

# handle → lista de archivos de origen (el primero es la foto principal). «ia» = foto editada con IA (fondo/modelo generados)
FOTOS = {
    'enterito-animal-print-sisine': ['DRIVE/Enterito Sisine.jfif', 'DRIVE/Enterito Sisine (2).jfif'],
    'camisa-de-lino-agata': ['Camisa Agatha.jfif'],
    'chaqueta-leopardo-chopping': ['DRIVE/Chaqueta Conjunto Chopping.jfif', 'DRIVE/WhatsApp Image 2026-10-10 at 17.45.58 (1).jpeg'],
    'pantalon-leopardo-chopping': ['DRIVE/Pantalon Conjunto Chopping.jfif', 'DRIVE/WhatsApp Image 2026-10-10 at 17.45.56 (2).jpeg'],
    'pantalon-de-buzo-fever': ['DRIVE2/Conjunto Rodi Band 2.jpeg', 'DRIVE2/Conjunto Rodi Band.jpeg', 'pantalones buzo.jpeg'],
    'pantalon-vintage-ventura': ['DRIVE/Pantalón Ventura.png', 'DRIVE/Pantalon ventura.jpg'],
    'blusa-a-rayas-opener': ['Camisa Opener.jpeg', 'camisa rayas detalle bordado.jpeg', 'DRIVE3/Camisa Opener (2).jpeg'],
    'polera-love': ['WhatsApp Image 2026-07-15 at 08.20.37 (1).jpeg', 'ad271e77-b961-4aec-a2a4-452c14cf02dc.jfif'],
    'vestido-de-jeans-imprime': ['DRIVE2/vestido imprime (2).jpeg', 'DRIVE2/Vestido Imprime.jpeg', 'DRIVE2/Vestido imprime (3).jpeg', 'DRIVE2/Vestido Imprime.jfif'],
    'vestido-largo-monclaire': ['Vestido Buzo lila.jpeg', 'DRIVE2/Vestido Monclaire.jpg', 'DRIVE2/Vestido Monclaire.jpeg', 'DRIVE2/Vestido Monclaire.png'],
    'vestido-primaveral-iron-fist': ['vestido blanco y negro.jpeg', 'vestido negro.jpeg', 'DRIVE2/Vestido Iron.jfif', 'DRIVE2/Vestido Iron.jpeg'],
    'chaleco-oversize-sangiovese': ['DRIVE/WhatsApp Image 2026-10-10 at 17.45.58 (5).jpeg', 'DRIVE/WhatsApp Image 2026-10-10 at 17.45.58 (6).jpeg', 'DRIVE4/Gilet Sangiovese.png', 'DRIVE4/Gilet Sangiovese_1.png'],
    'chaleco-de-jeans-labiciano': ['Gilet Sangiovese.jpeg'],
    'jeans-bomber-bagnoli': ['DRIVE2/JEans Bagnoli.png', 'Jeans Bagnoli.webp'],  # 'jeans borde cafe.jpeg' era Hamal (Michelle lo renombró el 11-10)
    'falda-de-jeans-collatino': ['falda jeans.jpeg', 'Falda Collationo (2).jpeg', 'DRIVE/Falda Collationo.jpeg', 'DRIVE/WhatsApp Image 2026-10-08 at 16.30.57 (3).jpeg'],
    'bermuda-de-jeans-blanket': ['Bermuda Blanket.jpg', 'Bermuda Blanket (2).jpg'],
    'jardinera-de-jeans-materdai': ['DRIVE/jardinera materdai.jpeg', 'Jardinera jeans.jpeg', 'DRIVE/Jardinera Materdai (1).jpeg'],
    'chaqueta-veraniega-solana': ['Chaqueta Solana.jpg', 'Chaqueta Solana (3).jpg'],
    'polera-cuello-v-paradise': ['WhatsApp Image 2026-07-15 at 08.20.46 (3).jpeg', 'WhatsApp Image 2026-07-15 at 08.20.36 (4).jpeg', 'DRIVE/Polera Caketin (3).jpeg'],
    'polera-more': ['WhatsApp Image 2026-07-15 at 08.20.42 (2).jpeg', 'WhatsApp Image 2026-07-15 at 08.20.42 (1).jpeg'],
    'polera-anticons': ['DRIVE/Polera ridge relax.jfif', 'DRIVE/Polera ridge.jpeg', 'DRIVE/Polera ridge Cons.jpeg', 'DRIVE/poleras good coffee.jpeg', 'DRIVE3/Polera Ridge beach.jpg'],
    # en las fotos pero no en el catálogo de WhatsApp
    'vestido-sirio': ['DRIVE2/Vestido Sirio (2).jpeg', 'DRIVE2/Vestido Sirio.jpeg'],
    'polera-thor': ['WhatsApp Image 2026-07-15 at 08.20.36 (5).jpeg'],
    'polera-bolzano': ['WhatsApp Image 2026-07-15 at 08.20.36.jpeg'],
    'chaqueta-de-jeans-belle': ['Chaqueta Belle.jpg', 'Chaqueta Belle (2).jfif'],
    'chaqueta-de-jeans-montesacro': ['Chaqueta Montesacro.jpeg', 'Chaqueta MonteSacro.jfif'],
    'chaqueta-kimono': ['Chaqueta Kimono.jpg', 'Chaqueta Kimono (2).jpg'],
    'chaqueta-cuadrille-asparago': ['Chaqueta Asparago.jpg', 'Chaqueta Asparago (2).jpg'],
    'jeans-hamal': ['Jeans Hamal.jpeg', 'DRIVE2/Jeans hamal.png'],
    'bermuda-de-jeans-edgewater': ['Bermuda Edgewater.jpeg'],
    'camisa-de-jeans-biene': ['DRIVE/Chaqueta Biene.jpg', 'DRIVE/Chaqueta Biene.jfif', 'Chaqueta Biene (2).jfif'],
    'chaqueta-poleron-ciop': ['DRIVE/WhatsApp Image 2026-10-07 at 22.54.35.jpeg', 'DRIVE/WhatsApp Image 2026-10-07 at 22.54.34.jpeg', 'DRIVE/WhatsApp Image 2026-10-07 at 22.54.35 (1).jpeg', 'DRIVE/WhatsApp Image 2026-10-07 at 22.54.34 (1).jpeg'],
    'polera-estrella': ['DRIVE3/696513336_18322273972250984_4811060197628143740_n.jpg', 'WhatsApp Image 2026-07-15 at 08.20.47 (5).jpeg'],  # foto real (rosada) reemplaza a la editada con IA
    'vestido-azul': ['vestido azul.jpeg', 'vestido azul 1.jpeg'],
    'vestido-tenido': ['DRIVE2/Vestido fidene 3.jpeg', 'DRIVE2/Vestido Fidene.jpeg', 'DRIVE2/Vestido fidene4.jpeg', 'DRIVE2/Vestido fidene 2.jpeg'],
    'chaqueta-de-jeans-manga-corta': ['chaqueta jeans manga corta.jpeg', 'Chaqueta jeans oversize.png'],
    'chaleco-tai': ['DRIVE2/Chaleco Tai.jfif', 'DRIVE2/Chaleco Tai (2).jfif'],
    'polera-a-rayas-clavel': ['WhatsApp Image 2026-10-05 at 22.57.42.jpeg'],
    'chaqueta-jaspeada-porter': ['PORTADA/chaqueta-jaspeada-porter.jpg', 'DRIVE2/Chaqueta Porter 2.jpeg', 'DRIVE/WhatsApp Image 2026-10-08 at 16.30.51.jpeg', 'DRIVE/Chaqueta Porter.jpeg'],
    # fotos con nombre del Drive de Michelle (10-10): 13 productos que no tenían
    'bermuda-de-jeans-posillipo': ['DRIVE/WhatsApp Image 2026-10-08 at 16.30.52.jpeg', 'DRIVE/WhatsApp Image 2026-10-08 at 16.30.52 (1).jpeg', 'PORTADA/bermudas-crochet.jpg'],
    'camisa-escocesa-adda': ['DRIVE/Camisa Adda (4).jpeg', 'DRIVE/Camisa Adda (2).jpeg', 'DRIVE/Camisa Adda.jpeg', 'DRIVE/Camisa Adda (3).jpeg'],
    'camisa-estampada-cameron': ['DRIVE/Blusa Cameron.jpeg', 'DRIVE/Blusa Cameron blue.jpeg', 'DRIVE/Blusa cameron blue (2).jpeg', 'DRIVE/Blusa Cameron orange.png'],
    'enterito-de-jeans-rase-top': ['DRIVE3/Enterito Rase.jpeg', 'DRIVE/WhatsApp Image 2026-10-08 at 16.30.55 (3).jpeg', 'DRIVE/WhatsApp Image 2026-10-08 at 16.30.55 (4).jpeg', 'DRIVE/WhatsApp Image 2026-10-08 at 16.30.56.jpeg', 'DRIVE/689541825_18321909328250984_556067338974819024_n.jpg'],
    'enterito-de-jeans-spinne': ['DRIVE/772780069_1659272439540633_6907057961696254711_n.jpg', 'DRIVE/WhatsApp Image 2026-10-08 at 16.30.55 (1).jpeg', 'DRIVE4/COMBINAISON SPINNE FRONT.png', 'DRIVE4/COMBINAISON SPINNE BACK.png'],
    'chaleco-de-lana-rita': ['DRIVE/Chaleco Rita (3).jfif', 'DRIVE2/Chaleco Rita (2).jfif', 'DRIVE2/Chaleco Rita (1).jfif'],
    'pantalon-de-buzo-marble': ['DRIVE/Pantalon Marbel.jpeg'],
    'pantalon-de-jeans-delphine': ['DRIVE/Jeans Delphine.jpeg', 'DRIVE/Polera strange.jpeg'],
    'chaleco-con-flecos-divina': ['DRIVE2/Chaleco divina 2.jpeg', 'DRIVE2/Chaleco divina.jpeg', 'DRIVE/Chaleco Divina.jpg'],
    'pantalon-militar-fiffidi': ['DRIVE/Conjunto Casperino.jpeg', 'DRIVE/WhatsApp Image 2026-10-08 at 16.30.59 (2).jpeg'],
    'pantalon-de-buzo-homan': ['DRIVE/Pantalon Homan.jpeg', 'DRIVE/Pantalon Homan (2).jpeg', 'DRIVE/Pantalon Homan.jpg', 'DRIVE/Pantalon Homan (2).jpg', 'DRIVE4/Pantalone homan.png'],
    'polera-doctor-strange': ['DRIVE/Polera strange.jpeg', 'DRIVE/Polera Strange.jfif', 'DRIVE3/Polera doctor strange.jpeg'],
    'polera-love-logetta': ['DRIVE/Polera Love.jpeg', 'DRIVE/Polera Love (2).jpeg'],
    'chaqueta-militar-casperino': ['DRIVE/Conjunto Casperino 2.jpeg', 'DRIVE/Conjunto Casperino.jpeg', 'DRIVE/WhatsApp Image 2026-07-15 at 08.31.07.jpeg'],
    'chaqueta-rodi': ['DRIVE2/Chaqueta Rodi Band.jpeg', 'DRIVE2/Conjunto Rodi Band 2.jpeg', 'DRIVE2/Conjunto Rodi Band.jpeg'],
    'chaqueta-tejida-pallide': ['DRIVE/WhatsApp Image 2026-10-10 at 17.45.58 (13).jpeg', 'DRIVE/WhatsApp Image 2026-10-10 at 17.45.58 (14).jpeg', 'DRIVE/WhatsApp Image 2026-10-10 at 17.45.58 (7).jpeg', 'DRIVE4/chaqueta pallide front.png', 'DRIVE4/Chaqueta Pallide back.png', 'DRIVE4/Chaqueta Pallide front - inside.png', 'DRIVE4/Chaqueta Pallide inside.png'],
    'jeans-pescador-larch': ['DRIVE/WhatsApp Image 2026-10-08 at 16.30.58 (3).jpeg', 'DRIVE4/Jeans Larch Negros.png', 'DRIVE4/Jeans Larch - Blusa Torrone.png'],
    'chaleco-lia': ['DRIVE2/Poleron Lia.jpeg', 'DRIVE2/Poleron Lia 2.jpeg', 'DRIVE2/Poleron Lia 3.jpeg'],
    'vestido-decumani': ['DRIVE2/Vestido Decumani.jpg', 'DRIVE2/Vestido Decumani.jfif', 'DRIVE2/Vestido Decumani.jpeg'],
    'vestido-estampado-namrek': ['DRIVE2/Vestido Namrek blue.jpeg', 'DRIVE2/Vestido Namrek orange.jpeg', 'DRIVE2/Vestido Namrek blue.jpg', 'DRIVE2/Vestido Namrek orange.jfif', 'DRIVE2/Vestido Namrek blue (2).jpeg'],
    'vestido-canguro-terrano': ['DRIVE2/Vestido Terrano.jpg', 'DRIVE2/Vestido Terrano (2).jpg'],
    'poleron-basilea': ['DRIVE2/Poleron basilea.jpg', 'DRIVE3/699891122_1573764154758129_4756085291388833152_n.jpg'],
    'chaqueta-de-lino-marvel': ['DRIVE2/Chaqueta Marvel.jpeg', 'DRIVE2/Chaqueta MArvel pantalon chester.jpeg'],
    'pantalon-de-lino-chester': ['DRIVE2/Chaqueta MArvel pantalon chester.jpeg', 'DRIVE2/Chaqueta Marvel.jpeg'],
    'blusa-de-encaje-torrone': ['DRIVE2/Blusa Torrone.jpeg', 'DRIVE2/WhatsApp Image 2026-10-10 at 17.45.58 (2) - copia.jpeg', 'DRIVE4/Jeans Larch - Blusa Torrone.png'],
    'polera-de-encaje-englewood': ['DRIVE2/Englewood 2.jpeg', 'DRIVE2/Polera Englewood.jpeg'],
    'poleron-birch': ['DRIVE2/WhatsApp Image 2026-10-10 at 17.45.58 (12).jpeg', 'DRIVE2/Poleron Birch.jpg'],
    # portada
    'tile-vestidos': ['DRIVE2/Vestido Namrek blue.jpeg'],
    'tile-enteritos': ['DRIVE/WhatsApp Image 2026-10-08 at 16.30.55 (3).jpeg'],
    'tile-camisas': ['Camisa Opener.jpeg'],
    'tile-poleras': ['WhatsApp Image 2026-07-15 at 08.20.50 (3).jpeg'],
    'tile-jeans': ['jeans borde cafe.jpeg'],
    'tile-faldas': ['Falda Collationo (2).jpeg'],
    'tile-chaquetas': ['Chaqueta Belle.jpg'],
    'tile-conjuntos': ['Arreglo natural en un interior acogedor-10.png'],
    'showroom': ['Vista trasera de catálogo con cabello natural-1.png'],
    'chaleco-tai': ['DRIVE2/Chaleco Tai.jfif', 'DRIVE2/Chaleco Tai (2).jfif'],
    'polera-a-rayas-clavel': ['WhatsApp Image 2026-10-05 at 22.57.42.jpeg'],
    'chaqueta-jaspeada-porter': ['PORTADA/chaqueta-jaspeada-porter.jpg'],
    # portada: las 4 fotos que mandó Michelle el 10-10 (WhatsApp, en ~/Downloads)
    'chaleco-tai': ['DRIVE2/Chaleco Tai.jfif', 'DRIVE2/Chaleco Tai (2).jfif'],
    'polera-a-rayas-clavel': ['WhatsApp Image 2026-10-05 at 22.57.42.jpeg'],
    'chaqueta-jaspeada-porter': ['PORTADA/chaqueta-jaspeada-porter.jpg'],
    # portada: fotos que mandó Michelle el 10-10, guardadas en contexto/fotos-portada (las dos de la escalera quedaron fuera por chicas, 443×590)
    'hero-1': ['PORTADA/polera-french-saludo.jpg'],
    'hero-2': ['PORTADA/bermudas-crochet.jpg'],
    'hero-3': ['PORTADA/jardinera-tarro.jpg'],
    'nosotras': ['DRIVE14/Michelle - Valerie - 2.png'],   # 23-10: Michelle y Valerie con los trajes de leopardo y verde (antes: DRIVE3/correo/nosotras.jpeg)
    'showroom-amigas': ['DRIVE3/correo/nosotras 2.jpeg'],   # la otra foto de las dos en el showroom (correo 11-10), para la página de showroom   # las dos, en el showroom; la mandó Michelle por correo el 11-10
    'hero-4': ['DRIVE2/753531211_18331346782250984_8704258790926439866_n.jpg'],   # de la carpeta Portada del Drive de Michelle (pantalón Homan en la escalera); reemplaza la foto editada con IA
}
IA = {'Retrato', 'Arreglo natural', 'Cuidado natural', 'Mujer rubia', 'Look de lino', 'Vestido maxi lila', 'vestido blanco.png',
      'Polera estrella.png', 'Poleron jeans', 'vestido teñido', 'Vestido teñido', 'Vista trasera', 'Camisa Jeans one size',
      'pantalones grises', 'vestido jeans back', 'Modelo rubia', 'Paso natural', 'Posado frontal', 'Rostro y cabello'}

# 14-10-2026: Michelle numeró las fotos en el Drive (1 = principal). Este bloque pisa el orden de FOTOS para esos productos;
# después de las numeradas van las que ya estaban (sin repetir). Generado por tamaño de archivo contra las descargas locales.
# Las 3 fotos que ella llamó 'Gilet Sangiovese 1-3' son el chaleco de jeans con cierre (= Labiciano según su Excel): van a Labiciano.
ORDEN_MICHELLE_1014 = {
 "bermuda-de-jeans-blanket": [
  "Bermuda Blanket (2).jpg",
  "Bermuda Blanket.jpg",
  "DRIVE5/Bermuda Blanket3.jfif",
  "DRIVE/WhatsApp Image 2026-10-08 at 16.30.51 (2).jpeg"
 ],
 "bermuda-de-jeans-edgewater": [
  "DRIVE/744915740_18329842297250984_4779587733397228947_n.jpg",
  "Bermuda Edgewater.jpeg"
 ],
 "bermuda-de-jeans-posillipo": [
  "DRIVE5/Bermuda Posillipo1.jfif",
  "DRIVE/WhatsApp Image 2026-10-08 at 16.30.52.jpeg",
  "DRIVE5/Bermuda Posillipo3.jfif",
  "DRIVE5/Bermuda Posillipo 4.jfif"
 ],
 "jeans-bomber-bagnoli": [
  "Polera estrella y jeans.png",
  "Jeans Bagnoli.webp"
 ],
 "falda-de-jeans-collatino": ["Mujer rubia con conjunto denim azul-2.png", "DRIVE/WhatsApp Image 2026-10-08 at 16.30.57 (3).jpeg", "falda jeans.jpeg", "DRIVE5/Falda Collatino5.jfif", "DRIVE5/Falda Collatino6.jfif"],
 "jeans-hamal": [
  "Jeans Hamal.jpeg",
  "Jeans borde cafe - zoom.png"
 ],
 "pantalon-de-buzo-marble": [
  "Posado frontal con cabello rubio liso-1.png",
  "Paso natural con melena rubia lisa-2.png",
  "Retrato de moda con pose relajada-3.png",
  "DRIVE/Pantalon Marbel.jpeg",
  "DRIVE5/Pantalon marble 6.jpeg"
 ],
 "jeans-pescador-larch": [
  "DRIVE4/Jeans Larch Negros.png",
  "DRIVE/WhatsApp Image 2026-10-08 at 16.30.58 (3).jpeg",
  "DRIVE4/Jeans Larch - Blusa Torrone.png",
  "DRIVE4/Gilet Sangiovese_1.png"
 ],
 "pantalon-leopardo-chopping": [
  "DRIVE/Pantalon Conjunto Chopping.jfif",
  "DRIVE5/Pantalon conjunto chopping 2.jpeg",
  "DRIVE/648652680_18312697750250984_8476852772817699616_n.jpg",
  "DRIVE/WhatsApp Image 2026-10-10 at 17.45.56 (2).jpeg"
 ],
 "pantalon-de-jeans-delphine": [
  "DRIVE/Jeans Delphine.jpeg",
  "DRIVE/Polera strange.jpeg"
 ],
 "pantalon-de-buzo-homan": [
  "DRIVE/Pantalon Homan (2).jpg",
  "DRIVE/Pantalon Homan (2).jpeg",
  "pantalones grises y polera blanca naranjo fluor front.png",
  "DRIVE/Pantalon Homan.jpg",
  "DRIVE/Pantalon Homan.jpeg",
  "DRIVE4/Pantalone homan.png"
 ],
 "vestido-decumani": [
  "DRIVE2/Vestido Decumani.jpeg",
  "DRIVE2/Vestido Decumani.jfif",
  "DRIVE2/Vestido Decumani.jpg"
 ],
 "vestido-primaveral-iron-fist": [
  "Retrato elegante con rostro ovalado definido-1.png",
  "DRIVE2/Vestido Iron.jpeg",
  "DRIVE2/Vestido Iron (2).jpeg",
  "DRIVE2/Vestido Iron (2).jfif",
  "DRIVE2/Vestido Iron.jfif"
 ],
 "vestido-largo-monclaire": [
  "Vestido maxi lila con gráfico musical-2.png",
  "Vestido Buzo lila.jpeg",
  "DRIVE2/Vestido Monclaire.jpg",
  "DRIVE2/Vestido Monclaire.jpeg"
 ],
 "vestido-estampado-namrek": [
  "DRIVE2/Vestido Namrek blue.jpg",
  "DRIVE2/Vestido Namrek blue.jpeg",
  "DRIVE2/Vestido Namrek blue (2).jpeg",
  "Retrato editorial en vestido floral naranja.png",
  "DRIVE2/Vestido Namrek orange.jpeg",
  "DRIVE2/Vestido Namrek orange.jfif"
 ],
 "vestido-de-jeans-imprime": [
  "DRIVE2/Vestido Imprime.jfif",
  "DRIVE2/vestido imprime (2).jpeg",
  "DRIVE2/Vestido Imprime.jpeg",
  "DRIVE2/Vestido imprime (3).jpeg"
 ],
 "vestido-sirio": [
  "Vestido piña front.png",
  "DRIVE2/Vestido Sirio (2).jpeg",
  "DRIVE2/Vestido Sirio.jpeg"
 ],
 "vestido-canguro-terrano": [
  "DRIVE2/Vestido Terrano.jpg",
  "DRIVE2/Vestido Terrano (2).jpg"
 ],
 "jardinera-de-jeans-materdai": [
  "DRIVE3/Jardinera Materdai.jpeg",
  "DRIVE5/Jardinera Materdai 2.jfif",
  "DRIVE/jardinera materdai.jpeg",
  "Jardinera jeans.jpeg",
  "DRIVE/Jardinera Materdai (1).jpeg"
 ],
 "polera-bolzano": [
  "DRIVE5/Polera Bolzano 1con collar caballito de mar.jfif",
  "WhatsApp Image 2026-07-15 at 08.20.36.jpeg"
 ],
 "polera-cuello-v-paradise": [
  "DRIVE3/Polera Caketin.jpeg",
  "WhatsApp Image 2026-07-15 at 08.20.46 (3).jpeg",
  "DRIVE/Polera Caketin (3).jpeg"
 ],
 "polera-circle": [
  "DRIVE5/Polera circle 1.jpeg",
  "WhatsApp Image 2026-07-15 at 08.20.50 (3).jpeg",
  "DRIVE5/Polera circel 3con collar aji.jfif",
  "DRIVE5/Polera circle 4con collar star XXL.jfif"
 ],
 "polera-a-rayas-clavel": [
  "0178389a-c507-482e-8418-448ce49f6c8d.jfif",
  "708304752_1582971887170689_7243958627193220175_n.jpg",
  "WhatsApp Image 2026-10-05 at 22.57.42.jpeg"
 ],
 "polera-estrella": [
  "DRIVE/Polera Deneb.jpeg",
  "DRIVE3/Polera Deneb Star.jpeg",
  "Polera estrella.png",
  "WhatsApp Image 2026-07-15 at 08.20.47 (5).jpeg",
  "DRIVE3/Polera estrella.jfif",
  "Retrato con zapatillas blancas minimalistas.png"
 ],
 "polera-doctor-strange": [
  "DRIVE/Polera strange.jpeg",
  "da6b4586-e842-4349-85b9-41b248178177.jfif",
  "DRIVE3/Polera doctor strange.jpeg"
 ],
 "polera-love": [
  "DRIVE5/polera gaiola 1.jpeg",
  "ad271e77-b961-4aec-a2a4-452c14cf02dc.jfif",
  "WhatsApp Image 2026-07-15 at 08.20.37 (1).jpeg"
 ],
 "polera-anticons": [
  "e3c4ee3e-9117-4d86-8c6b-1b7fd8b44a8f.jfif",
  "poleras good coffee.jpeg",
  "DRIVE/Polera ridge2.jpeg",
  "DRIVE/Polera ridge.jpeg",
  "WhatsApp Image 2026-07-15 at 08.20.42 (1).jpeg",
  "pantalones grises y polera blanca naranjo fluor.png"
 ],
 "polera-ridge-cons": [
  "WhatsApp Image 2026-07-15 at 08.20.49 (1).jpeg",
  "WhatsApp Image 2026-07-15 at 08.20.48 (5).jpeg",
  "WhatsApp Image 2026-06-19 at 08.13.15.jpeg"
 ],
 "polera-thor": [
  "WhatsApp Image 2026-07-15 at 08.20.36 (5).jpeg",
  "WhatsApp Image 2026-07-15 at 08.20.36 (4).jpeg"
 ],
 "chaqueta-poleron-ciop": [
  "DRIVE/WhatsApp Image 2026-10-07 at 22.54.35.jpeg",
  "Polerones de jeans.jpeg",
  "DRIVE/WhatsApp Image 2026-10-07 at 22.54.34 (1).jpeg",
  "DRIVE/WhatsApp Image 2026-10-07 at 22.54.34.jpeg"
 ],
 "chaqueta-de-jeans-montesacro": [
  "Rostro y cabello con cuidado natural-2.png",
  "Conjunto vaquero holgado en interior luminoso.png",
  "Bermuda Blanket.jfif",
  "DRIVE5/Chaqueta montesacro4.jpeg",
  "DRIVE5/Cahaqueta montesacro5.jpeg",
  "Chaqueta Montesacro.jpeg",
  "Chaqueta MonteSacro.jfif"
 ],
 "chaleco-de-jeans-labiciano": [
  "DRIVE5/Gilete Sangiovese1.jfif",
  "Gilet Sangiovese.jpeg",
  "DRIVE5/Giletete Sangiovese3.jfif"
 ]
}
FOTOS.update(ORDEN_MICHELLE_1014)

RECORTE_ESPECIAL = {'polera-estrella-estudio-ia.jpg': (0.07, 0.12, 0.93),
                    # 14-10: marca 'AI+' o 'CapCut Ai' arriba a la izquierda en fotos que Michelle editó con IA
                    'Polera Deneb.jpeg': (0.08, 0.08, 0.92), 'Polera Deneb Star.jpeg': (0.08, 0.08, 0.92),
                    'Polera circle 1.jpeg': (0.08, 0.08, 0.92), 'Polera circle 4con collar star XXL.jfif': (0.08, 0.08, 0.92),
                    'Polera Caketin.jpeg': (0.12, 0.08, 0.88), 'Falda Collatino5.jfif': (0.25, 0.0, 1.0),
                    'Blusa torrone1.jfif': (0.25, 0.0, 1.0)}   # 15-10: marca 'CapCut AI'  # (izq, arriba, der) en fracción: deja fuera la marca "AI+"

def recorte_3_4(im, alto=900, nombre='', centrado=False):
    im = ImageOps.exif_transpose(im).convert('RGB')
    if nombre in RECORTE_ESPECIAL:
        a, b, c = RECORTE_ESPECIAL[nombre]; w0, h0 = im.size
        im = im.crop((int(w0 * a), int(h0 * b), int(w0 * c), h0))
    w, h = im.size
    tw = min(w, int(h * 3 / 4)); th = min(h, int(tw * 4 / 3))
    l = (w - tw) // 2; t = max(0, int((h - th) * (0.5 if centrado else 0.25)))  # un poco más arriba que el centro: caras y cuellos; accesorios centrados
    im = im.crop((l, t, l + tw, t + th)); im.thumbnail((int(alto * 3 / 4), alto))
    return im

def guardar(im, destino, calidad=78):
    im.save(destino, 'JPEG', quality=calidad, optimize=True, progressive=True)

# 15-10: el orden de las fotos sale de los nombres que Michelle pone en el Drive (modelo + número, 1 = principal).
# fotos-desde-drive.py arma orden-drive.json desde el listado del Drive; acá cada foto se ubica en disco por tamaño de archivo.
# Pisa FOTOS para los productos que aparecen en su Drive; los demás (Fiffidi, Logetta, Mintaka, Mirach) quedan como estaban.
import json as _json
ORDEN_DRIVE = AQUI.parent / 'orden-drive.json'
if ORDEN_DRIVE.exists():
    _bases = [('', ORIGEN), ('DRIVE/', DRIVE), ('DRIVE2/', DRIVE2), ('DRIVE3/', DRIVE3), ('DRIVE4/', DRIVE4), ('DRIVE5/', DRIVE5), ('DRIVE6/', DRIVE6), ('DRIVE7/', DRIVE7), ('DRIVE8/', DRIVE8), ('DRIVE9/', DRIVE9), ('DRIVE10/', DRIVE10), ('DRIVE11/', DRIVE11), ('DRIVE12/', DRIVE12), ('DRIVE13/', DRIVE13), ('DRIVE14/', DRIVE14), ('DRIVE15/', DRIVE15), ('DRIVE16/', DRIVE16)]
    def _ruta(n):
        for pref, base in _bases[1:]:
            if n.startswith(pref): return base / n[len(pref):]
        return PORTADA / n[8:] if n.startswith('PORTADA/') else ORIGEN / n
    por_tamano = {}
    for _lista in FOTOS.values():   # primero los nombres ya usados, para que RECORTE_ESPECIAL siga calzando
        for _n in _lista:
            _r = _ruta(_n)
            if _r.exists(): por_tamano.setdefault(_r.stat().st_size, _n)
    for _pref, _base in _bases:
        for _f in _base.rglob('*'):
            if _f.is_file(): por_tamano.setdefault(_f.stat().st_size, _pref + str(_f.relative_to(_base)))
    for _h, _fs in _json.load(open(ORDEN_DRIVE, encoding='utf-8')).items():
        _rutas = [por_tamano[f['size']] for f in _fs if f['size'] in por_tamano]
        _faltan = [f['title'] for f in _fs if f['size'] not in por_tamano]
        if _faltan: print('  sin bajar todavía:', _h, _faltan)
        if _rutas: FOTOS[_h] = _rutas

FOTOS['polera-love-logetta'] = []   # 15-10: sus fotos eran las de Strange Love (Michelle) y está agotada: queda sin foto y no se publica

# accesorios: las fotos salen de accesorios.csv (una fila por accesorio, columna fotos con nombres separados por |)
def _slug(t):
    import unicodedata, re
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')
ACCESORIOS_CSV = AQUI.parent / 'accesorios.csv'
if ACCESORIOS_CSV.exists():
    for r in csv.DictReader(open(ACCESORIOS_CSV, encoding='utf-8')):
        fs = [f for f in (r.get('fotos') or '').split('|') if f]
        if fs: FOTOS['acc-' + _slug(r['nombre'])] = [f if '/' in f else 'DRIVE4/accesorios/' + f for f in fs]   # con '/' ya trae su carpeta (DRIVE7/accesorios/…)
    FOTOS['tile-accesorios'] = ['DRIVE4/accesorios/Prendedor mariposa.jpeg']

TAPAR_MARCA = {'Polera Circle 3.jpg': (18, 18, 104, 70), 'Polera Deneb Star.jpeg': (26, 30, 132, 92), 'Polera Deneb.jpeg': (26, 30, 132, 92)}

filas = []
for handle, archivos in FOTOS.items():
    salida = []
    huellas = []   # 14-10: Michelle tiene la misma foto guardada varias veces (zip, WhatsApp, copias renombradas, PNG y JPG);
                   # si una foto es visualmente igual a otra ya puesta en este producto, se salta. Umbral bajo (<=4 de 256):
                   # dos fotos de la misma sesión con distinta polera dan 9 o más y se conservan.
    i = 0
    for nombre in archivos:
        src = PORTADA / nombre[8:] if nombre.startswith('PORTADA/') else DRIVE / nombre[6:] if nombre.startswith('DRIVE/') else DRIVE2 / nombre[7:] if nombre.startswith('DRIVE2/') else DRIVE3 / nombre[7:] if nombre.startswith('DRIVE3/') else DRIVE4 / nombre[7:] if nombre.startswith('DRIVE4/') else DRIVE5 / nombre[7:] if nombre.startswith('DRIVE5/') else DRIVE6 / nombre[7:] if nombre.startswith('DRIVE6/') else DRIVE7 / nombre[7:] if nombre.startswith('DRIVE7/') else DRIVE8 / nombre[7:] if nombre.startswith('DRIVE8/') else DRIVE9 / nombre[7:] if nombre.startswith('DRIVE9/') else DRIVE10 / nombre[8:] if nombre.startswith('DRIVE10/') else DRIVE11 / nombre[8:] if nombre.startswith('DRIVE11/') else DRIVE12 / nombre[8:] if nombre.startswith('DRIVE12/') else DRIVE13 / nombre[8:] if nombre.startswith('DRIVE13/') else DRIVE14 / nombre[8:] if nombre.startswith('DRIVE14/') else DRIVE15 / nombre[8:] if nombre.startswith('DRIVE15/') else DRIVE16 / nombre[8:] if nombre.startswith('DRIVE16/') else ORIGEN / nombre
        if not src.exists():
            print('FALTA', nombre); continue
        im = Image.open(src)
        if src.name in TAPAR_MARCA:   # 23-10: marca "AI+" de la app de edición: se cubre con el fondo liso de al lado
            x0, y0, x1, y1 = TAPAR_MARCA[src.name]; im = im.convert('RGB')
            parche = im.crop((x1, y0, x1 + (x1 - x0), y1)).filter(ImageFilter.GaussianBlur(2)); im.paste(parche, (x0, y0))
        im = recorte_3_4(im, 1600 if handle.startswith(('showroom-amigas', 'nosotras')) else 1200 if handle.startswith(('hero', 'showroom')) else 900, src.name, centrado=handle.startswith('acc-'))
        g = im.convert('L').resize((17, 16)); px = list(g.getdata())
        huella = sum(1 << k for k, (x, y) in enumerate((px[r * 17 + c], px[r * 17 + c + 1]) for r in range(16) for c in range(16)) if x > y)
        if any(bin(huella ^ h).count('1') <= 4 for h in huellas):
            print('  repetida, se salta:', handle, '←', nombre); continue
        huellas.append(huella); i += 1
        destino = IMG / f'{handle}-{i}.jpg'
        guardar(im, destino)
        salida.append(destino.name)
        filas.append({'handle': handle, 'archivo_web': destino.name, 'origen': nombre, 'editada_con_ia': 'sí' if any(k in nombre for k in IA) or (nombre.startswith('DRIVE4/') and nombre.endswith('.png')) else 'no'})
    print(handle, '→', ', '.join(salida))

with open(AQUI / 'fotos.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['handle', 'archivo_web', 'origen', 'editada_con_ia']); w.writeheader(); w.writerows(filas)

# rellenar la columna imagenes del catálogo neutro
cat = list(csv.DictReader(open(CATALOGO, encoding='utf-8')))
por = {}
for r in filas: por.setdefault(r['handle'], []).append(r['archivo_web'])
for c in cat:
    if c['handle'] in por: c['imagenes'] = ','.join(por[c['handle']])
with open(CATALOGO, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(cat[0].keys())); w.writeheader(); w.writerows(cat)
print('catálogo con fotos:', sum(1 for c in cat if c['imagenes']), 'de', len(cat))
