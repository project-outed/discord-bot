from enum import Enum

class ConsoleLevel(Enum):
    INFO = ("INFO", "\033[34m")
    SUCCESS = ("SUCCESS", "\033[32m")
    WARNING = ("WARNING", "\033[33m")
    ERROR = ("ERROR", "\033[31m")
    DEBUG = ("DEBUG", "\033[36m")
    DEFAULT = ("LOG", "\033[35m")