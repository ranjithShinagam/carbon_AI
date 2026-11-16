import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { PredictionProvider } from './context/PredictionContext';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import LandingPage from './pages/LandingPage';
import Dashboard from './pages/Dashboard';
import AboutPage from './pages/AboutPage';
import SectorAnalysisPage from './pages/SectorAnalysisPage';
import InsightsPage from './pages/InsightsPage';
import { LoginPage, RegisterPage } from './pages/AuthPages';
import DatasetChatbot from './components/DatasetChatbot';

function App() {
  return (
    <AuthProvider>
      <PredictionProvider>
        <Router>
          <div className="min-h-screen bg-deep-blue text-soft-white font-sans selection:bg-neon-green selection:text-deep-blue flex flex-col">
            <Navbar />
            <main className="flex-1 pt-20">
              <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/about" element={<AboutPage />} />
                <Route path="/sectors" element={<SectorAnalysisPage />} />
                <Route path="/insights" element={<InsightsPage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/dashboard" element={<Dashboard />} />
              </Routes>
            </main>
            <DatasetChatbot />
            <Footer />
          </div>
        </Router>
      </PredictionProvider>
    </AuthProvider>
  );
}

export default App;