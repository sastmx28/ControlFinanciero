from django.contrib import admin
from .models import Deposito, Retiro, ComisionDetalle, AplicacionRetiro
from .forms import RetiroForm

@admin.register(Deposito)
class DepositoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'empresa', 'banco', 'monto', 'fecha', 'saldo_pendiente']
    readonly_fields = ['saldo_pendiente']

@admin.register(Retiro)
class RetiroAdmin(admin.ModelAdmin):
    form = RetiroForm
    list_display = ['cliente', 'beneficiario', 'monto', 'fecha', 'banco_destino']

admin.site.register(ComisionDetalle)
admin.site.register(AplicacionRetiro)
