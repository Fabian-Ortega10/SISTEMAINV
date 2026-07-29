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
from core.services.inventario import (
    procesar_detalle_compra,
    revertir_detalle_compra,
    StockInsuficienteError,
)

# Formset — solo materias primas (mejora 2 acumulada)
DetalleCompraFormSet = inlineformset_factory(
    OrdenCompra,
    DetalleCompra,
    fields=["producto", "cantidad", "precio_unitario"],
    extra=1,
    can_delete=True,
)

def _filtrar_formset_materias(formset):
    """Restringe el campo producto a solo materias primas."""
    qs = Producto.objects.filter(
        tipo=Producto.TipoProducto.MATERIA_PRIMA
    ).order_by("nombre")
    for form in formset.forms:
        form.fields["producto"].queryset = qs
        form.fields["producto"].label = "Materia prima"


# ── Lista ─────────────────────────────────────────────────────────────────────
class OrdenCompraListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = OrdenCompra
    template_name = "compras/ordencompra_list.html"
    permission_required = "compras.view_ordencompra"
    raise_exception = True
    context_object_name = "ordenes"

    def get_queryset(self):
        return OrdenCompra.objects.select_related("proveedor").prefetch_related(
            "detalles__producto"
        )


# ── Crear ─────────────────────────────────────────────────────────────────────
class OrdenCompraCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = OrdenCompra
    # estado incluido: el usuario puede elegir, pero por defecto es PENDIENTE
    fields = ["proveedor", "estado"]
    template_name = "compras/ordencompra_form.html"
    success_url = reverse_lazy("compras:ordencompra_list")
    permission_required = "compras.add_ordencompra"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            fs = DetalleCompraFormSet(self.request.POST)
        else:
            fs = DetalleCompraFormSet()
        _filtrar_formset_materias(fs)
        context["detalle_formset"] = fs
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context["detalle_formset"]

        if not detalle_formset.is_valid():
            messages.error(self.request, "Revisa los productos ingresados.")
            return self.render_to_response(self.get_context_data(form=form))

        self.object = form.save()
        detalle_formset.instance = self.object

        # Si se crea directamente en estado RECIBIDA, procesar stock
        if self.object.es_recibida:
            try:
                for detalle_form in detalle_formset:
                    if detalle_form.cleaned_data and not detalle_form.cleaned_data.get("DELETE"):
                        detalle = detalle_form.save()
                        procesar_detalle_compra(detalle)
            except StockInsuficienteError as e:
                messages.error(self.request, f"Error al actualizar stock: {e}")
                return redirect(self.success_url)
        else:
            detalle_formset.save()

        messages.success(
            self.request,
            f"Orden de compra registrada como {self.object.get_estado_display()}."
        )
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Error al registrar la orden. Verifique los datos.")
        return super().form_invalid(form)


# ── Editar / Transición de estado ─────────────────────────────────────────────
class OrdenCompraUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = OrdenCompra
    fields = ["proveedor", "estado"]
    template_name = "compras/ordencompra_form.html"
    success_url = reverse_lazy("compras:ordencompra_list")
    permission_required = "compras.change_ordencompra"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            fs = DetalleCompraFormSet(self.request.POST, instance=self.object)
        else:
            fs = DetalleCompraFormSet(instance=self.object)
        _filtrar_formset_materias(fs)
        context["detalle_formset"] = fs
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        detalle_formset = context["detalle_formset"]

        if not detalle_formset.is_valid():
            messages.error(self.request, "Revisa los productos ingresados.")
            return self.render_to_response(self.get_context_data(form=form))

        # Leer estado ANTES de guardar el form
        estado_anterior = OrdenCompra.objects.values_list(
            "estado", flat=True
        ).get(pk=self.object.pk)

        self.object = form.save()
        nuevo_estado = self.object.estado

        # ── Transición PENDIENTE → RECIBIDA ──────────────────────────────────
        # Solo en este momento se actualiza el stock (igual que producción)
        if estado_anterior == "PENDIENTE" and nuevo_estado == "RECIBIDA":
            detalle_formset.save()
            try:
                for detalle in self.object.detalles.all():
                    procesar_detalle_compra(detalle)
            except StockInsuficienteError as e:
                # Revertir estado a PENDIENTE si algo falla
                self.object.estado = "PENDIENTE"
                self.object.save(update_fields=["estado"])
                messages.error(
                    self.request,
                    f"No se pudo marcar como recibida: {e}"
                )
                return redirect(self.success_url)

            messages.success(
                self.request,
                "Orden marcada como RECIBIDA — stock actualizado correctamente."
            )

        # ── Transición PENDIENTE / RECIBIDA → CANCELADA ───────────────────────
        elif nuevo_estado == "CANCELADA" and estado_anterior == "RECIBIDA":
            # Si estaba recibida y se cancela, revertir el stock
            detalle_formset.save()
            for detalle in self.object.detalles.all():
                revertir_detalle_compra(detalle)
            messages.warning(
                self.request,
                "Orden CANCELADA — el stock ha sido revertido."
            )

        elif nuevo_estado == "CANCELADA" and estado_anterior == "PENDIENTE":
            detalle_formset.save()
            messages.warning(
                self.request,
                "Orden CANCELADA — no afectó el stock (estaba pendiente)."
            )

        # ── Sin cambio de estado ──────────────────────────────────────────────
        else:
            # Bloquear edición de detalles si ya fue recibida o cancelada
            if estado_anterior in ("RECIBIDA", "CANCELADA"):
                messages.warning(
                    self.request,
                    f"La orden está {self.object.get_estado_display()} "
                    "y no puede modificar los productos."
                )
            else:
                detalle_formset.save()
                messages.success(self.request, "Orden de compra actualizada correctamente.")

        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar la orden. Verifique los datos.")
        return super().form_invalid(form)


# ── Eliminar ─────────────────────────────────────────────────────────────────
class OrdenCompraDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = OrdenCompra
    template_name = "compras/ordencompra_confirm_delete.html"
    success_url = reverse_lazy("compras:ordencompra_list")
    permission_required = "compras.delete_ordencompra"
    raise_exception = True

    def form_valid(self, form):
        orden = self.get_object()
        if orden.es_recibida:
            messages.error(
                self.request,
                "No se puede eliminar una orden ya RECIBIDA — afectaría el stock registrado."
            )
            return redirect(self.success_url)
        messages.success(self.request, "Orden de compra eliminada correctamente.")
        return super().form_valid(form)


# ── Detalle de Compra ─────────────────────────────────────────────────────────
class DetalleCompraListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = DetalleCompra
    template_name = "compras/detallecompra_list.html"
    permission_required = "compras.view_detallecompra"
    raise_exception = True
    context_object_name = "detalles"


# ── Proveedor ─────────────────────────────────────────────────────────────────
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


# ── Exportación CSV ───────────────────────────────────────────────────────────
@login_required
@permission_required('compras.view_ordencompra', raise_exception=True)
def exportar_compras_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="compras.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['ID', 'Proveedor', 'Fecha', 'Estado', 'Productos', 'Total'])

    for orden in OrdenCompra.objects.select_related('proveedor').prefetch_related(
        'detalles__producto'
    ).order_by('-fecha'):
        productos = ' | '.join(
            f"{d.cantidad}x {d.producto.nombre}" for d in orden.detalles.all()
        )
        writer.writerow([
            orden.id,
            orden.proveedor.nombre,
            orden.fecha,
            orden.get_estado_display(),
            productos,
            orden.get_total(),
        ])

    return response
