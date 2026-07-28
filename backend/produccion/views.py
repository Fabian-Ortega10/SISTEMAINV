from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.forms import inlineformset_factory, ModelChoiceField
from django.shortcuts import redirect
from django.utils import timezone

from .models import OrdenProduccion, ConsumoMateriaPrima, ProductoFinal
from inventario.models import Producto
from core.services.inventario import (
    finalizar_orden_produccion,
    StockInsuficienteError,
)


# ── Querysets filtrados por tipo ────────────────────────────────────────────────
# Solo materias primas aparecen en el formset de consumo
qs_materias_primas = Producto.objects.filter(
    tipo=Producto.TipoProducto.MATERIA_PRIMA
).order_by("nombre")

# Solo productos terminados aparecen en el formset de productos finales
qs_productos_terminados = Producto.objects.filter(
    tipo=Producto.TipoProducto.PRODUCTO_TERMINADO
).order_by("nombre")


# ── Formsets con querysets filtrados ────────────────────────────────────────────
ConsumoFormSet = inlineformset_factory(
    OrdenProduccion,
    ConsumoMateriaPrima,
    fields=["producto", "cantidad"],
    extra=1,
    can_delete=True,
)

ProductoFinalFormSet = inlineformset_factory(
    OrdenProduccion,
    ProductoFinal,
    fields=["producto", "cantidad"],
    extra=1,
    can_delete=True,
)


def _aplicar_querysets(formset, qs_materias, qs_terminados, es_consumo=True):
    """
    Restringe el queryset del campo 'producto' en cada form del formset
    según si es consumo (materias primas) o producto final (terminados).
    Se llama después de instanciar el formset.
    """
    qs = qs_materias if es_consumo else qs_terminados
    for form in formset.forms:
        form.fields["producto"].queryset = qs
        form.fields["producto"].label = (
            "Materia prima" if es_consumo else "Producto terminado"
        )


# ── Lista ─────────────────────────────────────────────────────────────────────
class OrdenProduccionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = OrdenProduccion
    template_name = "produccion/ordenproduccion_list.html"
    permission_required = "produccion.view_ordenproduccion"
    raise_exception = True
    context_object_name = "ordenes"


# ── Crear ─────────────────────────────────────────────────────────────────────
class OrdenProduccionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = OrdenProduccion
    fields = ['descripcion', 'estado']
    template_name = "produccion/ordenproduccion_form.html"
    success_url = reverse_lazy('produccion:ordenproduccion_list')
    permission_required = "produccion.add_ordenproduccion"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            consumo_fs = ConsumoFormSet(self.request.POST, prefix="consumo")
            final_fs   = ProductoFinalFormSet(self.request.POST, prefix="final")
        else:
            consumo_fs = ConsumoFormSet(prefix="consumo")
            final_fs   = ProductoFinalFormSet(prefix="final")

        # Aplicar filtros de tipo
        _aplicar_querysets(consumo_fs, qs_materias_primas, qs_productos_terminados, es_consumo=True)
        _aplicar_querysets(final_fs,   qs_materias_primas, qs_productos_terminados, es_consumo=False)

        context["consumo_formset"] = consumo_fs
        context["final_formset"]   = final_fs
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        consumo_formset = context["consumo_formset"]
        final_formset   = context["final_formset"]

        form.instance.estado = "PENDIENTE"

        if consumo_formset.is_valid() and final_formset.is_valid():
            self.object = form.save()
            consumo_formset.instance = self.object
            final_formset.instance   = self.object
            consumo_formset.save()
            final_formset.save()
            messages.success(self.request, "Orden de producción registrada correctamente.")
            return redirect(self.success_url)
        else:
            messages.error(self.request, "Revisa los materiales y productos ingresados.")
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.error(self.request, "Error al registrar la orden de producción. Verifique los datos.")
        return super().form_invalid(form)


# ── Editar / Finalizar ──────────────────────────────────────────────────────────
class OrdenProduccionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = OrdenProduccion
    fields = ['descripcion', 'estado']
    template_name = "produccion/ordenproduccion_form.html"
    success_url = reverse_lazy('produccion:ordenproduccion_list')
    permission_required = "produccion.change_ordenproduccion"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            consumo_fs = ConsumoFormSet(self.request.POST, instance=self.object, prefix="consumo")
            final_fs   = ProductoFinalFormSet(self.request.POST, instance=self.object, prefix="final")
        else:
            consumo_fs = ConsumoFormSet(instance=self.object, prefix="consumo")
            final_fs   = ProductoFinalFormSet(instance=self.object, prefix="final")

        # Aplicar filtros de tipo
        _aplicar_querysets(consumo_fs, qs_materias_primas, qs_productos_terminados, es_consumo=True)
        _aplicar_querysets(final_fs,   qs_materias_primas, qs_productos_terminados, es_consumo=False)

        context["consumo_formset"] = consumo_fs
        context["final_formset"]   = final_fs
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        consumo_formset = context["consumo_formset"]
        final_formset   = context["final_formset"]

        if not (consumo_formset.is_valid() and final_formset.is_valid()):
            messages.error(self.request, "Revisa los materiales y productos ingresados.")
            return self.render_to_response(self.get_context_data(form=form))

        orden = self.object
        estado_anterior = OrdenProduccion.objects.values_list(
            'estado', flat=True
        ).get(pk=orden.pk)

        if orden.ya_finalizada:
            if form.cleaned_data["estado"] != "FINALIZADA":
                messages.error(
                    self.request,
                    "Esta orden ya fue finalizada y no puede regresar a 'Pendiente'."
                )
                return self.render_to_response(self.get_context_data(form=form))

            form.instance.estado = "FINALIZADA"
            self.object = form.save()
            messages.warning(
                self.request,
                "La orden ya estaba finalizada. Los materiales y productos no se modificaron."
            )
            return redirect(self.success_url)

        self.object = form.save()
        consumo_formset.instance = self.object
        final_formset.instance   = self.object
        consumo_formset.save()
        final_formset.save()

        nuevo_estado = self.object.estado

        if estado_anterior != "FINALIZADA" and nuevo_estado == "FINALIZADA":
            try:
                finalizar_orden_produccion(self.object)
            except StockInsuficienteError as e:
                self.object.estado = "PENDIENTE"
                self.object.save(update_fields=["estado"])
                messages.error(self.request, f"No se pudo finalizar la orden: {e}")
                return redirect(self.success_url)

            self.object.finalizada_en = timezone.now()
            self.object.save(update_fields=["finalizada_en"])
            messages.success(
                self.request,
                "Orden finalizada: stock actualizado (materias primas descontadas, "
                "productos finales agregados)."
            )
        else:
            messages.success(self.request, "Orden de producción actualizada correctamente.")

        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar la orden. Verifique los datos.")
        return super().form_invalid(form)


# ── Eliminar ─────────────────────────────────────────────────────────────────
class OrdenProduccionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = OrdenProduccion
    template_name = "produccion/ordenproduccion_confirm_delete.html"
    success_url = reverse_lazy('produccion:ordenproduccion_list')
    permission_required = "produccion.delete_ordenproduccion"
    raise_exception = True

    def form_valid(self, form):
        if self.get_object().ya_finalizada:
            messages.error(
                self.request,
                "No se puede eliminar una orden ya finalizada (afectaría el stock registrado)."
            )
            return redirect(self.success_url)
        messages.success(self.request, "Orden de producción eliminada correctamente.")
        return super().form_valid(form)