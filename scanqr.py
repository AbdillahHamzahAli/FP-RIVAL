import cv2
import numpy as np
import json
import time
import motor

def scan_qr(position):
    ar_motor = motor.MotorController()
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
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
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

            if not qr_found:
                cv2.line(frame, (width // 2, 0), (width // 2, height), (255, 0, 0), 2)
                if position == "kiri":
                    print("Active : belok kiri - mencari qr")
                    ar_motor.kiri(0.6)
                elif position == "kanan":
                    print("Active : belok kanan - mencari qr")
                    ar_motor.kanan(0.6)
            else:
                break

            cv2.imshow("QR Code Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if qr_found:
        elapsed_time = time.time() - start_time
        if position == "kiri":
            print("Active : belok kanan - kembali ke posisi awal selama {} detik".format(elapsed_time))
            ar_motor.kanan(0.6)
            time.sleep(elapsed_time)
        elif position == "kanan":
            ar_motor.kiri(0.6)
            print("Active : belok kiri - kembali ke posisi awal selama {} detik".format(elapsed_time))
            time.sleep(elapsed_time)

    cap.release()
    cv2.destroyAllWindows()
    ar_motor.berhenti()
    print("motor stop")
    return True

if __name__ == "__main__":
    scan_qr("kiri")