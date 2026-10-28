#!/usr/bin/env python3
"""Convierte la bitácora publicada en Claude (tools/source-artifact.html) en la app web de Capacitor (www/index.html)."""
import re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / 'tools' / 'source-artifact.html').read_text()
s = src

def rep(a, b, count=1):
    global s
    n = s.count(a)
    assert n == count, f'esperaba {count} y encontré {n}: {a[:90]!r}'
    s = s.replace(a, b)

def rep_block(start, end, new):
    """Reemplaza desde `start` (incluido) hasta `end` (excluido)."""
    global s
    i = s.index(start); j = s.index(end, i)
    s = s[:i] + new + s[j:]

# ---------- head / fuentes ----------
rep('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
s = re.sub(r'<link rel="preconnect"[^>]*>\n', '', s)
s = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\n', '', s)

fonts = ''.join(
    f"@font-face{{font-family:'{fam}';font-style:normal;font-weight:{w};font-display:swap;src:url(fonts/{file}-latin-{w}-normal.woff2) format('woff2')}}\n"
    for fam, file, ws in [('Barlow', 'barlow', (400, 500, 600)), ('Barlow Condensed', 'barlow-condensed', (600, 700, 800))]
    for w in ws)

# zonas seguras: env() + variables que inyecta Capacitor
s = re.sub(r'env\(safe-area-inset-(top|bottom|left|right),\s*0px\)', r'var(--sa-\1)', s)
rep('<style>\n', '<style>\n' + fonts)
rep(':root{\n  --bg:', ':root{\n  --sa-top:max(env(safe-area-inset-top,0px),var(--safe-area-inset-top,0px));--sa-bottom:max(env(safe-area-inset-bottom,0px),var(--safe-area-inset-bottom,0px));\n  --sa-left:max(env(safe-area-inset-left,0px),var(--safe-area-inset-left,0px));--sa-right:max(env(safe-area-inset-right,0px),var(--safe-area-inset-right,0px));\n  --bg:')
rep('body{background:var(--bg);color:var(--text);font:15px/1.45 var(--body);padding-bottom:130px}',
    'html{-webkit-text-size-adjust:100%;-webkit-tap-highlight-color:transparent}\nbody{margin:0;background:var(--bg);color:var(--text);font:15px/1.45 var(--body);padding-top:var(--sa-top);padding-bottom:calc(130px + var(--sa-bottom));overscroll-behavior-y:contain}')
rep('.sync[data-s="pending"] i{background:var(--accent)}',
    '.sync[data-s="pending"] i{background:var(--accent)}\n.sync{display:none}\n'
    '.top-actions{display:flex;align-items:center;gap:10px;min-width:0}\n'
    '.gear{width:40px;height:40px;border-radius:12px;border:1px solid var(--line);background:var(--surface);display:grid;place-items:center;color:var(--text);padding:0;flex:none}\n'
    '.gear svg{width:20px;height:20px}\n.gear[aria-pressed="true"]{border-color:var(--accent);color:var(--accent)}\n'
    '.set-key{flex:1;min-width:0;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg);font-size:16px;font-family:ui-monospace,monospace}\n'
    'a.link{display:inline-block;text-decoration:none}\n')

head = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<meta name="color-scheme" content="light dark">\n'
        '<meta name="theme-color" content="#111214">\n')
i = s.index('<style>'); j = s.index('</style>') + len('</style>')
title_and_style = s[:j]
rest = s[j:]
s = head + title_and_style + '\n</head>\n<body>\n' + rest.strip() + '\n</body>\n</html>\n'

# ---------- encabezado: estado + ajustes ----------
rep('<div class="sync" id="sync" data-s="loading"><i></i><span id="syncTxt">Conectando…</span></div>',
    '<div class="top-actions"><div class="sync" id="sync" data-s="local"><i></i><span id="syncTxt">Guardado en tu celular</span></div>'
    '<button class="gear" type="button" id="gearBtn" aria-label="Ajustes" aria-pressed="false">'
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg>'
    '</button></div>')
rep('<section id="view-progress" hidden></section>', '<section id="view-progress" hidden></section>\n  <section id="view-settings" hidden></section>')

