import csv
from django.http import HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Producto, Categoria
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages


class ProductoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Producto
    template_name = "inventario/producto_list.html"
    permission_required = "inventario.view_producto"
    raise_exception = True


class ProductoCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Producto
    fields = [
        'nombre', 'categoria', 'tipo',
        'precio_costo', 'precio_venta',
        'unidad_medida', 'stock', 'descripcion',
    ]
    template_name = "inventario/producto_form.html"
    success_url = reverse_lazy('inventario:producto_list')
    permission_required = "inventario.add_producto"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Producto registrado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al registrar el producto. Verifique los datos.")
        return super().form_invalid(form)


class ProductoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Producto
    fields = [
        'nombre', 'categoria', 'tipo',
        'precio_costo', 'precio_venta',
        'unidad_medida', 'stock', 'descripcion',
    ]
    template_name = "inventario/producto_form.html"
    success_url = reverse_lazy('inventario:producto_list')
    permission_required = "inventario.change_producto"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Producto actualizado correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar el producto. Verifique los datos.")
        return super().form_invalid(form)


class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Producto
    template_name = "inventario/producto_confirm_delete.html"
    success_url = reverse_lazy('inventario:producto_list')
    permission_required = "inventario.delete_producto"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Producto eliminado correctamente.")
        return super().form_valid(form)


class CategoriaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Categoria
    template_name = "inventario/categoria_list.html"
    permission_required = "inventario.view_categoria"
    raise_exception = True


class CategoriaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Categoria
    fields = ['nombre', 'descripcion']
    template_name = "inventario/categoria_form.html"
    success_url = reverse_lazy('inventario:categoria_list')
    permission_required = "inventario.add_categoria"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Categoría registrada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al registrar la categoría. Verifique los datos.")
        return super().form_invalid(form)


class CategoriaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Categoria
    fields = ['nombre', 'descripcion']
    template_name = "inventario/categoria_form.html"
    success_url = reverse_lazy('inventario:categoria_list')
    permission_required = "inventario.change_categoria"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Categoría actualizada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar la categoría. Verifique los datos.")
        return super().form_invalid(form)


class CategoriaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Categoria
    template_name = "inventario/categoria_confirm_delete.html"
    success_url = reverse_lazy('inventario:categoria_list')
    permission_required = "inventario.delete_categoria"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Categoría eliminada correctamente.")
        return super().form_valid(form)


# ── Exportación CSV ─────────────────────────────────────────────────────────────
@login_required
@permission_required('inventario.view_producto', raise_exception=True)
def exportar_inventario_csv(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="inventario.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Nombre', 'Categoría', 'Tipo',
        'Precio Costo', 'Precio Venta', 'Margen %',
        'Stock', 'Unidad de Medida', 'Descripción',
    ])

    for p in Producto.objects.select_related('categoria').order_by('nombre'):
        writer.writerow([
            p.id,
            p.nombre,
            p.categoria.nombre if p.categoria else '—',
            p.get_tipo_display(),
            p.precio_costo,
            p.precio_venta,
            f"{p.margen_ganancia}%" if p.margen_ganancia is not None else '—',
            p.stock,
            p.get_unidad_medida_display(),
            p.descripcion or '—',
        ])

    return response