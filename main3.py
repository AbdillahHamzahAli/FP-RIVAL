import cv2
import numpy as np
import time
webcam = cv2.VideoCapture(1)
KNOWN_WIDTH = 3.0
FOCAL_LENGTH = 1000

tercapit = False
posisi_awal = True

jalan_pertama = True
JALAN_KEDUA = False
JALAN_KETIGA = False
JALAN_KEEMPAT = False

object_kiri_atas = ''
object_kanan_atas = ''
object_kiri_bawah = ''
object_kanan_bawah = ''


belok_kiri_start_time = 0
total_belok_kiri_time = 0
maju_start_time = 0
total_maju_time = 0

def distance_to_camera(knownWidth, focalLength, perWidth):
    return (knownWidth * focalLength) / perWidth

def belok_kiri():
    global belok_kiri_start_time
    if belok_kiri_start_time == 0:
        belok_kiri_start_time = time.time()
    print("Belok kiri")

def belok_kanan():
    global belok_kiri_start_time, total_belok_kiri_time
    if belok_kiri_start_time != 0:
        total_belok_kiri_time += time.time() - belok_kiri_start_time
        belok_kiri_start_time = 0
    print("Belok kanan")

def stop():
    global belok_kiri_start_time, total_belok_kiri_time, maju_start_time, total_maju_time
    if belok_kiri_start_time != 0:
        total_belok_kiri_time += time.time() - belok_kiri_start_time
        belok_kiri_start_time = 0
    if maju_start_time != 0:
        total_maju_time += time.time() - maju_start_time
        maju_start_time = 0
    print("Stop")

def maju():
    global belok_kiri_start_time, total_belok_kiri_time, maju_start_time
    if belok_kiri_start_time != 0:
        total_belok_kiri_time += time.time() - belok_kiri_start_time
        belok_kiri_start_time = 0
    if maju_start_time == 0:
        maju_start_time = time.time()
    print("Maju")

def mundur():
    print("Mundur")

def capit():
    print("Capit")


var_orang_kiri_atas = None


print(torch.cuda.get_device_name(0))
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Using device: {device}')
model = YOLO('best.pt').to(device)
classNames = ["orang_biru", "orang_putih"]

while True:
    ret, frame = webcam.read()
    if not ret:
        break

    height, width = frame.shape[:2]
    center_y, center_h = height // 3, height // 3
    center_frame = frame[center_y:center_y+center_h, :]

    hsv = cv2.cvtColor(center_frame, cv2.COLOR_BGR2HSV)

    blue_mask = cv2.inRange(hsv, np.array([100, 150, 0]), np.array([140, 255, 255]))
    white_mask = cv2.inRange(hsv, np.array([0, 0, 200]), np.array([180, 30, 255]))

    contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    white_contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if jalan_pertama:
        if not tercapit:
            left_frame = center_frame[:, :width//2]
            left_hsv = cv2.cvtColor(left_frame, cv2.COLOR_BGR2HSV)

            # Detect blue objects on the left side
            left_blue_mask = cv2.inRange(left_hsv, np.array([100, 150, 0]), np.array([140, 255, 255]))
            left_contours, _ = cv2.findContours(left_blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Draw contours for blue objects on the left side
            for contour in left_contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Adjust this threshold as needed
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(center_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.putText(center_frame, "Blue Object", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Detect white objects on the left side
            left_white_mask = cv2.inRange(left_hsv, np.array([0, 0, 200]), np.array([180, 30, 255]))
            left_white_contours, _ = cv2.findContours(left_white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Draw contours for white objects on the left side
            for contour in left_white_contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Adjust this threshold as needed
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(center_frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    cv2.putText(center_frame, "White Object", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)



    frame[center_y:center_y+center_h, :] = center_frame
    cv2.rectangle(frame, (0, center_y), (width, center_y + center_h), (0, 255, 0), 2)
    cv2.line(frame, (width // 2, 0), (width // 2, height), (0, 255, 0), 2)

    cv2.putText(frame, f"Total belok kiri: {total_belok_kiri_time:.2f} detik", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    cv2.putText(frame, f"Total maju: {total_maju_time:.2f} detik", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Object Detection", frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

webcam.release()
cv2.destroyAllWindows()

print(f"Total waktu belok kiri: {total_belok_kiri_time:.2f} detik")
print(f"Total waktu maju: {total_maju_time:.2f} detik")
