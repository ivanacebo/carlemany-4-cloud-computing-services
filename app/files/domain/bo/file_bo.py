from dataclasses import dataclass
from typing import Optional


@dataclass
class FileBO:
    title: str
    author: str
    owner_external_id: int
    # Identifier of the file content in the storage, assigned when the content is
    # uploaded. A file exists as metadata before it has any content.
    remote_identifier: Optional[str] = None
    external_id: Optional[int] = None

    def is_owned_by(self, external_id: int) -> bool:
        return self.owner_external_id == external_id
