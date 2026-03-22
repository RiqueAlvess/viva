from fastapi import HTTPException, status


class VivaException(Exception):
    """Base exception for VIVA application."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(VivaException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found", status_code=404)


class UnauthorizedError(VivaException):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenError(VivaException):
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message, status_code=403)


class ConflictError(VivaException):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)


class ValidationError(VivaException):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=422)


class BusinessRuleError(VivaException):
    def __init__(self, message: str = "Business rule violation"):
        super().__init__(message, status_code=400)


# HTTP exceptions shortcuts
def raise_not_found(resource: str = "Resource"):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")


def raise_forbidden(message: str = "Access forbidden"):
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def raise_unauthorized(message: str = "Unauthorized"):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


def raise_conflict(message: str = "Resource already exists"):
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=message)


def raise_bad_request(message: str = "Bad request"):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
