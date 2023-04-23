from typing import List
from typing import Any
from dataclasses import dataclass
import json

@dataclass
class Permiso:
    id: int
    nombre_permiso: str
    descripcion: str

    @staticmethod
    def from_dict(obj: Any) -> 'Permiso':
        _id = int(obj.get("id"))
        _nombre_permiso = str(obj.get("nombre_permiso"))
        _descripcion = str(obj.get("descripcion"))
        return Permiso(_id, _nombre_permiso, _descripcion)

@dataclass
class Rol:
    id: int
    nombre_rol: str
    permisos: List[Permiso]

    @staticmethod
    def from_dict(obj: Any) -> 'Rol':
        _id = int(obj.get("id"))
        _nombre_rol = str(obj.get("nombre_rol"))
        _permisos = [Permiso.from_dict(y) for y in obj.get("permisos")]
        return Rol(_id, _nombre_rol, _permisos)

@dataclass
class Root:
    id: int
    nombre_usuario: str
    password: str
    rol: Rol
    telefono: str

    @staticmethod
    def from_dict(obj: Any) -> 'Root':
        _id = int(obj.get("id"))
        _nombre_usuario = str(obj.get("nombre_usuario"))
        _password = str(obj.get("password"))
        _rol = Rol.from_dict(obj.get("rol"))
        _telefono = str(obj.get("telefono"))
        return Root(_id, _nombre_usuario, _password, _rol, _telefono)

# Example Usage
# jsonstring = json.loads(myjsonstring)
# root = Root.from_dict(jsonstring)
