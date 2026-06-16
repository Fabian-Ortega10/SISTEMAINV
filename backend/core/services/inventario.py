from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from contabilidad.models import MovimientoContable
from inventario.models import Producto


class StockInsuficienteError(ValidationError):
    """Se lanza cuando no hay stock suficiente para una operación."""


def _ajustar_stock(producto_id: int, delta: int) -> Producto:
    """Bloquea la fila del producto y ajusta stock de forma atómica."""
    producto = Producto.objects.select_for_update().get(pk=producto_id)
    nuevo_stock = producto.stock + delta
    if nuevo_stock < 0:
        raise StockInsuficienteError(
            f"Stock insuficiente para '{producto.nombre}'. "
            f"Disponible: {producto.stock}, solicitado: {abs(delta)}."
        )
    producto.stock = nuevo_stock
    producto.save(update_fields=["stock"])
    return producto


def _registrar_movimiento(tipo: str, descripcion: str, monto: Decimal) -> None:
    MovimientoContable.objects.create(
        tipo=tipo,
        descripcion=descripcion,
        monto=monto,
    )


# ── Compras ──────────────────────────────────────────────────────────────────

@transaction.atomic
def procesar_detalle_compra(detalle) -> None:
    """
    Ejecutar SOLO al crear un DetalleCompra.
    Aumenta stock y registra egreso contable.
    """
    producto = _ajustar_stock(detalle.producto_id, detalle.cantidad)
    monto = detalle.cantidad * detalle.precio_unitario
    _registrar_movimiento(
        tipo="EGRESO",
        descripcion=(
            f"Compra: {detalle.cantidad} x {producto.nombre} "
            f"(Orden #{detalle.orden_id})"
        ),
        monto=monto,
    )


@transaction.atomic
def revertir_detalle_compra(detalle) -> None:
    """Ejecutar al eliminar un DetalleCompra. Revierte stock y egreso."""
    producto = _ajustar_stock(detalle.producto_id, -detalle.cantidad)
    monto = detalle.cantidad * detalle.precio_unitario
    _registrar_movimiento(
        tipo="INGRESO",
        descripcion=(
            f"Reversión compra: {detalle.cantidad} x {producto.nombre} "
            f"(Orden #{detalle.orden_id})"
        ),
        monto=monto,
    )


# ── Ventas ───────────────────────────────────────────────────────────────────

@transaction.atomic
def procesar_detalle_venta(detalle) -> None:
    """
    Ejecutar SOLO al crear un DetalleVenta.
    Disminuye stock y registra ingreso contable.
    """
    producto = _ajustar_stock(detalle.producto_id, -detalle.cantidad)
    monto = detalle.cantidad * detalle.precio_unitario
    _registrar_movimiento(
        tipo="INGRESO",
        descripcion=(
            f"Venta: {detalle.cantidad} x {producto.nombre} "
            f"(Venta #{detalle.venta_id})"
        ),
        monto=monto,
    )


@transaction.atomic
def revertir_detalle_venta(detalle) -> None:
    """Ejecutar al eliminar un DetalleVenta. Revierte stock e ingreso."""
    producto = _ajustar_stock(detalle.producto_id, detalle.cantidad)
    monto = detalle.cantidad * detalle.precio_unitario
    _registrar_movimiento(
        tipo="EGRESO",
        descripcion=(
            f"Reversión venta: {detalle.cantidad} x {producto.nombre} "
            f"(Venta #{detalle.venta_id})"
        ),
        monto=monto,
    )


# ── Producción ──────────────────────────────────────────────────────────────
#
# Filosofía: las filas de ConsumoMateriaPrima y ProductoFinal NO afectan
# stock al crearse (la orden puede estar en planeación y modificarse).
# El stock se ajusta UNA SOLA VEZ, cuando la orden pasa a estado FINALIZADA,
# mediante finalizar_orden_produccion().

@transaction.atomic
def finalizar_orden_produccion(orden) -> None:
    """
    Ejecutar cuando una OrdenProduccion cambia su estado a FINALIZADA.

    - Descuenta del stock cada ConsumoMateriaPrima (valida que haya
      suficiente materia prima; si no, lanza StockInsuficienteError
      y revierte toda la transacción).
    - Aumenta el stock de cada ProductoFinal generado.
    - Registra movimientos contables de egreso (consumo de materiales)
      e ingreso (valor de producción) si se desea trazabilidad contable.

    Esta función es idempotente a nivel de uso: debe llamarse una sola
    vez por orden. La vista es responsable de no volver a llamarla si
    la orden ya estaba FINALIZADA (ver OrdenProduccionUpdateView).
    """
    # 1. Descontar materias primas consumidas
    for consumo in orden.consumomateriaprima_set.select_related("producto"):
        producto = _ajustar_stock(consumo.producto_id, -consumo.cantidad)
        monto = consumo.cantidad * producto.precio
        _registrar_movimiento(
            tipo="EGRESO",
            descripcion=(
                f"Producción: consumo {consumo.cantidad} x {producto.nombre} "
                f"(Orden Prod. #{orden.id})"
            ),
            monto=monto,
        )

    # 2. Aumentar stock de productos finales generados
    for final in orden.productofinal_set.select_related("producto"):
        producto = _ajustar_stock(final.producto_id, final.cantidad)
        monto = final.cantidad * producto.precio
        _registrar_movimiento(
            tipo="INGRESO",
            descripcion=(
                f"Producción: ingreso {final.cantidad} x {producto.nombre} "
                f"(Orden Prod. #{orden.id})"
            ),
            monto=monto,
        )