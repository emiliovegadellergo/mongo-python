"""Reglas de negocio de artículos."""

from datetime import datetime, timezone
from typing import List, Optional

from modelos.articulo import Articulo
from repositorios.articulo_repositorio import ArticuloRepositorio
from repositorios.usuario_repositorio import UsuarioRepositorio
from servicios.excepciones import (ArticuloNoEncontradoError,
                                   UsuarioNoEncontradoError, ValidacionError)
from servicios.usuario_servicio import validar_email


def validar_nombre(nombre: str) -> str:
    """Devuelve el nombre sin espacios sobrantes.

    Raises:
        ValidacionError: si queda vacío (incluye cadenas de solo espacios).
    """
    limpio = nombre.strip()
    if not limpio:
        raise ValidacionError(
            "El nombre del artículo es obligatorio y no puede ser solo espacios.")
    return limpio


class ArticuloServicio:
    """Casos de uso del módulo de artículos."""

    def __init__(self, articulos: ArticuloRepositorio,
                 usuarios: UsuarioRepositorio) -> None:
        """Recibe los repositorios; usuarios se usa para validar al responsable."""
        self._articulos = articulos
        self._usuarios = usuarios

    def _validar_responsable(self, email: str) -> str:
        """Comprueba que el usuario responsable exista; devuelve su email.

        Mongo no tiene llaves foráneas, así que esta verificación sustituye a
        un ``FOREIGN KEY`` de SQL.
        """
        email = validar_email(email)
        if not self._usuarios.existe(email):
            raise UsuarioNoEncontradoError(
                f"No existe un usuario con el email {email}; registre primero "
                "al usuario para poder atribuirle la modificación.")
        return email

    def _validar_id(self, id_articulo: str) -> str:
        """Comprueba que el ID tenga formato de ObjectId antes de consultar."""
        id_articulo = id_articulo.strip()
        if not self._articulos.es_id_valido(id_articulo):
            raise ValidacionError(
                f"'{id_articulo}' no es un ID válido: debe tener 24 caracteres "
                "hexadecimales.")
        return id_articulo

    def crear(self, nombre: str, descripcion: str, marca: str,
              email_responsable: str) -> Articulo:
        """Registra un artículo atribuido a un usuario existente.

        Raises:
            ValidacionError, UsuarioNoEncontradoError
        """
        articulo = Articulo(
            nombre=validar_nombre(nombre),
            descripcion=descripcion.strip(),
            marca=marca.strip(),
            usuario_modifico=self._validar_responsable(email_responsable),
        )
        return self._articulos.insertar(articulo)

    def obtener(self, id_articulo: str) -> Articulo:
        """Busca un artículo por su ID.

        Raises:
            ValidacionError: ID mal formado.
            ArticuloNoEncontradoError: no existe.
        """
        id_articulo = self._validar_id(id_articulo)
        articulo = self._articulos.buscar_por_id(id_articulo)
        if articulo is None:
            raise ArticuloNoEncontradoError(
                f"No existe un artículo con el ID {id_articulo}.")
        return articulo

    def listar(self) -> List[Articulo]:
        """Devuelve todos los artículos."""
        return self._articulos.listar_todos()

    def actualizar(self, id_articulo: str, email_responsable: str,
                   nombre: Optional[str] = None,
                   descripcion: Optional[str] = None,
                   marca: Optional[str] = None) -> Articulo:
        """Modifica un artículo; ``None`` en un campo conserva su valor.

        Siempre registra quién hizo el cambio y cuándo.

        Raises:
            ValidacionError, UsuarioNoEncontradoError, ArticuloNoEncontradoError
        """
        articulo = self.obtener(id_articulo)
        responsable = self._validar_responsable(email_responsable)
        if nombre is not None:
            articulo.nombre = validar_nombre(nombre)
        if descripcion is not None:
            articulo.descripcion = descripcion.strip()
        if marca is not None:
            articulo.marca = marca.strip()
        articulo.usuario_modifico = responsable
        articulo.fecha_modificado = datetime.now(timezone.utc)
        if not self._articulos.actualizar(articulo):
            raise ArticuloNoEncontradoError(
                f"El artículo {articulo.id} fue eliminado durante la operación.")
        return articulo

    def eliminar(self, id_articulo: str) -> None:
        """Elimina un artículo por su ID.

        Raises:
            ValidacionError, ArticuloNoEncontradoError
        """
        id_articulo = self._validar_id(id_articulo)
        if not self._articulos.eliminar(id_articulo):
            raise ArticuloNoEncontradoError(
                f"No existe un artículo con el ID {id_articulo}.")
