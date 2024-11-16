import motor
import time
ar_motor = motor.MotorController()



while True:
    ar_motor.capit_tutup()
    time.sleep(1)
    ar_motor.lift_naik()
    time.sleep(1)