# ---------- scripts ----------
rep('<script>\n', '<script src="js/capacitor-core.js"></script>\n<script>\n' + r'''/* ---------- Plataforma (Android con Capacitor) ---------- */
const APP_VERSION = '__APP_VERSION__';
const CLOUD = false;
const CX = window.capacitorExports || null;
const IS_NATIVE = !!(window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform());
const plug = n => (CX && IS_NATIVE) ? CX.registerPlugin(n) : null;
const LN = plug('LocalNotifications'), KA = plug('KeepAwake'), FS = plug('Filesystem'), SH = plug('Share'), APP = plug('App'), HAP = plug('Haptics'), SB = plug('StatusBar');
const safe = async fn => { try { return await fn(); } catch(e){ console.warn(e); return null; } };

''')

# Sin nube: no marcar pendientes de subir
rep("function putDay(k, doc){ doc.date = k; S.food.days[k] = doc; S.food.dirty[k] = true;",
    "function putDay(k, doc){ doc.date = k; S.food.days[k] = doc; if (CLOUD) S.food.dirty[k] = true;")
rep("function saveNut(){ S.food.dirty._profile = true;", "function saveNut(){ if (CLOUD) S.food.dirty._profile = true;")
rep("S.food.profile = p; S.food.dirty._profile = true; showSetup = false;", "S.food.profile = p; if (CLOUD) S.food.dirty._profile = true; showSetup = false;")
rep("t.textContent = dbState === 'cloud' ? 'Guardado en tu cuenta' : dbState === 'local' ? 'Solo en este dispositivo' : 'Conectando…';",
    "t.textContent = 'Guardado en tu celular';")

