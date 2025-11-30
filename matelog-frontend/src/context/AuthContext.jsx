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
      const data = await authService.login(credentials);
      // CORRECCIÓN: El backend devuelve 'usuario', no 'user'
      const userData = data.usuario || data.user;
      setUser(userData);
      
      // Iniciar sesión de estudio
      const session = await trackingService.startSession();
      setSessionId(session.sesion_id);
      
      return { success: true, user: userData };
    } catch (error) {
      console.error('Error en login:', error);
      return { 
        success: false, 
        error: error.response?.data?.error || error.response?.data || 'Error al iniciar sesión' 
      };
    }
  };

  const register = async (userData) => {
    try {
      const data = await authService.register(userData);
      // CORRECCIÓN: El backend devuelve 'usuario', no 'user'
      const newUser = data.usuario || data.user;
      return { success: true, user: newUser };
    } catch (error) {
      console.error('Error en registro:', error);
      return { 
        success: false, 
        error: error.response?.data || 'Error al registrar usuario' 
      };
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