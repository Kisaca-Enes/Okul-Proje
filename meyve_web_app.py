# app.py
from flask import Flask, render_template_string, request, jsonify
import numpy as np
from PIL import Image
import requests
from io import BytesIO
import traceback

app = Flask(__name__)

# -------------------- RGB -> HSV (NumPy-safe) --------------------

def rgb_to_hsv_safe(rgb):
    """RGB [0..1] -> HSV array (h,s,v) with h in [0,1]."""
    rgb = np.clip(rgb, 0.0, 1.0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    maxc = np.max(rgb, axis=-1)
    minc = np.min(rgb, axis=-1)
    diff = maxc - minc

    h = np.zeros_like(maxc)
    s = np.zeros_like(maxc)
    v = maxc

    nonzero = maxc > 1e-10
    s[nonzero] = diff[nonzero] / maxc[nonzero]

    mask = diff > 1e-10
    idx = mask & (maxc == r)
    h[idx] = (g[idx] - b[idx]) / diff[idx]
    idx = mask & (maxc == g)
    h[idx] = 2.0 + (b[idx] - r[idx]) / diff[idx]
    idx = mask & (maxc == b)
    h[idx] = 4.0 + (r[idx] - g[idx]) / diff[idx]

    h = (h / 6.0) % 1.0
    hsv = np.stack([h, s, v], axis=-1)
    return hsv

# -------------------- color feature + similarity --------------------

def color_feature(img):
    """
    img: HxWx3 floats 0..1
    returns concatenated normalized histograms for H,S,V
    """
    hsv = rgb_to_hsv_safe(img)
    h_hist, _ = np.histogram(hsv[..., 0].ravel(), bins=32, range=(0, 1), density=True)
    s_hist, _ = np.histogram(hsv[..., 1].ravel(), bins=32, range=(0, 1), density=True)
    v_hist, _ = np.histogram(hsv[..., 2].ravel(), bins=32, range=(0, 1), density=True)
    feat = np.concatenate([h_hist, s_hist, v_hist]).astype(np.float32)
    norm = np.linalg.norm(feat) + 1e-9
    return feat / norm

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))

# -------------------- REFERENCE DB (images + meta) --------------------

