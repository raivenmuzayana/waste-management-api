# Waste Management Monitoring System 🚛♻️

**Project 4 - Kapita Selekta Analitika Data**

Sistem backend berbasis Python (FastAPI) untuk memantau volume dan jenis sampah di berbagai lokasi. Sistem ini dirancang untuk memudahkan monitoring, mengidentifikasi lokasi dengan produksi sampah tertinggi, memprediksi volume sampah di masa depan, serta mengoptimalkan rute pengumpulan sampah.

## 📋 Fitur Utama

### 1. Manajemen Data (CRUD)

* **Lokasi (Locations):** Mengelola data titik lokasi pembuangan sampah (Latitude/Longitude).
* **Kategori Sampah (Categories):** Mengelola jenis sampah (Organik, Plastik, Kertas, dll).
* **Catatan Pengumpulan (Collections):** Mencatat volume sampah harian berdasarkan lokasi dan kategori.

### 2. Autentikasi & Otorisasi

* **JWT Authentication:** Keamanan akses menggunakan JSON Web Token.
* **Role-Based Access Control:**

  * **Admin:** Akses penuh (CRUD Data User, Lokasi, Kategori).

### 3. Analisis Data Cerdas (Data Analytics)

API menyediakan endpoint analisis mendalam menggunakan `Pandas` dan `Scikit-Learn`:

* **Rata-rata Volume:** Per lokasi dan per kategori.
* **Tren Harian (Daily Trend):** Visualisasi pergerakan volume sampah dari waktu ke waktu (dilengkapi *Moving Average*).
* **Top Locations:** Identifikasi lokasi paling "kotor" atau produktif.
* **Distribusi Sampah:** Persentase komposisi jenis sampah.
* **Prediksi Volume (Machine Learning):** Menggunakan **Linear Regression** untuk memprediksi volume sampah 7 hari ke depan.
* **Optimasi Rute (Route Optimization):** Menggunakan algoritma **TSP (Traveling Salesperson Problem - Nearest Neighbor)** untuk menentukan rute pengumpulan sampah terpendek yang efisien.

### 4. Fitur Tambahan

* **Database Seeding:** Script otomatis untuk mengisi database dengan data dummy awal.
* **CSV Import:** Kemudahan import data massal dari file CSV.

---

## 🛠️ Teknologi yang Digunakan

* **Language:** Python 3.10+
* **Framework:** FastAPI
* **Database:** SQL Database (via SQLAlchemy ORM)
* **Data Analysis:** Pandas, NumPy
* **Machine Learning:** Scikit-Learn (Linear Regression)
* **Authentication:** PyJWT, Passlib (Bcrypt)
* **Testing:** Pytest

---

## 🚀 Instalasi dan Cara Menjalankan

Ikuti langkah-langkah berikut untuk menjalankan proyek di komputer lokal Anda:

### 1. Clone Repository

```bash
git clone https://github.com/username/waste-management-api.git
cd waste-management-api
```

### 2. Buat Virtual Environment

Disarankan menggunakan virtual environment agar *dependency* tidak bentrok.

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database & Seeding Data

Jalankan perintah berikut untuk membuat tabel dan mengisi data awal (User Admin & Data Dummy):

```bash
python seed.py
```

**Default User:**

* **Admin:** `admin` / `admin`

### 5. Jalankan Server

```bash
uvicorn main:app --reload
```

Server akan berjalan di: `http://127.0.0.1:8000`

---

## 📚 Dokumentasi API

FastAPI menyediakan dokumentasi interaktif secara otomatis. Setelah server berjalan, buka browser dan akses:

* **Swagger UI (Interaktif):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Endpoint Utama

| Method | Endpoint                   | Deskripsi                              | Role          |
| ------ | -------------------------- | -------------------------------------- | ------------- |
| `POST` | `/auth/token`              | Login untuk mendapatkan Access Token   | All           |
| `GET`  | `/analysis/summary`        | Ringkasan dashboard (KPI)              | Admin         |
| `GET`  | `/analysis/trend/daily`    | Tren volume sampah harian              | Admin         |
| `GET`  | `/analysis/prediction`     | Prediksi volume 7 hari ke depan        | Admin         |
| `GET`  | `/analysis/route/optimize` | Rekomendasi rute pengumpulan terpendek | Admin         |
| `GET`  | `/collections/`            | Melihat riwayat pengumpulan sampah     | Admin         |

---

## 🧪 Menjalankan Testing

Proyek ini dilengkapi dengan *Unit Testing* untuk memastikan fitur berjalan lancar.

```bash
pytest
```

---

## 📂 Struktur Folder

```text
waste-management-api/
├── models/             # Definisi Tabel Database & Pydantic Schemas
├── routers/            # Endpoint API (Auth, Collection, Analysis, dll)
├── services/           # Logika Bisnis (CRUD, Hitungan Analisis)
├── tests/              # Unit Tests
├── main.py             # Entry Point Aplikasi
├── database.py         # Koneksi Database
├── seed.py             # Script Seeding Data
└── requirements.txt    # Daftar Library
```

---
