"""Entidad Usuario."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class Usuario:
    """Usuario que puede modificar artículos.

    El ``email`` es la clave de negocio (única e inmutable); ``id`` guarda el
    ``_id`` técnico de MongoDB como texto para no acoplar el modelo a BSON.
    """

    email: str
    nombre: str
    apellido: str
    fecha_creado: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc))
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el usuario en un documento listo para guardar (sin _id)."""
        return {
            "email": self.email,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "fecha_creado": self.fecha_creado,
        }

    @classmethod
    def from_dict(cls, documento: Dict[str, Any]) -> "Usuario":
        """Construye un usuario a partir de un documento de MongoDB."""
        return cls(
            email=documento["email"],
            nombre=documento.get("nombre", ""),
            apellido=documento.get("apellido", ""),
            fecha_creado=documento["fecha_creado"],
            id=str(documento["_id"]) if "_id" in documento else None,
        )