REFERENCE_DB = {
    "elma": {
        "ph": 3.6,
        "ph_range": (3.3, 4.0),
        "asit": "orta-yüksek",
        "baz": "düşük",
        "protein": "0.3 g / 100g",
        "karbonhidrat": "13.8 g / 100g",
        "yag": "0.2 g / 100g",
        "kalori": "52 kcal / 100g",
        "vitamin": "C, B6",
        "mineraller": "Potasyum",
        "lif": "2.4 g / 100g",
        "su": "%85",
        "aciklama": "Elma, lif açısından zengindir.",
        "kullanim": "Taze, reçel, salata",
        "saglik": "Kolesterolü düşürebilir, antioksidan içerir.",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/1/15/Red_Apple.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/7/7d/Green_Apple.jpg"
        ]
    },
    "muz": {
        "ph": 4.9,
        "ph_range": (4.5, 5.2),
        "asit": "düşük-orta",
        "baz": "orta",
        "protein": "1.1 g / 100g",
        "karbonhidrat": "22.8 g / 100g",
        "yag": "0.3 g / 100g",
        "kalori": "89 kcal / 100g",
        "vitamin": "B6, C",
        "mineraller": "Potasyum",
        "lif": "2.6 g / 100g",
        "su": "%75",
        "aciklama": "Muz enerji verici bir meyvedir.",
        "kullanim": "Taze, smoothie, kek",
        "saglik": "Potasyum deposudur; kas fonksiyonlarını destekler.",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/8/8a/Banana-Single.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/4/44/Bananas_white_background.jpg"
        ]
    },
    "limon": {
        "ph": 2.3,
        "ph_range": (2.0, 2.6),
        "asit": "çok yüksek",
        "baz": "çok düşük",
        "protein": "1.1 g / 100g",
        "karbonhidrat": "9.3 g / 100g",
        "yag": "0.3 g / 100g",
        "kalori": "29 kcal / 100g",
        "vitamin": "C",
        "mineraller": "Potasyum",
        "lif": "2.8 g / 100g",
        "su": "%89",
        "aciklama": "Limon güçlü sitrik asit kaynağıdır.",
        "kullanim": "Limonata, sos",
        "saglik": "Sindirime yardımcı olabilir.",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/c/c4/Lemon.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/3/36/Lemon_and_cross_section.jpg"
        ]
    },
    "salatalik": {
        "ph": 5.5,
        "ph_range": (5.1, 5.9),
        "asit": "düşük",
        "baz": "düşük-orta",
        "protein": "0.7 g / 100g",
        "karbonhidrat": "3.6 g / 100g",
        "yag": "0.1 g / 100g",
        "kalori": "15 kcal / 100g",
        "vitamin": "K, C",
        "mineraller": "Potasyum",
        "lif": "0.5 g / 100g",
        "su": "%96",
        "aciklama": "Salatalık yüksek su içerir.",
        "kullanim": "Salata, turşu",
        "saglik": "Cildi yatıştırır.",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/9/96/Cucumis_sativus.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/1/12/Cucumber.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/b/bd/Cucumber_on_white.jpg"
        ]
    },
    "domates": {
        "ph": 4.6,
        "ph_range": (4.3, 4.9),
        "asit": "orta",
        "baz": "düşük",
        "protein": "0.9 g / 100g",
        "karbonhidrat": "3.9 g / 100g",
        "yag": "0.2 g / 100g",
        "kalori": "18 kcal / 100g",
        "vitamin": "C, A, K",
        "mineraller": "Potasyum",
        "lif": "1.2 g / 100g",
        "su": "%95",
        "aciklama": "Domates likopen bakımından zengindir.",
        "kullanim": "Salata, sos",
        "saglik": "Likopen bazı kanser risklerini azaltabilir.",
        "images": [
            "https://upload.wikimedia.org/wikipedia/commons/8/89/Tomato_je.jpg",
            "https://upload.wikimedia.org/wikipedia/commons/6/6f/Tomato.png"
        ]
    }
}

# -------------------- feature cache --------------------
FEATURE_CACHE = {}
FEATURE_URLS_AVAILABLE = {}

def load_image_from_url_safe(url):
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert("RGB")
        img.thumbnail((300, 300))
        arr = np.array(img, dtype=np.float32) / 255.0
        return arr
    except Exception as e:
        print(f"[WARN] couldn't fetch {url}: {e}")
        return None

def ensure_reference_features():
    if FEATURE_CACHE:
        return
    for label, meta in REFERENCE_DB.items():
        feats = []
        ok_urls = []
        for url in meta.get("images", []):
            img = load_image_from_url_safe(url)
            if img is None:
                continue
            try:
                feats.append(color_feature(img))
                ok_urls.append(url)
            except Exception as e:
                print(f"[WARN] feature extraction failed for {url}: {e}")
        if len(feats) > 0:
            FEATURE_CACHE[label] = np.mean(feats, axis=0)
            FEATURE_URLS_AVAILABLE[label] = ok_urls
            print(f"[INFO] prepared features for {label} ({len(ok_urls)} images)")
        else:
            FEATURE_CACHE[label] = None
            FEATURE_URLS_AVAILABLE[label] = []
            print(f"[WARN] no reference images for {label}, will use hue fallback")

# -------------------- analysis helpers --------------------

def hue_rule_label(img):
    hsv = rgb_to_hsv_safe(img)
    h = float(np.mean(hsv[...,0]))
    s = float(np.mean(hsv[...,1]))
    v = float(np.mean(hsv[...,2]))
    if 0.13 < h < 0.20:
        return "muz" if s > 0.5 else "limon"
    elif 0.25 < h < 0.40:
        return "salatalik"
    elif h < 0.08 or h > 0.92:
        return "domates" if s > 0.4 else "elma"
    else:
        return "elma"