# ---------- arranque: sin Claude, con Gemini y plugins nativos ----------
rep_block('async function initCloud(){', '/* ---------- Entrenar ---------- */', r'''async function initCloud(){
  dbState = 'local';
  downloads = true;
  S.food.dirty = {};
  if (!S.gemini || typeof S.gemini !== 'object') S.gemini = {};
  sampleState = geminiKey() ? 'ok' : 'none';
  sample = sampleState === 'ok' ? gemini : null;
  if (S.rest && S.rest.end > Date.now() - 20000){ rest = S.rest; $('#restbar').classList.add('show'); tick(); }
  onData();
  initNative();
}

/* ---------- Gemini (cálculo de comida) ---------- */
const GEM_BASE = 'https://generativelanguage.googleapis.com/v1beta';
const geminiKey = () => (S.gemini && S.gemini.key) || '';
async function gemFetch(path, opts = {}){
  const r = await fetch(GEM_BASE + path, Object.assign({}, opts, {headers: {'Content-Type': 'application/json', 'x-goog-api-key': geminiKey()}}));
  let data = null; try { data = await r.json(); } catch(_){}
  if (!r.ok) throw {status: r.status, message: (data && data.error && data.error.message) || ('HTTP ' + r.status)};
  return data;
}
async function detectModels(){
  const d = await gemFetch('/models?pageSize=200');
  const names = (d && d.models || []).filter(m => (m.supportedGenerationMethods || []).includes('generateContent'))
    .map(m => String(m.name || '').replace(/^models\//, ''))
    .filter(n => /gemini/.test(n) && /flash/.test(n) && !/(tts|image|audio|live|embedding|thinking|exp|native|computer|robotics)/.test(n));
  const ver = n => { const m = n.match(/gemini-(\d+(?:\.\d+)?)/); return m ? +m[1] : 0; };
  const score = n => ver(n) * 10 + (/lite/.test(n) ? 3 : 0) - (/preview/.test(n) ? 6 : 0) - (/-\d{3,}$/.test(n) ? 1 : 0);
  return [...new Set(names)].sort((a, b) => score(b) - score(a));
}
function mapGem(e){
  if (!e) return {code: 'upstream_error'};
  if (e.code) return e;
  if (e.name === 'AbortError') return {code: 'cancelled'};
  if (e.status === 429) return {code: 'rate_limited'};
  if (e.status === 401 || e.status === 403 || (e.status === 400 && /api.?key/i.test(e.message || ''))) return {code: 'bad_key'};
  return {code: 'upstream_error', message: e.message};
}
const gemini = {
  async json(prompt, opts = {}){
    if (!geminiKey()) throw {code: 'not_granted'};
    if (!S.gemini.model){
      try { S.gemini.models = await detectModels(); S.gemini.model = S.gemini.models[0] || ''; saveLocal(); } catch(e){ throw mapGem(e); }
      if (!S.gemini.model) throw {code: 'upstream_error', message: 'Sin modelos disponibles'};
    }
    const run = async model => {
      const body = {contents: [{role: 'user', parts: [{text: prompt}]}], generationConfig: {responseMimeType: 'application/json', temperature: 0.2}};
      const d = await gemFetch(`/models/${encodeURIComponent(model)}:generateContent`, {method: 'POST', body: JSON.stringify(body), signal: opts.signal});
      const txt = ((((d && d.candidates || [])[0] || {}).content || {}).parts || []).map(p => p.text || '').join('');
      if (!txt.trim()) throw {code: 'empty_completion'};
      const m = txt.match(/[\[{][\s\S]*[\]}]/);
      try { return JSON.parse(m ? m[0] : txt); } catch(_){ throw {code: 'invalid_json'}; }
    };
    try { return await run(S.gemini.model); }
    catch(e){
      if (opts.signal && opts.signal.aborted) throw {code: 'cancelled'};
      if (e && (e.status === 404 || e.status === 429)){
        const alt = (S.gemini.models || []).find(n => n !== S.gemini.model);
        if (alt){
          try { const out = await run(alt); if (e.status === 404){ S.gemini.model = alt; saveLocal(); } return out; }
          catch(e2){ throw mapGem(e2); }
        }
      }
      throw mapGem(e);
    }
  }
};

/* ---------- Funciones nativas ---------- */
let notifOK = false;
async function initNative(){
  if (!IS_NATIVE) return;
  if (SB) safe(() => SB.setStyle({style: matchMedia('(prefers-color-scheme: dark)').matches ? 'DARK' : 'LIGHT'}));
  if (LN){
    const p = await safe(() => LN.checkPermissions());
    let disp = p && p.display;
    if (disp !== 'granted'){ const r = await safe(() => LN.requestPermissions()); disp = r && r.display; }
    notifOK = disp === 'granted';
    if (notifOK){
      await safe(() => LN.createChannel({id: 'descanso', name: 'Fin del descanso', description: 'Te avisa cuando termina el descanso entre series', importance: 5, visibility: 1, vibration: true, lights: true}));
      if (rest) scheduleRestNotif();
    }
  }
  if (APP){
    APP.addListener('backButton', () => {
      if (!$('#modal').hidden){ closeModal(false); return; }
      if (view !== 'train'){ switchView('train'); return; }
      safe(() => APP.minimizeApp());
    });
    APP.addListener('appStateChange', st => {
      if (!st || !st.isActive) return;
      tick();
      if (S.draft && S.draft.start) requestWake();
      if (view === 'train') renderTrain();
      if (view === 'food') renderFood();
    });
  }
}

/* ---------- Ajustes ---------- */
function renderSettings(){
  const g = S.gemini || {};
  const status = g.key ? (g.model ? `Conectado. Modelo: ${esc(g.model)}` : 'Clave guardada. Toca "Guardar y probar".') : 'Sin clave: puedes usar Armar plato, tus frecuentes y la captura manual.';
  $('#view-settings').innerHTML = `
    <h2>Cálculo de comida con Gemini</h2>
    <p class="hint">Pega tu clave de la API de Gemini. Se guarda solo en este celular. La creas gratis en Google AI Studio con tu cuenta de Google.</p>
    <a class="link" href="https://aistudio.google.com/apikey" target="_blank" rel="noopener">Abrir Google AI Studio</a>
    <div class="wrow">
      <input id="gKey" class="set-key" type="password" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="Pega aquí tu clave" value="${esc(g.key || '')}">
      <button class="btn" type="button" id="gShow">Ver</button>
    </div>
    <div class="row-btns" style="margin-top:10px">
      ${g.key ? '<button class="btn danger" type="button" id="gClear">Quitar clave</button>' : ''}
      <button class="btn primary" type="button" id="gSave">Guardar y probar</button>
    </div>
    <p class="hint" id="gStatus">${status}</p>
    ${g.models && g.models.length > 1 ? `<label class="swap" for="gModel">Modelo<select id="gModel">${g.models.map(m => `<option value="${esc(m)}" ${m === g.model ? 'selected' : ''}>${esc(m)}</option>`).join('')}</select></label>
      <p class="hint">Los modelos "lite" tienen más consultas gratis al día.</p>` : ''}
    <h2>Tus datos</h2>
    <p class="hint">Todo se guarda en este celular. Exporta un respaldo cada semana y guárdalo en Drive o mándatelo por WhatsApp. Si cambias de celular, lo importas aquí.</p>
    <div class="tools">
      <button class="btn" type="button" id="sExp">Exportar respaldo</button>
      <button class="btn" type="button" id="sImp">Importar respaldo</button>
      <button class="btn" type="button" id="sCsv">Exportar a Excel (CSV)</button>
      <button class="btn danger" type="button" id="sWipe">Borrar todo</button>
    </div>
    <h2>Avisos de descanso</h2>
    <p class="hint">${!IS_NATIVE ? 'Los avisos con la pantalla apagada solo funcionan en la app instalada.' : notifOK ? 'Activos: al terminar el descanso el celular suena y vibra aunque esté bloqueado.' : 'Desactivados. Activa las notificaciones de Bitácora Gym en los ajustes de Android para que te avise con la pantalla apagada.'}</p>
    <p class="hint" style="margin-top:24px">Bitácora Gym · versión ${APP_VERSION}</p>`;
}
$('#view-settings').addEventListener('click', async e => {
  const b = e.target.closest('button'); if (!b) return;
  if (b.id === 'gShow'){ const k = $('#gKey'); k.type = k.type === 'password' ? 'text' : 'password'; b.textContent = k.type === 'password' ? 'Ver' : 'Ocultar'; return; }
  if (b.id === 'gClear'){
    if (!(await ask('¿Quitar tu clave de Gemini de este celular?', 'Quitar', true))) return;
    S.gemini = {}; saveLocal(); sample = null; sampleState = 'none'; renderSettings(); return;
  }
  if (b.id === 'gSave'){
    const key = $('#gKey').value.trim();
    if (!key){ toast('Pega tu clave de Gemini.'); return; }
    S.gemini = {key}; saveLocal();
    $('#gStatus').textContent = 'Probando la clave…'; b.disabled = true;
    try {
      const list = await detectModels();
      S.gemini.models = list; S.gemini.model = list[0] || ''; saveLocal();
      sample = gemini; sampleState = 'ok';
      renderSettings();
      toast(list.length ? 'Gemini conectado' : 'La clave funciona, pero no encontré modelos Flash');
    } catch(err){
      const c = mapGem(err).code;
      $('#gStatus').textContent = c === 'bad_key' ? 'La clave no es válida. Cópiala completa desde Google AI Studio.' : c === 'rate_limited' ? 'La clave funciona, pero llegaste al límite por ahora. Intenta más tarde.' : 'No pude conectar con Gemini. Revisa tu internet e intenta otra vez.';
      if (c === 'rate_limited'){ sample = gemini; sampleState = 'ok'; }
    } finally { b.disabled = false; }
    return;
  }
  if (b.id === 'sExp') exportJson();
  if (b.id === 'sImp') $('#importFile').click();
  if (b.id === 'sCsv') exportCsv();
  if (b.id === 'sWipe') wipeAll();
});
$('#view-settings').addEventListener('change', e => { if (e.target.id === 'gModel'){ S.gemini.model = e.target.value; saveLocal(); } });
$('#gearBtn').addEventListener('click', () => switchView(view === 'settings' ? 'train' : 'settings'));

/* ---------- Entrenar ---------- */''')

