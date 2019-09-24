from time import sleep
from djitellopy import Tello


class DroneActions:
    def __init__(self):
        self.tello = Tello()
        self.tello.connect()
        sleep(2)

    def takeoff(self):
        self.tello.takeoff()
        while self.tello.get_h() < 30:
            sleep(0.5)

    def land(self):
        self.tello.land()

    def execute(self, command):
        self.send_control_command(*command)

    def set_velocity(self, values):
        self.tello.send_rc_control(*values)

    def find_pink(self):
        self.set_velocity([0, 0, 0, 100])
        sleep(2)
        self.set_velocity([0, 0, 0, 0])

    def choreo(self):
        self.takeoff()
        self.find_pink()
        self.land()


