from django.db import models
from django.db import transaction

from aplicaciones.cliente.models import Cliente


class OrdenTrabajo(models.Model):
    registro_id = models.AutoField(primary_key=True)
    cliente_id = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    cod_trabajo = models.CharField(max_length=15, unique=True, blank=True)
    fecha_ingreso = models.DateField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,  # Añadido max_length
        choices=[
            ('Recibido', 'Recibido'),
            ('En Diagnostico', 'En Diagnóstico'),
            ('En Proceso', 'En Proceso'),
            ('Terminado', 'Terminado'),
            ('No retirado', 'No retirado'),
            ('Entregado', 'Entregado'),
            ('Cancelado', 'Cancelado'),
            ('Falta de pago', 'Falta de pago')
        ],
        default='Recibido'
    )
    fecha_entrega_estimada = models.DateField(blank=True, null=True)

    equipos = models.ManyToManyField(
        'Equipo',
        through='OrdenTrabajoEquipo',
        related_name='ordenes_trabajo',
        blank=True,
    )

    class Meta:
        verbose_name = 'Orden de Trabajo'
        verbose_name_plural = 'Órdenes de Trabajo'
        ordering = ['-fecha_ingreso']

    def save(self, *args, **kwargs):
        if not self.cod_trabajo:
            with transaction.atomic():
                # Obtener el último número de orden de forma segura
                last_orden = OrdenTrabajo.objects.select_for_update().order_by('-registro_id').first()
                if last_orden and last_orden.registro_id:
                    next_number = last_orden.registro_id + 1
                else:
                    next_number = 1
                self.cod_trabajo = f'ORDEN-{next_number:06d}'
        super().save(*args, **kwargs)

    def agregar_equipo(self, equipo, observaciones=""):
        """
        Método para agregar un equipo a la orden de trabajo
        """
        orden_equipo, created = OrdenTrabajoEquipo.objects.get_or_create(
            orden=self,
            equipo=equipo,
            defaults={'observaciones': observaciones}
        )
        return orden_equipo, created

    def remover_equipo(self, equipo):
        """
        Método para remover un equipo de la orden de trabajo
        """
        try:
            orden_equipo = OrdenTrabajoEquipo.objects.get(orden=self, equipo=equipo)
            orden_equipo.delete()
            return True
        except OrdenTrabajoEquipo.DoesNotExist:
            return False

    def get_equipos_con_detalles(self):
        """
        Obtiene todos los equipos con sus detalles de asociación
        """
        return OrdenTrabajoEquipo.objects.filter(orden=self).select_related('equipo')

    def __str__(self):
        return f"{self.cod_trabajo} - {self.cliente_id.persona_id.nombre} {self.cliente_id.persona_id.apellido}"

class Equipo(models.Model):
    TIPOS_EQUIPO = [
        ('Motor', 'Motor Eléctrico'),
        ('Bomba', 'Bomba'),
        ('Ventilador', 'Ventilador'),
        ('Compresor', 'Compresor'),
        ('Generador', 'Generador'),
        ('Transformador', 'Transformador'),
        ('Otro', 'Otro'),
    ]

    FASES = [
        (1, 'Monofásico'),
        (2, 'Bifásico'),
        (3, 'Trifásico'),
    ]

    equipo_id = models.AutoField(primary_key=True)
    cliente_id = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo_equipo = models.CharField(max_length=100, choices=TIPOS_EQUIPO, default='Motor')
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50, blank=True)
    descripcion_falla = models.TextField(blank=True)
    diagnostico = models.TextField(blank=True)
    solucion = models.TextField(blank=True)
    potencia_hp_kw = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Potencia en HP o KW"
    )
    voltaje = models.PositiveIntegerField(null=True, blank=True, help_text="Voltaje en V")
    rpm = models.PositiveIntegerField(null=True, blank=True, help_text="Revoluciones por minuto")
    fase = models.PositiveIntegerField(choices=FASES, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    fecha_diagnostico = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'
        ordering = ['tipo_equipo', 'marca', 'modelo']

    def get_ordenes_activas(self):
        """
        Obtiene las órdenes de trabajo activas para este equipo
        """
        return self.ordenes_trabajo.exclude(
            estado__in=['Entregado', 'Cancelado']
        )

    def get_historial_ordenes(self):
        """
        Obtiene el historial completo de órdenes para este equipo
        """
        return OrdenTrabajoEquipo.objects.filter(equipo=self).select_related('orden').order_by('-fecha_asociacion')

    def esta_en_orden_activa(self):
        """
        Verifica si el equipo está en alguna orden activa
        """
        return self.get_ordenes_activas().exists()

    def __str__(self):
        modelo_str = f" {self.modelo}" if self.modelo else ""
        return f"{self.tipo_equipo} - {self.marca}{modelo_str}"

class OrdenTrabajoEquipo(models.Model):
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name='orden_equipos')
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='equipo_ordenes')
    fecha_asociacion = models.DateTimeField(auto_now_add=True)  # Cambiado a DateTime para más precisión
    observaciones = models.TextField(blank=True, null=True)
    estado_equipo_en_orden = models.CharField(
        max_length=20,
        choices=[
            ('Pendiente', 'Pendiente'),
            ('En Diagnóstico', 'En Diagnóstico'),
            ('En Reparación', 'En Reparación'),
            ('Reparado', 'Reparado'),
            ('No Reparable', 'No Reparable'),
        ],
        default='Pendiente'
    )
    costo_reparacion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Costo de reparación para este equipo específico"
    )

    class Meta:
        unique_together = ('orden', 'equipo')
        verbose_name = 'Equipo en Orden de Trabajo'
        verbose_name_plural = 'Equipos en Órdenes de Trabajo'
        ordering = ['fecha_asociacion']

    def __str__(self):
        return f"{self.equipo} en {self.orden.cod_trabajo}"

class OrdenTrabajoManager:
    """
    Clase de utilidad para manejar operaciones complejas de órdenes de trabajo
    """

    @staticmethod
    def crear_orden_con_equipos(cliente, equipos_data):
        """
        Crea una orden de trabajo con múltiples equipos
        """
        with transaction.atomic():
            # Verificación: evitar agregar equipos ya asociados a órdenes activas
            for equipo_data in equipos_data:
                equipo = equipo_data.get('equipo')
                if equipo.esta_en_orden_activa():
                    raise ValueError(f"El equipo '{equipo}' ya está en una orden activa.")

            orden = OrdenTrabajo.objects.create(cliente_id=cliente)

            for equipo_data in equipos_data:
                equipo = equipo_data.get('equipo')
                observaciones = equipo_data.get('observaciones', '')
                OrdenTrabajoEquipo.objects.create(
                    orden=orden,
                    equipo=equipo,
                    observaciones=observaciones
                )

            return orden

    @staticmethod
    def transferir_equipo(equipo, orden_origen, orden_destino, observaciones=""):
        """
        Transfiere un equipo de una orden a otra
        """
        with transaction.atomic():
            # Remover de la orden origen
            OrdenTrabajoEquipo.objects.filter(
                orden=orden_origen,
                equipo=equipo
            ).delete()

            # Agregar a la orden destino
            OrdenTrabajoEquipo.objects.create(
                orden=orden_destino,
                equipo=equipo,
                observaciones=observaciones
            )