# ---------- temporizador: estado guardado + notificación nativa ----------
rep_block('let rest = null;\nfunction startRest', "$('#restbar').addEventListener('click', onRestTap);", r'''let rest = null;
const REST_NID = 7001;
function saveRest(){ S.rest = rest; saveLocal(); }
async function scheduleRestNotif(){
  if (!LN || !notifOK) return;
  await safe(() => LN.cancel({notifications: [{id: REST_NID}]}));
  if (!rest || rest.end <= Date.now() + 1000) return;
  await safe(() => LN.schedule({notifications: [{id: REST_NID, title: '¡A darle!', body: rest.label, channelId: 'descanso', smallIcon: 'ic_stat_timer', schedule: {at: new Date(rest.end), allowWhileIdle: true}}]}));
}
function startRest(sec, label){ rest = {end: Date.now() + sec*1000, total: sec, label, beeped: false}; $('#restbar').classList.add('show'); $('#restbar').classList.remove('over'); saveRest(); scheduleRestNotif(); tick(); }
function stopRest(){ const had = !!rest; rest = null; $('#restbar').classList.remove('show','over'); if (had) saveRest(); if (LN && notifOK) safe(() => LN.cancel({notifications: [{id: REST_NID}]})); }
function onRestTap(e){
  const b = e.target.closest && e.target.closest('button[data-rest]');
  if (!b){ if ($('#restbar').classList.contains('over')) stopRest(); return; }
  e.preventDefault();
  const v = b.dataset.rest;
  if (v === 'skip' || !rest) return stopRest();
  rest.end += (+v)*1000; rest.total = Math.max(1, rest.total + (+v));
  if (rest.end > Date.now()){ rest.beeped = false; $('#restbar').classList.remove('over'); }
  saveRest(); scheduleRestNotif(); tick();
}
''')
rep("function beep(){\n  try {\n    if (actx){",
    "function beep(){\n  if (HAP) safe(() => HAP.vibrate({duration: 450}));\n  if (notifOK) return;\n  try {\n    if (actx){")
