import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

import { getModelInsights } from '../api/api';

const FEATURE_LABELS = {
  NonRenewable_Energy_Consumption_kWh: 'Non-Renewable Energy',
  Total_Energy_Consumption_kWh: 'Total Energy',
  Renewable_Energy_Consumption_kWh: 'Renewable Energy',
  Renewable_Energy_Share: 'Renewable Share',
  NonRenewable_Energy_Share: 'Non-Renewable Share',
  NonRenewable_Energy_Ratio: 'Non-Renewable Ratio',
  Energy_Per_Production: 'Energy / Unit',
  NRE_Per_Production: 'NRE / Unit',
  Transport_Intensity: 'Transport Intensity',
  Raw_Material_Intensity: 'Material Intensity',
  Energy_Per_Employee: 'Energy / Employee',
  Production_Output_Units: 'Production Output',
  Supply_Chain_Transport_km: 'Transport Distance',
  Raw_Material_Usage_kg: 'Raw Materials',
  Employment_Count: 'Employment',
};

const formatFeatureLabel = (raw) => {
  if (!raw) return 'Unknown';
  if (FEATURE_LABELS[raw]) return FEATURE_LABELS[raw];
  return raw
    .replace('Supply_Chain_Transport_Mode_', 'Mode: ')
    .replace('Industry_Sectors_', 'Industry: ')
    .replace('Sector_', 'Sector: ')
    .replace(/_/g, ' ');
};

const FeatureImportanceChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFeatureImportance = async () => {
      try {
        const response = await getModelInsights();
        const rawImportance =
          response?.feature_importance ||
          response?.model?.feature_importance ||
          [];

        const formatted = rawImportance
          .map((item) => {
            const rawName = item.feature ?? item.Feature;
            const val = Number(item.importance ?? item.Importance ?? 0);
            return {
              feature: formatFeatureLabel(rawName),
              importance: Number((val * 100).toFixed(2)),
            };
          })
          .filter((item) => item.importance > 0)
          .sort((a, b) => b.importance - a.importance)
          .slice(0, 8);

        setData(formatted);
      } catch (error) {
        console.error('Failed to load feature importance:', error);
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchFeatureImportance();
  }, []);

  const colors = ['#39ff14', '#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ec4899', '#06b6d4', '#a855f7'];

  return (
    <div className="glass-card p-6 h-full min-h-[300px] flex flex-col">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-white">XGBoost Feature Importance</h3>
        <p className="text-xs text-gray-400">Top emission drivers from the trained v2 model</p>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-neon-green" />
        </div>
      ) : data.length === 0 ? (
        <div className="flex-1 flex items-center justify-center">
          <p className="text-sm text-gray-400">Feature importance data is not available.</p>
        </div>
      ) : (
        <div className="flex-1 w-full min-h-[220px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={data} margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
              <XAxis type="number" stroke="#9ca3af" fontSize={12} unit="%" />
              <YAxis dataKey="feature" type="category" stroke="#e5e7eb" fontSize={11} width={130} />
              <Tooltip
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                contentStyle={{
                  backgroundColor: '#0b1121',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  color: '#fff',
                }}
                formatter={(value) => [`${value}%`, 'Importance']}
              />
              <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                {data.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default FeatureImportanceChart;