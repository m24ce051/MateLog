from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models
from .models import Leccion, Tema, Ejercicio
from .serializers import (
    LeccionListSerializer,
    LeccionDetailSerializer,
    TemaDetailSerializer,
    EjercicioValidacionSerializer,
)
from tracking.models import (
    ProgresoLeccion,
    ProgresoTema,
    RespuestaEjercicio,
)


class LeccionListView(APIView):
    """
    Vista para listar todas las lecciones disponibles.
    Endpoint: GET /api/lecciones/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        lecciones = Leccion.objects.filter(is_active=True).order_by('orden')
        
        # Obtener el progreso del usuario para cada lección
        lecciones_data = []
        for leccion in lecciones:
            progreso = ProgresoLeccion.objects.filter(
                usuario=request.user,
                leccion=leccion
            ).first()
            
            serializer = LeccionListSerializer(leccion)
            leccion_dict = serializer.data
            
            if progreso:
                leccion_dict['progreso'] = {
                    'estado': progreso.estado,
                    'porcentaje_completado': float(progreso.porcentaje_completado)
                }
            else:
                leccion_dict['progreso'] = {
                    'estado': 'SIN_INICIAR',
                    'porcentaje_completado': 0.0
                }
            
            lecciones_data.append(leccion_dict)
        
        return Response(lecciones_data, status=status.HTTP_200_OK)


class LeccionDetailView(APIView):
    """
    Vista para obtener el detalle de una lección y sus temas.
    Endpoint: GET /api/lecciones/<id>/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, leccion_id):
        leccion = get_object_or_404(Leccion, id=leccion_id, is_active=True)
        
        # Crear o actualizar progreso de la lección
        from django.utils import timezone
        progreso_leccion, created = ProgresoLeccion.objects.get_or_create(
            usuario=request.user,
            leccion=leccion,
            defaults={'estado': 'EN_PROGRESO', 'fecha_inicio': timezone.now()}
        )
        
        if created or progreso_leccion.estado == 'SIN_INICIAR':
            progreso_leccion.estado = 'EN_PROGRESO'
            if not progreso_leccion.fecha_inicio:
                progreso_leccion.fecha_inicio = timezone.now()
            progreso_leccion.save()
        
        # Serializar la lección
        serializer = LeccionDetailSerializer(leccion)
        leccion_data = serializer.data
        
        # Agregar información de progreso para cada tema
        temas_con_progreso = []
        primer_tema_desbloqueado = False
        
        for tema_data in leccion_data['temas']:
            tema = Tema.objects.get(id=tema_data['id'])
            progreso_tema, _ = ProgresoTema.objects.get_or_create(
                usuario=request.user,
                tema=tema
            )
            
            # El primer tema siempre está desbloqueado
            if tema.orden == 1 and not progreso_tema.desbloqueado:
                progreso_tema.desbloqueado = True
                progreso_tema.save()
                primer_tema_desbloqueado = True
            
            tema_data['progreso'] = {
                'estado': progreso_tema.estado,
                'desbloqueado': progreso_tema.desbloqueado,
                'porcentaje_acierto': float(progreso_tema.porcentaje_acierto),
                'intentos_realizados': progreso_tema.intentos_realizados,
            }
            
            temas_con_progreso.append(tema_data)
        
        leccion_data['temas'] = temas_con_progreso
        leccion_data['progreso'] = {
            'estado': progreso_leccion.estado,
            'porcentaje_completado': float(progreso_leccion.porcentaje_completado)
        }
        
        return Response(leccion_data, status=status.HTTP_200_OK)


