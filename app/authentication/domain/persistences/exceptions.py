class WrongPasswordException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class UsernameAlreadyTakenException(Exception):
    pass


class TokenNotFound(Exception):
    pass


# Raised when the token store cannot be reached, so whether a token exists is unknown.
# Kept apart from TokenNotFound on purpose: mapping an outage onto "this token does not
# exist" would log every user out during the outage, and would report a successful logout
# while deleting nothing. It also keeps the redis exceptions from reaching the callers,
# which is the whole point of TokenInterface.
class TokenStorageUnavailable(Exception):
    pass
