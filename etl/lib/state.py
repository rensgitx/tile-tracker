from enum import Enum


class State(Enum):
    SETTLE = "Settle"
    UNSETTLE = "Unsettle"
    UNKNOWN = "Unknown"
    PENDING = "Pending"
