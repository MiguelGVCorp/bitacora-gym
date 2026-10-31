#!/usr/bin/env python3
"""Versión 2.0: aplica todas las mejoras de PENDIENTES.md a www/index.html (se corre una sola vez)."""
import pathlib, re
P = pathlib.Path(__file__).resolve().parent.parent / 'www' / 'index.html'
s = P.read_text()

def rep(a, b, count=1):
    global s
    n = s.count(a)
    assert n == count, f'esperaba {count} y encontré {n}: {a[:100]!r}'
    s = s.replace(a, b)

# =====================================================================
# ENTRENAMIENTO
# =====================================================================
rep("function newDraft(dayId){\n  const d = dayById(dayId), slots = {};\n  d.slots.forEach(sl => slots[sl.key] = {v: preferredVariant(sl), sets: emptySets(sl.sets)});",
r'''/* ---- Progresión, récords, calentamiento y semana de descarga ---- */
const repsTop = reps => { const m = String(reps).match(/(\d+)\s*$/); return m ? +m[1] : null; };
function incFor(exId, dayId){
  const ex = exInfo(exId), note = ex.note || '';
  if (ex.u === 'placas') return 1;
  if (ex.u === 'extra') return 2.5;
  if (/barras fijas/i.test(note)) return 5;
  if (/una mancuerna/i.test(note)) return 2;
  return /^P/.test(dayId) ? 5 : 2.5;
}
function progressHint(sl, exId, prev, dayId){
  if (!prev) return null;
  const top = repsTop(sl.reps); if (!top) return null;
  const sets = prev.sets.filter(s => s.r != null);
  if (sets.length < sl.sets) return null;
  const w = Math.max(...sets.map(s => s.w || 0));
  if (sets.filter(s => (s.w || 0) === w && s.r >= top).length < sl.sets) return null;
  return {from: w, to: Math.round((w + incFor(exId, dayId)) * 10) / 10, top};
}
const e1rm = s => (s.w || 0) * (1 + (s.r || 0) / 30);
function bestE1rm(exId){
  let best = 0;
  history().forEach(h => (h.sets && h.sets[exId] || []).forEach(s => { const v = e1rm(s); if (v > best) best = v; }));
  return best;
}
const roundTo = (v, step) => Math.max(0, Math.round(v / step) * step);
function warmupHTML(exId, w){
  const ex = exInfo(exId);
  if (ex.u !== 'kg' || !w || w < 20) return '';
  const step = /una mancuerna/i.test(ex.note || '') ? 1 : 2.5;
  return `<div class="warm">Calentamiento (no se anota): ${[[0.4, 10], [0.6, 6], [0.8, 3]].map(([p, r]) => `${roundTo(w * p, step)}×${r}`).join(' · ')}</div>`;
}
const isDeload = () => !!(S.deloadUntil && S.deloadUntil > Date.now());
function cycleInfo(){
  if (S.deloadUntil && S.deloadUntil <= Date.now()){ S.cycleStart = S.deloadUntil; S.deloadUntil = null; S.deloadSnooze = null; saveLocal(); }
  const h = history(); if (!h.length) return null;
  const start = S.cycleStart || h[0].date;
  return {week: Math.floor((Date.now() - start) / (7 * 864e5)) + 1, deload: isDeload()};
}
function cycleBanner(){
  const cy = cycleInfo(); if (!cy) return '';
  if (cy.deload) return `<div class="banner ok"><b>Semana de descarga</b><p>Hasta el ${dShort(S.deloadUntil)}: la mitad de las series y ~10% menos peso; ya viene precargado. Entrena suave y enfócate en la técnica.</p><button class="link" type="button" data-cycle="end">Terminar la descarga</button></div>`;
  if (cy.week >= 8 && !(S.deloadSnooze && S.deloadSnooze > Date.now())) return `<div class="banner"><b>Semana ${cy.week}: toca descarga</b><p>Una semana ligera (mitad de series y ~10% menos peso) te ayuda a recuperarte y regresar más fuerte.</p><div class="row-btns"><button class="btn" type="button" data-cycle="snooze">Ahora no</button><button class="btn primary" type="button" data-cycle="start">Activar esta semana</button></div></div>`;
  return '';
}
function newDraft(dayId){
  const d = dayById(dayId), slots = {};
  d.slots.forEach(sl => slots[sl.key] = {v: preferredVariant(sl), sets: emptySets(isDeload() ? Math.max(1, Math.ceil(sl.sets / 2)) : sl.sets)});''')

rep('''  html += `<div class="session">
      <div><div class="label">Tiempo de sesión</div>''', '''  html += cycleBanner();
  html += `<div class="session">
      <div><div class="label">Tiempo de sesión</div>''')

rep("  day.slots.forEach(sl => {\n    const st = D.slots[sl.key] || (D.slots[sl.key] = {v: sl.vars[0], sets: emptySets(sl.sets)});\n    const ex = exInfo(st.v), U = UNITS[ex.u];\n    const prev = lastFor(st.v);",
"  day.slots.forEach((sl, si) => {\n    const st = D.slots[sl.key] || (D.slots[sl.key] = {v: sl.vars[0], sets: emptySets(sl.sets)});\n    const ex = exInfo(st.v), U = UNITS[ex.u];\n    const prev = lastFor(st.v);\n    const hint = !isDeload() && progressHint(sl, st.v, prev, D.day);\n    const prevTop = prev ? Math.max(...prev.sets.map(s => s.w || 0)) : 0;\n    const wPh = p => { if (!p || p.w == null) return U.ph; if (hint) return hint.to; if (isDeload() && ex.u !== 'extra') return roundTo(p.w * 0.9, ex.u === 'placas' ? 1 : 2.5); return p.w; };")
rep("""      ? `<div class="prev">Última vez (${dShort(prev.date)}): <b>${prev.sets.map(s => fmtSet(s, ex.u)).join(' · ')}</b></div>`""",
"""      ? `<div class="prev">Última vez (${dShort(prev.date)}): <b>${prev.sets.map(s => fmtSet(s, ex.u)).join(' · ')}</b>${hint ? `<div class="up">↑ Completaste ${sl.sets}×${hint.top}: hoy sube a <b>${fmtW(hint.to, ex.u)}${ex.u === 'kg' ? ' kg' : ''}</b></div>` : ''}</div>`""")
rep("""      ${prevTxt}
      <div class="set-head">""", """      ${prevTxt}
      ${si < 2 ? warmupHTML(st.v, hint ? hint.to : prevTop) : ''}
      <div class="set-head">""")
