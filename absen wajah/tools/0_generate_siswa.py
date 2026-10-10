import csv
import os

os.makedirs("data", exist_ok=True)

# ==== KONFIGURASI ====
KELAS_10 = ["X-A", "X-B", "X-C", "X-D", "X-E", "X-F", "X-G"]
KELAS_11 = ["XI-Inkrea", "XI-Soshum", "XI-AI & IOT", "XI-Terapan", "XI-Manajerial", "XI-Nakes"]
KELAS_12 = ["XII-Inkrea", "XII-Soshum", "XII-AI & IOT", "XII-Terapan", "XII-Manajerial", "XII-Nakes", 'XII-Dikmu']
ANGKATAN = {
    "2029": KELAS_10,   # kelas 10 tahun ajaran ini
    "2028": KELAS_11,
    "2027": KELAS_12,
}
SISWA_PER_KELAS = 36

# ==== GENERATE TEMPLATE ====
rows = []
nis_counter = 24000  # mulai dari sini, sesuaikan

for angkatan, kelas_list in ANGKATAN.items():
    for kelas in kelas_list:
        for i in range(1, SISWA_PER_KELAS + 1):
            nis = str(nis_counter).zfill(6)
            rows.append({
                "nis": nis,
                "nama": f"NAMA_SISWA_{kelas}_{i:02d}",  # ganti manual nanti
                "angkatan": angkatan,
                "kelas": kelas,
            })
            nis_counter += 1

with open("data/siswa.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["nis", "nama", "angkatan", "kelas"])
    writer.writeheader()
    writer.writerows(rows)

print(f"[OK] {len(rows)} siswa ditulis ke data/siswa.csv")
print("[INFO] Buka file itu di Excel, ganti kolom 'nama' dengan nama asli.")