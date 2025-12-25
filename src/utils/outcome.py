from enum import Enum

class ScrapeOutcome(Enum):
    SUCCESS = "SUCCESS"
    EMPTY = "EMPTY"
    RESTRICTED = "RESTRICTED"