rep('''placeholder="${p && p.w != null ? p.w : U.ph}" aria-label="${U.head} serie ${i+1}">''', '''placeholder="${wPh(p)}" aria-label="${U.head} serie ${i+1}">''')

# Récords en vivo al marcar una serie
rep("""      if (s.r === '' && /^\\d+$/.test(rIn.placeholder)){ s.r = rIn.placeholder; rIn.value = s.r; }
      const wasStarted = !!S.draft.start;""", """      if (s.r === '' && /^\\d+$/.test(rIn.placeholder)){ s.r = rIn.placeholder; rIn.value = s.r; }
      const best = bestE1rm(st.v), val = e1rm({w: num(s.w), r: num(s.r)});
      S.draft.prs = S.draft.prs || {};
      if (best > 0 && val > best + 0.01 && val > (S.draft.prs[st.v] || 0)){
        S.draft.prs[st.v] = val;
        toast(`¡Récord en ${exInfo(st.v).name}! ${fmtSet({w: num(s.w), r: num(s.r)}, exInfo(st.v).u)}`);
        if (HAP) safe(() => HAP.vibrate({duration: 120}));
      }
      const wasStarted = !!S.draft.start;""")

# Botones del banner de descarga
rep("""$('#view-train').addEventListener('click', async e => {
  const t = e.target;""", """$('#view-train').addEventListener('click', async e => {
  const t = e.target;
  const cyb = t.closest('[data-cycle]');
  if (cyb){
    const a = cyb.dataset.cycle;
    if (a === 'start'){ S.deloadUntil = Date.now() + 7 * 864e5; if (!draftHasData()) S.draft = newDraft(S.draft.day); toast('Semana de descarga activada'); }
    if (a === 'snooze'){ S.deloadSnooze = Date.now() + 7 * 864e5; toast('Te lo recuerdo la próxima semana'); }
    if (a === 'end'){ S.deloadUntil = Date.now() - 1; if (!draftHasData()) S.draft = null; toast('Descarga terminada: empieza un nuevo ciclo'); }
    saveLocal(); renderTrain(); return;
  }""")

# Récords al guardar la sesión
rep("""  const rec = {id: uid(), day: D.day, date: D.start || Date.now(), end: Date.now(), duration: dur, sets, notes: D.notes || ''};""",
"""  const prs = [];
  Object.entries(sets).forEach(([exId, arr]) => {
    const best = bestE1rm(exId), top = arr.reduce((b, x) => e1rm(x) > e1rm(b) ? x : b, arr[0]);
    if (best > 0 && e1rm(top) > best + 0.01) prs.push({ex: exId, w: top.w, r: top.r});
  });
  const rec = {id: uid(), day: D.day, date: D.start || Date.now(), end: Date.now(), duration: dur, sets, notes: D.notes || '', prs, deload: isDeload() || undefined};""")
rep("""  toast('Sesión guardada');
  renderTrain(); switchView('history');""", """  toast(prs.length ? `Sesión guardada · ${prs.length} ${prs.length === 1 ? 'récord' : 'récords'} nuevo${prs.length === 1 ? '' : 's'}` : 'Sesión guardada');
  renderTrain(); switchView('history');""")

# Cuenta regresiva 3-2-1
rep("""    if (left <= 0 && !rest.beeped){ rest.beeped = true; $('#restbar').classList.add('over'); beep(); }""",
"""    const sec = Math.ceil(left);
    if (left > 0 && sec <= 3 && rest.cd !== sec){ rest.cd = sec; countdownTick(); }
    if (left <= 0 && !rest.beeped){ rest.beeped = true; $('#restbar').classList.add('over'); beep(); }""")
rep("function tick(){", r'''function countdownTick(){
  if (HAP) safe(() => HAP.vibrate({duration: 60}));
  const bar = $('#restbar'); bar.classList.remove('cd'); void bar.offsetWidth; bar.classList.add('cd');
  if (document.visibilityState !== 'visible' || !actx) return;
  try {
    const o = actx.createOscillator(), g = actx.createGain(), t0 = actx.currentTime;
    o.type = 'sine'; o.frequency.value = 660; o.connect(g); g.connect(actx.destination);
    g.gain.setValueAtTime(.0001, t0); g.gain.exponentialRampToValueAtTime(.25, t0 + .01); g.gain.exponentialRampToValueAtTime(.0001, t0 + .09);
    o.start(t0); o.stop(t0 + .1);
  } catch(e){}
}
function tick(){''')

# Historial: récords
rep("""          ${h._pending ? '<span class="pill wait">Por subir</span>' : `<span class="pill">${esc(d.name)}</span>`}</summary>""",
"""          <span class="pills">${h.prs && h.prs.length ? `<span class="pill pr">${h.prs.length} ${h.prs.length === 1 ? 'récord' : 'récords'}</span>` : ''}${h.deload ? '<span class="pill wait">Descarga</span>' : ''}${h._pending ? '<span class="pill wait">Por subir</span>' : `<span class="pill">${esc(d.name)}</span>`}</span></summary>""")
rep("""          ${h.notes ? `<div class="note">${esc(h.notes)}</div>` : ''}
          <button class="link" type="button" data-del""", """          ${h.prs && h.prs.length ? `<div class="note">Récords: ${h.prs.map(p => `${esc(exInfo(p.ex).name)} ${fmtSet(p, exInfo(p.ex).u)}`).join(' · ')}</div>` : ''}
          ${h.notes ? `<div class="note">${esc(h.notes)}</div>` : ''}
          <button class="link" type="button" data-del""")

# =====================================================================
# COMIDA
# =====================================================================
rep("""function totals(doc){
  const t = {kcal:0, p:0, c:0, f:0};
  (doc.entries || []).forEach(e =>""", """function totals(doc){
  const t = {kcal:0, p:0, c:0, f:0};
  (doc.entries || []).filter(e => !e.planned).forEach(e =>""")
rep("let foodMode = 'search',", "let foodPlanned = false, entryOpen = null, showScanInput = false;\nlet foodMode = 'search',")

