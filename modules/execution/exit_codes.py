from enum import IntEnum


class ExitCode(IntEnum):
    OK = 0
    ERROR = -1
    INF_RECURSION = -2
    MANUAL_TERMINATION = -3
    
    RESTART = 10
    RESTART_SAVE_MEMORY = 11

