import os
import shutil
from datetime import datetime

SRC = "database/absensi.db"
BACKUP_DIR = "backup"
MAX_BACKUP = 30

def backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)

    if not os.path.exists(SRC):
        print(f"[ERROR] {SRC} tidak ditemukan")
        return

    tanggal = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dst = os.path.join(BACKUP_DIR, f"absensi_{tanggal}.db")

    shutil.copy2(SRC, dst)
    print(f"[OK] Backup: {dst}")

    files = sorted([
        f for f in os.listdir(BACKUP_DIR)
        if f.startswith("absensi_") and f.endswith(".db")
    ])
    while len(files) > MAX_BACKUP:
        old = files.pop(0)
        os.remove(os.path.join(BACKUP_DIR, old))
        print(f"[HAPUS] Backup lama: {old}")

if __name__ == "__main__":
    backup()