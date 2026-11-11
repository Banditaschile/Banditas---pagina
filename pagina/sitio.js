
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
