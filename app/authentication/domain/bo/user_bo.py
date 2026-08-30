from dataclasses import dataclass
from typing import Optional


@dataclass
class UserBO:
    username: str
    password: str
    mail: str
    year_of_birth: Optional[int] = None
    external_id: Optional[int] = None
