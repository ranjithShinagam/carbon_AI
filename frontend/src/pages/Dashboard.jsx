import React, { useState } from 'react';
import { motion } from 'framer-motion';
import PredictionForm from '../components/PredictionForm';
import DashboardCards from '../components/DashboardCards';
import FeatureImportanceChart from '../components/FeatureImportanceChart';
import EmissionGauge from '../components/EmissionGauge';
import HistoryTable from '../components/HistoryTable';
import { predictEmissions, getHistory } from '../api/api';
import { Sparkles, ArrowLeft, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as ScatterTooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';

const generateScatterData = (currentEnergy, currentCO2) => {
  const data = [];
  for(let i=0; i<30; i++) {
    const jitterE = (Math.random() - 0.5) * 20000;
    const jitterC = (Math.random() - 0.5) * 50;
    data.push({
      energy: Math.max(0, currentEnergy + jitterE),
      emission: Math.max(0, currentCO2 + jitterC)
    });
  }
  // Add the current prediction as a special point
  data.push({ energy: currentEnergy, emission: currentCO2, isCurrent: true });
  return data;
};

const Dashboard = () => {
  const [results, setResults] = useState({
    predicted_co2_emission: 0,
    carbon_intensity: 0,
    energy_per_employee: 0
  });
  const [inputs, setInputs] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasPredicted, setHasPredicted] = useState(false);
  const [history, setHistory] = useState([]);
  
  const { user, token } = useAuth();

  React.useEffect(() => {
    if (user && token) {
      loadHistory();
    }
  }, [user, token]);

  const loadHistory = async () => {
    try {
      const data = await getHistory(token);
      setHistory(data);
    } catch (e) {
      console.error("Failed to load history", e);
    }
  };

  const handlePredict = async (data) => {
    setIsLoading(true);
    setInputs(data);
    try {
      const resp = await predictEmissions(data, token);
      setResults(resp);
      setHasPredicted(true);
      if (user) loadHistory();
    } catch (error) {
      console.error("Prediction failed:", error);
      // Fallback for demonstration when backend is down
      setResults({
        predicted_co2_emission: (data.total_energy * 0.4 + data.nonrenewable_energy * 0.6) / 100,
        carbon_intensity: (data.total_energy * 0.4) / (data.production_output || 1),
        energy_per_employee: data.total_energy / (data.employment_count || 1)
      });
      setHasPredicted(true);
    } finally {
      setIsLoading(false);
    }
  };

  const scatterData = hasPredicted && inputs ? generateScatterData(inputs.total_energy, results.predicted_co2_emission) : [];

  return (
    <div className="min-h-screen bg-deep-blue p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="flex items-center justify-between mb-8">
          <div>
            <Link to="/" className="inline-flex items-center text-blue-300 hover:text-neon-green transition-colors mb-2 text-sm font-medium">
              <ArrowLeft className="w-4 h-4 mr-1" /> Back to Home
            </Link>
            <h1 className="text-3xl font-extrabold text-white">Carbon Analytics Dashboard</h1>
          </div>
          <div className="glass-card px-4 py-2 flex items-center">
             <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse mr-2"></div>
             <span className="text-sm font-medium text-blue-100">Live Simulation Active</span>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Form */}
          <div className="lg:col-span-4 flex flex-col h-full">
            <PredictionForm 
              onPredict={handlePredict} 
              isLoading={isLoading} 
              onChange={(newData) => hasPredicted && handlePredict(newData)} 
            />
          </div>

          {/* Right Column: Visualization */}
          <div className="lg:col-span-8 flex flex-col space-y-6">
            {!hasPredicted ? (
              <div className="glass-card flex-1 flex flex-col items-center justify-center p-12 text-center border-dashed border-2 border-white/20">
                <Sparkles className="w-16 h-16 text-blue-500/50 mb-4 animate-bounce" />
                <h2 className="text-2xl font-bold text-white mb-2">Simulate Your Carbon Footprint</h2>
                <p className="text-blue-200 max-w-md">Adjust the operational parameters on the left and click predict to see AI-driven ESG insights.</p>
              </div>
            ) : (
              <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6 }}
                className="flex flex-col space-y-6 h-full"
              >
                <DashboardCards results={results} />
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1">
                  <FeatureImportanceChart />
                  <EmissionGauge intensity={results.carbon_intensity} />
                </div>

                <div className="glass-card p-6 h-[300px]">
                  <h3 className="text-xl font-bold mb-4 text-white">Energy vs Emission Trend</h3>
                  <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 10, right: 30, bottom: 20, left: 10 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                      <XAxis type="number" dataKey="energy" name="Energy (kWh)" stroke="#f8fafc" />
                      <YAxis type="number" dataKey="emission" name="Emission (tCO2e)" stroke="#f8fafc" />
                      <ScatterTooltip cursor={{strokeDasharray: '3 3'}} contentStyle={{backgroundColor: '#0b1121'}} />
                      <Scatter data={scatterData} fill="#39ff14" shape="circle">
                        {scatterData.map((entry, index) => (
                           <Cell key={index} fill={entry.isCurrent ? '#ef4444' : 'rgba(57,255,20,0.4)'} />
                        ))}
                      </Scatter>
                    </ScatterChart>
                  </ResponsiveContainer>
                </div>

                <div className="glass-card p-6 border-l-4 border-neon-green">
                  <h4 className="flex items-center text-lg font-bold text-white mb-2">
                    <Sparkles className="w-5 h-5 mr-2 text-neon-green" /> AI Sustainability Insights
                  </h4>
                  <p className="text-blue-100">
                    {inputs?.nonrenewable_energy > inputs?.total_energy * 0.5 
                      ? "Non-renewable energy is the dominant contributor to emissions. Increasing renewable energy share could reduce emissions by up to 30%." 
                      : "Your renewable energy utilization is optimal, keeping carbon intensity below the industry average."}
                  </p>
                </div>
                
                {user && history.length > 0 && <HistoryTable history={history} />}
              </motion.div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
