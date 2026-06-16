from django.test import TestCase
from .models import MovimientoContable

class ContabilidadTestCase(TestCase):
    def test_crear_ingreso(self):
        ingreso = MovimientoContable.objects.create(
            tipo="INGRESO",
            descripcion="Venta de prueba",
            monto=5000
        )
        self.assertEqual(ingreso.tipo, "INGRESO")
        self.assertEqual(float(ingreso.monto), 5000.0)

    def test_crear_egreso(self):
        egreso = MovimientoContable.objects.create(
            tipo="EGRESO",
            descripcion="Compra de prueba",
            monto=2000
        )
        self.assertEqual(egreso.tipo, "EGRESO")
        self.assertEqual(float(egreso.monto), 2000.0)
