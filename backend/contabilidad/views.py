from django.db.models import Sum
from django.shortcuts import render
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import MovimientoContable

# Vista basada en función: reporte de balance
@login_required
@permission_required('contabilidad.view_movimientocontable', raise_exception=True)
def reporte_balance(request):
    ingresos = MovimientoContable.objects.filter(tipo="INGRESO").aggregate(total=Sum('monto'))['total'] or 0
    egresos = MovimientoContable.objects.filter(tipo="EGRESO").aggregate(total=Sum('monto'))['total'] or 0
    balance = ingresos - egresos
    return render(request, "contabilidad/balance.html", {
        "ingresos": ingresos,
        "egresos": egresos,
        "balance": balance
    })

# Vista genérica: lista de movimientos
class MovimientoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = MovimientoContable
    template_name = "contabilidad/movimiento_list.html"
    permission_required = "contabilidad.view_movimientocontable"
    raise_exception = True

# Vista genérica: crear movimiento
class MovimientoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = MovimientoContable
    fields = ['tipo', 'monto', 'descripcion']  # ajusta según tu modelo
    template_name = "contabilidad/movimiento_form.html"
    success_url = reverse_lazy('contabilidad:movimiento_list')
    permission_required = "contabilidad.add_movimientocontable"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Movimiento contable registrado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al registrar el movimiento contable. Verifique los datos.")
        return super().form_invalid(form)