# Día siguiente: hasta 7 días adelante (para comidas planeadas)
rep("""  const dLabel = isToday ? 'Hoy' : foodDay === dkShift(today, -1) ? 'Ayer' : dkParse(foodDay).toLocaleDateString('es-MX', {weekday:'long'});""",
"""  const dLabel = isToday ? 'Hoy' : foodDay === dkShift(today, -1) ? 'Ayer' : foodDay === dkShift(today, 1) ? 'Mañana' : dkParse(foodDay).toLocaleDateString('es-MX', {weekday:'long'});""")
rep('''id="dNext" aria-label="Día siguiente" ${isToday ? 'disabled' : ''}>''', '''id="dNext" aria-label="Día siguiente" ${foodDay >= dkShift(today, 7) ? 'disabled' : ''}>''')
rep("if (n <= dk(Date.now())){ foodDay = n;", "if (n <= dkShift(dk(Date.now()), 7)){ foodDay = n;")

# Interruptor de "planeado"
rep("""data-meal="${k}" aria-pressed="${k === foodMeal}">${n}</button>`).join('')}</div>`;""",
"""data-meal="${k}" aria-pressed="${k === foodMeal}">${n}</button>`).join('')}</div>
      <label class="plan-tg" for="planTg"><input type="checkbox" id="planTg" ${foodPlanned ? 'checked' : ''}> Guardar como planeado (no cuenta hasta que lo comas)</label>`;""")
rep("""  doc.entries.push({id: uid(), meal: foodMeal, text: text.slice(0, 200), items: items.map(({base, ...i}) => i), t: Date.now()});
  putDay(foodDay, doc);""", """  const en = {id: uid(), meal: foodMeal, text: text.slice(0, 200), items: items.map(({base, ...i}) => i), t: Date.now()};
  if (foodPlanned) en.planned = true;
  doc.entries.push(en);
  putDay(foodDay, doc);
  if (foodPlanned){ foodPlanned = false; toast('Guardado como planeado: toca "Ya me lo comí" cuando lo comas'); }""")

# Escáner en la fila de botones
rep("""        <button class="btn" type="button" id="plateOn">Armar plato</button>""",
"""        <button class="btn" type="button" id="scanBtn">Escanear</button>
        <button class="btn" type="button" id="plateOn">Armar plato</button>""")
rep("""      ${foodPreview || foodBusy ? '' : `<div id="sugg">${suggHTML()}</div>`}""",
"""      ${showScanInput ? `<div class="wrow"><input id="bcIn" type="text" inputmode="numeric" placeholder="Código de barras (los números de abajo)" autocomplete="off"><button class="btn" type="button" id="bcGo">Buscar</button></div>` : ''}
      ${foodPreview || foodBusy ? '' : `<div id="sugg">${suggHTML()}</div>`}""")

# Registros: planeado, porción, mover
rep("""      const mk = es.reduce((a,e) => a + e.items.reduce((b,i) => b + (+i.kcal||0), 0), 0);""",
"""      const mk = es.filter(e => !e.planned).reduce((a,e) => a + e.items.reduce((b,i) => b + (+i.kcal||0), 0), 0);""")
rep("""        ${es.map(e => `<div class="entry">
          <div class="entry-t"><span>${esc(e.text)}</span><button class="link muted" type="button" data-edel="${esc(e.id)}">Quitar</button></div>
          ${e.items.map(i => `<div class="it"><span>${esc(i.name)}${i.qty ? ` <small>${esc(i.qty)}</small>` : ''}</span><span>${r0(i.kcal)}</span></div>`).join('')}
        </div>`).join('')}""",
"""        ${es.map(e => `<div class="entry${e.planned ? ' planned' : ''}">
          <div class="entry-t"><span>${e.planned ? '<b class="tag">Planeado</b> ' : ''}${esc(e.text)}${e.portion && e.portion !== 1 ? ` <b class="tag">× ${fmtPortion(e.portion)}</b>` : ''}</span></div>
          ${e.items.map(i => `<div class="it"><span>${esc(i.name)}${i.qty ? ` <small>${esc(i.qty)}</small>` : ''}</span><span>${r0(i.kcal)}</span></div>`).join('')}
          <div class="entry-a">${e.planned ? `<button class="link" type="button" data-eate="${esc(e.id)}">Ya me lo comí</button>` : ''}<button class="link muted" type="button" data-eopen="${esc(e.id)}:port">Porción</button><button class="link muted" type="button" data-eopen="${esc(e.id)}:move">Mover</button><button class="link muted" type="button" data-edel="${esc(e.id)}">Quitar</button></div>
          ${entryOpen === e.id + ':port' ? `<div class="chips">${PORTIONS.map(f => `<button class="chip" type="button" data-portion="${esc(e.id)}|${f}" aria-pressed="${(e.portion || 1) === f}">${fmtPortion(f)}</button>`).join('')}</div>` : ''}
          ${entryOpen === e.id + ':move' ? `<div class="chips">${moveTargets(foodDay).map(([k, lbl]) => `<button class="chip" type="button" data-moveto="${esc(e.id)}|${k}">${lbl}</button>`).join('')}</div>` : ''}
        </div>`).join('')}""")
