
from django.shortcuts import render
from django.http import HttpResponse
import openpyxl
from movimientos.models import Deposito, Retiro
from clientes.models import Cliente, Comisionado, ClienteComisionista
from decimal import Decimal

def estado_cuenta(request):
    cliente_id = request.GET.get("cliente")
    comisionado_id = request.GET.get("comisionado")

    clientes = Cliente.objects.all()
    comisionados = Comisionado.objects.all()
    cliente = Cliente.objects.filter(id=cliente_id).first() if cliente_id else None

    columnas = [
        "Fecha",
        "Razón Social / Nombre",
        "Monto Depósito",
        "Monto de Comisión",
        "Monto Retiro",
        "Saldo",
        "Cuenta/Cheque",
        "Banco/NoCheque",
        "Concepto",
    ]

    movimientos = []
    saldo = Decimal("0.00")

    if comisionado_id:
        clientes_vinculados = ClienteComisionista.objects.filter(
            comisionista__comisionado_id=comisionado_id
        ).values_list("cliente_id", flat=True)
    else:
        clientes_vinculados = Cliente.objects.values_list("id", flat=True)

    if cliente_id:
        if int(cliente_id) not in clientes_vinculados:
            cliente = None
        else:
            cliente = Cliente.objects.filter(id=cliente_id).first()
            clientes_vinculados = [cliente.id]

    depositos = Deposito.objects.filter(cliente_id__in=clientes_vinculados).order_by("fecha")
    retiros = Retiro.objects.filter(cliente_id__in=clientes_vinculados).order_by("fecha")

    eventos = [(d.fecha, "deposito", d) for d in depositos] + [(r.fecha, "retiro", r) for r in retiros]
    eventos.sort(key=lambda x: (x[0], 0 if x[1] == "deposito" else 1, x[2].id))

    for fecha, tipo, obj in eventos:
        if tipo == "deposito":
            razon = obj.cliente.nombre
            monto_deposito = obj.monto
            comision_total = obj.total_comision
            saldo += monto_deposito - comision_total
            movimientos.append([
                obj.fecha,
                razon,
                f"${monto_deposito:,.2f}",
                f"${comision_total:,.2f}",
                "",
                f"${saldo:,.2f}",
                "",
                obj.banco.nombre if obj.banco else "",
                ""
            ])
        else:
            razon = obj.beneficiario
            monto_retiro = obj.monto
            saldo -= monto_retiro
            movimientos.append([
                obj.fecha,
                razon,
                "",
                "",
                f"${monto_retiro:,.2f}",
                f"${saldo:,.2f}",
                obj.cuenta_cheque,
                obj.banco_destino,
                obj.concepto
            ])

    if request.GET.get("export") == "1":
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Estado de Cuenta"
        ws.append(columnas)
        for row in movimientos:
            ws.append([str(v) for v in row])
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=estado_cuenta.xlsx'
        wb.save(response)
        return response

    return render(request, "reportes/estado_cuenta.html", {
        "columnas": columnas,
        "movimientos": movimientos,
        "clientes": clientes,
        "comisionados": comisionados,
        "cliente_id": int(cliente_id) if cliente_id else "",
        "comisionado_id": int(comisionado_id) if comisionado_id else "",
    })
def reporte_comisiones(request):
    from movimientos.models import ComisionDetalle
    columnas = ["Fecha", "Cliente", "Empresa", "Banco", "Comisionista", "Tipo", "Porcentaje", "Monto"]
    filas = []

    detalles = ComisionDetalle.objects.select_related(
        "deposito", "deposito__cliente", "deposito__empresa", "deposito__banco", "comisionista"
    ).order_by("deposito__fecha")

    for det in detalles:
        filas.append([
            det.deposito.fecha,
            det.deposito.cliente.nombre,
            det.deposito.empresa.nombre if det.deposito.empresa else "",
            det.deposito.banco.nombre if det.deposito.banco else "",
            det.comisionista.nombre,
            det.tipo,
            f"{det.porcentaje:.2f}%",
            f"${det.monto:,.2f}",
        ])

    return render(request, "admin/reportes_tabla.html", {
        "titulo": "Comisiones por comisionista",
        "columnas": columnas,
        "filas": filas,
    })


def reporte_depositos(request):
    columnas = [
        "Fecha",
        "Cliente",
        "Empresa",
        "Banco",
        "Monto",
        "Comisión Total",
        "Retiros Aplicados",
        "Saldo Disponible"
    ]
    filas = []

    depositos = Deposito.objects.select_related(
        "cliente", "empresa", "banco"
    ).order_by("fecha")

    for dep in depositos:
        filas.append([
            dep.fecha,
            dep.cliente.nombre,
            dep.empresa.nombre if dep.empresa else "",
            dep.banco.nombre if dep.banco else "",
            f"${dep.monto:,.2f}",
            f"${dep.total_comision:,.2f}",
            f"${dep.total_retiros:,.2f}",
            f"${dep.saldo_pendiente:,.2f}",
        ])

    return render(request, "admin/reportes_tabla.html", {
        "titulo": "Desglose de depósitos",
        "columnas": columnas,
        "filas": filas,
    })
