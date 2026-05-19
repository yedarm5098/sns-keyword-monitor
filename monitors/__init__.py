from dataclasses import dataclass
from datetime import datetime


@dataclass
class Post:
    platform:   str
    author:     str
    text:       str
    url:        str
    keyword:    str
    created_at: datetime