rep("function addEntry(items, text){", r'''const PORTIONS = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2];
const fmtPortion = f => ({0.25: '¼', 0.5: '½', 0.75: '¾', 1: '1', 1.25: '1¼', 1.5: '1½', 2: '2'}[f] || String(f));
function moveTargets(day){
  const today = dk(Date.now()), out = [], lbl = k => k === today ? 'Hoy' : k === dkShift(today, -1) ? 'Ayer' : k === dkShift(today, 1) ? 'Mañana' : dkParse(k).toLocaleDateString('es-MX', {weekday: 'short', day: 'numeric'});
  [dkShift(day, -1), dkShift(day, 1), today, dkShift(today, 1)].forEach(k => { if (k !== day && k <= dkShift(today, 7) && !out.some(o => o[0] === k)) out.push([k, lbl(k)]); });
  return out;
}
function editEntry(id, fn){
  const doc = JSON.parse(JSON.stringify(dayDoc(foodDay)));
  const e = (doc.entries || []).find(x => x.id === id); if (!e) return null;
  fn(e, doc); putDay(foodDay, doc); return e;
}

/* ---- Escáner de código de barras (Open Food Facts) ---- */
const BS = plug('BarcodeScanner');
async function scanBarcode(){
  if (!BS){ showScanInput = !showScanInput; renderFood(); if (showScanInput) setTimeout(() => $('#bcIn') && $('#bcIn').focus(), 50); return; }
  try {
    const av = await BS.isGoogleBarcodeScannerModuleAvailable().catch(() => ({available: true}));
    if (av && av.available === false){
      toast('Descargando el escáner de Google, intenta en unos segundos…');
      await BS.installGoogleBarcodeScannerModule().catch(() => {});
      return;
    }
    const r = await BS.scan();
    const bc = r && r.barcodes && r.barcodes[0];
    const code = bc && (bc.rawValue || bc.displayValue);
    if (code) lookupBarcode(code);
  } catch(e){
    if (!/cancel/i.test(String((e && e.message) || e))) { toast('No se pudo abrir el escáner. Escribe el código.'); showScanInput = true; renderFood(); }
  }
}
async function lookupBarcode(raw){
  const code = String(raw || '').replace(/\D/g, ''); if (code.length < 6){ toast('Ese código no parece válido.'); return; }
  const known = Object.entries(S.food.foods || {}).find(([, f]) => f.code === code);
  const toPlate = (key, serv) => { plate.push({key, n: Math.round(serv || 100)}); foodMode = 'plate'; plQ = ''; showScanInput = false; renderFood(); };
  if (known){ toPlate(known[0], known[1].serv); toast(`${known[1].name}: ajusta los gramos`); return; }
  toast('Buscando el producto…');
  try {
    const r = await fetch(`https://world.openfoodfacts.org/api/v2/product/${code}.json?fields=product_name,product_name_es,brands,nutriments,serving_quantity`);
    const d = await r.json();
    const p = d && d.status === 1 && d.product, nm = (p && p.nutriments) || {};
    const kcal = nm['energy-kcal_100g'] != null ? +nm['energy-kcal_100g'] : (nm['energy_100g'] != null ? nm['energy_100g'] / 4.184 : null);
    if (!p || kcal == null){
      toast('No encontré ese producto: agrégalo con los datos de la etiqueta');
      modeBack = 'plate'; editFood = null; foodMode = 'newfood'; showScanInput = false; renderFood();
      return;
    }
    const name = [p.product_name_es || p.product_name || 'Producto', String(p.brands || '').split(',')[0].trim()].filter(Boolean).join(' · ').slice(0, 80);
    const key = norm(name), serv = +p.serving_quantity || 100;
    S.food.foods[key] = {name, unit: 'g', kcal, p: +(nm.proteins_100g || 0), c: +(nm.carbohydrates_100g || 0), f: +(nm.fat_100g || 0), code, serv};
    S.food.hidden = (S.food.hidden || []).filter(k => k !== key); saveNut();
    toPlate(key, serv);
    toast(`${name}: ${r0(kcal)} kcal por 100 g. Ajusta los gramos.`);
  } catch(e){ toast('Sin conexión para buscar el producto. Intenta de nuevo o captúralo a mano.'); }
}

function addEntry(items, text){''')

rep("""$('#view-food').addEventListener('click', async e => {
  const t = e.target, b = t.closest('button'); if (!b) return;""", """$('#view-food').addEventListener('click', async e => {
  const t = e.target, b = t.closest('button'); if (!b) return;
  if (b.id === 'scanBtn'){ scanBarcode(); return; }
  if (b.id === 'bcGo'){ lookupBarcode($('#bcIn').value); return; }
  if (b.dataset.eate){ editEntry(b.dataset.eate, en => { delete en.planned; en.t = Date.now(); }); toast('Listo, ya cuenta en tu día'); renderFood(); return; }
  if (b.dataset.eopen){ entryOpen = entryOpen === b.dataset.eopen ? null : b.dataset.eopen; renderFood(); return; }
  if (b.dataset.portion){
    const [id, fs] = b.dataset.portion.split('|'), fac = +fs;
    editEntry(id, en => {
      en.base = en.base || en.items.map(i => Object.assign({}, i));
      en.portion = fac;
      en.items = en.base.map(i => Object.assign({}, i, {kcal: r0(i.kcal * fac), p: r0(i.p * fac), c: r0(i.c * fac), f: r0(i.f * fac)}));
      if (fac === 1){ delete en.portion; }
    });
    entryOpen = null; toast(fac === 1 ? 'Porción completa' : `Ajustado a ${fmtPortion(fac)} de la porción`); renderFood(); return;
  }
  if (b.dataset.moveto){
    const [id, target] = b.dataset.moveto.split('|');
    const src = JSON.parse(JSON.stringify(dayDoc(foodDay)));
    const en = (src.entries || []).find(x => x.id === id); if (!en) return;
    src.entries = src.entries.filter(x => x.id !== id);
    const dst = JSON.parse(JSON.stringify(dayDoc(target)));
    dst.entries = dst.entries || []; dst.entries.push(en);
    putDay(foodDay, src); putDay(target, dst);
    entryOpen = null; toast(`Movido a ${moveTargets(foodDay).find(m => m[0] === target)?.[1] || target}`); renderFood(); return;
  }""")
rep("""$('#view-food').addEventListener('change', e => { if (e.target.dataset.pv != null) renderFood(); });""",
"""$('#view-food').addEventListener('change', e => {
  if (e.target.id === 'planTg'){ foodPlanned = e.target.checked; return; }
  if (e.target.dataset.pv != null) renderFood();
});
$('#view-food').addEventListener('keydown', e => { if (e.target.id === 'bcIn' && e.key === 'Enter'){ e.preventDefault(); lookupBarcode(e.target.value); } });""")

# =====================================================================
# PROGRESO: cintura y fotos
# =====================================================================
rep('<input type="file" id="importFile" accept="application/json,.json" hidden>',
    '<input type="file" id="importFile" accept="application/json,.json" hidden>\n<input type="file" id="photoFile" accept="image/*" multiple hidden>')
