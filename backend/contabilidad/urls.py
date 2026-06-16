from django.urls import path
from .views import MovimientoListView, MovimientoCreateView, reporte_balance

app_name = "contabilidad"

urlpatterns = [
    # Vista principal: lista de movimientos contables
    path('', MovimientoListView.as_view(), name='movimiento_list'),

    # Vista para registrar un nuevo movimiento contable
    path('nuevo/', MovimientoCreateView.as_view(), name='movimiento_create'),

    # Vista de reporte de balance
    path('balance/', reporte_balance, name='reporte_balance'),
]
