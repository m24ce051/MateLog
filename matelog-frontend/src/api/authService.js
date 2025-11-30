import api from './axios';

// Servicios de autenticación
export const authService = {
  // Registrar nuevo usuario
  register: async (userData) => {
    const response = await api.post('/users/register/', userData);
    return response.data;
  },

  // Iniciar sesión
  login: async (credentials) => {
    const response = await api.post('/users/login/', credentials);
    return response.data;
  },

  // Cerrar sesión
  logout: async () => {
    const response = await api.post('/users/logout/');
    return response.data;
  },

  // Obtener perfil del usuario actual
  getProfile: async () => {
    const response = await api.get('/users/profile/');
    return response.data;
  },
};

export default authService;