rep("""  let html = `<select id="exSel" aria-label="Ejercicio">` + ROUTINE.map(d => {""", """  let html = bodyHTML() + `<h2>Ejercicios</h2><select id="exSel" aria-label="Ejercicio">` + ROUTINE.map(d => {""")
rep("function renderProgress(){", r'''let showPhotos = false;
function weekAvgOf(field, endKey){
  const from = dkShift(endKey, -7);
  const a = Object.values(S.food.days || {}).filter(d => d[field] != null && d.date > from && d.date <= endKey).map(d => +d[field]);
  return a.length ? a.reduce((x, v) => x + v, 0) / a.length : null;
}
const imgSrc = p => p.src || (p.uri && window.Capacitor && window.Capacitor.convertFileSrc ? window.Capacitor.convertFileSrc(p.uri) : '');
const imgTag = p => `<img src="${esc(imgSrc(p))}" alt="Foto de progreso del ${esc(p.date)}" loading="lazy">`;
function miniChart(pts, unit){
  const W = 640, H = 170, L = 40, R = 16, T = 16, B = 26;
  let min = Math.min(...pts.map(p => p.v)), max = Math.max(...pts.map(p => p.v));
  if (max - min < 2){ min -= 1; max += 1; }
  const x = i => pts.length === 1 ? (L + W - R) / 2 : L + i * (W - L - R) / (pts.length - 1);
  const y = v => T + (1 - (v - min) / (max - min)) * (H - T - B);
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(p.v).toFixed(1)}`).join(' ');
  let g = '';
  [min, (min + max) / 2, max].forEach(v => g += `<line x1="${L}" x2="${W - R}" y1="${y(v).toFixed(1)}" y2="${y(v).toFixed(1)}" stroke="var(--line)"/><text x="${L - 6}" y="${(y(v) + 4).toFixed(1)}" text-anchor="end" font-size="11" fill="var(--muted)">${Math.round(v * 10) / 10}</text>`);
  g += `<text x="${L}" y="${H - 6}" font-size="11" fill="var(--muted)">${dShort(dkParse(pts[0].k))}</text><text x="${W - R}" y="${H - 6}" text-anchor="end" font-size="11" fill="var(--muted)">${dShort(dkParse(pts[pts.length - 1].k))}</text>`;
  return `<div class="chart"><svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Cintura en ${unit}">${g}<path d="${d}" fill="none" stroke="var(--accent)" stroke-width="3" stroke-linejoin="round"/>${pts.map((p, i) => `<circle cx="${x(i).toFixed(1)}" cy="${y(p.v).toFixed(1)}" r="4" fill="var(--accent)"/>`).join('')}</svg></div>`;
}
function bodyHTML(){
  const today = dk(Date.now()), doc = dayDoc(today);
  const ws = Object.values(S.food.days || {}).filter(d => d.waist).map(d => ({k: d.date, v: +d.waist})).sort((a, b) => a.k < b.k ? -1 : 1);
  const first = ws[0], last = ws[ws.length - 1];
  const wAvg = weekAvgOf('weight', today);
  const photos = S.photos || [], dates = [...new Set(photos.map(p => p.date))].sort();
  const firstSet = dates.length ? photos.filter(p => p.date === dates[0]) : [];
  const lastSet = dates.length > 1 ? photos.filter(p => p.date === dates[dates.length - 1]) : [];
  return `<section class="card body-card">
    <h3>Cuerpo</h3>
    <div class="stats">
      <div class="stat"><b>${wAvg ? wAvg.toFixed(1) : '–'}</b><small>peso prom. 7 días (kg)</small></div>
      <div class="stat"><b>${last ? last.v : '–'}</b><small>cintura (cm)${last ? ' · ' + dShort(dkParse(last.k)) : ''}</small></div>
      <div class="stat"><b>${first && last && ws.length > 1 ? ((last.v - first.v) > 0 ? '+' : '') + (Math.round((last.v - first.v) * 10) / 10) : '–'}</b><small>cintura desde el inicio</small></div>
    </div>
    <p class="hint">Mide tu cintura una vez por semana, en ayunas y a la altura del ombligo. Si baja, estás perdiendo grasa aunque la báscula casi no se mueva.</p>
    <div class="wrow"><input id="waistIn" type="number" inputmode="decimal" step="0.5" min="40" max="200" placeholder="Cintura de hoy (cm)" value="${doc.waist ?? ''}" aria-label="Cintura de hoy en cm"><button class="btn" type="button" id="waistSave">${doc.waist ? 'Actualizar' : 'Guardar'}</button></div>
    ${ws.length >= 2 ? miniChart(ws, 'cm') : ''}
    <h3 style="margin-top:18px">Fotos de progreso</h3>
    <p class="hint">De frente, de lado y de espalda, con la misma luz y a la misma hora. Se guardan solo en tu celular (no van en el respaldo).</p>
    <div class="row-btns" style="justify-content:flex-start"><button class="btn primary" type="button" id="photoAdd">Agregar fotos de hoy</button>${photos.length ? `<button class="link" type="button" id="photoToggle">${showPhotos ? 'Ocultar' : `Ver todas (${dates.length} ${dates.length === 1 ? 'día' : 'días'})`}</button>` : ''}</div>
    ${lastSet.length ? `<div class="cmp"><div><small>Inicio · ${dShort(dkParse(dates[0]))}</small>${firstSet.map(imgTag).join('')}</div><div><small>Última · ${dShort(dkParse(dates[dates.length - 1]))}</small>${lastSet.map(imgTag).join('')}</div></div>` : firstSet.length ? `<div class="gal">${firstSet.map(imgTag).join('')}</div>` : ''}
    ${showPhotos ? dates.slice().reverse().map(dd => `<div class="gal-d"><small>${dShort(dkParse(dd))}</small><div class="gal">${photos.filter(p => p.date === dd).map(p => `<span class="ph">${imgTag(p)}<button class="x sm" type="button" data-phdel="${esc(p.id)}" aria-label="Borrar foto">✕</button></span>`).join('')}</div></div>`).join('') : ''}
  </section>`;
}
function resizeImage(file, max){
  return new Promise((res, rej) => {
    const url = URL.createObjectURL(file), img = new Image();
    img.onload = () => {
      const k = Math.min(1, max / Math.max(img.width, img.height));
      const c = document.createElement('canvas'); c.width = Math.round(img.width * k); c.height = Math.round(img.height * k);
      c.getContext('2d').drawImage(img, 0, 0, c.width, c.height);
      URL.revokeObjectURL(url); res(c.toDataURL('image/jpeg', 0.82));
    };
    img.onerror = () => { URL.revokeObjectURL(url); rej(new Error('img')); };
    img.src = url;
  });
}
$('#photoFile').addEventListener('change', async e => {
  const files = [...e.target.files].slice(0, 6); e.target.value = '';
  if (!files.length) return;
  S.photos = S.photos || []; const date = dk(Date.now()); let n = 0;
  for (const f of files){
    try {
      const id = uid();
      if (IS_NATIVE && FS){
        const data = await resizeImage(f, 1280), path = `fotos/${date}-${id}.jpg`;
        const r = await FS.writeFile({path, data: data.split(',')[1], directory: 'DATA', recursive: true});
        S.photos.push({id, date, uri: r.uri, path});
      } else {
        S.photos.push({id, date, src: await resizeImage(f, 640)});
      }
      n++;
    } catch(err){}
  }
  saveLocal(); renderProgress();
  toast(n ? `${n} ${n === 1 ? 'foto guardada' : 'fotos guardadas'}` : 'No se pudieron guardar las fotos');
});
$('#view-progress').addEventListener('click', async e => {
  const b = e.target.closest('button'); if (!b) return;
  if (b.id === 'waistSave'){
    const v = num($('#waistIn').value);
    if (!v || v < 40 || v > 200){ toast('Escribe tu cintura en centímetros.'); return; }
    const k = dk(Date.now()), doc = JSON.parse(JSON.stringify(dayDoc(k)));
    doc.waist = Math.round(v * 10) / 10; putDay(k, doc); toast('Cintura guardada'); renderProgress(); return;
  }
  if (b.id === 'photoAdd'){ $('#photoFile').click(); return; }
  if (b.id === 'photoToggle'){ showPhotos = !showPhotos; renderProgress(); return; }
  if (b.dataset.phdel){
    if (!(await ask('¿Borrar esta foto?', 'Borrar', true))) return;
    const p = (S.photos || []).find(x => x.id === b.dataset.phdel);
    if (p && p.path && FS) await safe(() => FS.deleteFile({path: p.path, directory: 'DATA'}));
    S.photos = (S.photos || []).filter(x => x.id !== b.dataset.phdel); saveLocal(); renderProgress(); return;
  }
});
function renderProgress(){''')

