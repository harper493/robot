from IMU import IMU
from threading import Thread

class imu:

    def __init__(self, interval=0.1):
        self.interval = interval
        self.my_imu = IMU()
        self.my_thread = Thread(target=imu.run)
        self.pitch, self.roll, self.yaw = 0.0, 0.0, 0.0

    @staticmethod
    def run():
        while True:
            self.pitch, self.roll, self.yaw = my_imu.imuUpdate()
            time.sleep(self.interval)

    
