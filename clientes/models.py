from django.db import models
from movimientos.models import Deposito, AplicacionRetiro, ComisionDetalle
from decimal import Decimal

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


class Cliente(models.Model):
    clave = models.CharField(max_length=10, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    rfc = models.CharField(max_length=13, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.clave:
            folio = Folio.objects.get(modelo='Cliente')
            self.clave = folio.obtener_siguiente_folio()
            folio.incrementar()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.clave} - {self.nombre}"
    
    @property
    def saldo_disponible(self):
        # Total de depósitos
        total_depositado = Deposito.objects.filter(cliente=self).aggregate(
            total=models.Sum('monto')
        )['total'] or Decimal('0.00')

        # Total de comisiones
        total_comisiones = ComisionDetalle.objects.filter(
            deposito__cliente=self
        ).aggregate(total=models.Sum('monto'))['total'] or Decimal('0.00')

        # Total de retiros
        total_retirado = AplicacionRetiro.objects.filter(
            deposito__cliente=self
        ).aggregate(total=models.Sum('monto'))['total'] or Decimal('0.00')

        return round(total_depositado - total_comisiones - total_retirado, 2)


class Empresa(models.Model):
    clave = models.CharField(max_length=10, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    RFC = models.CharField(max_length=15, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.clave:
            folio = Folio.objects.get(modelo='Empresa')
            self.clave = folio.obtener_siguiente_folio()
            folio.incrementar()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.clave} - {self.nombre}"


class Banco(models.Model):
    clave = models.CharField(max_length=10, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    cuenta = models.CharField(max_length=50, blank=True, null=True)
    clabe = models.CharField(max_length=50, blank=True, null=True)
    sucursal = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.clave:
            folio = Folio.objects.get(modelo='Banco')
            self.clave = folio.obtener_siguiente_folio()
            folio.incrementar()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.clave} - {self.nombre}"


class Comisionado(models.Model):
    clave = models.CharField(max_length=10, unique=True, editable=False)
    nombre = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.clave:
            folio = Folio.objects.get(modelo='Comisionado')
            self.clave = folio.obtener_siguiente_folio()
            folio.incrementar()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.clave} - {self.nombre}"


class Comisionista(models.Model):
    clave = models.CharField(max_length=10, unique=True, editable=False)
    nombre = models.CharField(max_length=100)
    #comisionado = models.ForeignKey(Comisionado, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.clave:
            folio = Folio.objects.get(modelo='Comisionista')
            self.clave = folio.obtener_siguiente_folio()
            folio.incrementar()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.clave} - {self.nombre}"


class ClienteComisionista(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    comisionista = models.ForeignKey(Comisionista, on_delete=models.CASCADE)
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, null=True, blank=True)
    banco = models.ForeignKey(Banco, on_delete=models.CASCADE, null=True, blank=True)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tipo = models.CharField(max_length=20, choices=[('cliente', 'Cliente'), ('empresa', 'Empresa')])
    subtotal = models.BooleanField(default=False)

    class Meta:
        unique_together = ('cliente', 'comisionista', 'empresa', 'banco', 'tipo')

    def __str__(self):
        return f"{self.cliente} - {self.comisionista} ({self.tipo}) {self.empresa}/{self.banco}"