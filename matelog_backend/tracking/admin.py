from django.contrib import admin
from .models import (
    SesionEstudio, 
    ProgresoLeccion, 
    ProgresoTema, 
    RespuestaEjercicio, 
    ActividadPantalla,
    IntentoTema  # Modificación 7
)


@admin.register(SesionEstudio)
class SesionEstudioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_inicio', 'fecha_fin', 'duracion_minutos')
    list_filter = ('fecha_inicio', 'usuario')
    search_fields = ('usuario__username',)
    readonly_fields = ('fecha_inicio',)
    ordering = ('-fecha_inicio',)


@admin.register(ProgresoLeccion)
class ProgresoLeccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'leccion', 'estado', 'porcentaje_completado', 'fecha_inicio', 'fecha_completado')
    list_filter = ('estado', 'leccion', 'fecha_inicio')
    search_fields = ('usuario__username', 'leccion__titulo')
    readonly_fields = ('fecha_inicio', 'fecha_completado')
    ordering = ('leccion__orden', 'usuario')


@admin.register(ProgresoTema)
class ProgresoTemaAdmin(admin.ModelAdmin):
    list_display = (
        'usuario', 
        'tema', 
        'estado', 
        'desbloqueado', 
        'porcentaje_acierto', 
        'intentos_realizados',  # Modificación 7
        'fecha_completado'
    )
    list_filter = ('estado', 'desbloqueado', 'tema__leccion', 'fecha_inicio')
    search_fields = ('usuario__username', 'tema__titulo')
    readonly_fields = ('fecha_inicio', 'fecha_completado')
    ordering = ('tema__leccion__orden', 'tema__orden', 'usuario')
    
    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'tema', 'estado', 'desbloqueado')
        }),
        ('Progreso', {
            'fields': ('porcentaje_acierto', 'intentos_realizados')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_completado')
        }),
    )


@admin.register(RespuestaEjercicio)
class RespuestaEjercicioAdmin(admin.ModelAdmin):
    list_display = (
        'usuario', 
        'ejercicio_breve', 
        'es_correcta', 
        'uso_ayuda', 
        'tiempo_respuesta_segundos', 
        'fecha_respuesta'
    )
    list_filter = ('es_correcta', 'uso_ayuda', 'fecha_respuesta', 'ejercicio__tema')
    search_fields = ('usuario__username', 'ejercicio__enunciado')
    readonly_fields = ('fecha_respuesta',)
    ordering = ('-fecha_respuesta',)
    
    def ejercicio_breve(self, obj):
        return obj.ejercicio.enunciado[:50] + '...' if len(obj.ejercicio.enunciado) > 50 else obj.ejercicio.enunciado
    ejercicio_breve.short_description = 'Ejercicio'


@admin.register(ActividadPantalla)
class ActividadPantallaAdmin(admin.ModelAdmin):
    list_display = (
        'usuario_display', 
        'tipo_pantalla', 
        'tiempo_segundos', 
        'veces_volver_contenido',  # Modificación 4
        'tiempo_inicio',
        'tiempo_fin'
    )
    list_filter = ('tipo_pantalla', 'tiempo_inicio', 'usuario')
    search_fields = ('usuario__username',)
    readonly_fields = ('tiempo_inicio', 'tiempo_fin')
    ordering = ('-tiempo_inicio',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'tipo_pantalla', 'tiempo_inicio', 'tiempo_fin', 'tiempo_segundos')
        }),
        ('Metadatos', {
            'fields': ('leccion_id', 'tema_id')
        }),
        ('Navegación (Modificación 4)', {
            'fields': ('veces_volver_contenido',),
            'description': 'Tracking de clicks en el botón "Volver" durante el contenido del tema'
        }),
    )
    
    def usuario_display(self, obj):
        return obj.usuario.username if obj.usuario else 'Anónimo'
    usuario_display.short_description = 'Usuario'


# Modificación 7: Admin para IntentoTema
@admin.register(IntentoTema)
class IntentoTemaAdmin(admin.ModelAdmin):
    list_display = (
        'usuario',
        'tema',
        'numero_intento',
        'porcentaje_acierto',
        'aprobado',
        'ejercicios_correctos_display',
        'ejercicios_con_ayuda',
        'tiempo_total_minutos',
        'mejora_porcentaje',
        'fecha_finalizacion'
    )
    
    list_filter = (
        'aprobado',
        'tema__leccion',
        'tema',
        'numero_intento',
        'fecha_finalizacion'
    )
    
    search_fields = (
        'usuario__username',
        'tema__titulo'
    )
    
    readonly_fields = (
        'fecha_inicio',
        'fecha_finalizacion',
        'mejora_porcentaje'
    )
    
    ordering = ('-fecha_finalizacion',)
    
    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'tema', 'progreso_tema', 'numero_intento')
        }),
        ('Resultados del Intento', {
            'fields': (
                'ejercicios_correctos',
                'ejercicios_incorrectos',
                'ejercicios_totales',
                'porcentaje_acierto',
                'aprobado'
            )
        }),
        ('Uso de Ayuda', {
            'fields': ('ejercicios_con_ayuda',)
        }),
        ('Tiempos', {
            'fields': (
                'tiempo_total_segundos',
                'tiempo_promedio_por_ejercicio'
            )
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_finalizacion')
        }),
        ('Mejora', {
            'fields': ('mejora_porcentaje',),
            'description': 'Mejora en porcentaje respecto al intento anterior'
        }),
    )
    
    def ejercicios_correctos_display(self, obj):
        return f"{obj.ejercicios_correctos}/{obj.ejercicios_totales}"
    ejercicios_correctos_display.short_description = 'Correctos/Total'
    
    def tiempo_total_minutos(self, obj):
        return f"{obj.tiempo_total_segundos // 60} min"
    tiempo_total_minutos.short_description = 'Tiempo Total'
    
    # Acciones personalizadas
    actions = ['exportar_intentos_csv']
    
    def exportar_intentos_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="intentos_temas.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Usuario',
            'Tema',
            'Número Intento',
            'Porcentaje Acierto',
            'Aprobado',
            'Correctos',
            'Incorrectos',
            'Con Ayuda',
            'Tiempo Total (seg)',
            'Tiempo Promedio (seg)',
            'Mejora %',
            'Fecha Finalización'
        ])
        
        for intento in queryset:
            writer.writerow([
                intento.usuario.username,
                intento.tema.titulo,
                intento.numero_intento,
                intento.porcentaje_acierto,
                'Sí' if intento.aprobado else 'No',
                intento.ejercicios_correctos,
                intento.ejercicios_incorrectos,
                intento.ejercicios_con_ayuda,
                intento.tiempo_total_segundos,
                intento.tiempo_promedio_por_ejercicio,
                intento.mejora_porcentaje or 0,
                intento.fecha_finalizacion.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response
    
    exportar_intentos_csv.short_description = "Exportar intentos seleccionados a CSV"