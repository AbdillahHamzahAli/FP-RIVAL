from pyfirmata2 import Arduino, SERVO
import time

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

    def maju(self, kecepatan=0.5):
        self.set_motor_speed(kecepatan, kecepatan)
        self.board.digital[self.maju_kanan_depan_IN2].write(1)
        self.board.digital[self.mundur_kanan_depan_IN1].write(0)

        self.board.digital[self.maju_kanan_belakang_IN4].write(1)
        self.board.digital[self.mundur_kanan_belakang_IN3].write(0)

        self.board.digital[self.maju_kiri_depan_IN2].write(1)
        self.board.digital[self.mundur_kiri_depan_IN1].write(0)
        
        self.board.digital[self.maju_kiri_belakang_IN3].write(1)
        self.board.digital[self.mundur_kiri_belakang_IN4].write(0)

    def mundur(self, kecepatan=0.5):
        self.set_motor_speed(kecepatan, kecepatan)
        self.board.digital[self.maju_kanan_depan_IN2].write(0)
        self.board.digital[self.mundur_kanan_depan_IN1].write(1)

        self.board.digital[self.maju_kanan_belakang_IN4].write(0)
        self.board.digital[self.mundur_kanan_belakang_IN3].write(1)

        self.board.digital[self.maju_kiri_depan_IN2].write(0)
        self.board.digital[self.mundur_kiri_depan_IN1].write(1)
        
        self.board.digital[self.maju_kiri_belakang_IN3].write(0)
        self.board.digital[self.mundur_kiri_belakang_IN4].write(1)
        
    def kiri(self, kecepatan=0.5):
        self.set_motor_speed(kecepatan, kecepatan)
        self.board.digital[self.maju_kanan_depan_IN2].write(1)
        self.board.digital[self.mundur_kanan_depan_IN1].write(0)

        self.board.digital[self.maju_kanan_belakang_IN4].write(1)
        self.board.digital[self.mundur_kanan_belakang_IN3].write(0)

        self.board.digital[self.maju_kiri_depan_IN2].write(0)
        self.board.digital[self.mundur_kiri_depan_IN1].write(1)
        
        self.board.digital[self.maju_kiri_belakang_IN3].write(0)
        self.board.digital[self.mundur_kiri_belakang_IN4].write(1)
        
    def kanan(self, kecepatan=0.9):
        self.set_motor_speed(kecepatan, kecepatan)
        self.board.digital[self.maju_kiri_depan_IN2].write(1)
        self.board.digital[self.mundur_kiri_depan_IN1].write(0)
        
        self.board.digital[self.maju_kiri_belakang_IN3].write(1)
        self.board.digital[self.mundur_kiri_belakang_IN4].write(0)

        self.board.digital[self.maju_kanan_depan_IN2].write(0)
        self.board.digital[self.mundur_kanan_depan_IN1].write(1)

        self.board.digital[self.maju_kanan_belakang_IN4].write(0)
        self.board.digital[self.mundur_kanan_belakang_IN3].write(1)
        
    def berhenti(self, kecepatan=0.5):
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

if __name__ == "__main__":
    motor = MotorController()
    motor.lift_turun()
    motor.capit_tutup()
    
    try:
        i = 0
        while True:
            motor.maju(0.5)
            time.sleep(2)
            motor.berhenti()
            time.sleep(3)
            # if i % 2 == 0:
            #     print("jalan")
            #     motor.maju(1)
            # else:
            #     motor.berhenti()
            # i += 1
    except KeyboardInterrupt:
        motor.exit()