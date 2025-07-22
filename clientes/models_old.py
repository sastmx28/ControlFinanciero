from django.db import models

class Folio(models.Model):
    modelo = models.CharField(max_length=50, unique=True)
    prefijo = models.CharField(max_length=5)
    consecutivo = models.IntegerField(default=1)
    longitud = models.IntegerField(default=4)

    def obtener_siguiente_folio(self):
        numero = str(self.consecutivo).zfill(self.longitud)
        return f"{self.prefijo}{numero}"

    def incrementar(self):
        self.consecutivo += 1
        self.save()