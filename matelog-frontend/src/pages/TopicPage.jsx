import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { lessonService } from '../api/lessonService';
import { trackingService } from '../api/trackingService';
import { useScreenTracking } from '../hooks/useScreenTracking';
import './TopicPage.css';

const TopicPage = () => {
  const [topic, setTopic] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showingExercises, setShowingExercises] = useState(false);
  const [currentExercise, setCurrentExercise] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [showHelp, setShowHelp] = useState({});
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(true);
  const [startTimes, setStartTimes] = useState({});
  // NUEVO: Historial de navegación
  const [navigationHistory, setNavigationHistory] = useState([0]);

  const { topicId } = useParams();
  const navigate = useNavigate();
  
  // Tracking de pantalla - obtener activityId
  const { activityId } = useScreenTracking(
    showingExercises ? 'EJERCICIOS' : 'CONTENIDO_TEMA', 
    { tema_id: parseInt(topicId) }
  );

  useEffect(() => {
    loadTopic();
  }, [topicId]);

  useEffect(() => {
    if (showingExercises && topic) {
      const exerciseId = topic.ejercicios[currentExercise]?.id;
      if (exerciseId && !startTimes[exerciseId]) {
        setStartTimes(prev => ({ ...prev, [exerciseId]: Date.now() }));
      }
    }
  }, [showingExercises, currentExercise, topic]);

  const loadTopic = async () => {
    try {
      const data = await lessonService.getTopicContent(topicId);
      setTopic(data);

      // Modificación 6: Cargar respuestas previas y posicionar en siguiente sin responder
      if (data.ejercicios_respondidos && Object.keys(data.ejercicios_respondidos).length > 0) {
        const prevAnswers = {};
        const prevResults = {};
        
        data.ejercicios.forEach(ejercicio => {
          if (data.ejercicios_respondidos[ejercicio.id]) {
            const resp = data.ejercicios_respondidos[ejercicio.id];
            prevAnswers[ejercicio.id] = resp.respuesta_usuario;
            prevResults[ejercicio.id] = {
              es_correcta: resp.es_correcta,
              retroalimentacion: resp.es_correcta 
                ? ejercicio.retroalimentacion_correcta 
                : ejercicio.retroalimentacion_incorrecta
            };
          }
        });
        
        setUserAnswers(prevAnswers);
        setResults(prevResults);
      }
    } catch (err) {
      alert('Error al cargar el tema');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // MODIFICADO: Volver al contenido anterior en el historial
  const handleVolverClick = async () => {
    if (activityId && navigationHistory.length > 1) {
      try {
        await trackingService.registerVolverContenido(activityId);
      } catch (error) {
        console.error('Error al registrar volver:', error);
      }
    }
    
    // Volver al índice anterior en el historial
    if (navigationHistory.length > 1) {
      const newHistory = [...navigationHistory];
      newHistory.pop(); // Eliminar el índice actual
      const previousIndex = newHistory[newHistory.length - 1];
      
      setNavigationHistory(newHistory);
      setCurrentIndex(previousIndex);
    }
  };

  // MODIFICADO: Agregar al historial al avanzar
  const navigateToIndex = (newIndex) => {
    setNavigationHistory(prev => [...prev, newIndex]);
    setCurrentIndex(newIndex);
  };

  // Modificación 5: Ir directamente a ejercicios
  const handleGoToExercises = () => {
    // Modificación 6: Posicionar en el siguiente ejercicio sin responder
    if (topic.siguiente_ejercicio_index !== undefined) {
      setCurrentExercise(topic.siguiente_ejercicio_index);
    }
    setShowingExercises(true);
  };

  // MODIFICADO: Usar navigateToIndex
  const handleContinue = () => {
    if (currentIndex < topic.contenidos.length - 1) {
      const nextContent = topic.contenidos[currentIndex + 1];
      if (nextContent.tipo === 'EJEMPLO_EXTRA') {
        return; // No avanza automáticamente si es ejemplo extra
      }
      navigateToIndex(currentIndex + 1);
    } else {
      // Modificación 6: Al ir a ejercicios por última vez, posicionar correctamente
      if (topic.siguiente_ejercicio_index !== undefined) {
        setCurrentExercise(topic.siguiente_ejercicio_index);
      }
      setShowingExercises(true);
    }
  };

  // MODIFICADO: Usar navigateToIndex
  const handleShowExtraExample = () => {
    if (currentIndex < topic.contenidos.length - 1) {
      navigateToIndex(currentIndex + 1);
    }
  };

  // MODIFICADO: Usar navigateToIndex
  const handleSkipExtraExamples = () => {
    let nextIndex = currentIndex + 1;
    while (nextIndex < topic.contenidos.length && 
           topic.contenidos[nextIndex].tipo === 'EJEMPLO_EXTRA') {
      nextIndex++;
    }
    
    if (nextIndex < topic.contenidos.length) {
      navigateToIndex(nextIndex);
    } else {
      // Modificación 6: Posicionar en siguiente ejercicio sin responder
      if (topic.siguiente_ejercicio_index !== undefined) {
        setCurrentExercise(topic.siguiente_ejercicio_index);
      }
      setShowingExercises(true);
    }
  };

  const handleAnswerChange = (exerciseId, value) => {
    setUserAnswers(prev => ({ ...prev, [exerciseId]: value }));
  };

  const handleSubmitAnswer = async () => {
    const exercise = topic.ejercicios[currentExercise];
    const answer = userAnswers[exercise.id];

    if (!answer || answer.trim() === '') {
      alert('Por favor ingresa una respuesta');
      return;
    }

    const timeElapsed = startTimes[exercise.id] 
      ? Math.floor((Date.now() - startTimes[exercise.id]) / 1000)
      : 0;

    try {
      const result = await lessonService.validateAnswer({
        ejercicio_id: exercise.id,
        respuesta: answer,
        uso_ayuda: !!showHelp[exercise.id],
        tiempo_respuesta_segundos: timeElapsed,
      });

      setResults(prev => ({ ...prev, [exercise.id]: result }));
    } catch (err) {
      alert('Error al validar respuesta');
      console.error(err);
    }
  };

  const handleNextExercise = () => {
    if (currentExercise < topic.ejercicios.length - 1) {
      setCurrentExercise(currentExercise + 1);
    } else {
      handleFinishExercises();
    }
  };


  const handleFinishExercises = async () => {
  try {
    const result = await lessonService.finalizeTopic(topicId);
    
    if (result.aprobado) {
      // APROBADO: 80% o más
      const mensaje = result.siguiente_tema_id 
        ? `¡Felicidades! Obtuviste ${Math.round(result.porcentaje_acierto)}% de calificación.\n\n¿Deseas avanzar al siguiente tema?`
        : `¡Felicidades! Obtuviste ${Math.round(result.porcentaje_acierto)}% de calificación.\n\nHas completado todos los temas de esta lección.`;
      
      const continuar = window.confirm(mensaje);
      
      if (continuar && result.siguiente_tema_id) {
        // Ir al siguiente tema
        navigate(`/tema/${result.siguiente_tema_id}`);
      } else {
        // Volver a la lista de lecciones
        navigate(`/leccion/${result.leccion_id}`);
      }
    } else {
      // REPROBADO: Menos de 80%
      const mejora_texto = result.numero_intento > 1 && result.mejora_porcentaje !== null
        ? `\n\nMejoraste ${result.mejora_porcentaje > 0 ? '+' : ''}${Math.round(result.mejora_porcentaje)}% respecto a tu intento anterior.`
        : '';
      
      const mensaje = `Obtuviste ${Math.round(result.porcentaje_acierto)}% de calificación.\nNecesitas mínimo 80% para avanzar.${mejora_texto}\n\n¿Deseas volver a intentarlo?`;
      
      const reintentar = window.confirm(mensaje);
      
      if (reintentar) {
        // Llamar al endpoint de reintentar (borra respuestas del backend)
        try {
          await lessonService.retryTopic(topicId);
          
          // Resetear estado del frontend
          setShowingExercises(false);
          setCurrentIndex(0);
          setCurrentExercise(0);
          setUserAnswers({});
          setShowHelp({});
          setResults({});
          setStartTimes({});
          setNavigationHistory([0]);
          
          // Recargar el tema con datos frescos
          await loadTopic();
        } catch (error) {
          console.error('Error al reintentar:', error);
          alert('Error al reintentar el tema. Por favor intenta de nuevo.');
        }
      } else {
        // Volver a la lista de lecciones
        navigate(`/leccion/${result.leccion_id}`);
      }
    }
  } catch (err) {
    console.error('Error al finalizar tema:', err);
    alert('Error al finalizar tema. Por favor intenta de nuevo.');
  }
};
  /*const handleFinishExercises = async () => {
    try {
      const result = await lessonService.finalizeTopic(topicId);
      
      if (result.tema_completado) {
        alert(`¡Felicidades! Has completado el tema con ${Math.round(result.porcentaje_acierto)}% de aciertos`);
        navigate(`/leccion/${result.leccion_id}`);
      } else {
        const reintentar = window.confirm(
          `Obtuviste ${Math.round(result.porcentaje_acierto)}% de aciertos.\n` +
          `Necesitas al menos 80% para desbloquear el siguiente tema.\n\n` +
          `¿Deseas reintentar el tema?`
        );
        
        if (reintentar) {
          setShowingExercises(false);
          setCurrentIndex(0);
          setCurrentExercise(0);
          setUserAnswers({});
          setShowHelp({});
          setResults({});
          setStartTimes({});
          setNavigationHistory([0]); // Resetear historial
        } else {
          navigate(`/leccion/${result.leccion_id}`);
        }
      }
    } catch (err) {
      console.error('Error al finalizar tema:', err);
      alert('Error al finalizar tema. Por favor intenta de nuevo.');
    }
  };
*/
  const handleBackToTopic = async () => {
    try {
      await lessonService.returnToTopic(topicId);
      setShowingExercises(false);
      setCurrentIndex(0);
      setNavigationHistory([0]); // Resetear historial
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="topic-container"><div className="loading">Cargando...</div></div>;
  }

  if (!topic) {
    return <div className="topic-container"><div className="error-box">Tema no encontrado</div></div>;
  }

  // Vista de contenido (teoría/ejemplos)
  if (!showingExercises) {
    const currentContent = topic.contenidos[currentIndex];
    const hasNextExtraExample = currentIndex < topic.contenidos.length - 1 && 
                                 topic.contenidos[currentIndex + 1]?.tipo === 'EJEMPLO_EXTRA';

    return (
      <div className="topic-container">
        <header className="topic-header">
          <button onClick={() => navigate(-1)} className="back-btn">← Salir</button>
          <h1>{topic.titulo}</h1>
        </header>

        <div className="content-box">
          <div className="content-type-badge">{currentContent.tipo_display}</div>
          <div 
            className="content-text" 
            dangerouslySetInnerHTML={{ __html: currentContent.contenido_texto }}
          />

        </div>

        <div className="navigation-buttons">
          {/* Modificación 4: Botón Volver - solo si hay historial */}
          {navigationHistory.length > 1 && (
            <button onClick={handleVolverClick} className="btn btn-secondary">
              ← Volver
            </button>
          )}
          
          {hasNextExtraExample ? (
            <>
              <button onClick={handleShowExtraExample} className="btn btn-secondary">
                Ver Otro Ejemplo
              </button>
              <button onClick={handleSkipExtraExamples} className="btn btn-primary">
                Continuar
              </button>
            </>
          ) : (
            <button onClick={handleContinue} className="btn btn-primary">
              {currentIndex < topic.contenidos.length - 1 ? 'Continuar' : 'Ir a Ejercicios'}
            </button>
          )}

          {/* Modificación 5: Botón "Ir a Ejercicios" - visible solo cuando NO es la última pantalla */}
          {currentIndex < topic.contenidos.length - 1 && (
            <button onClick={handleGoToExercises} className="btn btn-accent">
              📝 Ir a Ejercicios
            </button>
          )}
        </div>

        {/* Modificación 6: Mostrar progreso de ejercicios si hay respuestas previas */}
        {topic.total_ejercicios_respondidos > 0 && (
          <div className="exercise-progress-info">
            Ya has respondido {topic.total_ejercicios_respondidos} de {topic.ejercicios.length} ejercicios.
            {topic.siguiente_ejercicio_index < topic.ejercicios.length && (
              <span> Continuarás desde el ejercicio {topic.siguiente_ejercicio_index + 1}.</span>
            )}
          </div>
        )}

        <div className="progress-indicator">
          {currentIndex + 1} / {topic.contenidos.length}
        </div>
      </div>
    );
  }

  // Vista de ejercicios
  const exercise = topic.ejercicios[currentExercise];
  const result = results[exercise.id];

  return (
    <div className="topic-container">
      <header className="topic-header">
        <button onClick={handleBackToTopic} className="back-btn">← Volver al Tema</button>
        <h1>Ejercicios - {topic.titulo}</h1>
      </header>

      <div className="exercise-box">
        <div className="exercise-header-row">
          <div className="exercise-number">Ejercicio {exercise.orden}</div>
          {exercise.mostrar_dificultad && (
            <div className="exercise-difficulty">{exercise.dificultad_display}</div>
          )}
        </div>
        
        <div className="exercise-instruction">{exercise.instruccion}</div>
        <div 
          className="exercise-question" 
          dangerouslySetInnerHTML={{ __html: exercise.enunciado }}
        />
        


        {!result && (
          <>
            {exercise.tipo === 'MULTIPLE' ? (
              <div className="options-list">
                {exercise.opciones.map(option => (
                  <label key={option.letra} className="option-item">
                    <input
                      type="radio"
                      name="answer"
                      value={option.letra}
                      checked={userAnswers[exercise.id] === option.letra}
                      onChange={(e) => handleAnswerChange(exercise.id, e.target.value)}
                    />
                    <span>{option.letra}. {option.texto}</span>
                  </label>
                ))}
              </div>
            ) : (
              <input
                type="text"
                className="answer-input"
                placeholder="Tu respuesta..."
                value={userAnswers[exercise.id] || ''}
                onChange={(e) => handleAnswerChange(exercise.id, e.target.value)}
              />
            )}

            {exercise.tiene_ayuda && (
              <button 
                onClick={() => setShowHelp(prev => ({ ...prev, [exercise.id]: !prev[exercise.id] }))}
                className="help-btn"
              >
                {showHelp[exercise.id] ? 'Ocultar Ayuda' : 'Ver Ayuda'}
              </button>
            )}

            {showHelp[exercise.id] && (
              <div className="help-box">{exercise.texto_ayuda}</div>
            )}

            <button onClick={handleSubmitAnswer} className="btn btn-primary submit-btn">
              Enviar Respuesta
            </button>
          </>
        )}

        {result && (
          <div className={`result-box ${result.es_correcta ? 'correct' : 'incorrect'}`}>
            <h3>{result.es_correcta ? '¡Correcto!' : 'Incorrecto'}</h3>
            
            {!result.es_correcta && exercise.texto_ayuda && !showHelp[exercise.id] && (
              <div className="auto-help-box">
                <p className="auto-help-title">💡 Ayuda:</p>
                <p>{exercise.texto_ayuda}</p>
              </div>
            )}

            {result.retroalimentacion && (
              <p className="feedback">{result.retroalimentacion}</p>
            )}

            <button onClick={handleNextExercise} className="btn btn-primary next-btn">
              {currentExercise < topic.ejercicios.length - 1 ? 'Siguiente Ejercicio' : 'Finalizar Tema'}
            </button>
          </div>
        )}
      </div>

      <div className="progress-indicator">
        Ejercicio {currentExercise + 1} / {topic.ejercicios.length}
      </div>
    </div>
  );
};

export default TopicPage;