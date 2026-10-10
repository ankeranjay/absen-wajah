import face_recognition
import os
import pickle
from imutils import paths

DATASET_DIR = "dataset"
OUTPUT = "data/encodings.pickle"

os.makedirs("data", exist_ok=True)

print("[INFO] Membaca dataset...")
image_paths = list(paths.list_images(DATASET_DIR))

known_encodings = []
known_names = []

for i, path in enumerate(image_paths):
    nama = path.split(os.path.sep)[-2]
    print(f"[{i+1}/{len(image_paths)}] Proses: {nama}")

    image = face_recognition.load_image_file(path)
    boxes = face_recognition.face_locations(image, model="hog")

    if len(boxes) == 0:
        print(f"   [SKIP] Tidak ada wajah terdeteksi")
        continue
    if len(boxes) > 1:
        print(f"   [SKIP] Terdeteksi {len(boxes)} wajah")
        continue

    encodings = face_recognition.face_encodings(image, boxes)
    for enc in encodings:
        known_encodings.append(enc)
        known_names.append(nama)

print("\n[INFO] Ringkasan per siswa:")
for nama in sorted(set(known_names)):
    jumlah = known_names.count(nama)
    print(f"  {nama}: {jumlah} encoding")

with open(OUTPUT, "wb") as f:
    pickle.dump({"encodings": known_encodings, "names": known_names}, f)

print(f"\n[SELESAI] {len(known_encodings)} encoding dari {len(set(known_names))} siswa.")