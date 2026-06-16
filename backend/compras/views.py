import csv
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.shortcuts import redirect

from .models import OrdenCompra, DetalleCompra, Proveedor
from inventario.models import Producto

DetalleCompraFormSet = inlineformset_factory(
    OrdenCompra,
    DetalleCompra,
    fields=["producto", "cantidad", "precio_unitario"],
    extra=1,
    can_delete=True,
)


# ── Orden de Compra ────────────────────────────────────────────────────────────

class OrdenCompraListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = OrdenCompra
    template_name = "compras/ordencompra_list.html"
    permission_required = "compras.view_ordencompra"
    raise_exception = True
    context_object_name = "ordenes"

    def get_queryset(self):
        return OrdenCompra.objects.select_related("proveedor").prefetch_related("detalles__producto")


class OrdenCompraCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = OrdenCompra
    fields = ["proveedor"]
    template_name = "compras/ordencompra_form.html"
    success_url = reverse_lazy("compras:ordencompra_list")
    permission_required = "compras.add_ordencompra"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["detalle_formset"] = DetalleCompraFormSet(self.request.POST)
        else:
            context["detalle_formset"] = DetalleCompraFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context["detalle_formset"]
        if detalle_formset.is_valid():
            self.object = form.save()
            detalle_formset.instance = self.object
            detalle_formset.save()
            messages.success(self.request, "Orden de compra registrada correctamente.")
            return redirect(self.success_url)
        else:
            messages.error(self.request, "Revisa los productos ingresados.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Error al registrar la orden de compra. Verifique los datos.")
        return super().form_invalid(form)


class OrdenCompraUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = OrdenCompra
    fields = ["proveedor"]
    template_name = "compras/ordencompra_form.html"
    success_url = reverse_lazy("compras:ordencompra_list")
    permission_required = "compras.change_ordencompra"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["detalle_formset"] = DetalleCompraFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context["detalle_formset"] = DetalleCompraFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context["detalle_formset"]
        if detalle_formset.is_valid():
            self.object = form.save()
            detalle_formset.instance = self.object
            detalle_formset.save()
            messages.success(self.request, "Orden de compra actualizada correctamente.")
            return redirect(self.success_url)
        else:
            messages.error(self.request, "Revisa los productos ingresados.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar la orden de compra. Verifique los datos.")
        return super().form_invalid(form)


class OrdenCompraDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = OrdenCompra
    template_name = "compras/ordencompra_confirm_delete.html"
    success_url = reverse_lazy("compras:ordencompra_list")
    permission_required = "compras.delete_ordencompra"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Orden de compra eliminada correctamente.")
        return super().form_valid(form)


# ── Detalle de Compra ──────────────────────────────────────────────────────────

class DetalleCompraListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = DetalleCompra
    template_name = "compras/detallecompra_list.html"
    permission_required = "compras.view_detallecompra"
    raise_exception = True
    context_object_name = "detalles"


# ── Proveedor ──────────────────────────────────────────────────────────────────

class ProveedorListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Proveedor
    template_name = "compras/proveedor_list.html"
    permission_required = "compras.view_proveedor"
    raise_exception = True
    context_object_name = "proveedores"


class ProveedorCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Proveedor
    fields = ["nombre", "contacto", "telefono", "direccion"]
    template_name = "compras/proveedor_form.html"
    success_url = reverse_lazy("compras:proveedor_list")
    permission_required = "compras.add_proveedor"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Proveedor registrado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al registrar el proveedor. Verifique los datos.")
        return super().form_invalid(form)


class ProveedorUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Proveedor
    fields = ["nombre", "contacto", "telefono", "direccion"]
    template_name = "compras/proveedor_form.html"
    success_url = reverse_lazy("compras:proveedor_list")
    permission_required = "compras.change_proveedor"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Proveedor actualizado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar el proveedor. Verifique los datos.")
        return super().form_invalid(form)


class ProveedorDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Proveedor
    template_name = "compras/proveedor_confirm_delete.html"
    success_url = reverse_lazy("compras:proveedor_list")
    permission_required = "compras.delete_proveedor"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Proveedor eliminado correctamente.")
        return super().form_valid(form)


# ── Exportación CSV ────────────────────────────────────────────────────────────

@login_required
@permission_required('compras.view_ordencompra', raise_exception=True)
def exportar_compras_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="compras.csv"'
    response.write('\ufeff')  # BOM para Excel en Windows

    writer = csv.writer(response)
    writer.writerow(['ID', 'Proveedor', 'Fecha', 'Productos', 'Total'])

    for orden in OrdenCompra.objects.select_related('proveedor').prefetch_related('detalles__producto').order_by('-fecha'):
        productos = ' | '.join(
            f"{d.cantidad}x {d.producto.nombre}" for d in orden.detalles.all()
        )
        writer.writerow([
            orden.id,
            orden.proveedor.nombre,
            orden.fecha,
            productos,
            orden.get_total(),
        ])

    return response
