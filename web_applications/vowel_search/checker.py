from flask import session
from functools import wraps


def check_logged_in(func) -> 'func':
    """
    Check user session if he/she is logged in. If he is, return the decorated
    function, if not then return string 'You are NOT logged in.'
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        This wrapper not only invokes the decorated function, but also
        augments it by wrapping extra code around the call. In this case,
        the extra code is checking to see if the logged_in key exists
        within your webapp’s session. Critically, if the user’s browser is
        not logged in, the decorated function is never invoked by wrapper.
        """
        if 'logged_in' in session:
            return func(*args, **kwargs)
        return 'You are NOT logged in.'

    return wrapper
