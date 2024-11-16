from ultralytics import YOLO
from pyfirmata2 import Arduino, SERVO
import cv2
import math 
import torch
import numpy as np
import time
import json

# INITIAL VARIABLE
posisi_qr = {}
classNames = ["PENJARA BIRU", "PENJARA PUTIH"] # for clas yolo


class MotorController:
    def __init__(self, port='COM3'):
        self.board = Arduino(port)

        # Definisi pin servo dan motor
        self.servo_capit_pin = 10
        self.servo_lifter_pin = 11

        self.board.digital[self.servo_capit_pin].mode = SERVO
        self.board.digital[self.servo_lifter_pin].mode = SERVO

        self.mundur_kanan_depan_IN1 = 2
        self.maju_kanan_depan_IN2 = 3
        self.maju_kanan_belakang_IN4 = 5
        self.mundur_kanan_belakang_IN3 = 4

        self.mundur_kiri_depan_IN1 = 7
        self.maju_kiri_depan_IN2 = 8
        self.maju_kiri_belakang_IN3 = 12
        self.mundur_kiri_belakang_IN4 = 13

        # Pin PWM untuk mengontrol kecepatan motor melalui ENA dan ENB
        self.ENA = 6   # PWM untuk motor kiri
        self.ENB = 9   # PWM untuk motor kanan

        # Atur ENA dan ENB sebagai output PWM
        self.ena_pwm = self.board.get_pin(f'd:{self.ENA}:p')
        self.enb_pwm = self.board.get_pin(f'd:{self.ENB}:p')
        self.servo_lifter = self.board.get_pin(f'd:{self.servo_lifter_pin}:s')
        self.servo_capit = self.board.get_pin(f'd:{self.servo_capit_pin}:s')

    def intial_servo():
        self.servo_capit.write(90)

    def capit_buka(self):
        self.servo_capit.write(80)
        print("capit_buka")

    def capit_tutup(self):
        self.servo_capit.write(40)
        print("capit_tutup")

    def lift_turun(self):
        self.servo_lifter.write(80)
        print("lift_turun")

    def lift_naik(self):
        self.servo_lifter.write(45)
        print("lift_naik")

    def set_motor_speed(self, kecepatan_kiri, kecepatan_kanan):
        self.ena_pwm.write(kecepatan_kiri)  # kecepatan_kiri adalah nilai antara 0 dan 1
        self.enb_pwm.write(kecepatan_kanan)  # kecepatan_kanan adalah nilai antara 0 dan 1

    def maju(self, kecepatan=1):
        self.set_motor_speed(kecepatan, kecepatan)
        self.board.digital[self.maju_kanan_depan_IN2].write(1)
        self.board.digital[self.mundur_kanan_depan_IN1].write(0)

        self.board.digital[self.maju_kanan_belakang_IN4].write(1)
        self.board.digital[self.mundur_kanan_belakang_IN3].write(0)

        self.board.digital[self.maju_kiri_depan_IN2].write(1)
        self.board.digital[self.mundur_kiri_depan_IN1].write(0)
        
        self.board.digital[self.maju_kiri_belakang_IN3].write(1)
        self.board.digital[self.mundur_kiri_belakang_IN4].write(0)

    def mundur(self, kecepatan=0.6):
        self.set_motor_speed(kecepatan, kecepatan)
        self.board.digital[self.maju_kanan_depan_IN2].write(0)
        self.board.digital[self.mundur_kanan_depan_IN1].write(1)

        self.board.digital[self.maju_kanan_belakang_IN4].write(0)
        self.board.digital[self.mundur_kanan_belakang_IN3].write(1)

        self.board.digital[self.maju_kiri_depan_IN2].write(0)
        self.board.digital[self.mundur_kiri_depan_IN1].write(1)
        
        self.board.digital[self.maju_kiri_belakang_IN3].write(0)
        self.board.digital[self.mundur_kiri_belakang_IN4].write(1)
        
    def kiri(self, kecepatan=0.6):
        self.set_motor_speed(kecepatan, kecepatan)
        self.board.digital[self.maju_kanan_depan_IN2].write(1)
        self.board.digital[self.mundur_kanan_depan_IN1].write(0)

        self.board.digital[self.maju_kanan_belakang_IN4].write(1)
        self.board.digital[self.mundur_kanan_belakang_IN3].write(0)

        self.board.digital[self.maju_kiri_depan_IN2].write(0)
        self.board.digital[self.mundur_kiri_depan_IN1].write(0)
        
        self.board.digital[self.maju_kiri_belakang_IN3].write(0)
        self.board.digital[self.mundur_kiri_belakang_IN4].write(0)
        
    def kanan(self, kecepatan=0.6):
        self.set_motor_speed(kecepatan, kecepatan)
        self.board.digital[self.maju_kanan_depan_IN2].write(0)
        self.board.digital[self.mundur_kanan_depan_IN1].write(0)

        self.board.digital[self.maju_kanan_belakang_IN4].write(0)
        self.board.digital[self.mundur_kanan_belakang_IN3].write(0)

        self.board.digital[self.maju_kiri_depan_IN2].write(1)
        self.board.digital[self.mundur_kiri_depan_IN1].write(0)
        
        self.board.digital[self.maju_kiri_belakang_IN3].write(1)
        self.board.digital[self.mundur_kiri_belakang_IN4].write(0)
        
    def berhenti(self, kecepatan=0.6):
        self.set_motor_speed(kecepatan, kecepatan)
        self.board.digital[self.maju_kanan_depan_IN2].write(0)
        self.board.digital[self.mundur_kanan_depan_IN1].write(0)

        self.board.digital[self.maju_kanan_belakang_IN4].write(0)
        self.board.digital[self.mundur_kanan_belakang_IN3].write(0)

        self.board.digital[self.maju_kiri_depan_IN2].write(0)
        self.board.digital[self.mundur_kiri_depan_IN1].write(0)
        
        self.board.digital[self.maju_kiri_belakang_IN3].write(0)
        self.board.digital[self.mundur_kiri_belakang_IN4].write(0)
        
        
    def exit(self):
        self.board.exit()