rep("async function requestWake(){ try { if ('wakeLock' in navigator && !wake) wake = await navigator.wakeLock.request('screen'); } catch(e){} }\nfunction releaseWake(){ try { wake && wake.release(); } catch(e){} wake = null; }",
    "async function requestWake(){ if (KA){ await safe(() => KA.keepAwake()); return; } try { if ('wakeLock' in navigator && !wake) wake = await navigator.wakeLock.request('screen'); } catch(e){} }\n"
    "function releaseWake(){ if (KA){ safe(() => KA.allowSleep()); return; } try { wake && wake.release(); } catch(e){} wake = null; }")

# ---------- historial: los datos se manejan en Ajustes ----------
rep_block("  const where = dbState === 'cloud'", "  $('#view-history').innerHTML = html;\n}",
    "  html += `<p class=\"hint\" style=\"margin-top:20px\">Respaldo, importar y exportar a Excel están en Ajustes (el engrane de arriba).</p>`;\n")

# ---------- exportar / importar / borrar con comida incluida ----------
rep("async function offerFile(name, text){\n  if (!downloads){ toast('La descarga no está disponible aquí.'); return; }\n  try { await downloads.save({filename: name, data: text}); }\n  catch(e){ if (e && e.code === 'declined') return; toast(e && e.code === 'rate_limited' ? 'Espera un momento e intenta otra vez.' : 'No se pudo generar el archivo.'); }\n}",
r'''async function offerFile(name, text){
  if (IS_NATIVE && FS && SH){
    try {
      const r = await FS.writeFile({path: name, data: text, directory: 'CACHE', encoding: 'utf8'});
      await SH.share({title: name, files: [r.uri], dialogTitle: 'Guardar o enviar'});
    } catch(e){ if (!/cancel/i.test(String((e && e.message) || e))) toast('No se pudo compartir el archivo.'); }
    return;
  }
  try {
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([text], {type: 'application/octet-stream'})); a.download = name;
    document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  } catch(e){ toast('No se pudo generar el archivo.'); }
}
function exportJson(){
  const food = {profile: S.food.profile, foods: S.food.foods || {}, hidden: S.food.hidden || [], days: S.food.days || {}};
  offerFile(`bitacora-gym-${dk(Date.now())}.json`, JSON.stringify({version: 4, exported: Date.now(), history: history().map(({_pending, ...h}) => h), food}, null, 2));
}
async function wipeAll(){
  if (!(await ask('Esto borra TODO: entrenamientos, comidas, peso, pasos y alimentos de este celular. No se puede deshacer.', 'Borrar todo', true))) return;
  S.pending = []; S.local = []; S.draft = null; S.rest = null; rest = null;
  S.food = {profile: null, foods: {}, hidden: [], days: {}, dirty: {}};
  saveLocal(); stopRest(); toast('Datos borrados'); switchView('train');
}''')

