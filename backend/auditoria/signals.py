from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
 
# ── Importaciones de modelos de negocio ───────────────────────────────────────
from inventario.models import Categoria, Producto
from ventas.models import Cliente, Venta, DetalleVenta
from compras.models import Proveedor, OrdenCompra, DetalleCompra
from produccion.models import OrdenProduccion
from contabilidad.models import MovimientoContable
 
from .models import RegistroAuditoria
from .middleware import get_current_user  # ver middleware.py más abajo
 
 
# ── Utilidad interna ──────────────────────────────────────────────────────────
 
def _registrar(accion: str, modelo: str, objeto_id: int, detalle: str) -> None:
    """Crea un RegistroAuditoria capturando el usuario del request actual."""
    usuario = get_current_user()
    username = usuario.username if usuario and usuario.is_authenticated else None
    RegistroAuditoria.objects.create(
        accion=accion,
        modelo=modelo,
        objeto_id=objeto_id,
        usuario=username,
        detalle=detalle,
    )
 
 
# ── Generador de handlers para evitar repetición ─────────────────────────────
 
def _make_save_handler(nombre_modelo: str, label_fn):
    """
    Devuelve un handler post_save que registra CREAR o ACTUALIZAR.
    label_fn(instance) → str  debe retornar la descripción legible del objeto.
    """
    def handler(sender, instance, created, **kwargs):
        accion = "CREAR" if created else "ACTUALIZAR"
        _registrar(accion, nombre_modelo, instance.pk, f"{accion} {label_fn(instance)}")
    return handler
 
 
def _make_delete_handler(nombre_modelo: str, label_fn):
    """Devuelve un handler post_delete que registra ELIMINAR."""
    def handler(sender, instance, **kwargs):
        _registrar("ELIMINAR", nombre_modelo, instance.pk, f"ELIMINAR {label_fn(instance)}")
    return handler
 
 
# ── Registro de signals ───────────────────────────────────────────────────────
 
_MODELOS = [
    # (Clase,            nombre_str,       label_fn)
    (Categoria,         "Categoria",       lambda o: f"categoría '{o.nombre}'"),
    (Producto,          "Producto",        lambda o: f"producto '{o.nombre}'"),
    (Cliente,           "Cliente",         lambda o: f"cliente '{o.nombre}'"),
    (Venta,             "Venta",           lambda o: f"venta #{o.pk} — {o.cliente}"),
    (DetalleVenta,      "DetalleVenta",    lambda o: f"{o.cantidad}×{o.producto.nombre} (venta #{o.venta_id})"),
    (Proveedor,         "Proveedor",       lambda o: f"proveedor '{o.nombre}'"),
    (OrdenCompra,       "OrdenCompra",     lambda o: f"orden compra #{o.pk} — {o.proveedor}"),
    (DetalleCompra,     "DetalleCompra",   lambda o: f"{o.cantidad}×{o.producto.nombre} (orden #{o.orden_id})"),
    (OrdenProduccion,   "OrdenProduccion", lambda o: f"orden producción #{o.pk} [{o.estado}]"),
    (MovimientoContable,"MovimientoContable", lambda o: f"movimiento {o.tipo} ${o.monto}"),
]
 
for _model_class, _nombre, _label_fn in _MODELOS:
    post_save.connect(
        _make_save_handler(_nombre, _label_fn),
        sender=_model_class,
        weak=False,
        dispatch_uid=f"audit_save_{_nombre}",
    )
    post_delete.connect(
        _make_delete_handler(_nombre, _label_fn),
        sender=_model_class,
        weak=False,
        dispatch_uid=f"audit_delete_{_nombre}",
    )