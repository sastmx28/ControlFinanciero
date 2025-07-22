from django.urls import path
from . import views

urlpatterns = [
    path('estado-cuenta/', views.estado_cuenta, name='reporte_estado_cuenta'),
    path('comisiones/', views.reporte_comisiones, name='reporte_comisiones'),
    path('depositos/', views.reporte_depositos, name='reporte_depositos'),
]
