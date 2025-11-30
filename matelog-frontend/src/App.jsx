import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AuthPage from './pages/AuthPage';
import LessonsPage from './pages/LessonsPage';
import LessonDetailPage from './pages/LessonDetailPage';
import TopicPage from './pages/TopicPage';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Ruta pública - Login/Registro */}
          <Route path="/" element={<AuthPage />} />
          
          {/* Rutas protegidas - requieren autenticación */}
          <Route
            path="/lecciones"
            element={
              <ProtectedRoute>
                <LessonsPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/leccion/:lessonId"
            element={
              <ProtectedRoute>
                <LessonDetailPage />
              </ProtectedRoute>
            }
          />
          
          <Route
            path="/tema/:topicId"
            element={
              <ProtectedRoute>
                <TopicPage />
              </ProtectedRoute>
            }
          />
          
          {/* Ruta por defecto - redirigir a auth */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
