from django.test import TestCase
from inventario.models import Categoria, Producto
from contabilidad.models import MovimientoContable
from .models import Cliente, Venta, DetalleVenta

class VentasTestCase(TestCase):
    def setUp(self):
        cat = Categoria.objects.create(nombre="Electrónica")
        self.prod = Producto.objects.create(nombre="Laptop", categoria=cat, precio=3000, stock=10)
        self.cli = Cliente.objects.create(nombre="ClienteX")
        self.venta = Venta.objects.create(cliente=self.cli)

    def test_venta_disminuye_stock_y_registra_ingreso(self):
        detalle = DetalleVenta.objects.create(
            venta=self.venta,
            producto=self.prod,
            cantidad=2,
            precio_unitario=3000
        )
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.stock, 8)  # stock inicial 10 - 2
        ingreso = MovimientoContable.objects.filter(tipo="INGRESO").first()
        self.assertIsNotNone(ingreso)
        self.assertEqual(float(ingreso.monto), 6000.0)
