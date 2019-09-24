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
        self.tello.connect()
        self.tello.takeoff()

        # Drone velocities between -100~100
        self.for_back_velocity = 0
        self.left_right_velocity = 0
        self.up_down_velocity = 0
        self.yaw_velocity = 0
        self.speed = 10

        self.command_queue = []
        self.shutdown = False

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
        frame_read = self.tello.get_frame_read()
        while True:
            if self.tello.state is State.initializing:
                log.info('Starting yaw')
                self.tello.state = State.yawing
                self.yaw_velocity = 50
            for event in pygame.event.get():
                if event.type == USEREVENT + 1:
                    self.update()
                if self.tello.state is State.yawing:
                    if event.type == GameEvents.VIDEO_EVENT.value:
                        self.yaw_velocity = 0
                        self.flip()
                elif self.tello.state is State.idle:
                    self.flip('f')
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        log.info('Landing')
                        self.tello.land()
                        break

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
