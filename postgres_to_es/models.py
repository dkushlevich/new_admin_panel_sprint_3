import uuid
from dataclasses import dataclass, field
from typing import Literal


@dataclass
class FilmWork:
    fw_id: uuid
    title: str
    description: str
    full_name: str
    id: uuid
    name: str
    role: Literal["actor", "director", "writer"]
    rating: float = field(default=0.0)
