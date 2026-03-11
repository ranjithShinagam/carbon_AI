import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

// Typical mock feature importance derived from the XGBoost model behavior on this dataset
const data = [
  { name: 'NonRenewable Energy', importance: 0.35 },
  { name: 'Production Output', importance: 0.25 },
  { name: 'Total Energy', importance: 0.15 },
  { name: 'Transport', importance: 0.12 },
  { name: 'Raw Material', importance: 0.08 },
  { name: 'Employees', importance: 0.05 },
];

const FeatureImportanceChart = () => {
  return (
    <div className="glass-card p-6 h-full flex flex-col">
      <h3 className="text-xl font-bold mb-6 text-neon-green">Feature Importance</h3>
      <div className="flex-1 w-full min-h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" horizontal={false} />
            <XAxis type="number" stroke="#f8fafc" />
            <YAxis dataKey="name" type="category" stroke="#f8fafc" width={120} fontSize={12} />
            <Tooltip 
              cursor={{fill: 'rgba(255,255,255,0.05)'}}
              contentStyle={{ backgroundColor: '#0b1121', borderColor: 'rgba(57,255,20,0.5)', borderRadius: '8px' }}
            />
            <Bar dataKey="importance" fill="#39ff14" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default FeatureImportanceChart;
