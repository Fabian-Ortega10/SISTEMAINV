from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import RegistroAuditoria

class AuditoriaListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = RegistroAuditoria
    template_name = "auditoria/lista_auditoria.html"
    permission_required = "auditoria.view_registroauditoria"
    raise_exception = True


class AuditoriaCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = RegistroAuditoria
    template_name = "auditoria/auditoria_form.html"
    fields = "__all__"
    success_url = reverse_lazy("auditoria:auditoria_list")
    permission_required = "auditoria.add_registroauditoria"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Auditoría registrada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al registrar la auditoría. Verifique los datos.")
        return super().form_invalid(form)


class AuditoriaUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = RegistroAuditoria
    template_name = "auditoria/auditoria_form.html"
    fields = "__all__"
    success_url = reverse_lazy("auditoria:auditoria_list")
    permission_required = "auditoria.change_registroauditoria"
    raise_exception = True

    def form_valid(self, form):
        messages.success(self.request, "Auditoría actualizada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Error al actualizar la auditoría. Verifique los datos.")
        return super().form_invalid(form)


class AuditoriaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = RegistroAuditoria
    template_name = "auditoria/auditoria_confirm_delete.html"
    success_url = reverse_lazy("auditoria:auditoria_list")
    permission_required = "auditoria.delete_registroauditoria"
    raise_exception = True

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Auditoría eliminada correctamente.")
        return super().delete(request, *args, **kwargs)

