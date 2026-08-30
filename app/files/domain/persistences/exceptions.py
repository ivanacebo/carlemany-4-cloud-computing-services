class FileNotFoundException(Exception):
    pass


# Raised by FileBOInterface, for missing metadata. FileNotFoundException above
# belongs to FileStorageInterface and means the content is missing from the
# storage: a stored file can have metadata and no content yet.
class FileBONotFoundException(Exception):
    pass


# Raised when an authenticated user acts on a file owned by somebody else. Kept
# apart from FileBONotFoundException so that the API layer stays free to answer
# either "forbidden" or "not found": merging them would take that decision here.
class FileOwnershipException(Exception):
    pass


# Raised when an operation needs the content of a file that only exists as metadata,
# because it was created by POST /files and never uploaded. Distinct from
# FileNotFoundException, which means the content was expected in the storage and is not
# there: here it was never put there at all, so the API can answer "conflict" rather than
# reporting a storage failure.
class FileContentNotUploadedException(Exception):
    pass
