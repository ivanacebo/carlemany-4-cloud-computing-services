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


# Raised when the file storage cannot serve a request at all: it is unreachable, the bucket
# is not there, or the credentials are refused. Kept apart from FileNotFoundException for
# the same reason TokenStorageUnavailable is kept apart from TokenNotFound: "the content is
# not there" and "I cannot tell whether it is there" are different answers, and only the
# first one is the file's fault. It also keeps the minio exceptions from reaching callers.
class FileStorageUnavailableException(Exception):
    pass
