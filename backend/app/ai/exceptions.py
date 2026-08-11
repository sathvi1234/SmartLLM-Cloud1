class AIProviderException(Exception):
    def __init__(self, message: str, provider: str, status_code: int = 500):
        self.message = message
        self.provider = provider
        self.status_code = status_code
        super().__init__(self.message)

class AIRateLimitException(AIProviderException):
    pass

class AITimeoutException(AIProviderException):
    pass
