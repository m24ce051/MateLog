import api from './axios';

// Servicios de lecciones
export const lessonService = {
  // Obtener todas las lecciones con progreso
  getAllLessons: async () => {
    const response = await api.get('/lessons/lecciones/');  // ✅ CORREGIDO
    return response.data;
  },

  // Obtener detalle de una lección específica
  getLessonDetail: async (lessonId) => {
    const response = await api.get(`/lessons/lecciones/${lessonId}/`);  // ✅ CORREGIDO
    return response.data;
  },

  // Obtener contenido completo de un tema
  getTopicContent: async (topicId) => {
    const response = await api.get(`/lessons/temas/${topicId}/`);
    return response.data;
  },

  // Finalizar un tema
  finalizeTopic: async (topicId) => {
    const response = await api.post(`/lessons/temas/${topicId}/finalizar/`);
    return response.data;
  },

  // Reintentar un tema (Modificación 7)
  retryTopic: async (topicId) => {
    const response = await api.post(`/lessons/temas/${topicId}/reintentar/`);
    return response.data;
  },

  // Registrar vuelta al tema desde ejercicios
  returnToTopic: async (topicId) => {
    const response = await api.post(`/lessons/temas/${topicId}/volver/`);
    return response.data;
  },

  // Validar respuesta de ejercicio
  validateAnswer: async (answerData) => {
    const response = await api.post('/lessons/ejercicios/validar/', answerData);
    return response.data;
  },
};

export default lessonService;