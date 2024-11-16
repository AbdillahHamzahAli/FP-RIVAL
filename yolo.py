def main():
    global ar_motor
    # start webcam
    cap = cv2.VideoCapture(1)
    # cap.set(3, 640)
    # cap.set(4, 480)

    print(torch.cuda.get_device_name(0))
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f'Using device: {device}')
    model = YOLO('best.pt').to(device)

    classNames = ["PENJARA BIRU", "PENJARA PUTIH"]

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

    def distance_to_camera(knownWidth, focalLength, perWidth):
        return (knownWidth * focalLength) / perWidth

    def belok_kiri():
        ar_motor.kiri()

    def belok_kanan():
        ar_motor.kanan()

    def maju():
        ar_motor.maju()

    def mundur():
        ar_motor.mundur()

    def berhenti():
        ar_motor.mundur()

    def capit():
        ar_motor.capit_tutup()
        ar_motor.lift_naik()

    def read_object_position():
        try:
            with open('data/posisi_qr.json', 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print("File data/posisi_object.json tidak ditemukan.")
            return None
        except json.JSONDecodeError:
            print("Error saat membaca file JSON.")
            return None

    posisi_qr = read_object_position()

    posisi_qr_kiri = posisi_qr['kiri']
    posisi_qr_kanan = posisi_qr['kanan']

    ar_motor.capit_buka()

    pas = False
    maju_start_time = None
    mundur_duration = 0
    belok_kanan_duration = 0

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
                # coordinates
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        # confidence
                        confidence = math.ceil((box.conf[0]*100))/100
                        if confidence > 0.8:
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

                            # Save the first detected object on the left side to object_kiri_atas
                            if object_kiri_atas == '':
                                object_kiri_atas = classNames[cls]
                                print(f"Object kiri atas: {object_kiri_atas}")
                            
                            object_detected = True
                            object_height = y2 - y1
                            if abs(center_x - width // 2) > 5 and posisi_awal == True:
                                belok_kiri()
                                belok_kanan_duration += 1/30
                            else:
                                if (distance < 240 and 1.5 * object_height <= object_width <= 2 * object_height) or object_detected == False:
                                    berhenti()
                                    capit() 
                                    tercapit = True
                                    mundur_duration = time.time() - maju_start_time if maju_start_time else 0
                                    maju_start_time = None
                                else:
                                    maju()
                                    posisi_awal = False
                                    if maju_start_time is None:
                                        maju_start_time = time.time()
                while mundur_duration > 0:
                    mundur()
                    mundur_duration -= 1/30

                if mundur_duration <= 0:
                    mundur_duration = 0
                    while belok_kanan_duration > 0:
                        belok_kanan()
                        belok_kanan_duration -= 1/30
                    belok_kanan_duration = 0
                
                if object_kiri_atas == posisi_qr_kiri:
                    print('masukan ke kiri')

                if object_kiri_atas == posisi_qr_kanan:
                    print('masukan ke kanan')

                cv2.putText(img, "Object tercapit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        elif jalan_kedua:
            right_75_percent = detection_area[:, int(width*0.25):]
            results = model.predict(right_75_percent, stream=True)

            object_detected = False
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    confidence = math.ceil((box.conf[0]*100))/100
                    if confidence > 0.8:
                        x1, y1, x2, y2 = box.xyxy[0]
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                        x1 += int(width*0.25)  # Adjust x-coordinates
                        x2 += int(width*0.25)
                        y1 += top
                        y2 += top

                        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                        cls = int(box.cls[0])
                        object_width = x2 - x1
                        distance = distance_to_camera(KNOWN_WIDTH, FOCAL_LENGTH, object_width)
                        distance = round(distance, 2)

                        cv2.putText(img, f"{classNames[cls]} {distance}cm", (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

                        center_x = (x1 + x2) // 2
                        center_y = (y1 + y2) // 2
                        cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)

                        if object_kanan_atas == '':
                            object_kanan_atas = classNames[cls]
                            print(f"Object kanan atas: {object_kanan_atas}")

                        object_detected = True
                        object_height = y2 - y1

                        if abs(center_x - (width * 0.625)) > 5:  # 62.5% of width (middle of right 75%)
                            if center_x < (width * 0.625):
                                belok_kiri()
                            else:
                                belok_kanan()
                        else:
                            if (distance < 240 and 1.5 * object_height <= object_width <= 2 * object_height) or not object_detected:
                                berhenti()
                                capit()
                                tercapit = True
                            else:
                                maju()

            if not object_detected:
                berhenti()
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

if __name__ == "__main__":
    main()
