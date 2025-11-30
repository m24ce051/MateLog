import { useEffect, useRef } from 'react';
import { trackingService } from '../api/trackingService';

/**
 * Hook personalizado para tracking automático de tiempo en pantallas
 * @param {string} screenType - Tipo de pantalla (LOGIN, REGISTRO, LISTA_LECCIONES, etc.)
 * @param {object} options - Opciones adicionales (leccion_id, tema_id, ejercicio_id)
 */
export const useScreenTracking = (screenType, options = {}) => {
  const activityIdRef = useRef(null);
  const startTimeRef = useRef(null);

  useEffect(() => {
    // Iniciar tracking al montar el componente
    const startTracking = async () => {
      try {
        startTimeRef.current = Date.now();
        const response = await trackingService.startActivity({
          tipo_pantalla: screenType,
          ...options,
        });
        activityIdRef.current = response.actividad_id;
      } catch (error) {
        console.error('Error al iniciar tracking:', error);
      }
    };

    startTracking();

    // Finalizar tracking al desmontar el componente
    return () => {
      const endTracking = async () => {
        if (activityIdRef.current) {
          try {
            await trackingService.endActivity(activityIdRef.current);
          } catch (error) {
            console.error('Error al finalizar tracking:', error);
          }
        }
      };

      endTracking();
    };
  }, [screenType, options.leccion_id, options.tema_id, options.ejercicio_id]);

  // Retornar el tiempo transcurrido en segundos
  const getElapsedTime = () => {
    if (!startTimeRef.current) return 0;
    return Math.floor((Date.now() - startTimeRef.current) / 1000);
  };

  return { getElapsedTime, activityId: activityIdRef.current };
};

export default useScreenTracking;
