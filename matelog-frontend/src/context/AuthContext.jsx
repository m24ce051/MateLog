import { createContext, useState, useContext, useEffect } from 'react';
import { authService } from '../api/authService';
import { trackingService } from '../api/trackingService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sessionId, setSessionId] = useState(null);

  // Verificar si hay una sesión activa al cargar
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const userData = await authService.getProfile();
      setUser(userData);
      
      // Iniciar sesión de estudio
      const session = await trackingService.startSession();
      setSessionId(session.sesion_id);
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      setLoading(true);
      setError(null);
    
      const data = await authService.login(credentials);
      const userData = data.usuario || data.user;
    
      if (userData) {
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
        navigate('/lecciones');
      } else {
        throw new Error('No se recibieron datos del usuario');
      }
    } catch (err) {
      console.error('Error en login:', err);
    
      // Manejar diferentes tipos de errores
      let errorMessage = 'Error al iniciar sesión';
    
      if (err.response?.data) {
        const errorData = err.response.data;
      
        // Si es un objeto con detail
        if (typeof errorData === 'object' && errorData.detail) {
          errorMessage = errorData.detail;
        }
        // Si es un objeto con mensaje
        else if (typeof errorData === 'object' && errorData.mensaje) {
          errorMessage = errorData.mensaje;
        }
        // Si es un objeto con error
        else if (typeof errorData === 'object' && errorData.error) {
          errorMessage = errorData.error;
        }
        // Si es una cadena
        else if (typeof errorData === 'string') {
          errorMessage = errorData;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
    
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      setLoading(true);
      setError(null);
    
      const data = await authService.register(userData);
      const user = data.usuario || data.user;
    
      if (user) {
        setUser(user);
        localStorage.setItem('user', JSON.stringify(user));
        navigate('/lecciones');
      } else {
        throw new Error('No se recibieron datos del usuario');
      }
    } catch (err) {
      console.error('Error en registro:', err);
    
      // Manejar diferentes tipos de errores
      let errorMessage = 'Error al registrarse';
    
      if (err.response?.data) {
        const errorData = err.response.data;
      
        if (typeof errorData === 'object' && errorData.detail) {
          errorMessage = errorData.detail;
        } else if (typeof errorData === 'object' && errorData.mensaje) {
          errorMessage = errorData.mensaje;
        } else if (typeof errorData === 'object' && errorData.error) {
          errorMessage = errorData.error;
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
    
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };
  const logout = async () => {
    try {
      // Finalizar sesión de estudio
      if (sessionId) {
        await trackingService.endSession(sessionId);
      }
      
      await authService.logout();
      setUser(null);
      setSessionId(null);
    } catch (error) {
      console.error('Error al cerrar sesión:', error);
    }
  };

  const value = {
    user,
    loading,
    sessionId,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Hook personalizado para usar el contexto
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de un AuthProvider');
  }
  return context;
};

export default AuthContext;