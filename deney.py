# sim_lab_with_explosion_sound_and_graph.py
from flask import Flask, render_template_string, jsonify
import traceback

app = Flask(__name__)

# Basit eğitim amaçlı reagent veritabanı
REAGENTS = {
    "HCl_0.1M": {"name":"HCl (0.1 M)","ph":1.0,"type":"strong-acid","description":"Güçlü asit (örnek)"},
    "HCl_0.01M":{"name":"HCl (0.01 M)","ph":2.0,"type":"strong-acid","description":"Zayıflatılmış HCl"},
    "NaOH_0.1M":{"name":"NaOH (0.1 M)","ph":13.0,"type":"strong-base","description":"Güçlü baz (örnek)"},
    "NaOH_0.01M":{"name":"NaOH (0.01 M)","ph":12.0,"type":"strong-base","description":"Zayıflatılmış NaOH"},
    "vinegar":{"name":"Sirke (~pH 2.9)","ph":2.9,"type":"weak-acid","description":"Sirke, zayıf asit"},
    "lemon_juice":{"name":"Limon suyu","ph":2.3,"type":"weak-acid","description":"Limon suyu"},
    "distilled_water":{"name":"Saf su","ph":7.0,"type":"neutral","description":"Nötr su"},
    "soap_solution":{"name":"Sabun çözeltisi","ph":9.5,"type":"base","description":"Hafif bazik"}
}

