import { createContext, useState, useContext, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../api/authService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
        const profile = await authService.getProfile();
        setUser(profile);
        localStorage.setItem('user', JSON.stringify(profile));
      }
    } catch (err) {
      console.error('Error verificando autenticación:', err);
      localStorage.removeItem('user');
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
      let errorMessage = 'Error de conexión. Intenta de nuevo.';
      
      if (err.response?.data) {
        const errorData = err.response.data;
        
        // Si es un objeto con detail
        if (typeof errorData === 'object' && errorData.detail) {
          errorMessage = String(errorData.detail);
        }
        // Si es un objeto con mensaje
        else if (typeof errorData === 'object' && errorData.mensaje) {
          errorMessage = String(errorData.mensaje);
        }
        // Si es un objeto con error
        else if (typeof errorData === 'object' && errorData.error) {
          errorMessage = String(errorData.error);
        }
        // Si es una cadena
        else if (typeof errorData === 'string') {
          errorMessage = errorData;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
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
          errorMessage = String(errorData.detail);
        } else if (typeof errorData === 'object' && errorData.mensaje) {
          errorMessage = String(errorData.mensaje);
        } else if (typeof errorData === 'object' && errorData.error) {
          errorMessage = String(errorData.error);
        } else if (typeof errorData === 'string') {
          errorMessage = errorData;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (err) {
      console.error('Error en logout:', err);
    } finally {
      setUser(null);
      localStorage.removeItem('user');
      navigate('/');
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};