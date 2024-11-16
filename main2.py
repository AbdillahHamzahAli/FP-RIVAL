import cv2
import numpy as np
import time
webcam = cv2.VideoCapture(1)
KNOWN_WIDTH = 3.0
FOCAL_LENGTH = 1000

tercapit = False
posisi_awal = True

JALAN_PERTAMA = True
JALAN_KEDUA = False
JALAN_KETIGA = False
JALAN_KEEMPAT = False

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

    


    if tercapit == False:    
        if var_orang_kiri_atas is None:
            left_area = blue_mask[:, :width//2]
            left_area_white = white_mask[:, :width//2]
            if np.sum(left_area) > 0:
                var_orang_kiri_atas = "Blue"
            elif np.sum(left_area_white) > 0:
                var_orang_kiri_atas = "White"

        if var_orang_kiri_atas == "Blue":
            for contour in contours:
                if cv2.contourArea(contour) > 1000:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(center_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    
                    center_point = (x + w // 2, y + h // 2)
                    cv2.circle(center_frame, center_point, 5, (255, 0, 0), -1)
                    
                    distance = distance_to_camera(KNOWN_WIDTH, FOCAL_LENGTH, w)
                    cv2.putText(center_frame, f"Blue: {distance:.2f} inches", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                    
                    frame_center = center_frame.shape[1] // 2
                    if distance <= 14 and frame_center - 2 <= center_point[0] <= frame_center + 2:
                        stop()
                        capit()
                        tercapit = True
                        time.sleep(2)
                    elif center_point[0] < frame_center - 2:
                        belok_kiri()
                        posisi_awal = False
                    elif center_point[0] > frame_center + 2:
                        belok_kanan()
                        posisi_awal = False
                    else:
                        stop()
                        maju()
                        posisi_awal = False
                    break
        elif var_orang_kiri_atas == "White":
            for contour in white_contours:
                if cv2.contourArea(contour) > 1000:
                    x, y, w, h = cv2.boundingRect(contour)
                    cv2.rectangle(center_frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    
                    center_point = (x + w // 2, y + h // 2)
                    cv2.circle(center_frame, center_point, 5, (255, 255, 255), -1)
                    
                    distance = distance_to_camera(KNOWN_WIDTH, FOCAL_LENGTH, w)
                    cv2.putText(center_frame, f"White: {distance:.2f} inches", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                    
                    frame_center = center_frame.shape[1] // 2
                    if distance <= 14 and frame_center - 2 <= center_point[0] <= frame_center + 2:
                        stop()
                        capit()
                        tercapit = True
                        time.sleep(2)
                    elif center_point[0] < frame_center - 2:
                        belok_kiri()
                        posisi_awal = False
                    elif center_point[0] > frame_center + 2:
                        belok_kanan()
                        posisi_awal = False
                    else:
                        stop()
                        maju()
                        posisi_awal = False
                    break                
    if tercapit == True:
        if JALAN_PERTAMA == True:
            mundur_time = total_maju_time
            belok_kanan_time = total_belok_kiri_time
            
            start_time = time.time()
            while time.time() - start_time < mundur_time:
                mundur()
                time.sleep(0.1)
            
            start_time = time.time()
            while time.time() - start_time < belok_kanan_time:
                belok_kanan()
                time.sleep(0.1)
            
            JALAN_PERTAMA = False
            JALAN_KEDUA = True

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