# =====================================================================
# RESUMEN DE LA SEMANA (Historial)
# =====================================================================
rep("""function renderHistory(){
  const all = history(), list = [...all].reverse();
  let html = '';""", r'''let sumWeek = 0;
function weekRange(offset){
  const d = new Date(); d.setHours(0, 0, 0, 0);
  const dow = (d.getDay() + 6) % 7; d.setDate(d.getDate() - dow - offset * 7);
  const start = dk(d), end = dkShift(start, 6);
  return {start, end, t0: dkParse(start).getTime(), t1: dkParse(end).getTime() + 864e5};
}
function weekSummary(offset){
  const w = weekRange(offset), prev = weekRange(offset + 1);
  const ses = history().filter(h => h.date >= w.t0 && h.date < w.t1);
  const timed = ses.filter(h => h.duration);
  const prs = ses.flatMap(h => h.prs || []);
  const days = Object.values(S.food.days || {}).filter(d => d.date >= w.start && d.date <= w.end);
  const T = S.food.profile && S.food.profile.targets;
  const logged = days.filter(d => (d.entries || []).some(e => !e.planned));
  const kc = logged.map(d => totals(d).kcal), pr = logged.map(d => totals(d).p);
  const avg = a => a.length ? a.reduce((x, v) => x + v, 0) / a.length : null;
  const inRange = (r, f) => Object.values(S.food.days || {}).filter(d => d[f] != null && d.date >= r.start && d.date <= r.end).map(d => +d[f]);
  const wt = avg(inRange(w, 'weight')), wtPrev = avg(inRange(prev, 'weight'));
  const st = inRange(w, 'steps');
  const wa = inRange(w, 'waist'), waPrev = inRange(prev, 'waist');
  return {w, ses: ses.length, target: ORDER.length, dur: timed.length ? avg(timed.map(h => h.duration)) / 60 : null, prs,
    logged: logged.length, kcal: avg(kc), kcalT: T && T.kcal, protOk: T ? pr.filter(p => p >= T.p).length : null, protT: T && T.p,
    wt, wtDiff: wt != null && wtPrev != null ? wt - wtPrev : null, steps: avg(st), stepsN: st.length, stepsOk: st.filter(v => v >= STEP_GOAL).length,
    waist: wa.length ? wa[wa.length - 1] : null, waistDiff: wa.length && waPrev.length ? wa[wa.length - 1] - waPrev[waPrev.length - 1] : null};
}
const sgn = (v, d = 1) => (v > 0 ? '+' : v < 0 ? '−' : '') + Math.abs(Math.round(v * 10 ** d) / 10 ** d);
function weekRangeLabel(w){ return `${dShort(dkParse(w.start))} – ${dShort(dkParse(w.end))}`; }
function summaryText(m){
  const L = [`Resumen Bitácora Gym · semana ${weekRangeLabel(m.w)}`];
  L.push(`Entrenamientos: ${m.ses} de ${m.target}${m.dur ? ` (prom. ${Math.round(m.dur)} min)` : ''}.${m.prs.length ? ' Récords: ' + m.prs.map(p => `${exInfo(p.ex).name} ${fmtSet(p, exInfo(p.ex).u)}`).join(', ') + '.' : ''}`);
  if (m.logged) L.push(`Comida: ${m.logged} días registrados, prom. ${r0(m.kcal).toLocaleString('es-MX')} kcal${m.kcalT ? ` (meta ${m.kcalT.toLocaleString('es-MX')})` : ''}; proteína cumplida ${m.protOk} de ${m.logged} días${m.protT ? ` (meta ${m.protT} g)` : ''}.`);
  if (m.wt != null) L.push(`Peso: ${m.wt.toFixed(1)} kg prom.${m.wtDiff != null ? ` (${sgn(m.wtDiff)} kg vs semana anterior)` : ''}.${m.waist != null ? ` Cintura: ${m.waist} cm${m.waistDiff != null ? ` (${sgn(m.waistDiff)})` : ''}.` : ''}`);
  if (m.stepsN) L.push(`Pasos: ${r0(m.steps).toLocaleString('es-MX')} prom., ${m.stepsOk} de ${m.stepsN} días con ${STEP_GOAL.toLocaleString('es-MX')}+.`);
  return L.join('\n');
}
function summaryHTML(){
  const m = weekSummary(sumWeek);
  const cell = (v, l) => `<div class="stat"><b>${v}</b><small>${l}</small></div>`;
  return `<section class="card sum">
    <div class="meal-h"><h3>Resumen de la semana</h3><span class="chips" style="margin:0"><button class="chip" type="button" data-sumw="0" aria-pressed="${sumWeek === 0}">Esta</button><button class="chip" type="button" data-sumw="1" aria-pressed="${sumWeek === 1}">Pasada</button></span></div>
    <p class="hint" style="margin-top:2px">${weekRangeLabel(m.w)}</p>
    <div class="stats">
      ${cell(`${m.ses}/${m.target}`, 'entrenamientos')}
      ${cell(m.kcal ? r0(m.kcal).toLocaleString('es-MX') : '–', `kcal prom.${m.kcalT ? ' (meta ' + m.kcalT.toLocaleString('es-MX') + ')' : ''}`)}
      ${cell(m.logged ? `${m.protOk}/${m.logged}` : '–', 'días con tu proteína')}
      ${cell(m.wt != null ? m.wt.toFixed(1) : '–', `kg prom.${m.wtDiff != null ? ' (' + sgn(m.wtDiff) + ')' : ''}`)}
      ${cell(m.stepsN ? r0(m.steps).toLocaleString('es-MX') : '–', `pasos prom. (${m.stepsOk}/${m.stepsN} con meta)`)}
      ${cell(m.waist != null ? m.waist : '–', `cintura cm${m.waistDiff != null ? ' (' + sgn(m.waistDiff) + ')' : ''}`)}
    </div>
    ${m.prs.length ? `<p class="hint">Récords: ${m.prs.map(p => `${esc(exInfo(p.ex).name)} ${fmtSet(p, exInfo(p.ex).u)}`).join(' · ')}</p>` : ''}
    <div class="row-btns"><button class="btn" type="button" id="sumShare">Compartir resumen</button><button class="btn primary" type="button" id="sumBackup">Exportar respaldo</button></div>
  </section>`;
}
function renderHistory(){
  const all = history(), list = [...all].reverse();
  let html = summaryHTML();''')
