from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone

from inventario.models import Producto
from ventas.models import Venta
from compras.models import OrdenCompra
from contabilidad.models import MovimientoContable
from produccion.models import OrdenProduccion


@login_required
def dashboard(request):
    hoy = timezone.now().date()

    # ── Inventario ─────────────────────────────────────────────────────────────
    total_productos = Producto.objects.count()
    # Stock bajo: productos con stock menor o igual a 5
    productos_stock_bajo = Producto.objects.filter(stock__lte=5).order_by("stock")

    # ── Ventas ─────────────────────────────────────────────────────────────────
    ventas_hoy = Venta.objects.filter(fecha=hoy).count()
    total_ventas = Venta.objects.count()

    # ── Compras ────────────────────────────────────────────────────────────────
    total_compras = OrdenCompra.objects.count()

    # ── Producción ─────────────────────────────────────────────────────────────
    ordenes_pendientes = OrdenProduccion.objects.filter(estado="PENDIENTE").count()
    ordenes_finalizadas = OrdenProduccion.objects.filter(estado="FINALIZADA").count()

    # ── Contabilidad ───────────────────────────────────────────────────────────
    ingresos = MovimientoContable.objects.filter(tipo="INGRESO").aggregate(
        total=Sum("monto")
    )["total"] or 0
    egresos = MovimientoContable.objects.filter(tipo="EGRESO").aggregate(
        total=Sum("monto")
    )["total"] or 0
    balance = ingresos - egresos

    # ── Últimas ventas ─────────────────────────────────────────────────────────
    ultimas_ventas = Venta.objects.select_related("cliente").order_by("-fecha")[:5]

    context = {
        "total_productos": total_productos,
        "productos_stock_bajo": productos_stock_bajo,
        "ventas_hoy": ventas_hoy,
        "total_ventas": total_ventas,
        "total_compras": total_compras,
        "ordenes_pendientes": ordenes_pendientes,
        "ordenes_finalizadas": ordenes_finalizadas,
        "ingresos": ingresos,
        "egresos": egresos,
        "balance": balance,
        "ultimas_ventas": ultimas_ventas,
        "hoy": hoy,
    }
    return render(request, "dashboard.html", context)