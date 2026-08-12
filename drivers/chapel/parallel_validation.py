""" Validate that code snippets are using the correct parallelism model for
    Chapel programs. Covers OpenMP, and MPI.
    author: Adapted from Daniel Nichols' C++ validation
    date: June 2025
"""
# std imports
from abc import ABC, abstractmethod


class Validator(ABC):
    parallelism_model: str

    def __init__(self, parallelism_model: str):
        self.parallelism_model = parallelism_model

    @abstractmethod
    def validate(self, source: str) -> bool:
        """ Validate that the given source is using the correct parallelism model. """
        raise NotImplementedError("validate() not implemented for this validator.")

    def must_contain(self, source: str, substr: str) -> bool:
        """ Check if the given source contains the given substring. """
        return substr in source


class ChapelOMPValidator(Validator):

    def __init__(self):
        super().__init__("omp")

    """ Validate that the given source uses OpenMP in Chapel. """
    def validate(self, source: str) -> bool:
        # Chapel uses begin/cobegin for parallelism or pragmas
        return (self.must_contain(source, "cobegin") or 
                self.must_contain(source, "begin") or
                self.must_contain(source, "#pragma omp"))


class ChapelMPIValidator(Validator):
    
    def __init__(self):
        super().__init__("mpi")

    """ Validate that the given source uses MPI in Chapel. """
    def validate(self, source: str) -> bool:
        # Chapel MPI would use Comm module or explicit MPI calls
        return (self.must_contain(source, "use Comm") or 
                self.must_contain(source, "Comm.") or
                self.must_contain(source, "MPI_") or
                self.must_contain(source, "MPI."))


class ChapelMPIandOMPValidator(Validator):
    
    def __init__(self):
        super().__init__("mpi+omp")
        self.mpi_validator = ChapelMPIValidator()
        self.omp_validator = ChapelOMPValidator()

    """ Validate that the given source uses MPI and OpenMP in Chapel. """
    def validate(self, source: str) -> bool:
        return self.mpi_validator.validate(source) and self.omp_validator.validate(source)


class ChapelEmptyValidator(Validator):

    def __init__(self):
        super().__init__("empty")

    """ Always returns true. """
    def validate(self, source: str) -> bool:
        return True
