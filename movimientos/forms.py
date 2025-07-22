from django import forms
from decimal import Decimal
from django.apps import apps
from .models import Retiro


class RetiroForm(forms.ModelForm):
    class Meta:
        model = Retiro
        fields = '__all__'

    def clean_monto(self):
        monto = self.cleaned_data.get('monto')
        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor a cero.")
        return monto

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get('cliente')
        monto = cleaned_data.get('monto')

        if cliente and monto:
            Cliente = apps.get_model('clientes', 'Cliente')
            saldo = Cliente.objects.get(id=cliente.id).saldo_disponible or Decimal('0.00')
            if monto > saldo:
                raise forms.ValidationError("Saldo insuficiente para realizar este retiro.")

        return cleaned_data


class CargaDepositosForm(forms.Form):
    archivo = forms.FileField(label="Archivo Excel de Depósitos")


class CargaRetirosForm(forms.Form):
    archivo = forms.FileField(label="Archivo Excel de Retiros")
