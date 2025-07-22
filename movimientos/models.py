from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.apps import apps
from django.core.exceptions import ValidationError

class Deposito(models.Model):
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    empresa = models.ForeignKey('clientes.Empresa', on_delete=models.CASCADE)
    banco = models.ForeignKey('clientes.Banco', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    saldo_pendiente = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        ClienteComisionista = apps.get_model('clientes', 'ClienteComisionista')
        ComisionDetalle = apps.get_model('movimientos', 'ComisionDetalle')

        es_nuevo = self.pk is None
        if es_nuevo:
            self.saldo_pendiente = self.monto

        super().save(*args, **kwargs)

        if es_nuevo:
            comisionistas = ClienteComisionista.objects.filter(
                cliente=self.cliente,
                empresa=self.empresa,
                banco=self.banco
            )

            total_comisiones = Decimal('0.00')

            for c in comisionistas:
                base = self.monto / Decimal('1.16') if c.subtotal else self.monto
                monto_comision = (base * (c.porcentaje / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                ComisionDetalle.objects.create(
                    deposito=self,
                    comisionista=c.comisionista,
                    tipo=c.tipo,
                    porcentaje=c.porcentaje,
                    monto=monto_comision
                )

                total_comisiones += monto_comision

            self.saldo_pendiente = (self.monto - total_comisiones).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            super().save(update_fields=['saldo_pendiente'])

    def __str__(self):
        return f"Depósito {self.id} - {self.cliente} - ${self.monto}"
    @property
    def total_comision(self):
        return sum(d.monto for d in self.comisiondetalle_set.all())
    @property
    def total_retiros(self):
        return sum(r.monto for r in self.aplicacionretiro_set.all())


class Retiro(models.Model):
    cliente = models.ForeignKey('clientes.Cliente', on_delete=models.CASCADE)
    beneficiario = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha = models.DateField()
    cuenta_cheque = models.CharField(max_length=100, blank=True, null=True)
    banco_destino = models.CharField(max_length=100, blank=True, null=True)
    concepto = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Retiro {self.id} - {self.cliente} - ${self.monto}"

    def save(self, *args, **kwargs):
        if not self.monto or self.monto <= 0:
            raise ValidationError("Debe ingresar un monto mayor a cero.")

        saldo_total = self.cliente.saldo_disponible
        if self.pk is None and self.monto > saldo_total:
            raise ValidationError("El cliente no tiene saldo suficiente para este retiro.")

        es_nuevo = self.pk is None
        super().save(*args, **kwargs)

        if es_nuevo:
            Deposito = apps.get_model('movimientos', 'Deposito')
            AplicacionRetiro = apps.get_model('movimientos', 'AplicacionRetiro')

            restante = self.monto
            depositos = Deposito.objects.filter(cliente=self.cliente).order_by('fecha', 'id')

            for deposito in depositos:
                disponible = deposito.saldo_pendiente
                if disponible <= 0:
                    continue

                aplicar = min(restante, disponible).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

                AplicacionRetiro.objects.create(
                    retiro=self,
                    deposito=deposito,
                    monto=aplicar
                )

                deposito.saldo_pendiente = (deposito.saldo_pendiente - aplicar).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                deposito.save(update_fields=['saldo_pendiente'])

                restante -= aplicar
                if restante <= 0:
                    break


class AplicacionRetiro(models.Model):
    retiro = models.ForeignKey(Retiro, on_delete=models.CASCADE)
    deposito = models.ForeignKey(Deposito, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.retiro} aplicado a {self.deposito}"


class ComisionDetalle(models.Model):
    deposito = models.ForeignKey(Deposito, on_delete=models.CASCADE)
    comisionista = models.ForeignKey('clientes.Comisionista', on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=[('cliente', 'Cliente'), ('empresa', 'Empresa')])
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Comisión {self.comisionista} - {self.monto}"
