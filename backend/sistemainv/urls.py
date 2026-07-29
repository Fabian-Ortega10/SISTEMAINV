"""
URL configuration for sistemainv project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import dashboard

urlpatterns = [
    # Dashboard
    path('', dashboard, name='dashboard'),

    path('admin/', admin.site.urls),

    # ── Autenticación ─────────────────────────────────────────────────────────
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='registration/login.html'),
         name='login'),

    path('accounts/logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),

    # ── Recuperación de contraseña (4 pasos de Django) ────────────────────────
    # 1. Formulario: el usuario ingresa su correo
    path('accounts/password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/',
         ),
         name='password_reset'),

    # 2. Confirmación: "Te enviamos el correo"
    path('accounts/password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html',
         ),
         name='password_reset_done'),

    # 3. Enlace del correo: el usuario ingresa la nueva contraseña
    path('accounts/password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/accounts/password-reset/complete/',
         ),
         name='password_reset_confirm'),

    # 4. Éxito: contraseña cambiada correctamente
    path('accounts/password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html',
         ),
         name='password_reset_complete'),

    # ── Módulos ────────────────────────────────────────────────────────────────
    path('inventario/',   include('inventario.urls')),
    path('compras/',      include('compras.urls')),
    path('produccion/',   include('produccion.urls')),
    path('ventas/',       include('ventas.urls')),
    path('contabilidad/', include('contabilidad.urls')),
    path('auditoria/',    include('auditoria.urls')),
]