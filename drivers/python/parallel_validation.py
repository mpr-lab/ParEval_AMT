""" Validate that Python code snippets are using the correct parallelism model. """
from abc import ABC, abstractmethod


class Validator(ABC):
    @abstractmethod
    def validate(self, source: str) -> bool:
        raise NotImplementedError

    def must_contain(self, source: str, substr: str) -> bool:
        return substr in source


class Charm4PyValidator(Validator):
    def validate(self, source: str) -> bool:
        return self.must_contain(source, "charm4py") or self.must_contain(source, "charm")


class PythonSerialValidator(Validator):
    def validate(self, source: str) -> bool:
        return True
