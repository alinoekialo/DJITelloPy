import logging
import numpy as np
from djitellopy import Tello, State
import cv2
import pygame
from pygame.locals import USEREVENT, KEYDOWN, K_ESCAPE
import time

from djitellopy.game_events import GameEvents

log = logging.getLogger()
FPS = 25


class Drone:
    SEARCH_TIMEOUT = 10 * 1000

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Tello video stream")
        self.screen = pygame.display.set_mode([960, 720])

        self.tello = Tello()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.command_queue = []
        self.shutdown = False
        self.should_stop = False

        # create update timer
        pygame.time.set_timer(USEREVENT + 1, 50)
        self.tello.state = State.initializing

    def flip(self, direction='b'):
        for event in pygame.event.get():
            if event.type == GameEvents.VIDEO_EVENT.value:
                log.info('Flipping')
                self.tello.state = State.flipping
                self.tello.flip(direction)
                log.info('Idle')
                self.tello.state = State.idle

    def fly(self):
        if not self.tello.connect():
            print("Tello not connected")
            return

        if not self.tello.set_speed(self.speed):
            print("Not set speed to lowest possible")
            return
        # In case streaming is on. This happens when we quit this program without the escape key.
        if not self.tello.streamoff():
            print("Could not stop video stream")
            return

        if not self.tello.streamon():
            print("Could not start video stream")
            return
        frame_read = self.tello.get_frame_read()
        time.sleep(2)
        self.tello.takeoff()
        if self.tello.state is State.initializing:
            self.tello.state = State.yawing
            self.yaw_velocity = 100
        while not self.should_stop:
            for event in pygame.event.get():
                if event.type == USEREVENT + 1:
                    if (self.tello.state is State.initializing or
                            self.tello.state is State.yawing or
                            self.tello.state is State.idle):
                        self.update()
                if event.type == GameEvents.VIDEO_EVENT.value:
                    if self.tello.state is State.yawing:
                        self.yaw_velocity = 0
                        self.tello.state = State.idle
                    elif self.tello.state is State.idle:
                        self.flip()
                elif event.type == KEYDOWN:
                    self.should_stop = True
                    # if event.key == K_ESCAPE:
                    #     log.info('Landing')
                    #     self.tello.land()
                    #     break
            if frame_read.stopped:
                frame_read.stop()
                break

            self.screen.fill([0, 0, 0])
            frame = cv2.cvtColor(frame_read.frame, cv2.COLOR_BGR2RGB)
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = pygame.surfarray.make_surface(frame)
            self.screen.blit(frame, (0, 0))
            pygame.display.update()

            time.sleep(1 / FPS)

        self.tello.end()

    def update(self):
        """ Update routine. Send velocities to Tello."""
        if self.tello.state is not State.flipping:
            self.tello.send_rc_control(
                self.left_right_velocity, self.for_back_velocity,
                self.up_down_velocity, self.yaw_velocity)


if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    drone = Drone()
    drone.fly()
