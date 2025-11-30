import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useScreenTracking } from '../hooks/useScreenTracking';
import { fetchCSRFToken } from '../api/axios';
import './AuthPage.css';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    password_confirm: '',
    grupo: '',
    especialidad: '',
    genero: '',
    edad: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const { login, register } = useAuth();
  const navigate = useNavigate();
  
  // Tracking de pantalla
  useScreenTracking(isLogin ? 'LOGIN' : 'REGISTRO');

  // Obtener CSRF token al montar el componente
  useEffect(() => {
    fetchCSRFToken();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Limpiar error del campo al escribir
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = 'El usuario es requerido';
    }

    if (!formData.password) {
      newErrors.password = 'La contraseña es requerida';
    } else if (formData.password.length < 6) {
      newErrors.password = 'La contraseña debe tener al menos 6 caracteres';
    }

    if (!isLogin) {
      if (formData.password !== formData.password_confirm) {
        newErrors.password_confirm = 'Las contraseñas no coinciden';
      }

      if (!formData.grupo.trim()) {
        newErrors.grupo = 'Selecciona tu grupo';
      }

      if (!formData.especialidad.trim()) {
        newErrors.especialidad = 'Selecciona tu especialidad';
      }

      if (!formData.genero) {
        newErrors.genero = 'Selecciona tu género';
      }

      if (!formData.edad) {
        newErrors.edad = 'Selecciona tu edad';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      if (isLogin) {
        const result = await login({
          username: formData.username,
          password: formData.password
        });

        if (result.success) {
          navigate('/lecciones');
        } else {
          setErrors({ general: result.error || 'Error al iniciar sesión' });
        }
      } else {
        const result = await register(formData);

        if (result.success) {
          alert('¡Registro exitoso! Ahora puedes iniciar sesión.');
          setIsLogin(true);
          setFormData({
            username: '',
            password: '',
            password_confirm: '',
            grupo: '',
            especialidad: '',
            genero: '',
            edad: '',
          });
        } else {
          if (typeof result.error === 'object') {
            setErrors(result.error);
          } else {
            setErrors({ general: result.error || 'Error al registrar usuario' });
          }
        }
      }
    } catch (error) {
      setErrors({ general: 'Error de conexión. Intenta de nuevo.' });
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setFormData({
      username: '',
      password: '',
      password_confirm: '',
      grupo: '',
      especialidad: '',
      genero: '',
      edad: '',
    });
    setErrors({});
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1>MateLog</h1>
          <p>Plataforma de Aprendizaje de Matemáticas</p>
        </div>

        <div className="auth-tabs">
          <button
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => !isLogin && switchMode()}
          >
            Iniciar Sesión
          </button>
          <button
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => isLogin && switchMode()}
          >
            Registrarse
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {errors.general && (
            <div className="error-message">{errors.general}</div>
          )}

          <div className="form-group">
            <label htmlFor="username">Usuario</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Ingresa tu usuario"
              disabled={loading}
            />
            {errors.username && <span className="error-text">{errors.username}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Contraseña</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Mínimo 6 caracteres"
              disabled={loading}
            />
            {errors.password && <span className="error-text">{errors.password}</span>}
          </div>

          {!isLogin && (
            <>
              <div className="form-group">
                <label htmlFor="password_confirm">Confirmar Contraseña</label>
                <input
                  type="password"
                  id="password_confirm"
                  name="password_confirm"
                  value={formData.password_confirm}
                  onChange={handleChange}
                  placeholder="Repite tu contraseña"
                  disabled={loading}
                />
                {errors.password_confirm && (
                  <span className="error-text">{errors.password_confirm}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="grupo">Grupo</label>
                <select
                  id="grupo"
                  name="grupo"
                  value={formData.grupo}
                  onChange={handleChange}
                  disabled={loading}
                >
                  <option value="">Selecciona tu grupo</option>
                  <option value="A">Grupo A</option>
                  <option value="B">Grupo B</option>
                  <option value="C">Grupo C</option>
                  <option value="D">Grupo D</option>
                </select>
                {errors.grupo && <span className="error-text">{errors.grupo}</span>}
              </div>

              <div className="form-group">
                <label htmlFor="especialidad">Especialidad</label>
                <select
                  id="especialidad"
                  name="especialidad"
                  value={formData.especialidad}
                  onChange={handleChange}
                  disabled={loading}
                >
                  <option value="">Selecciona tu especialidad</option>
                  <option value="INFORMATICA">Informática</option>
                  <option value="AGRONOMIA">Agronomía</option>
                  <option value="ADMINISTRACION">Administración</option>
                  <option value="ELECTRONICA">Electrónica</option>
                </select>
                {errors.especialidad && <span className="error-text">{errors.especialidad}</span>}
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="genero">Género</label>
                  <select
                    id="genero"
                    name="genero"
                    value={formData.genero}
                    onChange={handleChange}
                    disabled={loading}
                  >
                    <option value="">Selecciona...</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                    <option value="O">Otro</option>
                    <option value="N">Prefiero no decir</option>
                  </select>
                  {errors.genero && <span className="error-text">{errors.genero}</span>}
                </div>

                <div className="form-group">
                  <label htmlFor="edad">Edad</label>
                  <select
                    id="edad"
                    name="edad"
                    value={formData.edad}
                    onChange={handleChange}
                    disabled={loading}
                  >
                    <option value="">Selecciona...</option>
                    <option value="14">14 años</option>
                    <option value="15">15 años</option>
                    <option value="16">16 años</option>
                    <option value="17">17 años</option>
                    <option value="18">18 años</option>
                  </select>
                  {errors.edad && <span className="error-text">{errors.edad}</span>}
                </div>
              </div>
            </>
          )}

          <button
            type="submit"
            className="submit-button"
            disabled={loading}
          >
            {loading ? 'Procesando...' : (isLogin ? 'Iniciar Sesión' : 'Registrarse')}
          </button>
        </form>
      </div>
    </div>
  );
};

export default AuthPage;