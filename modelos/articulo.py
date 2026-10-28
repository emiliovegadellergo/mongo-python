"""Entidad Articulo."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class Articulo:
    """Artículo de inventario con trazabilidad de su última modificación.

    ``usuario_modifico`` guarda el email del usuario responsable y
    ``fecha_modificado`` el instante (UTC) del último create/update.
    """

    nombre: str
    descripcion: str
    marca: str
    usuario_modifico: str
    fecha_modificado: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el artículo en un documento listo para guardar (sin _id)."""
        return {
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "marca": self.marca,
            "usuario_modifico": self.usuario_modifico,
            "fecha_modificado": self.fecha_modificado,
        }

    @classmethod
    def from_dict(cls, documento: Dict[str, Any]) -> "Articulo":
        """Construye un artículo a partir de un documento de MongoDB."""
        return cls(
            nombre=documento["nombre"],
            descripcion=documento.get("descripcion", ""),
            marca=documento.get("marca", ""),
            usuario_modifico=documento["usuario_modifico"],
            fecha_modificado=documento["fecha_modificado"],
            id=str(documento["_id"]) if "_id" in documento else None,
        )
