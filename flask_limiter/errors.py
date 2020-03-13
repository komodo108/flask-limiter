"""
errors and exceptions
"""

from distutils.version import LooseVersion
from pkg_resources import get_distribution
from six import text_type
from werkzeug import exceptions

werkzeug_exception = None
internal_code = 429
werkzeug_version = get_distribution("werkzeug").version
if LooseVersion(werkzeug_version) < LooseVersion("0.9"):  # pragma: no cover
    # sorry, for touching your internals :).
    import werkzeug._internal
    werkzeug._internal.HTTP_STATUS_CODES[429] = 'Too Many Requests'
    werkzeug_exception = exceptions.HTTPException
else:
    # Werkzeug 0.9 and up have an existing exception for 429
    werkzeug_exception = exceptions.HTTPException

class RateLimitExceededInternal():
    limit = None

    def __init__(self, limit):
        self.limit = limit
        if limit.error_code:
            internal_code = limit.error_code

            # Some common error codes, can add more here
            if internal_code == 400:
                werkzeug_exception = exceptions.BadRequest
            elif internal_code == 401:
                werkzeug_exception = exceptions.Unauthorized
            elif internal_code == 403:
                werkzeug_exception = exceptions.Forbidden
            elif internal_code == 404:
                werkzeug_exception = exceptions.NotFound
            elif internal_code == 405:
                werkzeug_exception = exceptions.MethodNotAllowed
            elif internal_code == 406:
                werkzeug_exception = exceptions.NotAcceptable
            elif internal_code == 418:
                werkzeug_exception = exceptions.ImATeapot # <3
            elif internal_code == 500:
                werkzeug_exception = exceptions.InternalServerError
            elif internal_code == 501:
                werkzeug_exception = exceptions.NotImplemented

            # Generic if not given
            else:
                werkzeug_exception = exceptions.HTTPException

        if limit.error_message:
            description = limit.error_message if not callable(
                limit.error_message
            ) else limit.error_message()
        else:
            description = text_type(limit.limit)
        raise RateLimitExceeded(description)



class RateLimitExceeded(werkzeug_exception):
    """
    exception raised when a rate limit is hit.
    The exception results in ``abort(limit.error_code)`` being called.
    """
    code = internal_code

    def __init__(self, description):
        super(RateLimitExceeded, self).__init__(description=description)
