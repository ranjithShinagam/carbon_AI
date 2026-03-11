import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Database, TrendingUp, BarChart3, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import api from '../api/api';

const InsightsPage = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const response = await api.get('/dataset-insights');
        setInsights(response.data);
      } catch (err) {
        setError('Failed to load dataset insights.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchInsights();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-80px)]">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-neon-green"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center h-[calc(100vh-80px)] text-red-400">
        <p>{error}</p>
      </div>
    );
  }

  // Format correlation data for Recharts
  const correlationData = insights ? Object.keys(insights.correlations).map(key => ({
    name: key.replace(/_/g, ' '),
    correlation: Number(insights.correlations[key].toFixed(3))
  })).sort((a, b) => b.correlation - a.correlation) : [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl font-extrabold text-white mb-4">
          Dataset <span className="text-neon-green">Insights</span>
        </h1>
        <p className="text-xl text-gray-300 mb-10">
          Deep dive into the underlying real-time carbon intelligence model powered by <span className="font-mono text-blue-300">trail_df.csv</span>
        </p>
      </motion.div>

      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <motion.div 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl"
        >
          <div className="flex items-center text-neon-green mb-4">
            <Database className="w-8 h-8 mr-3" />
            <h3 className="text-lg font-semibold text-white">Total Records</h3>
          </div>
          <p className="text-3xl font-bold text-white">{insights.total_records.toLocaleString()}</p>
          <p className="text-sm text-gray-400 mt-2">Historical data points</p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl"
        >
          <div className="flex items-center text-blue-400 mb-4">
            <TrendingUp className="w-8 h-8 mr-3" />
            <h3 className="text-lg font-semibold text-white">Max Target tCO₂e</h3>
          </div>
          <p className="text-3xl font-bold text-white">{insights.max.target.toFixed(2)} t</p>
          <p className="text-sm text-gray-400 mt-2">Peak emission recorded</p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl"
        >
          <div className="flex items-center text-purple-400 mb-4">
            <Activity className="w-8 h-8 mr-3" />
            <h3 className="text-lg font-semibold text-white">Average Output</h3>
          </div>
          <p className="text-3xl font-bold text-white">{insights.averages.Production.toLocaleString(undefined, { maximumFractionDigits: 0 })}</p>
          <p className="text-sm text-gray-400 mt-2">Mean production units</p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-xl"
        >
          <div className="flex items-center text-yellow-400 mb-4">
            <BarChart3 className="w-8 h-8 mr-3" />
            <h3 className="text-lg font-semibold text-white">Mean tCO₂e</h3>
          </div>
          <p className="text-3xl font-bold text-white">{insights.averages.target.toFixed(2)} t</p>
          <p className="text-sm text-gray-400 mt-2">Average target emission</p>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Correlation Chart */}
        <motion.div 
           initial={{ opacity: 0, scale: 0.95 }}
           animate={{ opacity: 1, scale: 1 }}
           transition={{ delay: 0.5 }}
           className="lg:col-span-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6"
        >
          <h2 className="text-2xl font-bold text-white mb-6">Feature Correlation to Emissions</h2>
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={correlationData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" horizontal={false} />
                <XAxis type="number" stroke="#ccc" tick={{fill: '#ccc'}} domain={[-1, 1]} />
                <YAxis dataKey="name" type="category" stroke="#ccc" tick={{fill: '#ccc', fontSize: 12}} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="correlation" radius={[0, 4, 4, 0]}>
                  {correlationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.correlation > 0 ? '#39FF14' : '#ef4444'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-sm text-gray-400 mt-4">
            Displays the Pearson correlation coefficient between internal features and the final target emission. Green indicates a positive correlation (drives emissions up), red indicates negative.
          </p>
        </motion.div>

        {/* Global Averages Table */}
        <motion.div 
           initial={{ opacity: 0, scale: 0.95 }}
           animate={{ opacity: 1, scale: 1 }}
           transition={{ delay: 0.6 }}
           className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6"
        >
          <h2 className="text-2xl font-bold text-white mb-6">Dataset Averages</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left text-gray-300">
              <thead className="text-xs text-gray-400 uppercase bg-black/20 border-b border-white/10">
                <tr>
                  <th scope="col" className="px-4 py-3">Feature</th>
                  <th scope="col" className="px-4 py-3 text-right">Mean Value</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(insights.averages).filter(k => k !== 'target').map((key, i) => (
                  <tr key={key} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="px-4 py-3 font-medium text-white">{key.replace(/_/g, ' ')}</td>
                    <td className="px-4 py-3 text-right text-neon-green">{insights.averages[key].toLocaleString(undefined, { maximumFractionDigits: 1 })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>

    </div>
  );
};

export default InsightsPage;
