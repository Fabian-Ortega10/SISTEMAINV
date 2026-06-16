from django.test import TestCase
from inventario.models import Categoria, Producto
from auditoria.models import RegistroAuditoria

class AuditoriaTestCase(TestCase):
    def test_registro_creacion_producto(self):
        cat = Categoria.objects.create(nombre="Electrónica")
        prod = Producto.objects.create(nombre="Laptop", categoria=cat, precio=3000, stock=10)
        registro = RegistroAuditoria.objects.filter(modelo="Producto", objeto_id=prod.id).first()
        self.assertIsNotNone(registro)
        self.assertEqual(registro.accion, "CREAR")

    def test_registro_eliminacion_producto(self):
        cat = Categoria.objects.create(nombre="Electrónica")
        prod = Producto.objects.create(nombre="Tablet", categoria=cat, precio=1500, stock=5)
        prod_id = prod.id
        prod.delete()
        registro = RegistroAuditoria.objects.filter(modelo="Producto", objeto_id=prod_id).first()
        self.assertIsNotNone(registro)
        self.assertEqual(registro.accion, "ELIMINAR")
