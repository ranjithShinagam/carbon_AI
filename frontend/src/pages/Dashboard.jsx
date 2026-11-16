import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

import PredictionForm from '../components/PredictionForm';
import DashboardCards from '../components/DashboardCards';
import FeatureImportanceChart from '../components/FeatureImportanceChart';
import EmissionGauge from '../components/EmissionGauge';
import HistoryTable from '../components/HistoryTable';
import BatchUploader from '../components/BatchUploader';
import BatchResultsTable from '../components/BatchResultsTable';

import { predictEmissions, getHistory, formatApiError } from '../api/api';
import { Sparkles, ArrowLeft, Layers, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { usePrediction } from '../context/PredictionContext';

import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ScatterTooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

const Dashboard = () => {
  const [results, setResults] = useState(null);
  const [inputs, setInputs] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasPredicted, setHasPredicted] = useState(false);
  const [history, setHistory] = useState([]);
  const [simulationMode, setSimulationMode] = useState('single');
  const [batchResults, setBatchResults] = useState(null);
  const [error, setError] = useState(null);

  const { user, token } = useAuth();
  const { setCurrentPrediction } = usePrediction();

  useEffect(() => {
    if (user && token) {
      loadHistory();
    }
  }, [user, token]);

  const loadHistory = async () => {
    try {
      const data = await getHistory(token);
      setHistory(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to load history:', err);
      setHistory([]);
    }
  };

  const handlePredict = async (data) => {
    setIsLoading(true);
    setError(null);
    setInputs(data);

    try {
      const response = await predictEmissions(data, token);
      if (!response || !response.prediction) {
        throw new Error('Invalid prediction response from backend.');
      }

      setResults(response.prediction);
      setCurrentPrediction(response.prediction);
      setHasPredicted(true);

      if (user && token) {
        await loadHistory();
      }
    } catch (err) {
      console.error('Prediction failed:', err);
      setError(
        formatApiError(
          err,
          'Prediction failed. Please make sure the backend is running.'
        )
      );
      setHasPredicted(false);
    } finally {
      setIsLoading(false);
    }
  };

  const scatterData = [];
  history.forEach((item) => {
    if (
      item.total_energy !== undefined &&
      item.predicted_co2_emission !== undefined
    ) {
      scatterData.push({
        energy: Number(item.total_energy),
        emission: Number(item.predicted_co2_emission),
        isCurrent: false,
      });
    }
  });

  if (hasPredicted && inputs && results) {
    scatterData.push({
      energy: Number(inputs.total_energy),
      emission: Number(results.predicted_co2),
      isCurrent: true,
    });
  }

  return (
    <div className="min-h-screen bg-deep-blue p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <Link
              to="/"
              className="inline-flex items-center text-blue-300 hover:text-neon-green transition-colors mb-2 text-sm font-medium"
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              Back to Home
            </Link>
            <h1 className="text-3xl font-extrabold text-white">
              Carbon Analytics Dashboard
            </h1>
          </div>

          <div className="flex bg-black/40 rounded-lg p-1 border border-white/10 self-start sm:self-auto">
            <button
              onClick={() => setSimulationMode('single')}
              className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                simulationMode === 'single'
                  ? 'bg-neon-green text-deep-blue shadow-lg'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <Layers className="w-4 h-4 mr-2" />
              Single Predict
            </button>
            <button
              onClick={() => setSimulationMode('batch')}
              className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                simulationMode === 'batch'
                  ? 'bg-neon-green text-deep-blue shadow-lg'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              <FileText className="w-4 h-4 mr-2" />
              Batch Upload (CSV)
            </button>
          </div>
        </header>

        {simulationMode === 'single' ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-4 flex flex-col">
              <PredictionForm
                onPredict={handlePredict}
                isLoading={isLoading}
                onChange={setInputs}
              />
            </div>

            <div className="lg:col-span-8 flex flex-col space-y-6">
              {error && (
                <div className="glass-card p-4 border border-red-500/30 bg-red-500/10">
                  <p className="text-red-300 text-sm">{error}</p>
                </div>
              )}

              {!hasPredicted ? (
                <div className="glass-card flex-1 min-h-[420px] flex flex-col items-center justify-center p-12 text-center border-dashed border-2 border-white/20">
                  <Sparkles className="w-16 h-16 text-blue-500/50 mb-4 animate-bounce" />
                  <h2 className="text-2xl font-bold text-white mb-2">
                    Predict Your Carbon Footprint
                  </h2>
                  <p className="text-blue-200 max-w-md">
                    Optionally pick Sector, Industry, and Transport Mode, adjust
                    the operational parameters on the left, and click Predict
                    Emissions.
                  </p>
                </div>
              ) : (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5 }}
                  className="flex flex-col space-y-6"
                >
                  <DashboardCards results={results} />

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <FeatureImportanceChart />
                    <EmissionGauge intensity={results.carbon_intensity} />
                  </div>

                  <div className="glass-card p-6 h-[320px] flex flex-col">
                    <h3 className="text-xl font-bold mb-4 text-white">
                      Energy vs Emission Trend
                    </h3>
                    <div className="flex-1 min-h-0">
                      {scatterData.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <ScatterChart
                            margin={{ top: 10, right: 20, bottom: 10, left: 0 }}
                          >
                            <CartesianGrid
                              strokeDasharray="3 3"
                              stroke="rgba(255,255,255,0.05)"
                            />
                            <XAxis
                              type="number"
                              dataKey="energy"
                              name="Energy (kWh)"
                              stroke="#f8fafc"
                            />
                            <YAxis
                              type="number"
                              dataKey="emission"
                              name="Emission (tCO₂e)"
                              stroke="#f8fafc"
                            />
                            <ScatterTooltip
                              cursor={{ strokeDasharray: '3 3' }}
                              contentStyle={{
                                backgroundColor: '#0b1121',
                                border: '1px solid rgba(255,255,255,0.1)',
                                borderRadius: '8px',
                              }}
                            />
                            <Scatter
                              data={scatterData}
                              fill="#39ff14"
                              shape="circle"
                            >
                              {scatterData.map((entry, index) => (
                                <Cell
                                  key={index}
                                  fill={
                                    entry.isCurrent
                                      ? '#ef4444'
                                      : 'rgba(57,255,20,0.4)'
                                  }
                                />
                              ))}
                            </Scatter>
                          </ScatterChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="h-full flex items-center justify-center">
                          <p className="text-blue-200/60 text-sm">
                            No prediction history available yet.
                          </p>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="glass-card p-6 border-l-4 border-neon-green">
                    <h4 className="flex items-center text-lg font-bold text-white mb-2">
                      <Sparkles className="w-5 h-5 mr-2 text-neon-green" />
                      Prediction Summary
                    </h4>
                    <p className="text-blue-100">
                      Your model predicted{' '}
                      <span className="font-bold text-neon-green">
                        {results.predicted_co2.toFixed(2)} tCO₂e
                      </span>{' '}
                      of carbon emissions
                      {results.sector ? ` for ${results.sector}` : ''}
                      {results.industry_sector
                        ? ` (${results.industry_sector})`
                        : ''}
                      .
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4">
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-gray-400">Renewable Share</p>
                        <p className="text-lg font-bold text-white">
                          {(results.renewable_energy_ratio * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-gray-400">
                          Non-Renewable Share
                        </p>
                        <p className="text-lg font-bold text-white">
                          {(results.nonrenewable_energy_ratio * 100).toFixed(1)}
                          %
                        </p>
                      </div>
                      <div className="bg-white/5 rounded-lg p-3">
                        <p className="text-xs text-gray-400">
                          Energy / Employee
                        </p>
                        <p className="text-lg font-bold text-white">
                          {results.energy_per_employee.toFixed(2)} kWh
                        </p>
                      </div>
                    </div>
                  </div>

                  {user && history.length > 0 && (
                    <HistoryTable history={history} />
                  )}
                </motion.div>
              )}
            </div>
          </div>
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="w-full flex flex-col"
          >
            <div className="min-h-[380px]">
              <BatchUploader onBatchComplete={setBatchResults} />
            </div>
            {batchResults && <BatchResultsTable results={batchResults} />}
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;