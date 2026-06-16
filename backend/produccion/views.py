from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.forms import inlineformset_factory
from django.shortcuts import redirect
from django.utils import timezone

from .models import OrdenProduccion, ConsumoMateriaPrima, ProductoFinal
from core.services.inventario import (
    finalizar_orden_produccion,
    StockInsuficienteError,
)


# ── Formsets ────────────────────────────────────────────────────────────────────
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
            context["consumo_formset"] = ConsumoFormSet(self.request.POST, prefix="consumo")
            context["final_formset"] = ProductoFinalFormSet(self.request.POST, prefix="final")
        else:
            context["consumo_formset"] = ConsumoFormSet(prefix="consumo")
            context["final_formset"] = ProductoFinalFormSet(prefix="final")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        consumo_formset = context["consumo_formset"]
        final_formset = context["final_formset"]

        # Una orden nueva nunca puede crearse ya FINALIZADA directamente.
        # Forzamos PENDIENTE al crear; la finalización se hace después,
        # editando la orden, para garantizar que los formsets ya existen.
        form.instance.estado = "PENDIENTE"

        if consumo_formset.is_valid() and final_formset.is_valid():
            self.object = form.save()
            consumo_formset.instance = self.object
            final_formset.instance = self.object
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
            context["consumo_formset"] = ConsumoFormSet(
                self.request.POST, instance=self.object, prefix="consumo"
            )
            context["final_formset"] = ProductoFinalFormSet(
                self.request.POST, instance=self.object, prefix="final"
            )
        else:
            context["consumo_formset"] = ConsumoFormSet(instance=self.object, prefix="consumo")
            context["final_formset"] = ProductoFinalFormSet(instance=self.object, prefix="final")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        consumo_formset = context["consumo_formset"]
        final_formset = context["final_formset"]

        if not (consumo_formset.is_valid() and final_formset.is_valid()):
            messages.error(self.request, "Revisa los materiales y productos ingresados.")
            return self.render_to_response(self.get_context_data(form=form))

        orden = self.object
        # Leer el estado REAL desde BD antes de que el form lo sobreescriba
        estado_anterior = OrdenProduccion.objects.values_list('estado', flat=True).get(pk=orden.pk)

        # Si la orden ya estaba finalizada, no se permite editar materiales/productos
        # ni volver a finalizar (evita doble descuento/ingreso de stock).
        if orden.ya_finalizada:
            # Bloqueamos cambios de estado y de líneas; solo se permite
            # actualizar la descripción.
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

        # Orden aún no finalizada: guardamos cambios normales primero
        self.object = form.save()
        consumo_formset.instance = self.object
        final_formset.instance = self.object
        consumo_formset.save()
        final_formset.save()

        nuevo_estado = self.object.estado

        # Transición PENDIENTE -> FINALIZADA: ejecutar el ajuste de stock
        if estado_anterior != "FINALIZADA" and nuevo_estado == "FINALIZADA":
            try:
                finalizar_orden_produccion(self.object)
            except StockInsuficienteError as e:
                # Revertimos el estado a PENDIENTE: no hay suficiente
                # materia prima para finalizar esta orden todavía.
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
        messages.error(self.request, "Error al actualizar la orden de producción. Verifique los datos.")
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