rep_block("    const incoming = Array.isArray(data) ? data : data.history;\n    if (!Array.isArray(incoming)) throw 0;",
          "    saveLocal(); setStatus(); flushPending(); renderHistory();",
r'''    const incoming = Array.isArray(data) ? data : (data.history || []);
    if (!Array.isArray(incoming) && !data.food) throw 0;
    const have = new Set(history().map(h => h.id)); let added = 0, days = 0;
    incoming.forEach(h => {
      if (h && h.id && h.sets && h.day && !have.has(h.id)){
        const rec = {id: String(h.id).replace(/[^A-Za-z0-9_\-.~:@+]/g,'') || uid(), day: h.day, date: +h.date || Date.now(), end: +h.end || +h.date || Date.now(), duration: +h.duration || 0, sets: h.sets, notes: h.notes || ''};
        S.local.push(rec); added++;
      }
    });
    const F = data.food;
    if (F && typeof F === 'object'){
      if (F.profile && (!S.food.profile || (F.profile.updated || 0) > (S.food.profile.updated || 0))) S.food.profile = F.profile;
      S.food.foods = Object.assign({}, F.foods || {}, S.food.foods || {});
      S.food.hidden = [...new Set([...(S.food.hidden || []), ...(F.hidden || [])])];
      Object.entries(F.days || {}).forEach(([k, d]) => {
        if (!/^\d{4}-\d{2}-\d{2}$/.test(k) || !d) return;
        const cur = S.food.days[k];
        if (!cur){ S.food.days[k] = Object.assign({date: k, entries: [], weight: null}, d, {date: k}); days++; return; }
        const ids = new Set((cur.entries || []).map(x => x.id));
        const extra = (d.entries || []).filter(x => x && !ids.has(x.id));
        if (extra.length || (cur.weight == null && d.weight != null) || (cur.steps == null && d.steps != null)) days++;
        cur.entries = [...(cur.entries || []), ...extra];
        if (cur.weight == null && d.weight != null) cur.weight = d.weight;
        if (cur.steps == null && d.steps != null) cur.steps = d.steps;
      });
    }
''')
rep("    toast(added ? `Importadas ${added} sesiones` : 'No había sesiones nuevas en ese archivo');",
    "    onData(); if (view === 'settings') renderSettings();\n    toast(added || days ? `Importado: ${added} entrenamientos y ${days} días de comida` : 'No había datos nuevos en ese archivo');")

# ---------- cálculo de comida: mensajes para Gemini ----------
rep("    else if (c === 'rate_limited') foodMsg = 'Demasiadas consultas seguidas. Espera un momento y vuelve a intentar.';",
    "    else if (c === 'rate_limited') foodMsg = 'Llegaste al límite gratis de Gemini por ahora. Usa Armar plato o la captura manual, o intenta más tarde.';\n"
    "    else if (c === 'bad_key') foodMsg = 'Tu clave de Gemini no funciona. Revísala en Ajustes (el engrane de arriba).';")
rep("    else if (c === 'session_expired') foodMsg = 'Tu sesión de Claude expiró. Vuelve a iniciar sesión.';\n", "")
rep("""    html += `<textarea id="foodText" rows="2" placeholder="Busca o describe lo que comiste" """,
    """    if (!aiOn) html += `<p class="hint">Para calcular con IA lo que no esté en tu historial, agrega tu clave de Gemini en Ajustes (el engrane de arriba).</p>`;
    html += `<textarea id="foodText" rows="2" placeholder="Busca o describe lo que comiste" """)

# ---------- navegación con la vista de ajustes ----------
rep("  ['train','food','history','progress'].forEach(k => $('#view-' + k).hidden = k !== v);",
    "  ['train','food','history','progress','settings'].forEach(k => $('#view-' + k).hidden = k !== v);\n"
    "  $('#gearBtn').setAttribute('aria-pressed', v === 'settings');\n"
    "  if (v === 'settings') renderSettings();")

# limpiar restos de la versión web de Claude
assert 'window.claude' not in s, 'quedó una referencia a window.claude'
assert 'fonts.googleapis' not in s

version = (ROOT / 'VERSION').read_text().strip()
s = s.replace('__APP_VERSION__', version)
(ROOT / 'www' / 'index.html').write_text(s)
print('www/index.html listo', len(s), 'bytes, versión', version)
