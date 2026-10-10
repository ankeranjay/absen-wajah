import cv2
import os

NAMA_SISWA = input("Nama siswa (pakai spasi): ").strip()
NIS        = input("NIS: ").strip()

folder = f"dataset/{NIS}_{NAMA_SISWA.replace(' ', '_')}"
os.makedirs(folder, exist_ok=True)

cam = cv2.VideoCapture(0)
detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

print("\n[INFO] Arahkan wajah ke kamera. SPASI = ambil foto, ESC = keluar.")
print("[INFO] Ambil minimal 10-15 foto dari berbagai sudut.\n")

count = 0
while True:
    ret, frame = cam.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.putText(frame, f"Foto: {count}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow("Registrasi Wajah - SPASI ambil, ESC keluar", frame)

    key = cv2.waitKey(1)
    if key == 27:
        break
    elif key == 32 and len(faces) == 1:
        (x, y, w, h) = faces[0]
        m = 30
        x1, y1 = max(0, x-m), max(0, y-m)
        x2, y2 = min(frame.shape[1], x+w+m), min(frame.shape[0], y+h+m)
        wajah = frame[y1:y2, x1:x2]

        count += 1
        cv2.imwrite(f"{folder}/{count}.jpg", wajah)
        print(f"[OK] Foto {count} tersimpan")

cam.release()
cv2.destroyAllWindows()
print(f"\n[SELESAI] {count} foto tersimpan di {folder}")