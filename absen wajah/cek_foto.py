import face_recognition
import cv2
import os
from imutils import paths

folder = input("Folder siswa (misal: dataset/244458_Haikal_Azfar_Febrian): ")
fotos = sorted(list(paths.list_images(folder)))

for p in fotos:
    img = face_recognition.load_image_file(p)
    boxes = face_recognition.face_locations(img, model="hog")

    if len(boxes) == 0:
        status = "❌ TIDAK TERDETEKSI"
    elif len(boxes) > 1:
        status = f"⚠️ {len(boxes)} WAJAH"
    else:
        status = "✅ OK"

    print(f"{os.path.basename(p):<10} {status}")

    # simpan preview dengan kotak
    frame = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    for (t, r, b, l) in boxes:
        cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)
    cv2.imwrite(f"preview_{os.path.basename(p)}", frame)

print("\nFile preview_*.jpg sudah disimpan, buka untuk lihat hasilnya.")
