from django.test import TestCase
from inventario.models import Categoria, Producto
from .models import Proveedor, OrdenCompra, DetalleCompra

class ComprasTestCase(TestCase):
    def setUp(self):
        cat = Categoria.objects.create(nombre="Electrónica")
        self.prod = Producto.objects.create(nombre="Laptop", categoria=cat, precio=3000, stock=10)
        self.prov = Proveedor.objects.create(nombre="ProveedorX")
        self.orden = OrdenCompra.objects.create(proveedor=self.prov)

    def test_compra_aumenta_stock(self):
        detalle = DetalleCompra.objects.create(
            orden=self.orden,
            producto=self.prod,
            cantidad=5,
            precio_unitario=2500
        )
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.stock, 15)  # stock inicial 10 + 5

