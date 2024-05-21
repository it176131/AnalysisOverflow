from functools import wraps


def check_user_ids(method):
    """
    Decorator function that sets `ids` to the User's ID if not included.
    """
    @wraps(method)
    def wrapper(ref, user_ids=None):
        if user_ids is None:
            user_ids = [ref.user_id]

        return method(ref, user_ids)

    return wrapper
