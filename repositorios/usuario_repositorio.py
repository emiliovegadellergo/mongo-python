"""Acceso a datos de la colección ``usuarios``."""

from typing import List, Optional

from pymongo import ASCENDING
from pymongo.database import Database

from modelos.usuario import Usuario
from repositorios.errores import traducir_errores


class UsuarioRepositorio:
    """Operaciones CRUD sobre la colección ``usuarios``."""

    def __init__(self, bd: Database) -> None:
        """Recibe la base de datos a usar (permite separar pruebas)."""
        self._coleccion = bd.usuarios

    def insertar(self, usuario: Usuario) -> Usuario:
        """Inserta el usuario y devuelve una copia con su ``id`` asignado.

        Raises:
            ClaveDuplicadaError: si el email ya existe (índice único).
        """
        with traducir_errores():
            resultado = self._coleccion.insert_one(usuario.to_dict())
        usuario.id = str(resultado.inserted_id)
        return usuario

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """Devuelve el usuario con ese email o ``None``."""
        with traducir_errores():
            documento = self._coleccion.find_one({"email": email})
        return Usuario.from_dict(documento) if documento else None

    def existe(self, email: str) -> bool:
        """Indica si hay un usuario con ese email."""
        with traducir_errores():
            return self._coleccion.count_documents({"email": email},
                                                   limit=1) > 0

    def listar_todos(self) -> List[Usuario]:
        """Devuelve todos los usuarios ordenados por email."""
        with traducir_errores():
            documentos = list(self._coleccion.find().sort("email", ASCENDING))
        return [Usuario.from_dict(d) for d in documentos]

    def actualizar(self, email: str, nombre: str, apellido: str) -> bool:
        """Actualiza nombre y apellido; el email es inmutable.

        Returns:
            ``True`` si se encontró el usuario.
        """
        with traducir_errores():
            resultado = self._coleccion.update_one(
                {"email": email},
                {"$set": {"nombre": nombre, "apellido": apellido}},
            )
        return resultado.matched_count == 1

    def eliminar(self, email: str) -> bool:
        """Elimina el usuario; devuelve ``True`` si existía."""
        with traducir_errores():
            resultado = self._coleccion.delete_one({"email": email})
        return resultado.deleted_count == 1
