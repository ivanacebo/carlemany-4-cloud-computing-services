class FileNotFoundException(Exception):
    pass


# Raised by FileBOInterface, for missing metadata. FileNotFoundException above
# belongs to FileStorageInterface and means the content is missing from the
# storage: a stored file can have metadata and no content yet.
class FileBONotFoundException(Exception):
    pass
