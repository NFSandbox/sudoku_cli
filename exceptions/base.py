class BaseError(Exception):
    def __init__(self, name: str, message: str) -> None:
        self.name = name
        self.message = message

    def __repr__(self) -> str:
        return f"{self.message} ({self.name})"
