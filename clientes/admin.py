from django.contrib import admin
from .models import Empresa, Banco, Comisionado, Comisionista, Cliente, ClienteComisionista
from django.contrib.admin import AdminSite

admin.site.site_header = "Control Financiero"
admin.site.site_title = "Control Financiero"
admin.site.index_title = "Bienvenido al Sistema de Administración"

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ['clave', 'nombre']
    list_filter = ['nombre']
    search_fields = ['clave', 'nombre']

@admin.register(Banco)
class BancoAdmin(admin.ModelAdmin):
    list_display = ['clave', 'nombre', 'cuenta', 'clabe', 'sucursal']
    list_filter = ['nombre']
    search_fields = ['clave', 'nombre']

@admin.register(Comisionado)
class ComisionadoAdmin(admin.ModelAdmin):
    list_display = ['clave', 'nombre']
    list_filter = ['nombre']
    search_fields = ['clave', 'nombre']

@admin.register(Comisionista)
class ComisionistaAdmin(admin.ModelAdmin):
    list_display = ['clave', 'nombre']
    list_filter = ['nombre']
    search_fields = ['clave', 'nombre']

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['clave', 'nombre', 'rfc','saldo_disponible']
    readonly_fields = ['saldo_disponible']
    list_filter = ['nombre']
    search_fields = ['nombre']

@admin.register(ClienteComisionista)
class ClienteComisionistaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'comisionista', 'empresa', 'banco', 'tipo', 'porcentaje', 'subtotal']
    list_filter = ['tipo', 'empresa', 'banco']
    search_fields = ['cliente__nombre', 'comisionista__nombre']

