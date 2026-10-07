class LaunchLensError(Exception):
    """Expected error displayed without a traceback."""

class SourceError(LaunchLensError):
    pass

class ConfigurationError(LaunchLensError):
    pass

class APIError(LaunchLensError):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code

class ResponseError(LaunchLensError):
    pass