from django.test import TestCase
from .models import Categoria, Producto

class InventarioTestCase(TestCase):
    def setUp(self):
        self.cat = Categoria.objects.create(nombre="Electrónica")
        self.prod = Producto.objects.create(
            nombre="Laptop",
            categoria=self.cat,
            precio=3000,
            stock=10
        )

    def test_crear_producto(self):
        self.assertEqual(self.prod.nombre, "Laptop")
        self.assertEqual(self.prod.stock, 10)

    def test_actualizar_stock(self):
        self.prod.stock += 5
        self.prod.save()
        self.assertEqual(self.prod.stock, 15)
