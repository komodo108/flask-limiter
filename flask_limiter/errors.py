"""
errors and exceptions
"""

from distutils.version import LooseVersion
from pkg_resources import get_distribution
from six import text_type
from werkzeug import exceptions, Response

werkzeug_exception = None
werkzeug_version = get_distribution("werkzeug").version
if LooseVersion(werkzeug_version) < LooseVersion("0.9"):  # pragma: no cover
    # sorry, for touching your internals :).
    import werkzeug._internal
    werkzeug._internal.HTTP_STATUS_CODES[429] = 'Too Many Requests'
    werkzeug_exception = exceptions.HTTPException
else:
    werkzeug_exception = exceptions.HTTPException

class RateLimitExceeded(werkzeug_exception):
    """
    exception raised when a rate limit is hit.
    The exception results in ``abort(limit.error_code)`` being called.
    """
    limit = None

    def __init__(self, limit):
        self.limit = limit

        code = 429
        exception = exceptions.TooManyRequests

        if limit.error_code:
            code = limit.error_code
            exception = exceptions.HTTPException

        if limit.error_message:
            description = limit.error_message if not callable(
                limit.error_message
            ) else limit.error_message()
        else:
            description = text_type(limit.limit)
        super(RateLimitExceeded, self).__init__(description=description, response=Response(self.get_body(), code, self.get_headers()))
