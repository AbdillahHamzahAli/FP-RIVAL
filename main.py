import scanqr
import json
import motor


qr_kiri_ditemukan = False
qr_kanan_ditemukan = False

orang_kiri_atas = False;



def read_object_position():
    try:
        with open('data/posisi_object.json', 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("File data/posisi_object.json tidak ditemukan.")
        return None
    except json.JSONDecodeError:
        print("Error saat membaca file JSON.")
        return None


def main():
    global qr_kiri_ditemukan
    global qr_kanan_ditemukan

#    ar_motor =  motor.MotorController()
#    ar_motor.lift_turun()

    if not qr_kiri_ditemukan:
        qr_kiri_ditemukan = scanqr.main("kiri")
    if not qr_kanan_ditemukan:
        qr_kanan_ditemukan = scanqr.main("kanan")


if __name__ == "__main__":
    main()