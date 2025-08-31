# Tugas Calon Asisten Lab Teknik Kendali 2025

## UAV Ground Control Station

Aplikasi interfacing UAV ke laptop yang memiliki fitur-fitur berupa:
- Status UAV (data kemiringan, kecepatan, posisi, visualisasi arah, dan tampilan 3D) dengan PyQt5 dan PyQt3D
- Grafik PID tuning dengan perhitungan numerik NumPy dan visualisasi Matplotlib
- Maps waypoint dengan protokol MAVLink dan library MAVSDK

## Prerequisites

### Sistem Operasi
- **Ubuntu 20.04 LTS atau lebih baru** (Recommended)
- WSL2 dengan Ubuntu (untuk Windows users)
- Python 3.8+

### Dependencies Utama
- PX4-Autopilot
- Gazebo Garden Simulator
- PyQt5 & PyQt3D
- NumPy
- Matplotlib
- MAVSDK
- MAVLink

## Instalasi

### Dev Setup
Ikuti panduan lengkap di: https://docs.px4.io/main/en/dev_setup/dev_env_linux_ubuntu.html#simulation-and-nuttx-pixhawk-targets

#### Untuk Windows Users: Install WSL2

**Pastikan virtualization sudah diaktifkan di BIOS:**
- Cari setting "Virtualization Technology", "Intel VT-x" atau "AMD-V" di BIOS
- Enable fitur tersebut

**Install WSL2 dengan Ubuntu:**

1. Buka `cmd.exe` sebagai administrator:
   - Tekan Start key, ketik `cmd`
   - Klik kanan pada Command Prompt → "Run as administrator"

2. Execute salah satu command berikut:

```bash
# Default version (Ubuntu 22.04) - untuk Gazebo Garden
wsl --install

# Atau pilih versi spesifik:
# Ubuntu 20.04 (untuk Gazebo-Classic)
wsl --install -d Ubuntu-20.04

# Ubuntu 22.04 (untuk Gazebo Garden) - Recommended
wsl --install -d Ubuntu-22.04
```

3. WSL akan meminta username dan password untuk Ubuntu installation
   - **Catat credentials ini!** Akan dibutuhkan nanti

4. Restart computer jika diminta

### 1. Setup PX4-Autopilot (Wajib di Ubuntu)

```bash
# Clone PX4-Autopilot repository
git clone https://github.com/PX4/PX4-Autopilot.git --recursive
cd PX4-Autopilot

# Install dependencies (akan menginstall Gazebo, toolchain, dll)
bash ./Tools/setup/ubuntu.sh

# Restart terminal atau source bashrc
source ~/.bashrc

# Build PX4 untuk simulasi
make px4_sitl gz_x500
```

### 2. Install Python Dependencies

```bash
# Pastikan berada di direktori
cd teken-4-drone-gcs

# Install Python dependencies
pip install -e .
```

### 3. Setup Project

```bash
# Clone project repository
git clone <repository-url>
cd teken-4-drone-gcs
```

## Cara Menjalankan

### 1. Start Gazebo Simulation

```bash
# Terminal 1: Start PX4 SITL dengan Gazebo Garden
cd PX4-Autopilot
make px4_sitl gz_x500

# Tunggu hingga muncul pesan "pxh>" dan Gazebo terbuka
# Drone X500 akan muncul di Gazebo
```

### 2. Run Ground Control Station

```bash
# Terminal 2: Run aplikasi GCS (Masuk ke venv)
cd teken-4-drone-gcs/src
python main.py
```

### 3. Verifikasi Koneksi

- Pastikan Gazebo menampilkan drone X500
- GCS seharusnya menampilkan status "Connected" 
- Telemetry data mulai streaming (altitude, attitude, GPS, dll)

## Struktur Aplikasi

```
teken-4-drone-gcs/
├── src/
│   ├── main.py              # Entry point aplikasi
│   ├── gui/                 # PyQt5 GUI components
│   ├── communication/       # MAVLink/MAVSDK handlers
│   ├── visualization/       # PyQt3D dan Matplotlib
│   └── utils/              # Helper functions
├── resources/              # Icons, images, maps
├── docs/                   # Documentation
└── requirements.txt        # Python dependencies
```