class TemaDetailView(APIView):
    """
    Vista para obtener el contenido completo de un tema.
    Endpoint: GET /api/temas/<id>/
    Modificación 6: Incluye ejercicios_respondidos y siguiente_ejercicio_index.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, tema_id):
        from django.utils import timezone
        
        tema = get_object_or_404(Tema, id=tema_id, is_active=True)
        
        # Verificar que el tema esté desbloqueado
        progreso_tema, created = ProgresoTema.objects.get_or_create(
            usuario=request.user,
            tema=tema
        )
        
        if not progreso_tema.desbloqueado and tema.orden != 1:
            return Response(
                {'error': 'Este tema aún no está desbloqueado'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Actualizar estado si es necesario
        if progreso_tema.estado == 'SIN_INICIAR':
            progreso_tema.estado = 'INICIADO'
            progreso_tema.fecha_inicio = timezone.now()
            progreso_tema.save()
        
        # Serializar el tema
        serializer = TemaDetailSerializer(tema)
        tema_data = serializer.data
        
        # Modificación 6: Obtener respuestas previas
        respuestas_previas = RespuestaEjercicio.objects.filter(
            usuario=request.user,
            progreso_tema=progreso_tema
        ).select_related('ejercicio')
        
        # Crear diccionario de ejercicios respondidos
        ejercicios_respondidos = {}
        for respuesta in respuestas_previas:
            ejercicios_respondidos[respuesta.ejercicio.id] = {
                'respuesta_usuario': respuesta.respuesta_usuario,
                'es_correcta': respuesta.es_correcta,
                'uso_ayuda': respuesta.uso_ayuda
            }
        
        # Determinar índice del siguiente ejercicio sin responder
        siguiente_ejercicio_index = 0
        for idx, ejercicio in enumerate(tema_data['ejercicios']):
            if ejercicio['id'] not in ejercicios_respondidos:
                siguiente_ejercicio_index = idx
                break
        
        # Si todos están respondidos, mantener en el último
        if len(ejercicios_respondidos) == len(tema_data['ejercicios']):
            siguiente_ejercicio_index = 0
        
        # Agregar información de progreso
        tema_data['ejercicios_respondidos'] = ejercicios_respondidos
        tema_data['siguiente_ejercicio_index'] = siguiente_ejercicio_index
        tema_data['total_ejercicios_respondidos'] = len(ejercicios_respondidos)
        
        return Response(tema_data, status=status.HTTP_200_OK)


class ValidarRespuestaView(APIView):
    """
    Vista para validar la respuesta de un ejercicio.
    Endpoint: POST /api/ejercicios/validar/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            serializer = EjercicioValidacionSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            ejercicio_id = serializer.validated_data['ejercicio_id']
            respuesta_usuario = serializer.validated_data['respuesta']
            uso_ayuda = serializer.validated_data.get('uso_ayuda', False)
            tiempo_respuesta = serializer.validated_data.get('tiempo_respuesta_segundos', 0)
            
            # Obtener ejercicio (SIN is_active porque Ejercicio no tiene ese campo)
            try:
                ejercicio = Ejercicio.objects.get(id=ejercicio_id)
            except Ejercicio.DoesNotExist:
                return Response(
                    {'error': 'Ejercicio no encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Obtener o crear progreso del tema
            from django.utils import timezone
            progreso_tema, created = ProgresoTema.objects.get_or_create(
                usuario=request.user,
                tema=ejercicio.tema,
                defaults={
                    'desbloqueado': True,
                    'estado': 'INICIADO',
                    'fecha_inicio': timezone.now()
                }
            )
            
            # Si el progreso ya existía pero no tenía fecha de inicio, establecerla
            if not created and not progreso_tema.fecha_inicio:
                progreso_tema.fecha_inicio = timezone.now()
                progreso_tema.estado = 'INICIADO'
                progreso_tema.save()
            
            # Validar respuesta
            es_correcta = ejercicio.validar_respuesta(respuesta_usuario)
            
            # Verificar si ya existe una respuesta para este ejercicio en el progreso actual
            respuesta_existente = RespuestaEjercicio.objects.filter(
                usuario=request.user,
                ejercicio=ejercicio,
                progreso_tema=progreso_tema
            ).first()
            
            if respuesta_existente:
                # Ya existe una respuesta, devolver el resultado anterior
                response_data = {
                    'es_correcta': respuesta_existente.es_correcta,
                }
                
                if respuesta_existente.es_correcta and ejercicio.retroalimentacion_correcta:
                    response_data['retroalimentacion'] = ejercicio.retroalimentacion_correcta
                elif not respuesta_existente.es_correcta and ejercicio.retroalimentacion_incorrecta:
                    response_data['retroalimentacion'] = ejercicio.retroalimentacion_incorrecta
                
                return Response(response_data, status=status.HTTP_200_OK)
            
            # Registrar nueva respuesta
            RespuestaEjercicio.objects.create(
                usuario=request.user,
                ejercicio=ejercicio,
                progreso_tema=progreso_tema,
                respuesta_usuario=respuesta_usuario,
                es_correcta=es_correcta,
                uso_ayuda=uso_ayuda,
                tiempo_respuesta_segundos=tiempo_respuesta
            )
            
            # Preparar respuesta
            response_data = {
                'es_correcta': es_correcta,
            }
            
            # Agregar retroalimentación si existe
            if es_correcta and ejercicio.retroalimentacion_correcta:
                response_data['retroalimentacion'] = ejercicio.retroalimentacion_correcta
            elif not es_correcta and ejercicio.retroalimentacion_incorrecta:
                response_data['retroalimentacion'] = ejercicio.retroalimentacion_incorrecta
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log del error para debugging
            import traceback
            print("=" * 80)
            print("ERROR EN VALIDAR RESPUESTA:")
            print(f"Usuario: {request.user.username}")
            print(f"Ejercicio ID: {request.data.get('ejercicio_id')}")
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            print("=" * 80)
            
            return Response(
                {'error': f'Error al procesar respuesta: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FinalizarTemaView(APIView):
    """
    Vista para finalizar un tema y calcular el progreso.
    Endpoint: POST /api/temas/<id>/finalizar/
    Modificación 7: Registra cada intento en IntentoTema.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, tema_id):
        try:
            from django.utils import timezone
            from tracking.models import IntentoTema
            
            tema = get_object_or_404(Tema, id=tema_id, is_active=True)
            
            # Obtener el progreso del tema
            progreso_tema, _ = ProgresoTema.objects.get_or_create(
                usuario=request.user,
                tema=tema,
                defaults={
                    'desbloqueado': True,
                    'estado': 'INICIADO',
                    'fecha_inicio': timezone.now()
                }
            )
            
            # Obtener todas las respuestas del usuario para este tema
            respuestas = RespuestaEjercicio.objects.filter(
                usuario=request.user,
                progreso_tema=progreso_tema
            )
            
            # Calcular estadísticas
            total_ejercicios = tema.ejercicios.count()
            ejercicios_correctos = respuestas.filter(es_correcta=True).count()
            ejercicios_incorrectos = respuestas.filter(es_correcta=False).count()
            ejercicios_con_ayuda = respuestas.filter(uso_ayuda=True).count()
            
            # Calcular porcentaje de aciertos
            if total_ejercicios > 0:
                porcentaje_acierto = (ejercicios_correctos / total_ejercicios) * 100
            else:
                porcentaje_acierto = 0
            
            # Calcular tiempos
            tiempo_total_segundos = respuestas.aggregate(
                total=models.Sum('tiempo_respuesta_segundos')
            )['total'] or 0
            
            tiempo_promedio_por_ejercicio = (
                tiempo_total_segundos // total_ejercicios if total_ejercicios > 0 else 0
            )
            
            # Determinar si aprobó (80% o más)
            aprobado = porcentaje_acierto >= 80
            
            # Incrementar contador de intentos
            progreso_tema.intentos_realizados += 1
            
            # Modificación 7: Crear registro de intento
            intento = IntentoTema.objects.create(
                usuario=request.user,
                tema=tema,
                progreso_tema=progreso_tema,
                numero_intento=progreso_tema.intentos_realizados,
                ejercicios_correctos=ejercicios_correctos,
                ejercicios_incorrectos=ejercicios_incorrectos,
                ejercicios_totales=total_ejercicios,
                porcentaje_acierto=porcentaje_acierto,
                ejercicios_con_ayuda=ejercicios_con_ayuda,
                tiempo_total_segundos=tiempo_total_segundos,
                tiempo_promedio_por_ejercicio=tiempo_promedio_por_ejercicio,
                aprobado=aprobado,
                fecha_inicio=progreso_tema.fecha_inicio or timezone.now()
            )
            
            # Calcular mejora respecto al intento anterior
            intento.calcular_mejora()
            intento.save()
            
            # Actualizar progreso del tema
            progreso_tema.porcentaje_acierto = porcentaje_acierto
            
            siguiente_tema_id = None
            
            if aprobado:
                progreso_tema.estado = 'COMPLETADO'
                progreso_tema.fecha_completado = timezone.now()
                
                # Desbloquear el siguiente tema
                siguiente_tema = Tema.objects.filter(
                    leccion=tema.leccion,
                    orden=tema.orden + 1,
                    is_active=True
                ).first()
                
                if siguiente_tema:
                    ProgresoTema.objects.get_or_create(
                        usuario=request.user,
                        tema=siguiente_tema,
                        defaults={'desbloqueado': True}
                    )
                    siguiente_tema_id = siguiente_tema.id
                
                # Actualizar progreso de la lección
                progreso_leccion, _ = ProgresoLeccion.objects.get_or_create(
                    usuario=request.user,
                    leccion=tema.leccion
                )
                
                temas_totales = tema.leccion.temas.filter(is_active=True).count()
                temas_completados = ProgresoTema.objects.filter(
                    usuario=request.user,
                    tema__leccion=tema.leccion,
                    estado='COMPLETADO'
                ).count()
                
                if temas_totales > 0:
                    progreso_leccion.porcentaje_completado = (temas_completados / temas_totales) * 100
                
                if temas_completados == temas_totales:
                    progreso_leccion.estado = 'COMPLETADA'
                    progreso_leccion.fecha_completado = timezone.now()
                
                progreso_leccion.save()
            
            progreso_tema.save()
            
            return Response({
                'aprobado': aprobado,
                'porcentaje_acierto': float(porcentaje_acierto),
                'ejercicios_correctos': ejercicios_correctos,
                'ejercicios_totales': total_ejercicios,
                'leccion_id': tema.leccion.id,
                'tema_id': tema.id,
                'siguiente_tema_id': siguiente_tema_id,
                'numero_intento': progreso_tema.intentos_realizados,
                'mejora_porcentaje': float(intento.mejora_porcentaje) if intento.mejora_porcentaje else None,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print("=" * 80)
            print("ERROR EN FINALIZAR TEMA:")
            print(f"Usuario: {request.user.username}")
            print(f"Tema ID: {tema_id}")
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            print("=" * 80)
            
            return Response(
                {'error': f'Error al finalizar tema: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VolverAlTemaView(APIView):
    """
    Vista para registrar cuando un usuario vuelve desde ejercicios al contenido del tema.
    Endpoint: POST /api/temas/<id>/volver/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, tema_id):
        tema = get_object_or_404(Tema, id=tema_id, is_active=True)
        
        # Simplemente confirmamos que el usuario puede volver
        # No hacemos cambios en el progreso
        
        return Response({
            'mensaje': 'Puede volver al contenido del tema',
            'tema_id': tema.id
        }, status=status.HTTP_200_OK)


class ReintentarTemaView(APIView):
    """
    Vista para reintentar un tema.
    Borra las respuestas del intento actual y resetea el progreso.
    Endpoint: POST /api/temas/<id>/reintentar/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, tema_id):
        try:
            tema = get_object_or_404(Tema, id=tema_id, is_active=True)
            
            # Obtener progreso del tema
            progreso_tema = get_object_or_404(
                ProgresoTema,
                usuario=request.user,
                tema=tema
            )
            
            # Borrar todas las respuestas del intento actual
            RespuestaEjercicio.objects.filter(
                usuario=request.user,
                progreso_tema=progreso_tema
            ).delete()
            
            # Resetear estado del progreso (no incrementar intentos aún)
            from django.utils import timezone
            progreso_tema.estado = 'INICIADO'
            progreso_tema.fecha_inicio = timezone.now()
            # NO modificar intentos_realizados aquí, se incrementa en finalizar
            progreso_tema.save()
            
            return Response({
                'mensaje': 'Tema reiniciado correctamente',
                'tema_id': tema.id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            print("=" * 80)
            print("ERROR EN REINTENTAR TEMA:")
            print(f"Usuario: {request.user.username}")
            print(f"Tema ID: {tema_id}")
            print(f"Error: {str(e)}")
            print(traceback.format_exc())
            print("=" * 80)
            
            return Response(
                {'error': f'Error al reintentar tema: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )