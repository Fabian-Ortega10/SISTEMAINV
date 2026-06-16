from django.core.management.base import BaseCommand
from django.db import models
from contabilidad.models import MovimientoContable

class Command(BaseCommand):
    help = "Genera un reporte contable básico (balance y flujo de caja)"

    def handle(self, *args, **kwargs):
        ingresos = MovimientoContable.objects.filter(tipo='INGRESO').aggregate(total=models.Sum('monto'))['total'] or 0
        egresos = MovimientoContable.objects.filter(tipo='EGRESO').aggregate(total=models.Sum('monto'))['total'] or 0
        balance = ingresos - egresos

        self.stdout.write(self.style.SUCCESS("=== REPORTE CONTABLE ==="))
        self.stdout.write(f"Ingresos: {ingresos}")
        self.stdout.write(f"Egresos: {egresos}")
        self.stdout.write(f"Balance: {balance}")
        self.stdout.write("\n=== Flujo de Caja ===")
        for mov in MovimientoContable.objects.order_by('fecha'):
            self.stdout.write(f"{mov.fecha} | {mov.tipo} | {mov.descripcion} | {mov.monto}")
