# persona_model.py
# Modelo de personas.

# Importar módulos de Python.
from datetime import datetime

# Importar módulos de Django.
from django.db import models

# Modelo de persona.
class Persona( models.Model ):
    id_persona: int = models.AutoField( primary_key=True )
    nombre: str = models.CharField( max_length=50, blank=True, null=True )
    apellido: str = models.CharField( max_length=50, blank=True, null=True )
    telefono: str = models.CharField( max_length=20, blank=True, null=True )
    correo: str = models.CharField( max_length=100, blank=True, null=True )
    tipo_persona: str = models.CharField( max_length=20, blank=True, null=True )
    carrera: str = models.CharField( max_length=100, blank=True, null=True )
    seccion: str = models.CharField( max_length=10, blank=True, null=True )
    carnet: str = models.CharField( max_length=20, blank=True, null=True )
    fecha_registro: datetime = models.DateTimeField( blank=True, null=True )
    vector_facial: bytes = models.BinaryField( blank=True, null=True )
    path_photo: str = models.CharField( max_length=255, blank=True, null=True )

    # Metadatos del modelo.
    class Meta:
        db_table = 'personas'
