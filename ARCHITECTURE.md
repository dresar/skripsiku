# Arsitektur Sistem - Latex Smart Monitoring

Diagram berikut dapat digunakan untuk Bab 3 Skripsi (Rancang Bangun Sistem).

## Diagram Arsitektur Umum

```mermaid
flowchart TB
    subgraph Device["Layer Perangkat"]
        ESP32["ESP32\n(Sensor pH, TDS, Suhu)\nAlgoritma Thresholding pH"]
    end

    subgraph Transport["Layer Transport"]
        MQTT["MQTT Broker\n(e.g. HiveMQ)"]
    end

    subgraph Backend["Layer Backend"]
        API["FastAPI\nREST API"]
        WS["WebSocket\nRealtime"]
        MQTTClient["MQTT Subscriber"]
        DB[(SQLite\nDatabase)]
    end

    subgraph Frontend["Layer Presentasi"]
        Dashboard["Dashboard Web\n(Jinja2 + Tailwind + Chart.js)"]
    end

    ESP32 -->|"Publish JSON"| MQTT
    MQTT -->|"Subscribe"| MQTTClient
    MQTTClient -->|"Simpan"| DB
    MQTTClient -->|"Broadcast"| WS
    API -->|"Baca/Tulis"| DB
    Dashboard -->|"HTTP / REST"| API
    Dashboard -->|"WS"| WS
```

## Alur Data (Sequence)

```mermaid
sequenceDiagram
    participant ESP32
    participant MQTT
    participant Backend
    participant DB
    participant WS
    participant Dashboard

    ESP32->>MQTT: Publish { ph, tds, suhu, status }
    MQTT->>Backend: Message (topic: latex/monitoring)
    Backend->>Backend: Validasi (Pydantic)
    Backend->>DB: INSERT latex_readings
    Backend->>WS: Broadcast payload
    WS->>Dashboard: Update realtime

    Dashboard->>Backend: GET /api/latest
    Backend->>DB: SELECT terbaru
    Backend->>Dashboard: JSON response

    Dashboard->>Backend: GET /api/history?page=1
    Backend->>DB: SELECT + pagination
    Backend->>Dashboard: JSON list
```

## Struktur Modul Backend

```mermaid
graph LR
    subgraph app
        main["main.py\n(Lifespan, WS, CORS)"]
        config["config.py\n(.env)"]
        database["database.py\n(Session, init_db)"]
        models["models.py\n(LatexReading)"]
        schemas["schemas.py\n(Pydantic)"]
        mqtt["mqtt_client.py\n(Subscribe, Save, Callback)"]
        api["routes/api.py\nREST"]
        views["routes/views.py\nHTML"]
    end

    main --> config
    main --> database
    main --> mqtt
    main --> api
    main --> views
    mqtt --> config
    mqtt --> database
    mqtt --> models
    mqtt --> schemas
    api --> database
    api --> models
    api --> schemas
```

## Tabel Database

| Kolom      | Tipe     | Keterangan        |
|-----------|----------|-------------------|
| id        | INTEGER  | Primary key       |
| ph        | FLOAT    | Nilai pH (0–14)   |
| tds       | FLOAT    | TDS (ppm)         |
| suhu      | FLOAT    | Suhu (°C)         |
| status    | VARCHAR  | Mutu (Prima/Sedang/Buruk) |
| created_at| DATETIME | Waktu pencatatan  |

---

*Dokumen pendukung untuk skripsi: Rancang Bangun Sistem Deteksi Mutu Lateks Portabel Berbasis IoT.*
