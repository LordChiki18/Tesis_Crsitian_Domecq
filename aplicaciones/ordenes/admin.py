from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.forms import Textarea
from .models import OrdenTrabajo, Equipo, OrdenTrabajoEquipo


# Inline para manejar equipos dentro de una orden de trabajo
class OrdenTrabajoEquipoInline(admin.TabularInline):
    model = OrdenTrabajoEquipo
    extra = 1  # Líneas extra para agregar nuevos equipos
    autocomplete_fields = ['equipo']  # Para búsqueda rápida de equipos

    fields = ('equipo', 'estado_equipo_en_orden', 'observaciones', 'costo_reparacion', 'fecha_asociacion')
    readonly_fields = ('fecha_asociacion',)

    # Personalizar el widget para observaciones
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 40})},
    }

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('equipo')


# Inline inverso para ver órdenes desde un equipo
class EquipoOrdenTrabajoInline(admin.TabularInline):
    model = OrdenTrabajoEquipo
    extra = 0
    autocomplete_fields = ['orden']

    fields = ('orden', 'estado_equipo_en_orden', 'observaciones', 'costo_reparacion', 'fecha_asociacion')
    readonly_fields = ('fecha_asociacion',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('orden').order_by('-fecha_asociacion')


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    list_display = (
        'cod_trabajo',
        'cliente_nombre',
        'estado',
        'fecha_ingreso',
        'fecha_entrega_estimada',
        'cantidad_equipos',
        'estado_color'
    )

    list_filter = (
        'estado',
        'fecha_ingreso',
        'fecha_entrega_estimada',
        ('cliente_id', admin.RelatedOnlyFieldListFilter),
    )

    search_fields = (
        'cod_trabajo',
        'cliente_id__persona_id__nombre',
        'cliente_id__persona_id__apellido',
    )

    # Comentar autocomplete_fields si Cliente no tiene admin con search_fields
    # autocomplete_fields = ['cliente_id']

    readonly_fields = ('cod_trabajo', 'fecha_ingreso', 'cantidad_equipos_readonly')

    # fieldsets = (
    #     ('Información Básica', {
    #         'fields': ('cod_trabajo', 'cliente_id', 'fecha_ingreso', 'estado')
    #     }),
    #     ('Fechas', {
    #         'fields': ('fecha_entrega_estimada'),
    #         'classes': ('collapse',)
    #     }),
    #     ('Detalles Técnicos', {
    #         'fields': ('solucion_aplicada'),
    #         'classes': ('collapse',)
    #     }),
    #     ('Resumen', {
    #         'fields': ('cantidad_equipos_readonly',),
    #         'classes': ('collapse',)
    #     })
    # )

    inlines = [OrdenTrabajoEquipoInline]

    # Acciones personalizadas
    actions = ['marcar_en_diagnostico', 'marcar_en_proceso', 'marcar_terminado']

    # Personalizar el widget para campos de texto largos
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})},
    }

    def cliente_nombre(self, obj):
        """Mostrar nombre completo del cliente"""
        return f"{obj.cliente_id.persona_id.nombre} {obj.cliente_id.persona_id.apellido}"

    cliente_nombre.short_description = 'Cliente'
    cliente_nombre.admin_order_field = 'cliente_id__persona_id__nombre'

    def cantidad_equipos(self, obj):
        """Mostrar cantidad de equipos en la orden"""
        count = obj.equipos.count()
        if count > 0:
            # Cambiar 'ordenes' por el nombre real de tu app
            url = reverse('admin:ordenes_ordentrabajoequipo_changelist')
            return format_html(
                '<a href="{}?orden__id__exact={}">{} equipos</a>',
                url, obj.pk, count
            )
        return "0 equipos"

    cantidad_equipos.short_description = 'Equipos'

    def cantidad_equipos_readonly(self, obj):
        """Versión de solo lectura para fieldsets"""
        if obj.pk:
            return self.cantidad_equipos(obj)
        return "Guarde primero para ver equipos"

    cantidad_equipos_readonly.short_description = 'Equipos Asociados'

    def estado_color(self, obj):
        """Mostrar estado con color"""
        colores = {
            'Recibido': 'blue',
            'En Diagnostico': 'orange',
            'En Proceso': 'purple',
            'Terminado': 'green',
            'No retirado': 'red',
            'Entregado': 'darkgreen',
            'Cancelado': 'gray',
            'Falta de pago': 'darkred'
        }
        color = colores.get(obj.estado, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.estado
        )

    estado_color.short_description = 'Estado'

    # Acciones personalizadas
    def marcar_en_diagnostico(self, request, queryset):
        count = queryset.update(estado='En Diagnostico')
        self.message_user(request, f'{count} órdenes marcadas como "En Diagnóstico"')

    marcar_en_diagnostico.short_description = 'Marcar como "En Diagnóstico"'

    def marcar_en_proceso(self, request, queryset):
        count = queryset.update(estado='En Proceso')
        self.message_user(request, f'{count} órdenes marcadas como "En Proceso"')

    marcar_en_proceso.short_description = 'Marcar como "En Proceso"'

    def marcar_terminado(self, request, queryset):
        count = queryset.update(estado='Terminado')
        self.message_user(request, f'{count} órdenes marcadas como "Terminado"')

    marcar_terminado.short_description = 'Marcar como "Terminado"'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cliente_id__persona_id'
        ).prefetch_related('equipos')


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        'tipo_equipo',
        'marca',
        'modelo',
        'voltaje',
        'potencia_hp_kw',
        'ordenes_activas_count',
        'fecha_creacion'
    )

    list_filter = (
        'tipo_equipo',
        'marca',
        'fase',
        'fecha_creacion',
    )

    search_fields = (
        'tipo_equipo',
        'marca',
        'modelo',
        'descripcion_falla'
    )

    readonly_fields = ('fecha_creacion', 'fecha_modificacion', 'ordenes_activas_readonly')

    fieldsets = (
        ('Información Básica', {
            'fields': ('tipo_equipo', 'marca', 'modelo')
        }),
        ('Especificaciones Técnicas', {
            'fields': ('potencia_hp_kw', 'voltaje', 'rpm', 'fase'),
            'classes': ('collapse',)
        }),
        ('Detalles de Servicio', {
            'fields': ('descripcion_falla', 'diagnostico', 'solucion'),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_modificacion', 'ordenes_activas_readonly'),
            'classes': ('collapse',)
        })
    )

    inlines = [EquipoOrdenTrabajoInline]

    # Acciones personalizadas
    actions = ['duplicar_equipos']

    # Personalizar widgets
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 60})},
    }

    def ordenes_activas_count(self, obj):
        """Mostrar cantidad de órdenes activas"""
        count = obj.get_ordenes_activas().count()
        if count > 0:
            return format_html(
                '<span style="color: orange; font-weight: bold;">{} activas</span>',
                count
            )
        return "0 activas"

    ordenes_activas_count.short_description = 'Órdenes Activas'

    def ordenes_activas_readonly(self, obj):
        """Versión readonly para fieldsets"""
        if obj.pk:
            activas = obj.get_ordenes_activas()
            if activas.exists():
                ordenes_html = []
                for orden in activas[:5]:  # Mostrar máximo 5
                    # Cambiar 'ordenes' por el nombre real de tu app
                    url = reverse('admin:ordenes_ordentrabajo_change', args=[orden.pk])
                    ordenes_html.append(f'<a href="{url}">{orden.cod_trabajo}</a>')
                result = ', '.join(ordenes_html)
                if activas.count() > 5:
                    result += f' y {activas.count() - 5} más...'
                return mark_safe(result)
            return "Sin órdenes activas"
        return "Guarde primero para ver órdenes"

    ordenes_activas_readonly.short_description = 'Órdenes Activas'

    def duplicar_equipos(self, request, queryset):
        """Acción para duplicar equipos seleccionados"""
        count = 0
        for equipo in queryset:
            nuevo_equipo = Equipo.objects.create(
                tipo_equipo=equipo.tipo_equipo,
                marca=equipo.marca,
                modelo=f"{equipo.modelo} (Copia)" if equipo.modelo else "Copia",
                descripcion_falla=equipo.descripcion_falla,
                potencia_hp_kw=equipo.potencia_hp_kw,
                voltaje=equipo.voltaje,
                rpm=equipo.rpm,
                fase=equipo.fase
            )
            count += 1
        self.message_user(request, f'{count} equipos duplicados exitosamente')

    duplicar_equipos.short_description = 'Duplicar equipos seleccionados'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('ordenes_trabajo')


@admin.register(OrdenTrabajoEquipo)
class OrdenTrabajoEquipoAdmin(admin.ModelAdmin):
    list_display = (
        'orden_codigo',
        'equipo_descripcion',
        'estado_equipo_en_orden',
        'costo_reparacion',
        'fecha_asociacion'
    )

    list_filter = (
        'estado_equipo_en_orden',
        'fecha_asociacion',
        ('orden', admin.RelatedOnlyFieldListFilter),
        ('equipo__tipo_equipo', admin.AllValuesFieldListFilter),
    )

    search_fields = (
        'orden__cod_trabajo',
        'equipo__tipo_equipo',
        'equipo__marca',
        'equipo__modelo',
        'observaciones'
    )

    autocomplete_fields = ['orden', 'equipo']

    readonly_fields = ('fecha_asociacion',)

    # Personalizar widgets
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 50})},
    }

    def orden_codigo(self, obj):
        """Mostrar código de orden con enlace"""
        # Cambiar 'ordenes' por el nombre real de tu app
        url = reverse('admin:ordenes_ordentrabajo_change', args=[obj.orden.pk])
        return format_html('<a href="{}">{}</a>', url, obj.orden.cod_trabajo)

    orden_codigo.short_description = 'Orden'
    orden_codigo.admin_order_field = 'orden__cod_trabajo'

    def equipo_descripcion(self, obj):
        """Mostrar descripción del equipo con enlace"""
        # Cambiar 'ordenes' por el nombre real de tu app
        url = reverse('admin:ordenes_equipo_change', args=[obj.equipo.pk])
        return format_html('<a href="{}">{}</a>', url, str(obj.equipo))

    equipo_descripcion.short_description = 'Equipo'
    equipo_descripcion.admin_order_field = 'equipo__tipo_equipo'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('orden', 'equipo')


# Configuración adicional para mejorar la experiencia del admin
admin.site.site_header = "Sistema de Gestión de Órdenes de Trabajo"
admin.site.site_title = "Gestión de Órdenes"
admin.site.index_title = "Panel de Administración"