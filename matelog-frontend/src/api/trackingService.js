import api from './axios';

// Servicios de tracking
export const trackingService = {
  // Iniciar tracking de una pantalla
  startActivity: async (activityData) => {
    const response = await api.post('/tracking/iniciar/', activityData);
    return response.data;
  },

  // Finalizar tracking de una pantalla
  endActivity: async (activityId) => {
    const response = await api.post('/tracking/finalizar/', { actividad_id: activityId });
    return response.data;
  },

  // Iniciar sesión de estudio
  startSession: async () => {
    const response = await api.post('/tracking/sesion/iniciar/');
    return response.data;
  },

  // Finalizar sesión de estudio
  endSession: async (sessionId) => {
    const response = await api.post('/tracking/sesion/finalizar/', { sesion_id: sessionId });
    return response.data;
  },

  // Obtener actividades del usuario
  getUserActivities: async () => {
    const response = await api.get('/tracking/actividades/');
    return response.data;
  },

  // Modificación 4: Registrar click en botón "Volver" del contenido
  registerVolverContenido: async (activityId) => {
    const response = await api.post('/tracking/volver-contenido/', {
      actividad_id: activityId
    });
    return response.data;
  },
};

export default trackingService;