"""Reglas de negocio de usuarios."""

import re
from typing import List, Optional

from modelos.usuario import Usuario
from repositorios.articulo_repositorio import ArticuloRepositorio
from repositorios.errores import ClaveDuplicadaError
from repositorios.usuario_repositorio import UsuarioRepositorio
from servicios.excepciones import (EmailDuplicadoError,
                                   IntegridadReferencialError,
                                   UsuarioNoEncontradoError, ValidacionError)

# Validación básica: algo@algo.dominio, sin espacios.
_PATRON_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalizar_email(email: str) -> str:
    """Quita espacios y pasa a minúsculas para evitar duplicados aparentes."""
    return email.strip().lower()


def validar_email(email: str) -> str:
    """Normaliza y valida el email; devuelve la versión normalizada.

    Raises:
        ValidacionError: si está vacío o no tiene formato de email.
    """
    normalizado = normalizar_email(email)
    if not normalizado:
        raise ValidacionError("El email es obligatorio.")
    if not _PATRON_EMAIL.match(normalizado):
        raise ValidacionError(f"'{normalizado}' no es un email válido.")
    return normalizado


class UsuarioServicio:
    """Casos de uso del módulo de usuarios."""

    def __init__(self, usuarios: UsuarioRepositorio,
                 articulos: ArticuloRepositorio) -> None:
        """Recibe los repositorios; artículos se usa para la regla RESTRICT."""
        self._usuarios = usuarios
        self._articulos = articulos

    def crear(self, email: str, nombre: str, apellido: str) -> Usuario:
        """Registra un usuario nuevo.

        Raises:
            ValidacionError: email vacío o mal formado.
            EmailDuplicadoError: el email ya está registrado.
        """
        email = validar_email(email)
        # Primera barrera: mensaje claro antes de intentar insertar.
        if self._usuarios.existe(email):
            raise EmailDuplicadoError(
                f"Ya existe un usuario con el email {email}.")
        usuario = Usuario(email=email, nombre=nombre.strip(),
                          apellido=apellido.strip())
        try:
            return self._usuarios.insertar(usuario)
        except ClaveDuplicadaError as error:
            # Segunda barrera: otro proceso lo insertó entre la verificación
            # y la inserción; el índice único lo detecta.
            raise EmailDuplicadoError(
                f"Ya existe un usuario con el email {email}.") from error

    def obtener(self, email: str) -> Usuario:
        """Busca un usuario por email.

        Raises:
            ValidacionError: email mal formado.
            UsuarioNoEncontradoError: no existe.
        """
        email = validar_email(email)
        usuario = self._usuarios.buscar_por_email(email)
        if usuario is None:
            raise UsuarioNoEncontradoError(
                f"No existe un usuario con el email {email}.")
        return usuario

    def listar(self) -> List[Usuario]:
        """Devuelve todos los usuarios."""
        return self._usuarios.listar_todos()

    def actualizar(self, email: str, nombre: Optional[str] = None,
                   apellido: Optional[str] = None) -> Usuario:
        """Modifica nombre y/o apellido; ``None`` conserva el valor actual.

        El email no se puede cambiar porque es la clave que referencian los
        artículos.

        Raises:
            ValidacionError, UsuarioNoEncontradoError
        """
        usuario = self.obtener(email)
        if nombre is not None:
            usuario.nombre = nombre.strip()
        if apellido is not None:
            usuario.apellido = apellido.strip()
        if not self._usuarios.actualizar(usuario.email, usuario.nombre,
                                         usuario.apellido):
            raise UsuarioNoEncontradoError(
                f"El usuario {usuario.email} fue eliminado durante la "
                "operación.")
        return usuario

    def eliminar(self, email: str) -> None:
        """Elimina un usuario si ningún artículo lo referencia (RESTRICT).

        Raises:
            ValidacionError, UsuarioNoEncontradoError,
            IntegridadReferencialError: tiene artículos asociados.
        """
        usuario = self.obtener(email)
        referencias = self._articulos.contar_por_usuario(usuario.email)
        if referencias > 0:
            raise IntegridadReferencialError(
                f"No se puede eliminar a {usuario.email}: es el último "
                f"modificador de {referencias} artículo(s). Reasigne o "
                "elimine esos artículos primero.",
                referencias,
            )
        if not self._usuarios.eliminar(usuario.email):
            raise UsuarioNoEncontradoError(
                f"No existe un usuario con el email {usuario.email}.")