HTML = r'''
<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Sanal Asit–Baz Laboratuvarı — Efekt & Grafik</title>
<style>
/* temel stil (kısaltılmış, temiz) */
body{font-family:Inter, "Segoe UI", Arial;margin:0;background:#f4f7fb;color:#123;padding:16px}
.container{max-width:1200px;margin:0 auto}
.header{display:flex;justify-content:space-between;align-items:center}
h1{margin:0;font-size:1.5rem}
.row{display:flex;gap:12px;align-items:flex-start}
.sidebar{width:320px;background:white;padding:12px;border-radius:10px;box-shadow:0 8px 28px rgba(12,24,60,0.06)}
.main{flex:1;background:white;padding:12px;border-radius:10px;box-shadow:0 8px 28px rgba(12,24,60,0.04)}
.reagent{border:1px solid #eef4fb;padding:8px;margin-bottom:8px;border-radius:8px;cursor:grab;display:flex;justify-content:space-between;align-items:center}
.btn{background:#2563eb;color:white;padding:8px 10px;border-radius:8px;border:none;cursor:pointer}
.beaker-area{display:flex;gap:12px;flex-wrap:wrap}
.beaker{width:260px;min-height:200px;border-radius:8px;border:2px dashed #cdd7e6;padding:8px;position:relative;background:linear-gradient(180deg,#fff,#f7fbff)}
.slot{height:100px;overflow:auto;border-radius:6px;border:1px solid #f1f5f9;padding:6px;background:#fff}
.item{padding:6px;margin-bottom:6px;border-radius:6px;background:#f8fafc;display:flex;justify-content:space-between}
.log{max-height:120px;overflow:auto;background:#0f172433;padding:8px;border-radius:6px;margin-top:8px;font-size:0.9rem}
.right-panel{width:380px}
.readout{padding:10px;border-radius:8px;background:linear-gradient(90deg,#f7fbff,#ffffff);border:1px solid #eef6ff}
.scale{height:18px;background:linear-gradient(90deg,#e74c3c 0%, #f1c40f 50%, #2ecc71 100%);border-radius:9px;position:relative;margin-top:6px}
.marker{position:absolute;top:-6px;width:12px;height:30px;background:#111;border-radius:6px;transform:translateX(-50%);transition:left 600ms}
.effects{position:absolute;left:6px;bottom:6px;right:6px;height:60px;pointer-events:none}
.tube-wrap{width:160px;padding:8px;border-radius:8px;border:2px solid #e6eef8;background:linear-gradient(180deg,#fff,#f7fbff);position:relative}
.tube{width:56px;height:220px;margin:0 auto;background:linear-gradient(180deg,#dceffd,#bfe0ff);border-radius:28px 28px 10px 10px;position:relative;overflow:hidden;display:flex;align-items:flex-end;justify-content:center}
.tube-liquid{width:100%;height:10%;position:absolute;bottom:0;transition:height 600ms, background 600ms}
.tube-neck{width:24px;height:24px;border-radius:20px;background:#fff;margin:8px auto 0}
.explosion{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:40px;height:40px;border-radius:50%;background:radial-gradient(circle at 30% 30%, #fff 0%, #fff3 10%, rgba(255,200,0,0.6) 20%, rgba(255,80,0,0.2) 40%, transparent 70%);animation:explode 700ms ease-out forwards;pointer-events:none;z-index:30}
@keyframes explode{0%{transform:translate(-50%,-50%) scale(0.4);opacity:1}60%{transform:translate(-50%,-50%) scale(2.6);opacity:0.85}100%{transform:translate(-50%,-50%) scale(4.5);opacity:0}}
.puff{position:absolute;border-radius:50%;background:rgba(255,255,255,0.85);width:24px;height:12px;bottom:30%;left:50%;transform:translateX(-50%);animation:puff 1800ms forwards;opacity:0.9}
@keyframes puff{0%{transform:translate(-50%,0) scale(0.6);opacity:0.9}50%{transform:translate(-50%,-40px) scale(1.4);opacity:0.6}100%{transform:translate(-50%,-80px) scale(2.2);opacity:0}}
.particle{position:absolute;width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,0.95);pointer-events:none;animation:rise 1200ms linear forwards}
@keyframes rise{from{transform:translateY(0);opacity:1}to{transform:translateY(-120px);opacity:0}}
.tube-flash{position:absolute;inset:0;background:rgba(255,255,255,0.6);animation:flash 300ms ease-out;pointer-events:none}
@keyframes flash{0%{opacity:1}100%{opacity:0}}
/* glass shard */
.shard{position:absolute;background:linear-gradient(180deg,rgba(255,255,255,0.9),rgba(220,230,255,0.9));width:8px;height:20px;border-radius:2px;opacity:0.95;transform-origin:center}
@keyframes shardFly{to{transform:translate(var(--dx), var(--dy)) rotate(360deg); opacity:0}}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div><h1>Sanal Asit–Baz Laboratuvarı — Efekt & Reaksiyon Grafiği</h1><div style="font-size:0.9rem;color:#556">Patlama & kırılma efektleri tamamen sanal.</div></div>
    <div><button class="btn" onclick="resetAll()">Yeni Deney</button></div>
  </div>

  <div style="height:12px"></div>

  <div class="row">
    <div class="sidebar">
      <h3>Reaktifler</h3>
      <div id="reagentList"></div>
      <div style="height:10px"></div>
      <div class="small">Sürükle ve test tüpüne / beherlere bırakın. Tüp için küçük hacim (20 mL) önerilir.</div>
      <div style="height:8px"></div>
      <div class="log" id="safetyLog">Simülasyon eğitim amaçlıdır.</div>
    </div>

    <div class="main">
      <div style="display:flex;gap:12px">
        <div style="flex:1">
          <h3>Beherler & Test Tüpü</h3>
          <div class="beaker-area" id="beakerArea"></div>

          <div style="margin-top:12px; display:flex; gap:8px;">
            <button class="btn" onclick="mixAll()">Karıştır (Beherler)</button>
            <button class="btn" onclick="mixTestTube()">Karıştır (Test Tüpü)</button>
            <button class="btn" onclick="clearTestTube()">Tüpü Boşalt</button>
          </div>

          <div style="margin-top:12px;display:flex;gap:12px;align-items:flex-start">
            <div class="tube-wrap" ondragover="event.preventDefault()" ondrop="handleDropTube(event)">
              <div class="tube" id="testTube">
                <div class="tube-liquid" id="tubeLiquid" style="height:10%;background:linear-gradient(180deg,#ffd6d6,#ff6b6b)"></div>
              </div>
              <div class="tube-neck"></div>
              <div style="text-align:center;margin-top:6px;font-size:0.9rem">Test Tüpü</div>
            </div>

            <div style="flex:1">
              <div class="small">Tüp içeriği:</div>
              <div id="tubeContents" style="min-height:80px;border-radius:6px;border:1px solid #eef4fb;padding:6px;background:#fff"></div>
              <div style="margin-top:6px" class="small">Küçük hacimde tepkimeler daha dramatik görünebilir.</div>
            </div>
          </div>

        </div>

        <div class="right-panel">
          <div class="readout">
            <div><strong>Seçili:</strong> <span id="selName">—</span></div>
            <div class="small" style="margin-top:6px">Toplam Hacim (tüp): <span id="tubeVol">0</span> mL</div>
            <div class="small">Tahmini pH (tüp): <strong id="tubePh">—</strong></div>

            <div style="margin-top:8px">Asidik ↔ Bazik</div>
            <div class="scale" id="phScale"><div class="marker" id="phMarker" style="left:50%"></div></div>

            <div style="margin-top:8px">Efektler:</div>
            <div style="position:relative;height:120px;border-radius:6px;background:#f7fbff;margin-top:6px;overflow:hidden">
              <div id="tubeEffects" class="effects"></div>
            </div>

            <div style="margin-top:8px;display:flex;gap:8px">
              <button class="btn" onclick="measureTubePH()">pH Ölç</button>
              <button class="btn" onclick="pourToTubeFromBeaker()">Beherden Tüp</button>
            </div>
          </div>

          <div style="margin-top:12px">
            <h4>Reaksiyon Grafiği (zaman — pH)</h4>
            <canvas id="phChart" width="360" height="220"></canvas>
          </div>

          <div style="margin-top:12px">
            <h4>Etkinlik Akışı</h4>
            <div id="eventLog" class="log"></div>
          </div>
        </div>
      </div>

      <div style="margin-top:12px">
        <h4>Kayıt</h4>
        <div id="saved" class="log"></div>
      </div>

    </div>
  </div>
</div>

<!-- Chart.js CDN -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
/* --- App state --- */
let REAGENTS = {};
let beakers = [];
let tube = {contents: []};
let beakerCount = 0;

/* --- Audio (WebAudio) --- */
const AudioCtx = window.AudioContext || window.webkitAudioContext;
const audioCtx = AudioCtx ? new AudioCtx() : null;
function playExplosionSound(){
  if(!audioCtx) return;
  const o = audioCtx.createOscillator();
  const g = audioCtx.createGain();
  o.type = 'sawtooth';
  o.frequency.setValueAtTime(150, audioCtx.currentTime);
  o.frequency.exponentialRampToValueAtTime(60, audioCtx.currentTime + 0.6);
  g.gain.setValueAtTime(0.0001, audioCtx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.7, audioCtx.currentTime + 0.02);
  g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.9);
  o.connect(g); g.connect(audioCtx.destination);
  o.start();
  setTimeout(()=>{ try{o.stop()}catch(e){} }, 950);
}
function playPuffSound(){
  if(!audioCtx) return;
  const o = audioCtx.createOscillator();
  const g = audioCtx.createGain();
  o.type='triangle';
  o.frequency.setValueAtTime(600, audioCtx.currentTime);
  o.frequency.exponentialRampToValueAtTime(200, audioCtx.currentTime + 0.3);
  g.gain.setValueAtTime(0.0001, audioCtx.currentTime);
  g.gain.linearRampToValueAtTime(0.2, audioCtx.currentTime + 0.02);
  g.gain.linearRampToValueAtTime(0.0001, audioCtx.currentTime + 0.6);
  o.connect(g); g.connect(audioCtx.destination);
  o.start();
  setTimeout(()=>{ try{o.stop()}catch(e){} }, 700);
}

/* --- Utilities --- */
function logEvent(msg){
  const el = document.getElementById('eventLog');
  el.innerHTML = `<div>${new Date().toLocaleTimeString()} — ${msg}</div>` + el.innerHTML;
}

/* --- Load reagents & UI init --- */
async function loadReagents(){
  const r = await fetch('/reagents'); REAGENTS = await r.json();
  renderReagentList();
  createBeaker(); createBeaker();
}
function renderReagentList(){
  const cont = document.getElementById('reagentList'); cont.innerHTML='';
  Object.keys(REAGENTS).forEach(key=>{
    const r = REAGENTS[key];
    const d = document.createElement('div'); d.className='reagent'; d.draggable=true;
    d.ondragstart = (e)=> e.dataTransfer.setData('text/plain', key);
    d.innerHTML = `<div><strong>${r.name}</strong><div style="font-size:0.9rem;color:#556">${r.type} • pH ${r.ph}</div></div>
                   <div><button class="btn" onclick="alert(r.description || '')">Detay</button></div>`;
    cont.appendChild(d);
  });
}

/* --- Beaker handling (lightweight) --- */
function createBeaker(){ beakerCount++; beakers.push({id:'B'+beakerCount,name:'Beher '+beakerCount,contents:[]}); renderBeakers(); }
function renderBeakers(){
  const area = document.getElementById('beakerArea'); area.innerHTML='';
  beakers.forEach(b=>{
    const div = document.createElement('div'); div.className='beaker';
    div.ondragover = e=>e.preventDefault();
    div.ondrop = e=>{ e.preventDefault(); const key = e.dataTransfer.getData('text/plain'); addToBeaker(b.id, key, 50); };
    div.innerHTML = `<h4>${b.name}</h4>
      <div class="slot" id="slot_${b.id}">${b.contents.map((c,idx)=>`<div class="item">${REAGENTS[c.key].name} — ${c.vol} mL <button onclick="removeFromBeaker('${b.id}',${idx})">Sil</button></div>`).join('')}</div>
      <div style="margin-top:8px;display:flex;gap:6px"><button class="btn" onclick="selectBeaker('${b.id}')">Seç</button><button class="btn" onclick="pourToTube('${b.id}')">→ Tüpe Dök</button></div>
      <div class="effects" id="effects_${b.id}"></div>`;
    area.appendChild(div);
  });
}
function addToBeaker(id,key,vol){ const b=beakers.find(x=>x.id===id); if(!b) return; b.contents.push({key:key,vol:vol}); renderBeakers(); logEvent(`${REAGENTS[key].name} eklendi: ${vol} mL → ${id}`); }
function removeFromBeaker(id,idx){ const b=beakers.find(x=>x.id===id); if(!b) return; const r=b.contents.splice(idx,1)[0]; renderBeakers(); logEvent(`${REAGENTS[r.key].name} çıkarıldı`); }
function selectBeaker(id){ document.getElementById('selName').innerText = id; updateTubeReadout(); }
function pourToTube(fromBeakerId){ const b = beakers.find(x=>x.id===fromBeakerId); if(!b || b.contents.length===0) return alert('Beher boş'); const c=b.contents.pop(); tube.contents.push({key:c.key,vol:Math.min(c.vol,20)}); logEvent(`${REAGENTS[c.key].name} tüpe döküldü (${Math.min(c.vol,20)} mL)`); renderBeakers(); renderTubeContents(); updateTubeReadout(); }
function pourToTubeFromBeaker(){ if(beakers.length===0) return alert('Beher yok'); pourToTube(beakers[0].id); }

/* --- Tube handling --- */
function handleDropTube(e){ e.preventDefault(); const key=e.dataTransfer.getData('text/plain'); tube.contents.push({key:key,vol:20}); renderTubeContents(); updateTubeReadout(); logEvent(`${REAGENTS[key].name} tüpe eklendi (20 mL)`); }
function renderTubeContents(){ const el=document.getElementById('tubeContents'); el.innerHTML = tube.contents.map((c,i)=>`<div style="padding:6px;border-radius:6px;background:#f8fafc;margin-bottom:6px">${REAGENTS[c.key].name} — ${c.vol} mL <button onclick="removeFromTube(${i})">Sil</button></div>`).join(''); }
function removeFromTube(idx){ if(idx<0||idx>=tube.contents.length) return; const r=tube.contents.splice(idx,1)[0]; renderTubeContents(); updateTubeReadout(); logEvent(`${REAGENTS[r.key].name} tüpten çıkarıldı`); }
function clearTestTube(){ tube.contents=[]; renderTubeContents(); updateTubeReadout(); document.getElementById('tubeEffects').innerHTML=''; logEvent('Tüp temizlendi'); }

/* --- Chemistry approx --- */
function computePHforContents(contents){
  let totalVolL=0, totalHmol=0, totalOHmol=0;
  contents.forEach(c=>{
    const r = REAGENTS[c.key]; const volL = c.vol/1000; totalVolL += volL;
    const Hconc = Math.pow(10, -Number(r.ph));
    const OHc = 1e-14 / Math.max(Hconc, 1e-30);
    totalHmol += Hconc * volL; totalOHmol += OHc * volL;
  });
  if(totalVolL <= 0) return {ph:7.0, severity:0, netH:0, totalVol:0};
  const netH = totalHmol - totalOHmol;
  let finalPH=7.0;
  if(netH>0) finalPH = -Math.log10(netH/totalVolL);
  else if(netH<0){ const pOH = -Math.log10((-netH)/totalVolL); finalPH = 14 - pOH; }
  if(!isFinite(finalPH)) finalPH = netH>0?0:14;
  finalPH = Math.max(0, Math.min(14, Number(finalPH.toFixed(2))));
  const density = Math.abs(netH) / Math.max(totalVolL, 1e-6);
  const hasStrongAcid = contents.some(c=> REAGENTS[c.key].type.includes('strong-acid'));
  const hasStrongBase = contents.some(c=> REAGENTS[c.key].type.includes('strong-base'));
  let severity = density * 1000;
  if(hasStrongAcid && hasStrongBase) severity *= 3;
  if(severity > 100) severity = 100;
  return {ph: finalPH, severity: severity, netH: netH, totalVol: Math.round(totalVolL*1000)};
}

/* --- Effects & explosion with sound & glass shards --- */
function mixTestTube(){
  if(tube.contents.length===0) return alert('Tüp boş');
  const res = computePHforContents(tube.contents);
  const effArea = document.getElementById('tubeEffects'); effArea.innerHTML = '';
  updateTubeReadout();
  // start time-series sim
  startPHTimeSeries(res.ph);
  if(res.severity > 45){
    // explosion: sound + shards + clearing
    createExplosion(effArea);
    playExplosionSound();
    setTimeout(()=>{ tube.contents=[]; renderTubeContents(); updateTubeReadout(); logEvent('Büyük patlama! Tüp boşaldı. (sanal)'); }, 700);
  } else if(res.severity > 18){
    createBubbles(effArea, Math.min(20, Math.round(res.severity/2)));
    createPuff(effArea, 2);
    playPuffSound();
    logEvent('Şiddetli reaksiyon: kabarcıklar ve yoğun sis.');
  } else if(res.severity > 6){
    createBubbles(effArea, Math.min(12, Math.round(res.severity/1.5)));
    flashTube();
    playPuffSound();
    logEvent('Orta şiddette reaksiyon.');
  } else {
    createBubbles(effArea, 4);
    logEvent('Hafif reaksiyon.');
  }
}

function createExplosion(parent){
  const ex = document.createElement('div'); ex.className='explosion'; parent.appendChild(ex);
  // glass shards
  const tubeEl = document.getElementById('testTube');
  for(let i=0;i<12;i++){
    const s = document.createElement('div'); s.className='shard';
    const angle = (Math.random()*360);
    const dx = (Math.cos(angle) * (60 + Math.random()*140)) + 'px';
    const dy = (-(50 + Math.random()*180)) + 'px';
    s.style.left = (45 + Math.random()*10) + '%';
    s.style.bottom = (10 + Math.random()*20) + '%';
    s.style.width = (6 + Math.random()*8) + 'px';
    s.style.height = (12 + Math.random()*30) + 'px';
    s.style.transform = `rotate(${Math.random()*45}deg)`;
    s.style.setProperty('--dx', dx);
    s.style.setProperty('--dy', dy);
    s.style.animation = `shardFly 1000ms forwards`;
    s.style.transition = 'transform 1s, opacity 1s';
    parent.appendChild(s);
    // animate using JS for random translation
    setTimeout(()=>{ s.style.transform = `translate(${dx}, ${dy}) rotate(${Math.random()*720}deg)`; s.style.opacity=0; }, 20);
    setTimeout(()=>s.remove(), 1400);
  }
  setTimeout(()=>ex.remove(), 900);
  const flash = document.createElement('div'); flash.className='tube-flash'; tubeEl.appendChild(flash);
  setTimeout(()=>flash.remove(), 350);
}

function createPuff(parent, count){
  for(let i=0;i<count;i++){
    const puff = document.createElement('div'); puff.className='puff';
    puff.style.left = 30 + Math.random()*40 + '%';
    parent.appendChild(puff);
    setTimeout(()=>puff.remove(), 2200 + Math.random()*800);
  }
}

function createBubbles(parent, n){
  for(let i=0;i<n;i++){
    const b = document.createElement('div'); b.className='particle';
    b.style.left = (30 + Math.random()*40) + '%';
    b.style.bottom = (10 + Math.random()*30) + '%';
    b.style.width = (6 + Math.random()*8) + 'px';
    b.style.height = b.style.width;
    b.style.background = 'rgba(255,255,255,0.95)';
    parent.appendChild(b);
    b.animate([{transform:'translateY(0)', opacity:1},{transform:'translateY(-120px)', opacity:0}], {duration:1000+Math.random()*800});
    setTimeout(()=>b.remove(), 1500);
  }
}

function flashTube(){ const t=document.getElementById('testTube'); const f=document.createElement('div'); f.className='tube-flash'; t.appendChild(f); setTimeout(()=>f.remove(),350); }

/* --- Readout updates + color mapping --- */
function updateTubeReadout(){
  const res = computePHforContents(tube.contents);
  document.getElementById('tubeVol').innerText = res.totalVol;
  document.getElementById('tubePh').innerText = res.ph;
  const percent = Math.max(0,Math.min(100,(res.ph/14)*100));
  document.getElementById('phMarker').style.left = percent + '%';
  const color = phToColor(res.ph);
  const liquid = document.getElementById('tubeLiquid');
  const height = Math.min(90, Math.max(6, 10 + res.totalVol*0.4));
  liquid.style.height = height + '%';
  liquid.style.background = `linear-gradient(180deg, ${color.brighter}, ${color.base})`;
}

/* pH -> color */
function phToColor(pH){
  pH = Math.max(0, Math.min(14, pH));
  if(pH <= 3) return {base:'#ff6b6b', brighter:'#ffb3b3'};
  if(pH <= 6) return {base:'#ffb84d', brighter:'#ffe6b3'};
  if(pH <= 8) return {base:'#8fe39a', brighter:'#d6f6df'};
  if(pH <= 11) return {base:'#7fb3ff', brighter:'#dbe9ff'};
  return {base:'#9aa8ff', brighter:'#e1e7ff'};
}

/* --- pH time-series graph (Chart.js) --- */
let phChart = null;
let phSeriesTimer = null;
let phSeriesData = [];
function initChart(){
  const ctx = document.getElementById('phChart').getContext('2d');
  phChart = new Chart(ctx, {
    type: 'line',
    data: { labels: [], datasets: [{ label: 'pH', data: [], borderWidth: 2, tension:0.3, borderColor:'#2563eb', backgroundColor:'rgba(37,99,235,0.12)', pointRadius:2 }]},
    options: { animation:false, scales:{ y:{ min:0, max:14 } }, plugins:{ legend:{ display:false } } }
  });
}
function startPHTimeSeries(startPH){
  // stop existing
  if(phSeriesTimer) clearInterval(phSeriesTimer);
  phSeriesData = [];
  phChart.data.labels = [];
  phChart.data.datasets[0].data = [];
  phChart.update();
  let t = 0;
  let currentPH = startPH;
  phSeriesTimer = setInterval(()=>{
    // simulate small drift towards neutral over time (simple model)
    const drift = (7 - currentPH) * 0.02; // tends to neutral slowly
    // apply small random jitter
    const jitter = (Math.random()-0.5)*0.05;
    currentPH = currentPH + drift + jitter;
    currentPH = Math.max(0, Math.min(14, currentPH));
    phSeriesData.push(currentPH);
    phChart.data.labels.push(t.toString());
    phChart.data.datasets[0].data.push(currentPH);
    phChart.update();
    t += 1;
    if(t > 60) { clearInterval(phSeriesTimer); phSeriesTimer = null; }
  }, 300);
}

/* --- measurement & misc --- */
function measureTubePH(){ const res = computePHforContents(tube.contents); const measured = Number((res.ph + (Math.random()-0.5)*0.05).toFixed(2)); logEvent('Tüp pH ölçümü: ' + measured); updateTubeReadout(); startPHTimeSeries(measured); return measured; }
function mixAll(){ beakers.forEach(b=>{ if(b.contents.length===0) return; logEvent(`${b.name} karıştırıldı.`); const eff = document.getElementById('effects_' + b.id); if(eff){ for(let i=0;i<6;i++){ const p=document.createElement('div'); p.className='particle'; p.style.left=(10+Math.random()*80)+'%'; p.style.bottom=(6+Math.random()*20)+'%'; eff.appendChild(p); p.animate([{transform:'translateY(0)',opacity:1},{transform:'translateY(-80px)',opacity:0}],{duration:900+Math.random()*500}); setTimeout(()=>p.remove(),1400); } } }); }

/* --- init & start --- */
loadReagents();
createBeaker(); createBeaker();
initChart();

function resetAll(){ beakers=[]; beakerCount=0; tube.contents=[]; document.getElementById('eventLog').innerHTML=''; createBeaker(); createBeaker(); renderTubeContents(); renderBeakers(); updateTubeReadout(); if(phSeriesTimer) clearInterval(phSeriesTimer); phSeriesData=[]; phChart.data.labels=[]; phChart.data.datasets[0].data=[]; phChart.update(); logEvent('Yeni deney başlatıldı.'); }
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/reagents')
def reagents():
    try:
        return jsonify(REAGENTS)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Sanal Asit–Baz Laboratuvarı (efekt & grafik) başlatılıyor — http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

