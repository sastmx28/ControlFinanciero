from django.core.management.base import BaseCommand
from django.apps import apps

class Command(BaseCommand):
    help = "Borra todos los datos de clientes, movimientos, bancos y empresas"

    def handle(self, *args, **kwargs):
        modelos = [
            "AplicacionRetiro",
            "Retiro",
            "ComisionDetalle",
            "Deposito",
            "ClienteComisionista",
            "Cliente",
            "Comisionista",
            "Comisionado",
            "Empresa",
            "Banco",
        ]

        for nombre in modelos:
            app = "movimientos" if nombre in [
                "Deposito", "Retiro", "ComisionDetalle", "AplicacionRetiro", "Empresa", "Banco"
            ] else "clientes"

            modelo = apps.get_model(app, nombre)
            modelo.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f"{app}.{nombre} → datos eliminados"))
