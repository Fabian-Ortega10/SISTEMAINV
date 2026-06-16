from django.urls import path
from .views import AuditoriaListView

app_name = "auditoria"

urlpatterns = [
    # Vista principal: lista de registros de auditoría
    path('', AuditoriaListView.as_view(), name='auditoria_list'),
]
