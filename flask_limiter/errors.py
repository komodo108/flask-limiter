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
        self.code = 429
        self.body = self.get_body()
        self.headers = self.get_headers()

        # Get the description
        if limit.error_message:
            description = limit.error_message if not callable(
                limit.error_message
            ) else limit.error_message()
        else:
            self.description = text_type(limit.limit)

        # If error is given, get body & headers
        if self.limit.error_code:
            self.code = limit.error_code
            exception = exceptions.HTTPException(description=description)

            # Some common error codes, can add more here	
            if self.code == 400:	
                exception = exceptions.BadRequest(description=description)
            elif self.code == 401:	
                exception = exceptions.Unauthorized(description=description)
            elif self.code == 403:	
                exception = exceptions.Forbidden(description=description)
            elif self.code == 404:	
                exception = exceptions.NotFound(description=description)
            elif self.code == 405:	
                exception = exceptions.MethodNotAllowed(description=description)
            elif self.code == 406:	
                exception = exceptions.NotAcceptable(description=description)
            elif self.code == 418:	
                exception = exceptions.ImATeapot(description=description) # <3	
            elif self.code == 500:	
                exception = exceptions.InternalServerError(description=description)
            elif self.code == 501:	
                exception = exceptions.NotImplemented(description=description)

            # Update body & headers
            self.body = exception.get_body()
            self.headers = exception.get_headers()
        else:
            exception = exceptions.TooManyRequests(description=description)
            
            # Update body & headers
            self.body = exception.get_body()
            self.headers = exception.get_headers()
        super(RateLimitExceeded, self).__init__(description=self.description, response=Response(self.body, code, self.headers))
