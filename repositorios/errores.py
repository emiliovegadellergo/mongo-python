"""Errores de la capa de datos, independientes de pymongo.

Las capas superiores capturan estas excepciones en lugar de las de pymongo,
de modo que solo los repositorios conocen el driver.
"""

from contextlib import contextmanager
from typing import Iterator

from pymongo.errors import DuplicateKeyError, PyMongoError


class ErrorPersistencia(Exception):
    """Falla genérica al comunicarse con la base de datos."""


class ClaveDuplicadaError(ErrorPersistencia):
    """Se violó un índice único."""


@contextmanager
def traducir_errores() -> Iterator[None]:
    """Convierte las excepciones de pymongo en errores de persistencia."""
    try:
        yield
    except DuplicateKeyError as error:
        raise ClaveDuplicadaError(str(error)) from error
    except PyMongoError as error:
        raise ErrorPersistencia(str(error)) from error
