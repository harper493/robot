from IMU import IMU
from threading import Thread

@dataclass
class ImuData:
    pitch: float
    roll: float
    yaw: float

class Imu:

    the_imu: Imu = None

    def __init__(self, interval=0.1):
        self.interval = interval
        self.my_imu = IMU()
        self.my_thread = Thread(target=imu.run)
        self.data = ImuData()

    @staticmethod
    def run():
        while True:
            self.data = ImuData(*my_imu.imuUpdate())
            time.sleep(self.interval)

    @staticmethod
    def get():
        return (Imu.the_imu.pitch, Imu.the_imu.roll, Imu.the_imu.yaw)

    @staticmethod
    def init():
        Imu.the_imu = Imu()

    
