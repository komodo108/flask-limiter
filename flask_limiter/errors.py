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

        # Set defaults
        code = 429
        exception = exceptions.TooManyRequests
        body = self.get_body()
        headers = self.get_headers()

        # If error is given, get body & headers
        if limit.error_code:
            code = limit.error_code
            exception = exceptions.HTTPException

            # Some common error codes, can add more here	
            if code == 400:	
                exception = exceptions.BadRequest
            elif code == 401:	
                exception = exceptions.Unauthorized	
            elif code == 403:	
                exception = exceptions.Forbidden	
            elif code == 404:	
                exception = exceptions.NotFound	
            elif code == 405:	
                exception = exceptions.MethodNotAllowed	
            elif code == 406:	
                exception = exceptions.NotAcceptable	
            elif code == 418:	
                exception = exceptions.ImATeapot # <3	
            elif code == 500:	
                exception = exceptions.InternalServerError	
            elif code == 501:	
                exception = exceptions.NotImplemented	

            # Update body & headers
            body = exception().get_body()
            headers = exception().get_headers()

        # Get the description
        if limit.error_message:
            description = limit.error_message if not callable(
                limit.error_message
            ) else limit.error_message()
        else:
            description = text_type(limit.limit)
        super(RateLimitExceeded, self).__init__(description=description, response=Response(self.get_body(), code, self.get_headers()))