rep("""$('#view-history').addEventListener('click', async e => {
  const t = e.target;""", """$('#view-history').addEventListener('click', async e => {
  const t = e.target;
  const sw = t.closest('[data-sumw]'); if (sw){ sumWeek = +sw.dataset.sumw; renderHistory(); return; }
  if (t.id === 'sumBackup'){ exportJson(); return; }
  if (t.id === 'sumShare'){
    const text = summaryText(weekSummary(sumWeek));
    if (IS_NATIVE && SH){ try { await SH.share({title: 'Resumen de la semana', text, dialogTitle: 'Compartir resumen'}); } catch(err){} return; }
    try { await navigator.clipboard.writeText(text); toast('Resumen copiado'); } catch(err){ toast('No se pudo copiar'); }
    return;
  }""")

# =====================================================================
# RECORDATORIOS y COPIA AUTOMÁTICA
# =====================================================================
rep("function exportJson(){\n  const food = {profile: S.food.profile, foods: S.food.foods || {}, hidden: S.food.hidden || [], days: S.food.days || {}};\n  offerFile(`bitacora-gym-${dk(Date.now())}.json`, JSON.stringify({version: 5, exported: Date.now(), history: history().map(({_pending, ...h}) => h), food, routine: S.routine || null}, null, 2));\n}",
r'''function backupJSON(){
  const food = {profile: S.food.profile, foods: S.food.foods || {}, hidden: S.food.hidden || [], days: S.food.days || {}};
  return JSON.stringify({version: 6, exported: Date.now(), history: history().map(({_pending, ...h}) => h), food, routine: S.routine || null, rem: S.rem || null, cycleStart: S.cycleStart || null}, null, 2);
}
function exportJson(){ offerFile(`bitacora-gym-${dk(Date.now())}.json`, backupJSON()); }
async function autoBackup(force){
  if (!IS_NATIVE || !FS) return null;
  if (!force && Date.now() - (S.autoBackupAt || 0) < 6 * 864e5) return null;
  try {
    await FS.writeFile({path: `BitacoraGym/respaldo-${dk(Date.now())}.json`, data: backupJSON(), directory: 'DOCUMENTS', encoding: 'utf8', recursive: true});
    S.autoBackupAt = Date.now(); S.autoBackupOk = true; saveLocal();
    const ls = await FS.readdir({path: 'BitacoraGym', directory: 'DOCUMENTS'}).catch(() => null);
    const files = ((ls && ls.files) || []).map(f => typeof f === 'string' ? f : f.name).filter(n => /^respaldo-.*\.json$/.test(n)).sort();
    for (const f of files.slice(0, -4)) await safe(() => FS.deleteFile({path: 'BitacoraGym/' + f, directory: 'DOCUMENTS'}));
    return true;
  } catch(e){ S.autoBackupOk = false; saveLocal(); return false; }
}
const REM = {
  peso:     {id: 8001, label: 'Pesarte', when: 'Diario', h: 7, m: 30, title: 'Hora de pesarte', body: 'En ayunas, después del baño. Anótalo en Comida.', view: 'food'},
  pasos:    {id: 8002, label: 'Anotar tus pasos', when: 'Diario', h: 21, m: 30, title: 'Anota tus pasos', body: 'Copia tus pasos de Samsung Health en la app.', view: 'food'},
  cuerpo:   {id: 8003, label: 'Cintura y fotos', when: 'Domingo', h: 8, m: 0, weekday: 1, title: 'Cintura y fotos de la semana', body: 'Mide tu cintura y toma tus fotos en Progreso.', view: 'progress'},
  respaldo: {id: 8004, label: 'Resumen y respaldo', when: 'Domingo', h: 19, m: 0, weekday: 1, title: 'Resumen de tu semana', body: 'Revisa tu resumen y exporta tu respaldo a Drive.', view: 'history'}
};
const remCfg = k => Object.assign({on: false, h: REM[k].h, m: REM[k].m}, (S.rem || {})[k]);
async function applyReminders(){
  if (!LN || !notifOK) return;
  await safe(() => LN.cancel({notifications: Object.values(REM).map(r => ({id: r.id}))}));
  const list = Object.keys(REM).filter(k => remCfg(k).on).map(k => {
    const r = REM[k], c = remCfg(k), on = {hour: c.h, minute: c.m};
    if (r.weekday) on.weekday = r.weekday;
    return {id: r.id, title: r.title, body: r.body, channelId: 'recordatorios', smallIcon: 'ic_stat_timer', schedule: {on, allowWhileIdle: true}, extra: {view: r.view}};
  });
  if (list.length) await safe(() => LN.schedule({notifications: list}));
}''')