def estimate_ripeness_from_img(img):
    hsv = rgb_to_hsv_safe(img)
    s_mean = float(np.mean(hsv[...,1]))
    v_mean = float(np.mean(hsv[...,2]))
    if s_mean > 0.6 and v_mean > 0.65:
        return "olgun"
    elif s_mean > 0.45 and v_mean > 0.5:
        return "orta"
    else:
        return "ham"

def analyze_image(img, aggressiveness=1.0):
    ensure_reference_features()

    input_feat = color_feature(img)
    similarities = []
    for label, ref_feat in FEATURE_CACHE.items():
        if ref_feat is None:
            similarities.append((label, None))
            continue
        raw = cosine_similarity(input_feat, ref_feat)
        # aggressiveness: raise similarity to this power (aggr>1 => more peaky)
        # clamp
        adj = float(np.clip(raw, 0.0, 1.0) ** float(max(0.01, aggressiveness)))
        similarities.append((label, adj))

    scored = [(lab, sc) for lab, sc in similarities if sc is not None]
    if len(scored) == 0:
        label = hue_rule_label(img)
        confidence = 40.0
    else:
        scored.sort(key=lambda x: x[1], reverse=True)
        label, best_score = scored[0]
        confidence = float(best_score * 100)
        if best_score < 0.35:
            hue_label = hue_rule_label(img)
            if hue_label == label:
                confidence = max(confidence, 55.0)
            else:
                confidence = max(confidence, 45.0)

    ripeness = estimate_ripeness_from_img(img)
    base_ph = REFERENCE_DB.get(label, {}).get("ph", 6.0)
    if ripeness == "olgun":
        ph_adj = +0.25
    elif ripeness == "orta":
        ph_adj = +0.10
    else:
        ph_adj = -0.10
    final_ph = round(float(base_ph) + ph_adj, 2)

    sim_list = []
    for lab, sc in similarities:
        sim_list.append({
            "label": lab,
            "score": (None if sc is None else round(float(sc), 4)),
            "urls_loaded": FEATURE_URLS_AVAILABLE.get(lab, [])
        })
    sim_list.sort(key=lambda x: (x["score"] is not None, x["score"] if x["score"] is not None else -1), reverse=True)

    info = REFERENCE_DB.get(label, {})
    return {
        "label": label,
        "confidence": round(float(confidence), 1),
        "ripeness": ripeness,
        "ph": final_ph,
        "info": {
            "ph_range": info.get("ph_range"),
            "asit": info.get("asit"),
            "baz": info.get("baz"),
            "protein": info.get("protein"),
            "karbonhidrat": info.get("karbonhidrat"),
            "yag": info.get("yag"),
            "kalori": info.get("kalori"),
            "vitamin": info.get("vitamin"),
            "mineraller": info.get("mineraller"),
            "lif": info.get("lif"),
            "su": info.get("su"),
            "aciklama": info.get("aciklama"),
            "kullanim": info.get("kullanim"),
            "saglik": info.get("saglik")
        },
        "similarities": sim_list
    }

# -------------------- chemistry details endpoint --------------------

@app.route('/chemistry/<label>')
def chemistry_detail(label):
    label = label.lower()
    if label not in REFERENCE_DB:
        return jsonify({'error': 'Bilinmeyen ürün'}), 404
    return jsonify(REFERENCE_DB[label])

