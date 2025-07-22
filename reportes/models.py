from django.db import models

class ReporteDummy(models.Model):
    class Meta:
        managed = False  # No se crea en la base de datos
        verbose_name = 'Reportes'
        verbose_name_plural = 'Reportes'