rep("""      await safe(() => LN.createChannel({id: 'descanso', name: 'Fin del descanso', description: 'Te avisa cuando termina el descanso entre series', importance: 5, visibility: 1, vibration: true, lights: true}));""",
"""      await safe(() => LN.createChannel({id: 'descanso', name: 'Fin del descanso', description: 'Te avisa cuando termina el descanso entre series', importance: 5, visibility: 1, vibration: true, lights: true}));
      await safe(() => LN.createChannel({id: 'recordatorios', name: 'Recordatorios', description: 'Peso, pasos, cintura y respaldo', importance: 4, visibility: 1, vibration: true}));
      applyReminders();
      LN.addListener('localNotificationActionPerformed', ev => { const v = ev && ev.notification && ev.notification.extra && ev.notification.extra.view; if (v) switchView(v); });""")
rep("""    APP.addListener('appStateChange', st => {
      if (!st || !st.isActive) return;""", """    APP.addListener('appStateChange', st => {
      if (!st || !st.isActive) return;
      autoBackup();""")
rep("async function initNative(){\n  if (!IS_NATIVE) return;", "async function initNative(){\n  if (!IS_NATIVE) return;\n  setTimeout(() => autoBackup(), 4000);")

rep("""    <h2>Avisos de descanso</h2>""", """    <h2>Recordatorios</h2>
    <p class="hint">${!IS_NATIVE ? 'Los recordatorios solo funcionan en la app instalada.' : notifOK ? 'Te llegan como notificación a la hora que elijas.' : 'Activa las notificaciones de la app en Android para recibirlos.'}</p>
    ${Object.keys(REM).map(k => { const r = REM[k], c = remCfg(k); return `<div class="rem-row"><label for="rem-${k}"><input type="checkbox" id="rem-${k}" data-rem="${k}" ${c.on ? 'checked' : ''}> ${r.label} <small>${r.when}</small></label><input type="time" id="remt-${k}" data-remt="${k}" value="${pad(c.h)}:${pad(c.m)}" aria-label="Hora para ${r.label}"></div>`; }).join('')}
    <h2>Avisos de descanso</h2>""")
rep("""    <p class="hint">Todo se guarda en este celular. Exporta un respaldo cada semana y guárdalo en Drive o mándatelo por WhatsApp. Si cambias de celular, lo importas aquí.</p>""",
"""    <p class="hint">Todo se guarda en este celular. Exporta un respaldo cada semana y guárdalo en Drive o mándatelo por WhatsApp. Si cambias de celular, lo importas aquí.</p>
    ${IS_NATIVE ? `<p class="hint"><b style="color:var(--text)">Copia automática:</b> ${S.autoBackupAt ? `${S.autoBackupOk === false ? 'la última falló' : 'la última fue el ' + dShort(S.autoBackupAt)} · ` : ''}cada semana se guarda sola en la carpeta Documentos/BitacoraGym de tu celular (las 4 más recientes). Se conserva aunque desinstales la app.</p>` : ''}""")
rep("""$('#view-settings').addEventListener('change', e => { if (e.target.id === 'gModel'){ S.gemini.model = e.target.value; saveLocal(); } });""",
"""$('#view-settings').addEventListener('change', e => {
  const t = e.target;
  if (t.id === 'gModel'){ S.gemini.model = t.value; saveLocal(); return; }
  if (t.dataset.rem || t.dataset.remt){
    const k = t.dataset.rem || t.dataset.remt; S.rem = S.rem || {};
    const c = remCfg(k);
    if (t.dataset.rem) c.on = t.checked;
    else { const [h, m] = String(t.value || '').split(':').map(Number); if (!isNaN(h) && !isNaN(m)){ c.h = h; c.m = m; } }
    S.rem[k] = c; saveLocal(); applyReminders();
    toast(c.on ? `${REM[k].label}: ${REM[k].when.toLowerCase()} a las ${pad(c.h)}:${pad(c.m)}` : `${REM[k].label}: desactivado`);
  }
});""")

# =====================================================================
# ESTILOS
# =====================================================================
css = r'''
.up{margin-top:4px;color:var(--ok);font-weight:600}
.up b{color:var(--ok)}
.warm{font-size:12.5px;color:var(--muted);margin:-2px 0 8px;font-variant-numeric:tabular-nums}
.banner{background:var(--accent-soft);border-radius:var(--radius);padding:12px 14px;margin:0 0 14px;font-size:14px;line-height:1.4}
.banner.ok{background:var(--ok-soft)}
.banner b{display:block;font-family:var(--display);font-size:18px;text-transform:uppercase;letter-spacing:.02em}
.banner p{margin:4px 0 8px}
.pills{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.pill.pr{background:var(--ok-soft);color:var(--ok)}
.restbar.cd .inner{animation:cdpulse .35s ease}
@keyframes cdpulse{40%{transform:scale(1.03)}}
@media (prefers-reduced-motion: reduce){.restbar.cd .inner{animation:none}}
.plan-tg{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--muted);margin:-2px 0 10px}
.plan-tg input{width:18px;height:18px;accent-color:var(--accent)}
.entry.planned{opacity:.62}
.entry .tag{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;color:var(--accent)}
.entry-a{display:flex;flex-wrap:wrap;gap:4px 14px;margin-top:4px}
.entry-a .link{padding:2px 0;font-size:13px}
.entry .chips{margin:6px 0 2px}
.rem-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 0;border-bottom:1px dashed var(--line)}
.rem-row label{display:flex;align-items:center;gap:8px;font-size:15px;min-width:0}
.rem-row label small{color:var(--muted)}
.rem-row input[type=checkbox]{width:18px;height:18px;accent-color:var(--accent)}
.rem-row input[type=time]{padding:6px 8px;border:1px solid var(--line);border-radius:9px;background:var(--bg);font-size:15px}
.body-card .stats{margin-top:10px}
.cmp{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}
.cmp>div{display:flex;flex-direction:column;gap:6px;min-width:0}
.cmp small,.gal-d small{color:var(--muted);font-size:12px}
.cmp img,.gal img{width:100%;border-radius:10px;display:block;object-fit:cover;aspect-ratio:3/4;background:var(--surface-2)}
.gal{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;margin-top:6px}
.gal-d{margin-top:12px}
.ph{position:relative;display:block}
.x.sm{position:absolute;top:4px;right:4px;width:28px;height:28px;font-size:13px;background:rgba(0,0,0,.55);color:#fff}
.sum .stats{grid-template-columns:repeat(3,minmax(0,1fr))}
'''
rep("@media (max-width:380px){.day small{display:none}", css + "@media (max-width:380px){.day small{display:none}")

P.write_text(s)
print('v2 aplicado:', len(s), 'bytes')
