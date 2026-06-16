from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from inventario.models import Producto, Categoria
from compras.models import OrdenCompra, DetalleCompra
from ventas.models import Venta, DetalleVenta
from auditoria.models import RegistroAuditoria
from contabilidad.models import MovimientoContable
from produccion.models import OrdenProduccion, ConsumoMateriaPrima, ProductoFinal

class Command(BaseCommand):
    help = "Crea grupos de usuarios y asigna permisos"

    def handle(self, *args, **kwargs):
        # Admin: acceso completo
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        admin_group.permissions.set(Permission.objects.all())

        # Vendedor: acceso a Inventario y Ventas
        vendedor_group, _ = Group.objects.get_or_create(name="Vendedor")
        inventario_ct = ContentType.objects.get_for_model(Producto)
        ventas_ct = ContentType.objects.get_for_model(Venta)
        detalle_ct = ContentType.objects.get_for_model(DetalleVenta)
        permisos_vendedor = Permission.objects.filter(content_type__in=[inventario_ct, ventas_ct, detalle_ct])
        vendedor_group.permissions.set(permisos_vendedor)

        # Auditor: acceso solo a Auditoría
        auditor_group, _ = Group.objects.get_or_create(name="Auditor")
        auditor_ct = ContentType.objects.get_for_model(RegistroAuditoria)
        permisos_auditor = Permission.objects.filter(content_type=auditor_ct)
        auditor_group.permissions.set(permisos_auditor)

        # Inventarista: acceso a Inventario, Compras y Producción
        inventarista_group, _ = Group.objects.get_or_create(name="Inventarista")

        producto_ct = ContentType.objects.get_for_model(Producto)
        categoria_ct = ContentType.objects.get_for_model(Categoria)
        orden_ct = ContentType.objects.get_for_model(OrdenCompra)
        detalle_ct = ContentType.objects.get_for_model(DetalleCompra)

        ordenprod_ct = ContentType.objects.get_for_model(OrdenProduccion)
        consumo_ct = ContentType.objects.get_for_model(ConsumoMateriaPrima)
        final_ct = ContentType.objects.get_for_model(ProductoFinal)

        permisos_inventarista = Permission.objects.filter(
        content_type__in=[producto_ct, categoria_ct, orden_ct, detalle_ct,
                      ordenprod_ct, consumo_ct, final_ct]
        )

        inventarista_group.permissions.set(permisos_inventarista)

        #Contador: Acceso a Contabilidad
        contador_group, _ = Group.objects.get_or_create(name="Contador")
        contabilidad_ct = ContentType.objects.get_for_model(MovimientoContable)
        permisos_contador = Permission.objects.filter(content_type=contabilidad_ct)
        contador_group.permissions.set(permisos_contador)

        self.stdout.write(self.style.SUCCESS("Grupos creados y permisos asignados"))
