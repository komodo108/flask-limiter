"""
errors and exceptions
"""

from distutils.version import LooseVersion
from pkg_resources import get_distribution
from six import text_type
from werkzeug import exceptions

werkzeug_exception = None
werkzeug_version = get_distribution("werkzeug").version
if LooseVersion(werkzeug_version) < LooseVersion("0.9"):  # pragma: no cover
    # sorry, for touching your internals :).
    import werkzeug._internal
    werkzeug._internal.HTTP_STATUS_CODES[429] = 'Too Many Requests'
    werkzeug_exception = exceptions.HTTPException
else:
    # Werkzeug 0.9 and up have an existing exception for 429
    werkzeug_exception = exceptions.TooManyRequests


class RateLimitExceeded(werkzeug_exception):
    """
    exception raised when a rate limit is hit.
    The exception results in ``abort(limit.error_code)`` being called.
    """
    code = 429
    callclass = exceptions.TooManyRequests
    limit = None

    def __init__(self, limit):
        self.limit = limit
        if limit.error_code:
            code = limit.error_code

            # Some common error codes, can add more here
            if code == 400:
                callclass = exceptions.BadRequest
            elif code == 401:
                callclass = exceptions.Unauthorized
            elif code == 403:
                callclass = exceptions.Forbidden
            elif code == 404:
                callclass = exceptions.NotFound
            elif code == 405:
                callclass = exceptions.MethodNotAllowed
            elif code == 406:
                callclass = exceptions.NotAcceptable
            elif code == 418:
                callclass = exceptions.ImATeapot # <3

            # Generic if not given
            else:
                callclass = exceptions.HTTPException

        if limit.error_message:
            description = limit.error_message if not callable(
                limit.error_message
            ) else limit.error_message()
        else:
            description = text_type(limit.limit)

        super(RateLimitExceeded, self).__init__(description=description)