ar_motor = MotorController()

def scan_qr(position):
    cap = cv2.VideoCapture(1)
    start_time = time.time()
    qr_found = False
    qr_detector = cv2.QRCodeDetector()

    while True:
        ret, frame = cap.read()
    
        if ret:
            height, width = frame.shape[:2]
            retval, decoded_info, points, _ = qr_detector.detectAndDecodeMulti(frame)

            if retval:
                for s, p in zip(decoded_info, points):
                    if s:
                        frame = cv2.polylines(frame, [p.astype(int)], True, (0, 255, 0), 2)
                        
                        top_center = np.mean(p[0:2], axis=0).astype(int)
                        center = np.mean(p, axis=0).astype(int)
                        bottom_center = np.mean(p[2:4], axis=0).astype(int)
                        
                        cv2.circle(frame, tuple(top_center), 20, (0, 0, 255), -1)
                        cv2.circle(frame, tuple(center), 20, (0, 0, 255), -1)
                        cv2.circle(frame, tuple(bottom_center), 20, (0, 0, 255), -1)
                        
                        cv2.putText(frame, s, (int(p[0][0]), int(p[0][1]) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        try:
                            with open("./data/posisi_qr.json", "r") as f:
                                data = json.load(f)
                        except FileNotFoundError:
                            data = {"kiri": "", "kanan": ""}
                        
                        data[position] = s
                        with open("./data/posisi_qr.json", "w") as f:
                            json.dump(data, f)
                        qr_found = True
                        break

            if not qr_found :
                cv2.line(frame, (width // 2, 0), (width // 2, height), (255, 0, 0), 2)
                if position == "kiri":
                    print("Active : belok kiri - mencari qr")
                    ar_motor.kiri(1)
                    time.sleep(1)
                    ar_motor.berhenti()
                elif position == "kanan":
                    print("Active : belok kanan - mencari qr")
                    ar_motor.kanan(1)
                    time.sleep(1)
                    ar_motor.berhenti()
            else:
                elapsed_time = time.time() - start_time
                if position == "kiri": 
                    print("Active : belok kanan - kembali ke posisi awal selama {} detik".format(elapsed_time))
                    ar_motor.kanan(1)
                    time.sleep(elapsed_time)
                elif position == "kanan": 
                    ar_motor.kiri(1)
                    print("Active : belok kiri - kembali ke posisi awal selama {} detik".format(elapsed_time))
                    time.sleep(elapsed_time)
                break
        cv2.imshow("QR Code Scanner", frame)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


    cap.release()
    cv2.destroyAllWindows()
    ar_motor.berhenti()
    print("motor stop")
    return True

def read_object_position():
    try:
        with open('data/posisi_qr.json', 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("File data/posisi_qr.json tidak ditemukan.")
        return None
    except json.JSONDecodeError:
        print("Error saat membaca file JSON.")
        return None

def setup():
    ar_motor.capit_buka()
    ar_motor.lift_turun()

def robot_gerak():
    global ar_motor
    cap = cv2.VideoCapture(1)
    # cap.set(3, 640)
    # cap.set(4, 480)

    print(torch.cuda.get_device_name(0))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'Using device: {device}')
    
    model = YOLO('best.pt').to(device)

    classNames = ["PENJARA BIRU", "PENJARA PUTIH"]
        
    posisi_qr = read_object_position()
    posisi_qr_kiri = posisi_qr['kiri']
    posisi_qr_kanan = posisi_qr['kanan']

    KNOWN_WIDTH = 5
    FOCAL_LENGTH = 100

    tercapit = False
    posisi_awal = True

    jalan_pertama = True
    jalan_kedua = False
    jalan_ketiga = False
    jalan_keempat = False

    object_kiri_atas = ''
    object_kanan_atas = ''
    object_kiri_bawah = ''
    object_kanan_bawah = ''

    maju_duration = 0
    start_time = None
    mundur_start_time = None
    belok_kiri_start_time = None
    belok_kiri_duration = 0
    belok_kanan_start_time = None

    def distance_to_camera(knownWidth, focalLength, perWidth):
        return (knownWidth * focalLength) / perWidth

    def mencapit_orang():
        ar_motor.capit_tutup()
        ar_motor.lift_naik()

    def melepas_capit():
        ar_motor.capit_buka()
        ar_motor.lift_turun()

    def maju():
        ar_motor.maju(1)
        print("Active : maju")

    def belok_kiri():
        ar_motor.kiri(0.9)
        time.sleep(0.5)
        ar_motor.berhenti()

    ayo_stop = 0

    while True:
        success, img = cap.read()
        height, width = img.shape[:2]

        detection_height = 200
        top = (height - detection_height) // 2
        bottom = top + detection_height
        left = 0
        right = width

        detection_area = img[top:bottom, left:right]

        cv2.rectangle(img, (left, top), (right, bottom), (0, 255, 0), 2)

        results = model.predict(detection_area, stream=True)

        if jalan_pertama:
            if not tercapit:
                left_half = detection_area[:, :int(width*0.6)]
                results = model.predict(left_half, stream=True)      

                object_detected = False

                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        # confidence
                        confidence = math.ceil((box.conf[0]*100))/100
                        if confidence > 0.6:
                            # bounding box
                            x1, y1, x2, y2 = box.xyxy[0]
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) 
                            y1 += top
                            y2 += top

                            # put box in cam
                            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                            print("Confidence --->",confidence)

                            # class name
                            cls = int(box.cls[0])
                            print("Class name -->", classNames[cls])

                            # Calculate distance
                            object_width = x2 - x1
                            distance = distance_to_camera(KNOWN_WIDTH, FOCAL_LENGTH, object_width)
                            distance = round(distance, 2)

                            # object details
                            org = [x1, y1 - 30]  # Adjusted position for distance text
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            fontScale = 0.7
                            color = (255, 0, 0)
                            thickness = 2
                            cv2.putText(img, f"{classNames[cls]} {distance}cm", org, font, fontScale, color, thickness)

                            # Draw center point of the box
                            center_x = (x1 + x2) // 2
                            center_y = (y1 + y2) // 2
                            cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)

                            if object_kiri_atas == '':
                                object_kiri_atas = classNames[cls]
                                print(f"Object kiri atas: {object_kiri_atas}")
                            
                            object_detected = True
                            object_height = y2 - y1


                            if abs(center_x - width // 2) > 50 and posisi_awal == True:
                                if ayo_stop % 24 == 4:
                                    belok_kiri()
                                else:
                                    ar_motor.berhenti()
                                ayo_stop += 1
                            else:
                                ar_motor.berhenti()
                                maju()                                
                                if object_height == detection_height:
                                    mencapit_orang()
                                ar_motor.mundur()
                                time.sleep(0.8) 
                                posisi_awal = False
            else:
                # if object_kanan_atas == posisi_qr_kiri:
                #     print("masukan ke kiri")
                #     ar_motor.kiri(1)
                #     time.sleep(0.3)
                #     ar_motor.berhenti()
                #     time.sleep(5)
                #     ar_motor.maju()
                #     time.sleep(0.8)
                #     melepas_capit()
                #     ar_motor.mundur()
                #     time.sleep(0.8)
                #     ar_motor.kanan(1)
                #     time.sleep(1)
                #     posisi_awal = True
                # elif object_kanan_bawah == posisi_qr_kanan:
                #     print("masukan ke kanan")
                #     ar_motor.kanan(1)
                #     time.sleep(1.3)
                #     ar_motor.berhenti()
                #     time.sleep(5)
                #     ar_motor.maju()
                #     time.sleep(0.8)
                #     melepas_capit()
                #     ar_motor.mundur()
                #     time.sleep(0.8)
                cv2.putText(img, "Object tercapit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                jalan_pertama = False
                jalan_kedua = True
        elif jalan_kedua:
            # Add your code for jalan_kedua condition here
            pass
        elif jalan_ketiga:
            # Add your code for jalan_ketiga condition here
            pass
        elif jalan_keempat:
            # Add your code for jalan_keempat condition here
            pass

        center_x = width // 2
        cv2.line(img, (center_x, 0), (center_x, height), (0, 255, 255), 2)

        cv2.imshow('Webcam', img)
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
   

def main():
    setup()
    # scan_qr("kiri")
    # scan_qr("kanan")
    # posisi_qr = read_object_position()
    robot_gerak()


main()
