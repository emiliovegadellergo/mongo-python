"""Acceso a datos de la colección ``articulos``."""

from typing import List, Optional

from bson import ObjectId
from pymongo import DESCENDING
from pymongo.database import Database

from modelos.articulo import Articulo
from repositorios.errores import traducir_errores


class ArticuloRepositorio:
    """Operaciones CRUD sobre la colección ``articulos``."""

    def __init__(self, bd: Database) -> None:
        """Recibe la base de datos a usar (permite separar pruebas)."""
        self._coleccion = bd.articulos

    @staticmethod
    def es_id_valido(id_articulo: str) -> bool:
        """Indica si el texto tiene formato de ObjectId (24 hexadecimales)."""
        return ObjectId.is_valid(id_articulo)

    def insertar(self, articulo: Articulo) -> Articulo:
        """Inserta el artículo y devuelve el mismo objeto con su ``id``."""
        with traducir_errores():
            resultado = self._coleccion.insert_one(articulo.to_dict())
        articulo.id = str(resultado.inserted_id)
        return articulo

    def buscar_por_id(self, id_articulo: str) -> Optional[Articulo]:
        """Devuelve el artículo o ``None``; el id debe ser válido."""
        with traducir_errores():
            documento = self._coleccion.find_one(
                {"_id": ObjectId(id_articulo)})
        return Articulo.from_dict(documento) if documento else None

    def listar_todos(self) -> List[Articulo]:
        """Devuelve los artículos ordenados por modificación más reciente."""
        with traducir_errores():
            documentos = list(
                self._coleccion.find().sort("fecha_modificado", DESCENDING))
        return [Articulo.from_dict(d) for d in documentos]

    def actualizar(self, articulo: Articulo) -> bool:
        """Reemplaza los campos del artículo; devuelve ``True`` si existía."""
        with traducir_errores():
            resultado = self._coleccion.update_one(
                {"_id": ObjectId(articulo.id)}, {"$set": articulo.to_dict()})
        return resultado.matched_count == 1

    def eliminar(self, id_articulo: str) -> bool:
        """Elimina el artículo; devuelve ``True`` si existía."""
        with traducir_errores():
            resultado = self._coleccion.delete_one(
                {"_id": ObjectId(id_articulo)})
        return resultado.deleted_count == 1

    def contar_por_usuario(self, email: str) -> int:
        """Cuenta los artículos cuya última modificación hizo ``email``.

        Usa el índice ``ix_articulos_usuario_modifico``.
        """
        with traducir_errores():
            return self._coleccion.count_documents({"usuario_modifico": email})
