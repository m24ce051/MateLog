import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Función para obtener el token CSRF de las cookies
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Función para obtener el token CSRF del servidor
export const fetchCSRFToken = async () => {
  try {
    await api.get('/users/csrf/');
  } catch (error) {
    console.error('Error al obtener CSRF token:', error);
  }
};

// Interceptor para incluir el token CSRF en todas las peticiones
api.interceptors.request.use(
  (config) => {
    // Obtener token CSRF de las cookies
    const csrftoken = getCookie('csrftoken');
    
    // Si existe el token, agregarlo a los headers
    if (csrftoken) {
      config.headers['X-CSRFToken'] = csrftoken;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Usuario no autenticado
      console.log('Usuario no autenticado');
    } else if (error.response?.status === 403) {
      // Forbidden - posiblemente falta CSRF token
      console.error('Error 403 - CSRF token issue');
    }
    return Promise.reject(error);
  }
);

export default api;
