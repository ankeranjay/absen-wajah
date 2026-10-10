import sqlite3
import csv
import os

os.makedirs("database", exist_ok=True)

conn = sqlite3.connect("database/absensi.db")
c = conn.cursor()

c.executescript("""
CREATE TABLE IF NOT EXISTS siswa (
    nis TEXT PRIMARY KEY,
    nama TEXT NOT NULL,
    angkatan TEXT NOT NULL,
    kelas TEXT NOT NULL,
    aktif INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS hari_sekolah (
    tanggal TEXT PRIMARY KEY,
    keterangan TEXT
);

CREATE TABLE IF NOT EXISTS kehadiran (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nis TEXT NOT NULL,
    tanggal TEXT NOT NULL,
    jam_masuk TEXT,
    jam_pulang TEXT,
    status TEXT,
    FOREIGN KEY (nis) REFERENCES siswa(nis),
    UNIQUE(nis, tanggal)
);

CREATE TABLE IF NOT EXISTS pengaturan (
    key TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_kehadiran_tanggal ON kehadiran(tanggal);
CREATE INDEX IF NOT EXISTS idx_kehadiran_nis ON kehadiran(nis);
CREATE INDEX IF NOT EXISTS idx_siswa_kelas ON siswa(kelas);
""")

# Pengaturan awal
default = {
    "nama_sekolah": "MAN 11 Jakarta Selatan",
    "jam_masuk_batas": "06:30",
    "jam_pulang": "15:00",
}
for k, v in default.items():
    c.execute("INSERT OR IGNORE INTO pengaturan (key, value) VALUES (?, ?)", (k, v))

# Muat siswa dari CSV (auto-deteksi pemisah: TAB atau koma)
if os.path.exists("data/siswa.csv"):
    with open("data/siswa.csv", newline="", encoding="utf-8-sig") as f:
        sample = f.readline()
        f.seek(0)
        delimiter = "\t" if "\t" in sample else ","
        print(f"[INFO] Pemisah: {'TAB' if delimiter == chr(9) else 'koma'}")

        reader = csv.DictReader(f, delimiter=delimiter)
        # bersihkan nama kolom dari spasi/BOM
        reader.fieldnames = [h.strip() for h in reader.fieldnames]

        count = 0
        for row in reader:
            try:
                c.execute("""
                    INSERT OR REPLACE INTO siswa (nis, nama, angkatan, kelas)
                    VALUES (?, ?, ?, ?)
                """, (
                    row["nis"].strip(),
                    row["nama"].strip(),
                    row["angkatan"].strip(),
                    row["kelas"].strip()
                ))
                count += 1
            except KeyError as e:
                print(f"[ERROR] Kolom tidak ditemukan: {e}")
                print(f"[INFO] Header: {reader.fieldnames}")
                break
    print(f"[OK] {count} siswa dimuat ke database")
else:
    print("[WARN] data/siswa.csv tidak ditemukan")

conn.commit()
conn.close()
print("[OK] Database siap: database/absensi.db")