"""Excepciones de negocio que la UI traduce a mensajes para el usuario."""


class InventarioError(Exception):
    """Base de todas las excepciones de negocio de la aplicación."""


class ValidacionError(InventarioError):
    """Un dato de entrada no cumple las reglas (formato, obligatorio, etc.)."""


class EmailDuplicadoError(InventarioError):
    """Ya existe un usuario con ese email."""


class UsuarioNoEncontradoError(InventarioError):
    """No existe un usuario con el email indicado."""


class ArticuloNoEncontradoError(InventarioError):
    """No existe un artículo con el ID indicado."""


class IntegridadReferencialError(InventarioError):
    """La operación rompería una referencia entre colecciones (RESTRICT)."""

    def __init__(self, mensaje: str, referencias: int) -> None:
        """Guarda cuántos documentos dependen del registro afectado."""
        super().__init__(mensaje)
        self.referencias = referencias