# -------------------- HTML (UI) --------------------
# (Arayüzü senin verdiğinle büyük ölçüde birebir tuttum; ek kontroller ekledim)
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>🔬 Meyve & Sebze Analiz Sistemi</title>
<style>
/* temel stil (açık tema) */
:root{
  --bg-grad1: #667eea;
  --bg-grad2: #764ba2;
  --container-bg: #ffffff;
  --muted: #7f8c8d;
  --card-bg: #f8f9fa;
  --text: #2c3e50;
  --accent: #3498db;
}
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg,var(--bg-grad1) 0%,var(--bg-grad2) 100%); min-height:100vh; padding:20px; color:var(--text); }
.container { max-width:1200px; margin:0 auto; background:var(--container-bg); border-radius:20px; box-shadow:0 20px 60px rgba(0,0,0,0.3); overflow:hidden; }
header { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); color:white; padding:30px; text-align:center; }
.main-content { display:grid; grid-template-columns:1fr 1fr; gap:30px; padding:30px; }
.upload-section{ background:var(--card-bg); padding:20px; border-radius:15px; text-align:center;}
.upload-area{ border:3px dashed var(--accent); border-radius:15px; padding:20px; margin:10px 0; cursor:pointer; }
.upload-area:hover{ background:#e8f4f8; }
.upload-area img{ max-width:100%; max-height:300px; border-radius:10px; margin-top:10px; }
.controls { display:flex; gap:10px; justify-content:center; margin-top:10px; align-items:center; flex-wrap:wrap; }
.control { background:white; padding:8px 12px; border-radius:8px; box-shadow:0 2px 6px rgba(0,0,0,0.06); display:flex; gap:8px; align-items:center;}
.btn { background:#27ae60; color:white; border:none; padding:10px 18px; border-radius:10px; cursor:pointer; font-weight:bold; }
.results-section{ background:var(--card-bg); padding:20px; border-radius:15px; }
.result-card{ background:white; padding:16px; border-radius:10px; margin-bottom:12px; box-shadow:0 2px 10px rgba(0,0,0,0.08); }
.highlight{ background:var(--accent); color:white; padding:12px; border-radius:10px; text-align:center; font-size:1.2em; font-weight:bold; margin-bottom:10px;}
.scale { background: linear-gradient(90deg, #f39c12 0%, #f1c40f 50%, #2ecc71 100%); height:24px; border-radius:12px; position:relative; margin-top:12px; }
.marker { position:absolute; top:-6px; width:12px; height:36px; background:#111; border-radius:6px; box-shadow:0 2px 6px rgba(0,0,0,0.4); transform:translateX(-50%); transition:left 0.5s ease; }
.modal { position:fixed; inset:0; display:none; align-items:center; justify-content:center; background:rgba(0,0,0,0.5); z-index:2000; }
.modal .box { background:white; padding:20px; border-radius:10px; width:90%; max-width:800px; max-height:80vh; overflow:auto; }
.modal.show{ display:flex; }
.result-grid { display:grid; grid-template-columns:1fr 1fr; gap:10px; }
.sim-row { display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px solid #eee; }
.footer { background:#34495e; color:white; text-align:center; padding:12px; }

/* DARK THEME */
body.dark {
  --bg-grad1: #2c3e50;
  --bg-grad2: #1e293b;
  --container-bg: #0f1724;
  --muted: #94a3b8;
  --card-bg: #0b1220;
  --text: #e6eef8;
  --accent: #60a5fa;
}
body.dark header { background: linear-gradient(135deg,#2563eb 0%, #1e40af 100%); }
body.dark .result-card { background:#071025; color:var(--text); }
body.dark .modal .box { background:#071025; color:var(--text); }

/* responsive */
@media (max-width:768px){ .main-content{ grid-template-columns:1fr; } .result-grid{ grid-template-columns:1fr; } }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🔬 AKILLI MEYVE & SEBZE ANALİZ SİSTEMİ</h1>
    <p>Yapay Zeka Destekli Görüntü Analizi ve Besin Değeri Hesaplama</p>
  </header>

  <div class="main-content">
    <div class="upload-section">
      <h2>📸 GÖRÜNTÜ YÜKLEYİN</h2>
      <div class="upload-area" onclick="document.getElementById('fileInput').click()">
        <div id="uploadText">
          <h3>🖼️</h3>
          <p>Tıklayın veya sürükleyin</p>
          <p style="font-size:0.9em;color:var(--muted)">JPG, PNG, JPEG</p>
        </div>
        <img id="preview" style="display:none;" />
      </div>

      <input id="fileInput" type="file" accept="image/*" style="display:none" onchange="uploadImage()" />

      <div class="controls">
        <div class="control">
          <label for="aggr">Benzerlik Agresifliği</label>
          <input id="aggr" type="range" min="0.2" max="3.0" step="0.1" value="1.0" style="width:160px" oninput="document.getElementById('aggrVal').innerText=this.value" />
          <div id="aggrVal">1.0</div>
        </div>

        <div class="control">
          <label for="bgToggle">Tema</label>
          <select id="bgToggle" onchange="toggleTheme(this.value)">
            <option value="light">Açık</option>
            <option value="dark">Koyu</option>
          </select>
        </div>

        <div class="control">
          <button class="btn" onclick="document.getElementById('fileInput').click()">📂 Resim Seç</button>
        </div>
      </div>
    </div>

    <div class="results-section">
      <h2>📊 ANALİZ SONUÇLARI</h2>
      <div id="results" style="text-align:center; padding:50px; color:var(--muted);">
        <h3>🔍</h3>
        <p>Henüz analiz yapılmadı. Lütfen bir görüntü yükleyin.</p>
      </div>
    </div>
  </div>

  <footer class="footer">
    <p>Geliştirici: AI Analiz Sistemi | Bilim Şenliği 2026</p>
  </footer>
</div>

<!-- Chemistry modal -->
<div id="chemModal" class="modal" onclick="if(event.target===this) closeChem()">
  <div class="box">
    <button onclick="closeChem()" style="float:right">Kapat</button>
    <h2 id="chemTitle">Kimya Detayı</h2>
    <div id="chemBody"></div>
  </div>
</div>

<script>
function toggleTheme(val){
  if(val === 'dark') document.body.classList.add('dark');
  else document.body.classList.remove('dark');
}

function uploadImage(){
  const file = document.getElementById('fileInput').files[0];
  if(!file) return;

  const reader = new FileReader();
  reader.onload = function(e){
    const preview = document.getElementById('preview');
    preview.src = e.target.result;
    preview.style.display = 'block';
    document.getElementById('uploadText').style.display = 'none';
  };
  reader.readAsDataURL(file);

  const formData = new FormData();
  formData.append('image', file);
  // attach aggressiveness
  formData.append('aggressiveness', document.getElementById('aggr').value);

  fetch('/analyze', { method:'POST', body: formData })
    .then(r => r.json())
    .then(data => {
      if(data.error) { alert('Hata: '+data.error); return; }
      displayResults(data);
    })
    .catch(err => { alert('Analiz hatası: '+err); console.error(err); });
}

function displayResults(data){
  const resultsDiv = document.getElementById('results');
  const info = data.info;
  // marker position on scale (0-14 pH mapped to 0-100%)
  const posPercent = Math.max(0, Math.min(100, (data.ph / 14.0) * 100));

  resultsDiv.innerHTML = `
    <div class="highlight">🎯 ${data.label.toUpperCase()}</div>

    <div class="result-card">
      <h3>📋 Temel Bilgiler</h3>
      <div class="result-grid">
        <div><strong>Güven Skoru:</strong> %${data.confidence.toFixed(1)}</div>
        <div><strong>Olgunluk:</strong> ${data.ripeness}</div>
        <div><strong>pH (tahmini):</strong> ${data.ph.toFixed(2)}</div>
        <div><button class="btn" onclick="openChem('${data.label}')">🔬 Kimya Detayı</button></div>
      </div>
    </div>

    <div class="result-card">
      <h3>⚗️ Asidik ↔ Bazik Skalası</h3>
      <div style="display:flex;justify-content:space-between;font-weight:bold;margin-bottom:8px;">
        <div>Asidik</div><div>Bazik</div>
      </div>
      <div class="scale" id="phScale">
        <div class="marker" id="phMarker" style="left:${posPercent}%;"></div>
      </div>
      <div style="margin-top:8px;color:var(--muted);">pH konumu (0-14): ${data.ph.toFixed(2)}</div>
    </div>

    <div class="result-card">
      <h3>🍽️ Besin & Kimyasal Bilgiler (özet)</h3>
      <div class="result-item"><span class="label">Asit:</span> <span class="value">${info.asit}</span></div>
      <div class="result-item"><span class="label">Baz:</span> <span class="value">${info.baz}</span></div>
      <div class="result-item"><span class="label">Kalori:</span> <span class="value">${info.kalori}</span></div>
      <div class="result-item"><span class="label">Protein:</span> <span class="value">${info.protein}</span></div>
      <div class="result-item"><span class="label">Karbonhidrat:</span> <span class="value">${info.karbonhidrat}</span></div>
    </div>

    <div class="result-card">
      <h3>🔎 Benzerlik Skorları</h3>
      ${data.similarities.map(s => `
        <div class="sim-row">
          <div style="font-weight:bold">${s.label}</div>
          <div>${s.score === null ? 'bulunamadı' : s.score.toFixed(3)}</div>
        </div>
      `).join('')}
      <div style="margin-top:8px;color:var(--muted);font-size:0.9em;">
        Not: "Benzerlik Agresifliği" kaydırıcısı benzerlik skorlarını güçlendirir/gereksiz eşleşmeleri azaltır.
      </div>
    </div>
  `;
}

function openChem(label){
  fetch(`/chemistry/${label}`)
    .then(r => r.json())
    .then(data => {
      if(data.error){ alert('Hata: '+data.error); return; }
      const body = document.getElementById('chemBody');
      document.getElementById('chemTitle').innerText = `Kimya Detayı — ${label.toUpperCase()}`;
      body.innerHTML = `
        <h3>Temel Özet</h3>
        <p><strong>pH aralığı:</strong> ${data.ph_range ? data.ph_range[0]+' - '+data.ph_range[1] : '—'}</p>
        <p><strong>Asit:</strong> ${data.asit || '—'}</p>
        <p><strong>Baz:</strong> ${data.baz || '—'}</p>

        <h3>Besin Değerleri (100g)</h3>
        <p><strong>Kalori:</strong> ${data.kalori || '—'}</p>
        <p><strong>Protein:</strong> ${data.protein || '—'}</p>
        <p><strong>Karbonhidrat:</strong> ${data.karbonhidrat || '—'}</p>
        <p><strong>Yağ:</strong> ${data.yag || '—'}</p>
        <p><strong>Lif:</strong> ${data.lif || '—'}</p>

        <h3>Vitaminler & Mineraller</h3>
        <p>${data.vitamin || ''}</p>
        <p>${data.mineraller || ''}</p>

        <h3>Açıklama & Kullanım</h3>
        <p>${data.aciklama || ''}</p>
        <p><strong>Kullanım:</strong> ${data.kullanim || ''}</p>

        <h3>Referans Görseller (yüklenenler)</h3>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          ${(data.images || []).map(u=>`<img src="${u}" style="height:80px;border-radius:6px;">`).join('')}
        </div>
      `;
      document.getElementById('chemModal').classList.add('show');
    })
    .catch(err => { alert('Detay alınırken hata: '+err); console.error(err); });
}

function closeChem(){
  document.getElementById('chemModal').classList.remove('show');
}
</script>
</body>
</html>
'''

# -------------------- routes --------------------

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Görüntü bulunamadı'}), 400
        file = request.files['image']
        img = Image.open(file.stream).convert('RGB')
        img.thumbnail((400, 400))
        arr = np.array(img, dtype=np.float32) / 255.0

        aggr_raw = request.form.get('aggressiveness', '1.0')
        try:
            aggressiveness = float(aggr_raw)
            # clamp to reasonable
            if aggressiveness < 0.1: aggressiveness = 0.1
            if aggressiveness > 5.0: aggressiveness = 5.0
        except:
            aggressiveness = 1.0

        result = analyze_image(arr, aggressiveness=aggressiveness)
        return jsonify(result)
    except Exception as e:
        print("[ERROR] analyze:", e)
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/chemistry/<label>')
def chemistry(label):
    label = label.lower()
    if label not in REFERENCE_DB:
        return jsonify({'error': 'Bilinmeyen ürün'}), 404
    # return the full metadata (safe)
    return jsonify(REFERENCE_DB[label])

# -------------------- run --------------------

if __name__ == '__main__':
    print("🔬 Meyve & Sebze Analiz Sistemi başlatılıyor...")
    print("Arayüz: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