## Fitur Aplikasi

### 🚁 Status Monitor
- Real-time monitoring attitude (roll, pitch, yaw)
- Kecepatan ground speed dan air speed
- Posisi GPS (latitude, longitude, altitude)
- Battery status dan flight mode

### 🎮 3D Visualization
- Tampilan 3D orientasi drone dengan PyQt3D
- Visualisasi arah dan attitude secara real-time
- Ground track dan trajectory history

### 📊 PID Tuning Interface
- Interface untuk tuning parameter PID
- Grafik real-time response dengan Matplotlib
- Export/Import parameter settings
- Step response analysis

### 🗺️ Waypoint Management
- Interactive maps untuk set waypoint
- Mission planning dan execution
- Real-time tracking posisi drone
- Geofencing support

### 📡 Telemetry Display
- Raw MAVLink message viewer
- Data logging dan export
- Connection status monitoring

## Troubleshooting

### Connection Issues

```bash
# Check apakah PX4 SITL running
ps aux | grep px4

# Check port MAVLink (default: UDP 14540)
netstat -an | grep 14540
```

### Gazebo Issues

```bash
# Reset Gazebo jika hang
pkill -9 ruby
make px4_sitl gz_x500
```

### Default PID Parameters

Parameter PID default yang bisa digunakan sebagai starting point:

#### Rate Control
- **Roll Rate**: P=0.15, I=0.20, D=0.003
- **Pitch Rate**: P=0.15, I=0.20, D=0.003
- **Yaw Rate**: P=0.2, I=0.1, D=0.0

#### Attitude Control
- **Roll Attitude**: P=6.5, I=0.0, D=0.0
- **Pitch Attitude**: P=6.5, I=0.0, D=0.0
- **Yaw Attitude**: P=2.8, I=0.0, D=0.0

#### Velocity Control
- **Horizontal Velocity**: P=0.1, I=0.02, D=0.01
- **Vertical Velocity**: P=0.2, I=0.15, D=0.0

#### Position Control
- **Horizontal Position**: P=0.95, I=0.0, D=0.0
- **Vertical Position**: P=1.0, I=0.0, D=0.0

## Tim

**Kelompok 4:**
- Muhammad Alif Iqbal
- Kevin Imanuel Hutagaol  
- Muhammad Rafly Fadhilah Irsa
- Tsaqif Rizky Muhammad

## Kontribusi Anggota Kelompok:

> **Kevin** :
> Mengerjakan sisi frontend serta controller (integrasi BE dan FE) dari project, 
> serta Map Display Window, termasuk:
> - Window Map Display, yang dapat menampilkan pergerakan drone serta memodifikasi waypoints arah gerak drone
> - Main Window UI, yang menampilkan nilai dari parameter drone seperti attitude, position, velocity, condition
> - Drone 3D visualisation widget, yang memperlihatkan arah drone di 3 Dimensi
> - Class - class controller yang berguna alam komunikasi antar UI dari dan menuju DroneModel
> - Mengintegrasikan Berbagai class UI dengan fitur FE maupun BE lainnya 

> **Iqbal** :
> Mengerjakan Backend dari project, termasuk:
> - Koneksi ke drone oleh library mavsdk
> - Logic pengambilan dan pengiriman data dari dan kepada drone
> - Fungsi pergerakan drone
> - Pembuatan representasi DroneModel yang bisa berinteraksi dengan UI

> **Rafly** :
> Mengerjakan PID Tuning Window:
> Membuat UI PID Tuning, termasuk:
> - Window Tuning PID, dengan beberapa tab yang berisi nilai dan input parameter
> - Graphing nilai PID untuk parameter rate, attitude, velocity, position.
> - Komunikasi nilai PID antar dari dan kepada drone

> **Tsaqif** :
>
> Mengerjakan Data Logging Window:
> Membuat UI data logging, termasuk:
> - Graphing dari nilai velocity, position, attitude, battery voltage dan percentage
> - Timer untuk mengambil data dari Drone
> - Penyimpanan graph sebagai image, dan sebagai file csv 

---
*Tugas Calon Asisten Lab Teknik Kendali 2025*