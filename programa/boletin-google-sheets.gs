// Guarda los correos del formulario "Enterarme de lo nuevo" en esta planilla.
// Se pega en la planilla de Google: Extensiones → Apps Script, y se implementa
// como "Aplicación web" con acceso "Cualquier usuario". La dirección que entrega
// va en BOLETIN_URL, en programa/construir.py.

const HOJA = 'Suscriptoras';

function doPost(e) {
  const p = (e && e.parameter) || {};
  const correo = String(p.correo || '').trim().toLowerCase().slice(0, 200);
  if (!/^[^@\s=+\-][^@\s]*@[^@\s]+\.[^@\s]+$/.test(correo)) {
    return ContentService.createTextOutput('correo no válido');
  }
  let pagina = String(p.pagina || '').slice(0, 100);
  if (/^[=+\-@]/.test(pagina)) pagina = "'" + pagina;

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const libro = SpreadsheetApp.getActiveSpreadsheet();
    const hoja = libro.getSheetByName(HOJA) || libro.insertSheet(HOJA);
    if (hoja.getLastRow() === 0) hoja.appendRow(['Fecha', 'Correo', 'Página']);
    const n = hoja.getLastRow() - 1;
    const existentes = n > 0 ? hoja.getRange(2, 2, n, 1).getValues().map(function (f) { return f[0]; }) : [];
    if (existentes.indexOf(correo) === -1) hoja.appendRow([new Date(), correo, pagina]);
  } finally {
    lock.releaseLock();
  }
  return ContentService.createTextOutput('ok');
}
