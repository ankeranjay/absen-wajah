import face_recognition
import cv2
import pickle
import sqlite3
from datetime import datetime
import numpy as np
import os
import shutil

# ==== KONFIGURASI ====
THRESHOLD = 0.6
DB_PATH = "database/absensi.db"
ENCODINGS_PATH = "data/encodings.pickle"
SKALA_DETEKSI = 0.5
TAMPIL_INFO_DETIK = 5
BACKUP_SAAT_TUTUP = True

def get_conn():
    return sqlite3.connect(DB_PATH)

def get_pengaturan(key):
    conn = get_conn()
    row = conn.execute("SELECT value FROM pengaturan WHERE key=?", (key,)).fetchone()
    conn.close()
    return row[0] if row else None

def get_siswa(nis):
    conn = get_conn()
    row = conn.execute(
        "SELECT nis, nama, kelas, angkatan FROM siswa WHERE nis=?", (nis,)
    ).fetchone()
    conn.close()
    return row

def catat_absen(nis, jam_batas):
    """Return: ('baru', status, jam) atau ('sudah', jam_lama, None)."""
    conn = get_conn()
    tanggal = datetime.now().strftime("%Y-%m-%d")
    jam = datetime.now().strftime("%H:%M:%S")

    ada = conn.execute(
        "SELECT jam_masuk FROM kehadiran WHERE nis=? AND tanggal=?",
        (nis, tanggal)
    ).fetchone()
    if ada:
        conn.close()
        return ("sudah", ada[0], None)

    jam_sekarang = datetime.now().strftime("%H:%M")
    status = "Terlambat" if jam_sekarang > jam_batas else "Hadir"

    conn.execute("""
        INSERT INTO kehadiran (nis, tanggal, jam_masuk, status)
        VALUES (?, ?, ?, ?)
    """, (nis, tanggal, jam, status))
    conn.commit()
    conn.close()
    return ("baru", status, jam)

def backup_database():
    try:
        os.makedirs("backup", exist_ok=True)
        tgl = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dst = f"backup/absensi_{tgl}.db"
        shutil.copy2(DB_PATH, dst)
        print(f"[OK] Backup otomatis: {dst}")
    except Exception as e:
        print(f"[WARN] Backup gagal: {e}")

# ==== LOAD DATA ====
print("[INFO] Memuat encoding...")
with open(ENCODINGS_PATH, "rb") as f:
    data = pickle.load(f)
print(f"[INFO] {len(data['names'])} encoding siap.")

jam_batas = get_pengaturan("jam_masuk_batas") or "06:30"
nama_sekolah = get_pengaturan("nama_sekolah") or "MAN 11 Jakarta Selatan"
print(f"[INFO] Sekolah: {nama_sekolah} | Batas jam masuk: {jam_batas}")

# ==== KAMERA ====
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cam.set(cv2.CAP_PROP_FPS, 30)

cv2.namedWindow("Kiosk Absen", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Kiosk Absen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# ==== STATE ====
sudah_absen_sesi = {}
wajah_terakhir = []
info_per_nis = {}
info_terakhir = None
waktu_info = 0

SKALA_BALIK = int(1 / SKALA_DETEKSI)

print("[INFO] Kiosk absen berjalan. Tekan ESC untuk keluar.")

while True:
    ret, frame = cam.read()
    if not ret:
        break

    small = cv2.resize(frame, (0, 0), fx=SKALA_DETEKSI, fy=SKALA_DETEKSI)
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, boxes)

    wajah_frame_ini = []

    for (top, right, bottom, left), enc in zip(boxes, encodings):
        name = "Tidak dikenal"
        color = (0, 0, 255)
        nis = None

        if data["encodings"]:
            distances = face_recognition.face_distance(data["encodings"], enc)
            best = int(np.argmin(distances))

            if distances[best] < THRESHOLD:
                name = data["names"][best]
                nis = name.split("_")[0]
                color = (0, 200, 0)

                if nis in sudah_absen_sesi:
                    hasil, jam_lama, jam_baru = sudah_absen_sesi[nis]
                else:
                    hasil, jam_lama, jam_baru = catat_absen(nis, jam_batas)
                    sudah_absen_sesi[nis] = (hasil, jam_lama, jam_baru)

                siswa = get_siswa(nis)
                if siswa:
                    nama_tampil = siswa[1]
                    kelas = siswa[2]

                    if hasil == "sudah":
                        info = f"{nama_tampil} | {kelas} | Sudah absen ({jam_lama})"
                        color = (0, 165, 255)
                    else:
                        info = f"{nama_tampil} | {kelas} | {hasil} {jam_baru}"
                        print(f"[ABSEN] {info}")

                    info_per_nis[nis] = (info, cv2.getTickCount())
                    info_terakhir = info
                    waktu_info = cv2.getTickCount()

        wajah_frame_ini.append({
            "top": top * SKALA_BALIK,
            "right": right * SKALA_BALIK,
            "bottom": bottom * SKALA_BALIK,
            "left": left * SKALA_BALIK,
            "name": name,
            "color": color,
            "nis": nis,
        })

    if wajah_frame_ini:
        wajah_terakhir = wajah_frame_ini

    for w in wajah_terakhir:
        top = w["top"]
        right = w["right"]
        bottom = w["bottom"]
        left = w["left"]
        name = w["name"]
        color = w["color"]

        cv2.rectangle(frame, (left, top), (right, bottom), color, 3)

        label = name.split("_", 1)[1].replace("_", " ") if "_" in name else name
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.7, 2)
        cv2.rectangle(frame, (left, bottom), (left + tw + 20, bottom + th + 20), color, cv2.FILLED)
        cv2.putText(frame, label, (left + 10, bottom + th + 8),
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (255, 255, 255), 2)

    # ==== HEADER ====
    cv2.rectangle(frame, (0, 0), (frame.shape[1], 90), (25, 25, 35), cv2.FILLED)
    cv2.putText(frame, f"ABSENSI - {nama_sekolah}",
                (25, 40), cv2.FONT_HERSHEY_DUPLEX, 1.1, (255, 255, 255), 2)
    cv2.putText(frame, datetime.now().strftime("%A, %d %B %Y   %H:%M:%S WIB"),
                (25, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 200), 1)

    cv2.putText(frame, f"Hadir: {len(sudah_absen_sesi)}",
                (frame.shape[1] - 250, 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, (100, 255, 100), 2)

    # ==== FOOTER INFO TERAKHIR ====
    if info_terakhir:
        sisa = (cv2.getTickCount() - waktu_info) / cv2.getTickFrequency()
        if sisa < TAMPIL_INFO_DETIK:
            cv2.rectangle(frame, (0, frame.shape[0]-80), (frame.shape[1], frame.shape[0]),
                          (0, 110, 0), cv2.FILLED)
            cv2.putText(frame, info_terakhir,
                        (30, frame.shape[0]-28), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 2)

    cv2.imshow("Kiosk Absen", frame)
    if cv2.waitKey(1) == 27:
        break

cam.release()
cv2.destroyAllWindows()

# ==== BACKUP OTOMATIS SAAT TUTUP ====
if BACKUP_SAAT_TUTUP:
    backup_database()

print("[SELESAI] Kiosk ditutup.")