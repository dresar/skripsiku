# Latex Smart Monitoring

Sistem Deteksi Mutu Lateks Portabel Berbasis IoT — Backend & Dashboard.

## Arsitektur Sistem

```
                    +------------------+
                    |     ESP32        |
                    |  (Sensor pH,     |
                    |   TDS, Suhu)     |
                    +--------+---------+
                             | Publish JSON
                             v
                    +------------------+
                    |  MQTT Broker     |
                    | (e.g. HiveMQ)    |
                    +--------+---------+
                             | Subscribe
                             v
+------------------+  +------------------+  +------------------+
|  Dashboard Web   |  |  FastAPI         |  |  SQLite          |
|  (Jinja2 +       |<->|  Backend         |<->|  (latex_readings)|
|   Tailwind)      |  |  - REST API      |  +------------------+
+------------------+  |  - WebSocket     |
                      |  - MQTT Client   |
                      +------------------+
```

### Alur Data

1. **ESP32** membaca sensor (pH, TDS, suhu), menghitung status mutu (thresholding), lalu **publish** payload JSON ke topic MQTT.
2. **Backend** subscribe ke topic MQTT, validasi payload (Pydantic), simpan ke **SQLite**, dan **broadcast** ke client WebSocket.
3. **Dashboard** menampilkan data realtime via WebSocket, riwayat dan statistik via REST API.

---

## Struktur Folder

```
project/
├── app/
│   ├── main.py          # Entry point, WebSocket, lifespan
│   ├── config.py        # Baca .env
│   ├── database.py      # SQLAlchemy engine, session
│   ├── models.py        # ORM LatexReading
│   ├── schemas.py       # Pydantic payload & response
│   ├── mqtt_client.py   # MQTT subscribe, simpan DB, callback
│   └── routes/
│       ├── api.py       # GET /api/latest, /api/history, /api/statistics
│       └── views.py     # Halaman dashboard, history, statistics, settings
├── templates/
│   ├── base.html
│   ├── components/
│   │   ├── sidebar.html
│   │   ├── navbar.html
│   │   └── footer.html
│   └── pages/
│       ├── dashboard.html
│       ├── history.html
│       ├── statistics.html
│       ├── settings.html
│       └── about.html
├── static/
│   ├── css/
│   │   └── app.css
│   └── js/
│       ├── dashboard.js
│       ├── history.js
│       └── statistics.js
├── .env                 # Buat dari .env.example
├── .env.example
├── requirements.txt
└── README.md
```

---

## Cara Menjalankan

### 1. Persiapan

```bash
# Di root project
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

pip install -r requirements.txt

# Salin konfigurasi (Windows: copy .env.example .env)
cp .env.example .env   # Linux/Mac
# copy .env.example .env   # Windows CMD
# Edit .env jika perlu (broker, port, topic)
```

### 2. Jalankan Backend

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- Dashboard: http://localhost:8000  
- API docs: http://localhost:8000/docs  
- WebSocket: ws://localhost:8000/ws/realtime  

---

## Testing dengan ESP32

### Payload JSON yang dipublish ESP32

Format yang diharapkan backend (topic dari `.env`, default: `latex/monitoring`):

```json
{
  "ph": 6.85,
  "tds": 520,
  "suhu": 29.5,
  "status": "Mutu Prima"
}
```

- **ph**: 0–14 (float)  
- **tds**: ≥ 0 (float, ppm)  
- **suhu**: -40–85 (°C)  
- **status**: string (contoh: "Mutu Prima", "Mutu Sedang", "Mutu Buruk")

### Testing tanpa ESP32 (MQTT Explorer / mosquitto_pub)

1. Pasang [MQTT Explorer](http://mqtt-explorer.com/) atau gunakan `mosquitto_pub`.
2. Connect ke broker yang sama dengan backend (mis. `broker.hivemq.com:1883`).
3. Publish ke topic **sama** dengan `MQTT_TOPIC` di `.env` (mis. `latex/monitoring`), payload:

```json
{"ph": 6.85, "tds": 520, "suhu": 29.5, "status": "Mutu Prima"}
```

4. Buka dashboard http://localhost:8000 — card dan grafik akan update (realtime via WebSocket).

### Contoh mosquitto_pub

```bash
mosquitto_pub -h broker.hivemq.com -p 1883 -t "latex/monitoring" -m '{"ph": 6.85, "tds": 520, "suhu": 29.5, "status": "Mutu Prima"}'
```

---

## API

| Method | Endpoint | Keterangan |
|--------|----------|------------|
| GET | `/api/latest` | Data terbaru (satu record) |
| GET | `/api/history?page=1&per_page=20&date_from=&date_to=` | Riwayat + pagination + filter tanggal |
| GET | `/api/statistics` | Rata-rata pH/TDS/suhu, total, status counts, status dominan |
| WS | `/ws/realtime` | Realtime stream (broadcast setiap ada data MQTT baru) |

---

## Konfigurasi (.env)

Semua dibaca dari `.env` (lihat `.env.example`):

- **APP_NAME**, **APP_VERSION**, **DEBUG**
- **API_HOST**, **API_PORT**
- **MQTT_BROKER**, **MQTT_PORT**, **MQTT_TOPIC**, **MQTT_CLIENT_ID**, **MQTT_KEEPALIVE**
- **MQTT_USERNAME**, **MQTT_PASSWORD** (opsional)
- **MQTT_USE_TLS**
- **DATABASE_URL** (default: `sqlite:///./monitoring.db`)

---

## Penjelasan untuk Bab 3 Skripsi

- **Arsitektur**: Layered; device (ESP32) → MQTT → backend (FastAPI) → database (SQLite) dan dashboard (templating + REST/WS).
- **Komponen**: (1) ESP32 + sensor + algoritma thresholding pH, (2) MQTT broker, (3) Backend (subscriber MQTT, validasi, penyimpanan, REST & WebSocket), (4) Database, (5) Dashboard modular (Jinja2, Tailwind, Chart.js).
- **Alur data**: One-way dari sensor ke broker, backend subscribe → validasi → simpan → broadcast WebSocket; dashboard konsumsi via REST (history/statistics) dan WebSocket (realtime).
- **Struktur kode**: Pemisahan config, model, schema, route API, route view, dan template; siap dipakai sebagai dasar deployment production (env-based config, logging, modular route).

---

## Lisensi

Skripsi — Rancang Bangun Sistem Deteksi Mutu Lateks Portabel Berbasis IoT.
