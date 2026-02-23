from enum import Enum

class IsPublish(Enum):
    NOT_PUBLISHED = "NOT_PUBLISHED"
    PUBLISHED = "PUBLISHED"

    def __str__(self):
        return self.value
