import csv
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.shortcuts import redirect

from .models import Venta, DetalleVenta, Cliente
from inventario.models import Producto

DetalleVentaFormSet = inlineformset_factory(
    Venta,
    DetalleVenta,
    fields=["producto", "cantidad", "precio_unitario"],
    extra=1,
    can_delete=True,
)


# ── Venta ──────────────────────────────────────────────────────────────────────

class VentaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Venta
    template_name = "ventas/venta_list.html"
    permission_required = "ventas.view_venta"
    raise_exception = True
    context_object_name = "ventas"

    def get_queryset(self):
        return Venta.objects.select_related("cliente").prefetch_related("detalles__producto")


class VentaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Venta
    fields = ["cliente"]
    template_name = "ventas/venta_form.html"
    success_url = reverse_lazy("ventas:venta_list")
    permission_required = "ventas.add_venta"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["detalle_formset"] = DetalleVentaFormSet(self.request.POST)
        else:
            context["detalle_formset"] = DetalleVentaFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context["detalle_formset"]
        if detalle_formset.is_valid():
            self.object = form.save()
            detalle_formset.instance = self.object
            detalle_formset.save()
            messages.success(self.request, "Venta registrada correctamente.")
            return redirect(self.success_url)
        else:
            messages.error(self.request, "Revisa los productos ingresados.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Error al registrar la venta. Verifique los datos.")
        return super().form_invalid(form)


class VentaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Venta
    fields = ["cliente"]
    template_name = "ventas/venta_form.html"
    success_url = reverse_lazy("ventas:venta_list")
    permission_required = "ventas.change_venta"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["detalle_formset"] = DetalleVentaFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["detalle_formset"] = DetalleVentaFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context["detalle_formset"]
        if detalle_formset.is_valid():
            self.object = form.save()
            detalle_formset.instance = self.object
            detalle_formset.save()
            messages.success(self.request, "Venta actualizada correctamente.")
            return redirect(self.success_url)
        else:
            messages.error(self.request, "Revisa los productos ingresados.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar la venta. Verifique los datos.")
        return super().form_invalid(form)


class VentaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Venta
    template_name = "ventas/venta_confirm_delete.html"
    success_url = reverse_lazy("ventas:venta_list")
    permission_required = "ventas.delete_venta"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Venta eliminada correctamente.")
        return super().form_valid(form)


class DetalleVentaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = DetalleVenta
    template_name = "ventas/detalleventa_list.html"
    permission_required = "ventas.view_detalleventa"
    raise_exception = True
    context_object_name = "detalles"


# ── Cliente ────────────────────────────────────────────────────────────────────

class ClienteListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Cliente
    template_name = "ventas/cliente_list.html"
    permission_required = "ventas.view_cliente"
    raise_exception = True
    context_object_name = "clientes"


class ClienteCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Cliente
    fields = ["nombre", "correo", "telefono"]
    template_name = "ventas/cliente_form.html"
    success_url = reverse_lazy("ventas:cliente_list")
    permission_required = "ventas.add_cliente"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Cliente registrado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al registrar el cliente. Verifique los datos.")
        return super().form_invalid(form)


class ClienteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Cliente
    fields = ["nombre", "correo", "telefono"]
    template_name = "ventas/cliente_form.html"
    success_url = reverse_lazy("ventas:cliente_list")
    permission_required = "ventas.change_cliente"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Cliente actualizado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar el cliente. Verifique los datos.")
        return super().form_invalid(form)


class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Cliente
    template_name = "ventas/cliente_confirm_delete.html"
    success_url = reverse_lazy("ventas:cliente_list")
    permission_required = "ventas.delete_cliente"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Cliente eliminado correctamente.")
        return super().form_valid(form)


# ── Exportación CSV ────────────────────────────────────────────────────────────

@login_required
@permission_required('ventas.view_venta', raise_exception=True)
def exportar_ventas_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="ventas.csv"'
    response.write('\ufeff')  # BOM para Excel en Windows

    writer = csv.writer(response)
    writer.writerow(['ID', 'Cliente', 'Fecha', 'Productos', 'Total'])

    for venta in Venta.objects.select_related('cliente').prefetch_related('detalles__producto').order_by('-fecha'):
        productos = ' | '.join(
            f"{d.cantidad}x {d.producto.nombre}" for d in venta.detalles.all()
        )
        writer.writerow([
            venta.id,
            venta.cliente.nombre,
            venta.fecha,
            productos,
            venta.get_total(),
        ])

    return response