import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { lessonService } from '../api/lessonService';
import { useScreenTracking } from '../hooks/useScreenTracking';
import './LessonDetailPage.css';
import './HTMLContent.css';

const LessonDetailPage = () => {
  const [lesson, setLesson] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const { lessonId } = useParams();
  const navigate = useNavigate();
  
  useScreenTracking('DETALLE_LECCION', { leccion_id: parseInt(lessonId) });

  useEffect(() => {
    loadLesson();
  }, [lessonId]);

  const loadLesson = async () => {
    try {
      setLoading(true);
      const data = await lessonService.getLessonDetail(lessonId);
      setLesson(data);
    } catch (err) {
      if (err.response?.status === 403) {
        setError('Debes completar la lección anterior primero');
      } else {
        setError('Error al cargar la lección');
      }
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleTopicClick = (topic) => {
    // Verificar si está desbloqueado
    const desbloqueado = topic.progreso?.desbloqueado || false;
    
    if (desbloqueado) {
      navigate(`/tema/${topic.id}`);
    } else {
      alert('Debes completar el tema anterior primero');
    }
  };

  const getTopicStatusClass = (estado) => {
    switch (estado) {
      case 'SIN_INICIAR':
        return 'topic-grey';
      case 'INICIADO':
        return 'topic-blue';
      case 'COMPLETADO':
        return 'topic-green';
      default:
        return 'topic-grey';
    }
  };

  const getTopicStatusText = (estado) => {
    switch (estado) {
      case 'SIN_INICIAR':
        return 'Sin iniciar';
      case 'INICIADO':
        return 'En progreso';
      case 'COMPLETADO':
        return 'Completado';
      default:
        return 'Sin iniciar';
    }
  };

  if (loading) {
    return <div className="lesson-detail-container"><div className="loading">Cargando...</div></div>;
  }

  if (error) {
    return (
      <div className="lesson-detail-container">
        <div className="error-box">{error}</div>
        <button onClick={() => navigate('/lecciones')} className="back-btn">
          Volver a Lecciones
        </button>
      </div>
    );
  }

  if (!lesson) {
    return <div className="lesson-detail-container"><div className="loading">No hay datos</div></div>;
  }

  return (
    <div className="lesson-detail-container">
      <header className="lesson-detail-header">
        <button onClick={() => navigate('/lecciones')} className="back-button">
          ← Volver
        </button>
        <h1>{lesson.titulo}</h1>
        {/* Renderizar descripción con HTML */}
        <div 
          className="content-text lesson-description"
          dangerouslySetInnerHTML={{ __html: lesson.descripcion }}
        />
      </header>

      <main className="topics-content">
        <h2>Temas de la Lección</h2>
        
        {lesson.temas && lesson.temas.length > 0 ? (
          <div className="topics-grid">
            {lesson.temas.map((topic) => {
              const estado = topic.progreso?.estado || 'SIN_INICIAR';
              const desbloqueado = topic.progreso?.desbloqueado || false;
              const porcentajeAcierto = topic.progreso?.porcentaje_acierto || 0;
              const intentosRealizados = topic.progreso?.intentos_realizados || 0;
              
              return (
                <div
                  key={topic.id}
                  className={`topic-card ${getTopicStatusClass(estado)} ${
                    !desbloqueado ? 'locked' : ''
                  }`}
                  onClick={() => handleTopicClick(topic)}
                >
                  {!desbloqueado && <div className="lock-overlay">🔒</div>}
                  
                  <div className="topic-header">
                    <span className="topic-number">Tema {topic.orden}</span>
                    <span className={`topic-status ${estado.toLowerCase()}`}>
                      {getTopicStatusText(estado)}
                    </span>
                  </div>
                  
                  <h3>{topic.titulo}</h3>
                  
                  {/* Renderizar descripción del tema con HTML */}
                  <div 
                    className="content-text topic-description"
                    dangerouslySetInnerHTML={{ __html: topic.descripcion }}
                  />
                  
                  {porcentajeAcierto > 0 && (
                    <div className="topic-score">
                      <span>Aciertos: {Math.round(porcentajeAcierto)}%</span>
                      {intentosRealizados > 1 && (
                        <span className="topic-attempts"> (Intento {intentosRealizados})</span>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : (
          <div className="no-topics">No hay temas disponibles en esta lección</div>
        )}
      </main>
    </div>
  );
};

export default LessonDetailPage;