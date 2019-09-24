from enum import Enum
from pygame.locals import USEREVENT


class GameEvents(Enum):
    VIDEO_EVENT = USEREVENT + 2
