from enum import Enum

class NewsStatus(Enum):
    FETCH_NEWS='FETCH_NEWS'
    EDITED_NEWS = 'EDITED_NEWS'
    LIVE_NEWS = 'LIVE_NEWS'
    # INACTIVE = 'INACTIVE'