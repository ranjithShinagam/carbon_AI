import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

const EmissionGauge = ({ intensity = 0 }) => {
  // Normalize intensity to a 0-1 range for the gauge display (假设 max reasonable intensity is 5 tCO2/unit)
  const maxIntensity = 5.0;
  const value = Math.min(intensity, maxIntensity);
  const remainder = maxIntensity - value;

  const data = [
    { name: 'Intensity', value: value },
    { name: 'Remaining', value: remainder }
  ];

  const COLORS = ['#39ff14', 'rgba(255,255,255,0.1)'];

  // Change color based on severity
  if (value > 3) COLORS[0] = '#ef4444'; // Red
  else if (value > 1.5) COLORS[0] = '#eab308'; // Yellow

  return (
    <div className="glass-card p-6 flex flex-col justify-center items-center h-full">
      <h3 className="text-xl font-bold text-blue-100 self-start w-full mb-2">Carbon Intensity</h3>
      <div className="w-full aspect-square max-h-[200px] relative">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="70%"
              startAngle={180}
              endAngle={0}
              innerRadius="70%"
              outerRadius="90%"
              paddingAngle={0}
              dataKey="value"
              stroke="none"
              cornerRadius={4}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-x-0 bottom-[10%] flex flex-col items-center">
          <span className="text-2xl font-bold text-white">{intensity.toFixed(2)}</span>
          <span className="text-xs text-blue-200">tCO₂e / unit</span>
        </div>
      </div>
    </div>
  );
};

export default EmissionGauge;
